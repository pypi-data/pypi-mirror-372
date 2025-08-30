"""
NAKALA Pre-population Assistant

Intelligently pre-populates metadata templates based on user context, existing data,
and file analysis. Part of the Complete Metadata Management System - Intelligence Phase.
"""

import logging
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .templates import MetadataTemplate, TemplateField
from .vocabulary import NakalaVocabularyService
from .user_info import NakalaUserInfoClient
from .common.utils import NakalaCommonUtils

logger = logging.getLogger(__name__)


@dataclass
class PrePopulationResult:
    """Result of pre-population analysis."""

    template: MetadataTemplate
    populated_fields: Dict[str, Any]
    confidence_scores: Dict[str, float]
    suggestions: Dict[str, List[str]]
    analysis_notes: List[str]
    processing_time: float


@dataclass
class UserContext:
    """Comprehensive user context for pre-population."""

    user_id: str
    name: Optional[str] = None
    affiliation: Optional[str] = None
    orcid: Optional[str] = None
    default_language: str = "en"
    recent_projects: List[Dict[str, Any]] = None
    common_keywords: List[str] = None
    preferred_licenses: List[str] = None
    frequent_collaborators: List[str] = None
    domain_expertise: List[str] = None
    geographic_focus: Optional[str] = None
    historical_period: Optional[str] = None

    def __post_init__(self):
        if self.recent_projects is None:
            self.recent_projects = []
        if self.common_keywords is None:
            self.common_keywords = []
        if self.preferred_licenses is None:
            self.preferred_licenses = []
        if self.frequent_collaborators is None:
            self.frequent_collaborators = []
        if self.domain_expertise is None:
            self.domain_expertise = []


class UserContextService:
    """Service for building and managing user context."""

    def __init__(self, user_client: NakalaUserInfoClient):
        self.user_client = user_client
        self.utils = NakalaCommonUtils()

    async def build_user_context(self, api_key: str) -> UserContext:
        """Build comprehensive user context from available data."""
        logger.info("Building user context for pre-population")

        try:
            # Get basic user profile
            user_profile = self.user_client.get_complete_user_profile()

            context = UserContext(
                user_id=self._extract_user_id(api_key),
                name=self._extract_user_name(user_profile),
                default_language=self._detect_default_language(user_profile),
            )

            # Analyze user's existing data for patterns
            if user_profile.get("datasets"):
                await self._analyze_datasets(context, user_profile["datasets"])

            if user_profile.get("collections"):
                await self._analyze_collections(context, user_profile["collections"])

            # Extract domain expertise from keywords and titles
            context.domain_expertise = self._extract_domain_expertise(user_profile)

            # Detect geographic and temporal patterns
            context.geographic_focus = self._detect_geographic_focus(user_profile)
            context.historical_period = self._detect_historical_period(user_profile)

            logger.info(
                f"Built user context with {len(context.common_keywords)} keywords, "
                f"{len(context.preferred_licenses)} licenses, "
                f"{len(context.frequent_collaborators)} collaborators"
            )

            return context

        except Exception as e:
            logger.warning(f"Failed to build complete user context: {e}")
            # Return minimal context
            return UserContext(
                user_id=self._extract_user_id(api_key), default_language="en"
            )

    def _extract_user_id(self, api_key: str) -> str:
        """Extract or generate user ID from API key."""
        # Create a hash of the API key for consistent user identification
        return hashlib.md5(api_key.encode()).hexdigest()[:12]

    def _extract_user_name(self, user_profile: Dict[str, Any]) -> Optional[str]:
        """Extract user name from profile data."""
        # Look for name in various possible locations
        name_sources = [
            user_profile.get("user", {}).get("name"),
            user_profile.get("user", {}).get("fullName"),
            user_profile.get("user", {}).get("displayName"),
        ]

        for name in name_sources:
            if name and isinstance(name, str) and len(name.strip()) > 0:
                return name.strip()

        return None

    def _detect_default_language(self, user_profile: Dict[str, Any]) -> str:
        """Detect user's default language from their data."""
        language_counts = {}

        # Analyze language usage in datasets and collections
        all_items = user_profile.get("datasets", []) + user_profile.get(
            "collections", []
        )

        for item in all_items:
            metas = item.get("metas", [])
            for meta in metas:
                lang = meta.get("lang", "en")
                language_counts[lang] = language_counts.get(lang, 0) + 1

        # Return most common language, default to English
        if language_counts:
            return max(language_counts, key=language_counts.get)

        return "en"

    async def _analyze_datasets(
        self, context: UserContext, datasets: List[Dict[str, Any]]
    ):
        """Analyze user's datasets for patterns."""
        for dataset in datasets[-10:]:  # Analyze last 10 datasets
            metas = dataset.get("metas", [])

            # Extract keywords
            for meta in metas:
                if "subject" in meta.get("propertyUri", "").lower():
                    value = meta.get("value", "")
                    if value:
                        keywords = [k.strip() for k in value.split(";") if k.strip()]
                        context.common_keywords.extend(keywords)

            # Extract licenses
            for meta in metas:
                if "license" in meta.get("propertyUri", "").lower():
                    license_value = meta.get("value", "")
                    if (
                        license_value
                        and license_value not in context.preferred_licenses
                    ):
                        context.preferred_licenses.append(license_value)

            # Extract creators/contributors for collaboration patterns
            for meta in metas:
                if (
                    "creator" in meta.get("propertyUri", "").lower()
                    or "contributor" in meta.get("propertyUri", "").lower()
                ):
                    creator = meta.get("value", "")
                    if creator and creator not in context.frequent_collaborators:
                        context.frequent_collaborators.append(creator)

        # Keep only most common items
        context.common_keywords = self._get_most_common(context.common_keywords, 20)
        context.preferred_licenses = self._get_most_common(
            context.preferred_licenses, 5
        )
        context.frequent_collaborators = self._get_most_common(
            context.frequent_collaborators, 10
        )

    async def _analyze_collections(
        self, context: UserContext, collections: List[Dict[str, Any]]
    ):
        """Analyze user's collections for organizational patterns."""
        # Extract project patterns from collection titles and descriptions
        for collection in collections[-5:]:  # Analyze last 5 collections
            title = self._extract_meta_value(collection.get("metas", []), "title")
            if title:
                context.recent_projects.append(
                    {
                        "id": collection.get("identifier"),
                        "title": title,
                        "created": collection.get("created", ""),
                    }
                )

    def _extract_domain_expertise(self, user_profile: Dict[str, Any]) -> List[str]:
        """Extract domain expertise from keywords and titles."""
        all_text = []

        # Collect all textual content
        all_items = user_profile.get("datasets", []) + user_profile.get(
            "collections", []
        )
        for item in all_items:
            metas = item.get("metas", [])
            for meta in metas:
                if meta.get("value"):
                    all_text.append(str(meta["value"]))

        # Extract domain terms using simple keyword analysis
        domain_terms = set()
        combined_text = " ".join(all_text).lower()

        # Academic domain keywords
        academic_domains = {
            "archaeology": ["archaeology", "archaeological", "artifact", "excavation"],
            "history": ["history", "historical", "archive", "manuscript"],
            "linguistics": ["linguistics", "language", "corpus", "phonetic"],
            "art_history": ["art", "painting", "sculpture", "museum"],
            "anthropology": ["anthropology", "cultural", "ethnographic", "social"],
            "literature": ["literature", "literary", "text", "narrative"],
            "philosophy": ["philosophy", "philosophical", "ethics", "theory"],
            "geography": ["geography", "spatial", "location", "mapping"],
            "sociology": ["sociology", "society", "community", "behavior"],
        }

        for domain, keywords in academic_domains.items():
            if any(keyword in combined_text for keyword in keywords):
                domain_terms.add(domain)

        return list(domain_terms)[:5]  # Limit to top 5

    def _detect_geographic_focus(self, user_profile: Dict[str, Any]) -> Optional[str]:
        """Detect geographic focus from spatial metadata."""
        geographic_terms = []

        all_items = user_profile.get("datasets", []) + user_profile.get(
            "collections", []
        )
        for item in all_items:
            metas = item.get("metas", [])
            for meta in metas:
                if (
                    "coverage" in meta.get("propertyUri", "").lower()
                    or "spatial" in meta.get("propertyUri", "").lower()
                ):
                    value = meta.get("value", "")
                    if value:
                        geographic_terms.append(value)

        # Return most common geographic term
        if geographic_terms:
            return self._get_most_common(geographic_terms, 1)[0]

        return None

    def _detect_historical_period(self, user_profile: Dict[str, Any]) -> Optional[str]:
        """Detect historical period focus from temporal metadata."""
        dates = []

        all_items = user_profile.get("datasets", []) + user_profile.get(
            "collections", []
        )
        for item in all_items:
            metas = item.get("metas", [])
            for meta in metas:
                if (
                    "temporal" in meta.get("propertyUri", "").lower()
                    or "date" in meta.get("propertyUri", "").lower()
                ):
                    value = meta.get("value", "")
                    if value:
                        # Extract years from date strings
                        years = re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", value)
                        dates.extend(years)

        if dates:
            years = [int(year) for year in dates]
            max_year = max(years)

            # Categorize historical periods
            if max_year < 1500:
                return "medieval"
            elif max_year < 1800:
                return "early_modern"
            elif max_year < 1900:
                return "19th_century"
            elif max_year < 2000:
                return "20th_century"
            else:
                return "contemporary"

        return None

    def _extract_meta_value(
        self, metas: List[Dict], property_name: str, language: str = "en"
    ) -> str:
        """Extract metadata value by property name."""
        for meta in metas:
            property_uri = meta.get("propertyUri", "")
            if property_name.lower() in property_uri.lower():
                return meta.get("value", "")
        return ""

    def _get_most_common(self, items: List[str], limit: int) -> List[str]:
        """Get most common items from a list."""
        from collections import Counter

        if not items:
            return []
        counts = Counter(items)
        return [item for item, count in counts.most_common(limit)]


class FileMetadataExtractor:
    """Extracts metadata from files for pre-population."""

    def __init__(self):
        self.utils = NakalaCommonUtils()

    async def extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a file."""
        file_path = Path(file_path)

        metadata = {
            "file_name": file_path.name,
            "file_size": None,
            "mime_type": None,
            "suggested_title": None,
            "suggested_description": None,
            "suggested_keywords": [],
            "suggested_type": None,
            "technical_metadata": {},
        }

        try:
            if file_path.exists():
                metadata["file_size"] = file_path.stat().st_size
                metadata["mime_type"] = self._detect_mime_type(file_path)
                metadata["suggested_type"] = self._suggest_resource_type(
                    metadata["mime_type"]
                )

            # Generate suggestions based on filename
            metadata["suggested_title"] = self._generate_title_from_filename(
                file_path.name
            )
            metadata["suggested_description"] = (
                self._generate_description_from_filename(file_path.name)
            )
            metadata["suggested_keywords"] = self._extract_keywords_from_filename(
                file_path.name
            )

            # Extract technical metadata based on file type
            if metadata["mime_type"]:
                metadata["technical_metadata"] = await self._extract_technical_metadata(
                    file_path, metadata["mime_type"]
                )

        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {e}")

        return metadata

    def _detect_mime_type(self, file_path: Path) -> Optional[str]:
        """Detect MIME type from file extension."""
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
            ".mp4": "video/mp4",
            ".mp3": "audio/mpeg",
            ".zip": "application/zip",
            ".tar": "application/x-tar",
            ".py": "text/x-python",
            ".r": "text/x-r",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        return mime_types.get(file_path.suffix.lower())

    def _suggest_resource_type(self, mime_type: str) -> Optional[str]:
        """Suggest COAR resource type based on MIME type."""
        if not mime_type:
            return None

        type_mappings = {
            "application/pdf": "http://purl.org/coar/resource_type/c_18cf",  # text
            "text/": "http://purl.org/coar/resource_type/c_18cf",  # text
            "image/": "http://purl.org/coar/resource_type/c_c513",  # image
            "video/": "http://purl.org/coar/resource_type/c_12ce",  # video
            "audio/": "http://purl.org/coar/resource_type/c_18cc",  # sound
            "application/json": "http://purl.org/coar/resource_type/c_ddb1",  # dataset
            "text/csv": "http://purl.org/coar/resource_type/c_ddb1",  # dataset
            "text/x-python": "http://purl.org/coar/resource_type/c_5ce6",  # software
            "text/x-r": "http://purl.org/coar/resource_type/c_5ce6",  # software
        }

        for pattern, resource_type in type_mappings.items():
            if mime_type.startswith(pattern):
                return resource_type

        return "http://purl.org/coar/resource_type/c_1843"  # other

    def _generate_title_from_filename(self, filename: str) -> str:
        """Generate a human-readable title from filename."""
        # Remove extension
        title = Path(filename).stem

        # Replace underscores and hyphens with spaces
        title = re.sub(r"[_-]", " ", title)

        # Capitalize words
        title = " ".join(word.capitalize() for word in title.split())

        return title

    def _generate_description_from_filename(self, filename: str) -> str:
        """Generate a description based on filename patterns."""
        filename_lower = filename.lower()

        descriptions = {
            "readme": "Documentation file containing project information and instructions",
            "data": "Data file containing research or analysis data",
            "analysis": "Analysis file containing computational analysis or results",
            "report": "Report document containing findings and conclusions",
            "presentation": "Presentation file for sharing research findings",
            "code": "Source code file for computational analysis",
            "script": "Script file for data processing or analysis",
            "image": "Image file containing visual data or documentation",
            "photo": "Photograph file documenting research subjects or activities",
            "chart": "Chart or graph visualizing data or results",
            "table": "Tabular data file containing structured information",
        }

        for pattern, description in descriptions.items():
            if pattern in filename_lower:
                return description

        return f"File: {self._generate_title_from_filename(filename)}"

    def _extract_keywords_from_filename(self, filename: str) -> List[str]:
        """Extract keywords from filename."""
        # Remove extension and split on common separators
        base_name = Path(filename).stem.lower()
        words = re.split(r"[_\-\s\.]+", base_name)

        # Filter out common stop words and short words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "a",
            "an",
        }
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        return keywords[:5]  # Limit to 5 keywords

    async def _extract_technical_metadata(
        self, file_path: Path, mime_type: str
    ) -> Dict[str, Any]:
        """Extract technical metadata based on file type."""
        technical = {}

        try:
            if mime_type.startswith("image/"):
                # For images, we could extract dimensions, color space, etc.
                # This would require PIL or similar library
                technical["format"] = mime_type

            elif mime_type.startswith("text/"):
                # For text files, we could extract encoding, line count, etc.
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        technical["character_count"] = len(content)
                        technical["line_count"] = content.count("\n")
                        technical["word_count"] = len(content.split())

        except Exception as e:
            logger.warning(f"Failed to extract technical metadata: {e}")

        return technical


class PrePopulationAssistant:
    """Main pre-population assistant that coordinates all intelligence services."""

    def __init__(
        self, user_client: NakalaUserInfoClient, vocab_service: NakalaVocabularyService
    ):
        self.user_client = user_client
        self.vocab_service = vocab_service
        self.context_service = UserContextService(user_client)
        self.file_extractor = FileMetadataExtractor()
        self.utils = NakalaCommonUtils()

    async def pre_populate_template(
        self,
        template: MetadataTemplate,
        api_key: str,
        file_path: str = None,
        additional_context: Dict[str, Any] = None,
    ) -> PrePopulationResult:
        """Pre-populate a metadata template with intelligent suggestions."""
        start_time = datetime.now()

        logger.info(f"Pre-populating template: {template.name}")

        # Build user context
        user_context = await self.context_service.build_user_context(api_key)

        # Extract file metadata if file provided
        file_metadata = {}
        if file_path:
            file_metadata = await self.file_extractor.extract_file_metadata(file_path)

        # Combine contexts
        combined_context = {
            "user": asdict(user_context),
            "file": file_metadata,
            "additional": additional_context or {},
        }

        # Pre-populate fields
        populated_fields = {}
        confidence_scores = {}
        suggestions = {}
        analysis_notes = []

        for field in template.fields:
            field_result = await self._populate_field(field, combined_context)

            if field_result["value"] is not None:
                populated_fields[field.name] = field_result["value"]
                confidence_scores[field.name] = field_result["confidence"]

            if field_result["suggestions"]:
                suggestions[field.name] = field_result["suggestions"]

            if field_result["notes"]:
                analysis_notes.extend(field_result["notes"])

        processing_time = (datetime.now() - start_time).total_seconds()

        result = PrePopulationResult(
            template=template,
            populated_fields=populated_fields,
            confidence_scores=confidence_scores,
            suggestions=suggestions,
            analysis_notes=analysis_notes,
            processing_time=processing_time,
        )

        logger.info(
            f"Pre-populated {len(populated_fields)} fields in {processing_time:.2f}s"
        )
        return result

    async def _populate_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate a single field based on context."""
        result = {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

        # Context is used directly in field-specific population methods

        # Field-specific population logic
        if field.name == "title":
            result.update(await self._populate_title_field(field, context))
        elif field.name == "description":
            result.update(await self._populate_description_field(field, context))
        elif field.name == "creator":
            result.update(await self._populate_creator_field(field, context))
        elif field.name == "date":
            result.update(await self._populate_date_field(field, context))
        elif field.name == "language":
            result.update(await self._populate_language_field(field, context))
        elif field.name == "keywords":
            result.update(await self._populate_keywords_field(field, context))
        elif field.name == "license":
            result.update(await self._populate_license_field(field, context))
        elif field.name == "type":
            result.update(await self._populate_type_field(field, context))
        elif field.name == "contributor":
            result.update(await self._populate_contributor_field(field, context))
        elif field.name == "spatial":
            result.update(await self._populate_spatial_field(field, context))
        elif field.name == "temporal":
            result.update(await self._populate_temporal_field(field, context))

        return result

    async def _populate_title_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate title field."""
        file_context = context.get("file", {})

        if file_context.get("suggested_title"):
            return {
                "value": file_context["suggested_title"],
                "confidence": 0.7,
                "suggestions": [file_context["suggested_title"]],
                "notes": ["Title suggested from filename"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_description_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate description field."""
        file_context = context.get("file", {})

        if file_context.get("suggested_description"):
            return {
                "value": file_context["suggested_description"],
                "confidence": 0.6,
                "suggestions": [file_context["suggested_description"]],
                "notes": ["Description suggested from file analysis"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_creator_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate creator field."""
        user_context = context.get("user", {})

        if user_context.get("name"):
            return {
                "value": user_context["name"],
                "confidence": 0.9,
                "suggestions": [user_context["name"]],
                "notes": ["Creator populated from user profile"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_date_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate date field."""
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            "value": today,
            "confidence": 0.8,
            "suggestions": [today, datetime.now().strftime("%Y")],
            "notes": ["Date populated with current date"],
        }

    async def _populate_language_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate language field."""
        user_context = context.get("user", {})

        default_lang = user_context.get("default_language", "en")
        return {
            "value": default_lang,
            "confidence": 0.8,
            "suggestions": [default_lang, "en", "fr"],
            "notes": ["Language populated from user preferences"],
        }

    async def _populate_keywords_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate keywords field."""
        user_context = context.get("user", {})
        file_context = context.get("file", {})

        suggestions = []

        # Add user's common keywords
        if user_context.get("common_keywords"):
            suggestions.extend(user_context["common_keywords"][:5])

        # Add file-based keywords
        if file_context.get("suggested_keywords"):
            suggestions.extend(file_context["suggested_keywords"])

        # Add domain expertise
        if user_context.get("domain_expertise"):
            suggestions.extend(user_context["domain_expertise"])

        if suggestions:
            # Create multilingual keyword string
            keywords_str = ";".join(suggestions[:5])
            return {
                "value": keywords_str,
                "confidence": 0.7,
                "suggestions": suggestions,
                "notes": ["Keywords compiled from user history and file analysis"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_license_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate license field."""
        user_context = context.get("user", {})

        preferred_licenses = user_context.get("preferred_licenses", [])
        if preferred_licenses:
            return {
                "value": preferred_licenses[0],
                "confidence": 0.8,
                "suggestions": preferred_licenses[:3] + ["CC-BY-4.0", "CC-BY-SA-4.0"],
                "notes": ["License suggested from user history"],
            }

        return {
            "value": "CC-BY-4.0",
            "confidence": 0.5,
            "suggestions": ["CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0"],
            "notes": ["Default license suggested"],
        }

    async def _populate_type_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate type field."""
        file_context = context.get("file", {})

        if file_context.get("suggested_type"):
            return {
                "value": file_context["suggested_type"],
                "confidence": 0.8,
                "suggestions": [file_context["suggested_type"]],
                "notes": ["Resource type suggested from file analysis"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_contributor_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate contributor field."""
        user_context = context.get("user", {})

        collaborators = user_context.get("frequent_collaborators", [])
        if collaborators:
            return {
                "value": (
                    collaborators[0]
                    if len(collaborators) == 1
                    else ";".join(collaborators[:3])
                ),
                "confidence": 0.6,
                "suggestions": collaborators[:5],
                "notes": ["Contributors suggested from collaboration history"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_spatial_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate spatial field."""
        user_context = context.get("user", {})

        if user_context.get("geographic_focus"):
            return {
                "value": user_context["geographic_focus"],
                "confidence": 0.7,
                "suggestions": [user_context["geographic_focus"]],
                "notes": ["Geographic focus detected from user data"],
            }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}

    async def _populate_temporal_field(
        self, field: TemplateField, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Populate temporal field."""
        user_context = context.get("user", {})

        if user_context.get("historical_period"):
            current_year = datetime.now().year
            period_ranges = {
                "medieval": "500/1500",
                "early_modern": "1500/1800",
                "19th_century": "1800/1900",
                "20th_century": "1900/2000",
                "contemporary": f"2000/{current_year}",
            }

            period = user_context["historical_period"]
            if period in period_ranges:
                return {
                    "value": period_ranges[period],
                    "confidence": 0.6,
                    "suggestions": [period_ranges[period]],
                    "notes": ["Temporal coverage suggested from historical focus"],
                }

        return {"value": None, "confidence": 0.0, "suggestions": [], "notes": []}


# Factory function
def create_prepopulation_assistant(
    user_client: NakalaUserInfoClient, vocab_service: NakalaVocabularyService
) -> PrePopulationAssistant:
    """Create a pre-population assistant with required services."""
    return PrePopulationAssistant(user_client, vocab_service)
