"""
NAKALA Relationship Discovery Service

Discovers and suggests relationships between resources based on content similarity,
user patterns, and metadata analysis. Part of the Complete Metadata Management
System - Intelligence Phase.
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import Counter

from .user_info import NakalaUserInfoClient
from .common.utils import NakalaCommonUtils

logger = logging.getLogger(__name__)


@dataclass
class RelationshipSuggestion:
    """Represents a suggested relationship between resources."""

    target_id: str
    target_title: str
    relationship_type: str
    confidence: float
    reason: str
    target_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.target_metadata is None:
            self.target_metadata = {}


@dataclass
class RelationshipAnalysis:
    """Complete relationship analysis result."""

    source_id: str
    source_title: str
    suggestions: List[RelationshipSuggestion]
    processing_time: float
    analysis_notes: List[str]
    similarity_matrix: Dict[str, float] = None

    def __post_init__(self):
        if self.similarity_matrix is None:
            self.similarity_matrix = {}


class ContentSimilarityAnalyzer:
    """Analyzes content similarity between resources."""

    def __init__(self):
        self.utils = NakalaCommonUtils()

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using multiple methods."""
        if not text1 or not text2:
            return 0.0

        # Normalize texts
        text1_norm = self._normalize_text(text1)
        text2_norm = self._normalize_text(text2)

        # Calculate different similarity metrics
        jaccard_sim = self._jaccard_similarity(text1_norm, text2_norm)
        word_overlap = self._word_overlap_similarity(text1_norm, text2_norm)
        trigram_sim = self._trigram_similarity(text1_norm, text2_norm)

        # Weighted combination
        similarity = jaccard_sim * 0.4 + word_overlap * 0.4 + trigram_sim * 0.2

        return min(similarity, 1.0)

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation and extra spaces
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 and not words2:
            return 1.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _word_overlap_similarity(self, text1: str, text2: str) -> float:
        """Calculate word overlap similarity."""
        words1 = text1.split()
        words2 = text2.split()

        if not words1 or not words2:
            return 0.0

        # Count common words
        counter1 = Counter(words1)
        counter2 = Counter(words2)

        overlap = sum((counter1 & counter2).values())
        total = max(len(words1), len(words2))

        return overlap / total if total > 0 else 0.0

    def _trigram_similarity(self, text1: str, text2: str) -> float:
        """Calculate character trigram similarity."""
        trigrams1 = self._get_trigrams(text1)
        trigrams2 = self._get_trigrams(text2)

        if not trigrams1 and not trigrams2:
            return 1.0

        intersection = len(trigrams1.intersection(trigrams2))
        union = len(trigrams1.union(trigrams2))

        return intersection / union if union > 0 else 0.0

    def _get_trigrams(self, text: str) -> Set[str]:
        """Extract character trigrams from text."""
        trigrams = set()
        text = f"  {text}  "  # Add padding

        for i in range(len(text) - 2):
            trigrams.add(text[i : i + 3])

        return trigrams

    def calculate_metadata_similarity(
        self, meta1: Dict[str, Any], meta2: Dict[str, Any]
    ) -> float:
        """Calculate similarity based on metadata fields."""
        similarities = []

        # Compare specific metadata fields
        field_weights = {
            "keywords": 0.3,
            "language": 0.2,
            "type": 0.2,
            "creator": 0.15,
            "temporal": 0.1,
            "spatial": 0.05,
        }

        for field, weight in field_weights.items():
            sim = self._compare_metadata_field(meta1.get(field), meta2.get(field))
            similarities.append(sim * weight)

        return sum(similarities)

    def _compare_metadata_field(self, value1: Any, value2: Any) -> float:
        """Compare two metadata field values."""
        if value1 is None or value2 is None:
            return 0.0

        # Convert to strings for comparison
        str1 = str(value1).lower()
        str2 = str(value2).lower()

        if str1 == str2:
            return 1.0

        # For text fields, use text similarity
        if len(str1) > 10 or len(str2) > 10:
            return self.calculate_text_similarity(str1, str2)

        # For short values, check for substring matches
        if str1 in str2 or str2 in str1:
            return 0.5

        return 0.0


class RelationshipTypeClassifier:
    """Classifies the type of relationship between resources."""

    def __init__(self):
        self.relationship_patterns = {
            "isPartOf": [
                "part of",
                "belongs to",
                "contained in",
                "subset of",
                "volume",
                "chapter",
                "section",
                "episode",
            ],
            "hasPart": [
                "contains",
                "includes",
                "has part",
                "comprises",
                "collection of",
                "series of",
                "set of",
            ],
            "isVersionOf": [
                "version",
                "edition",
                "revision",
                "update",
                "draft",
                "final",
                "revised",
            ],
            "isFormatOf": [
                "format",
                "copy",
                "reproduction",
                "digitization",
                "transcription",
                "translation",
            ],
            "references": [
                "cites",
                "references",
                "mentions",
                "discusses",
                "based on",
                "derived from",
                "inspired by",
            ],
            "isReferencedBy": [
                "cited by",
                "referenced by",
                "mentioned in",
                "discussed in",
                "basis for",
            ],
            "requires": [
                "requires",
                "depends on",
                "needs",
                "prerequisite",
                "supplemented by",
                "accompanied by",
            ],
            "isRequiredBy": [
                "required by",
                "dependency of",
                "needed by",
                "supplement to",
                "accompanies",
            ],
            "replaces": [
                "replaces",
                "supersedes",
                "updates",
                "corrects",
                "new version of",
                "improvement of",
            ],
            "isReplacedBy": [
                "replaced by",
                "superseded by",
                "updated by",
                "corrected by",
                "improved by",
            ],
            "conformsTo": [
                "conforms to",
                "follows",
                "implements",
                "based on standard",
                "according to",
                "compliant with",
            ],
            "relation": [
                "related to",
                "associated with",
                "connected to",
                "similar to",
                "comparable to",
                "linked to",
            ],
        }

    def classify_relationship(
        self,
        source_metadata: Dict[str, Any],
        target_metadata: Dict[str, Any],
        similarity_score: float,
    ) -> Tuple[str, float, str]:
        """Classify the relationship type between two resources."""

        # Extract text for analysis
        source_text = self._extract_text_for_analysis(source_metadata)
        target_text = self._extract_text_for_analysis(target_metadata)

        # Check for explicit relationship indicators
        explicit_type = self._detect_explicit_relationship(source_text, target_text)
        if explicit_type:
            return explicit_type, 0.9, "Explicit relationship detected in metadata"

        # Infer relationship from metadata patterns
        inferred_type = self._infer_relationship_from_metadata(
            source_metadata, target_metadata
        )
        if inferred_type:
            return inferred_type, 0.7, "Relationship inferred from metadata patterns"

        # Default to generic relation if similarity is high enough
        if similarity_score > 0.6:
            return (
                "relation",
                similarity_score,
                "Generic relationship based on content similarity",
            )

        return "relation", similarity_score, "Default relationship type"

    def _extract_text_for_analysis(self, metadata: Dict[str, Any]) -> str:
        """Extract relevant text from metadata for relationship analysis."""
        text_parts = []

        # Extract from common text fields
        text_fields = ["title", "description", "abstract", "keywords"]
        for field in text_fields:
            if field in metadata and metadata[field]:
                text_parts.append(str(metadata[field]))

        return " ".join(text_parts).lower()

    def _detect_explicit_relationship(
        self, source_text: str, target_text: str
    ) -> Optional[str]:
        """Detect explicit relationship mentions in text."""
        combined_text = f"{source_text} {target_text}"

        for relationship_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    return relationship_type

        return None

    def _infer_relationship_from_metadata(
        self, source_metadata: Dict[str, Any], target_metadata: Dict[str, Any]
    ) -> Optional[str]:
        """Infer relationship type from metadata patterns."""

        # Check for collection/part relationships
        source_type = source_metadata.get("type", "")
        target_type = target_metadata.get("type", "")

        if "collection" in source_type.lower() and "dataset" in target_type.lower():
            return "hasPart"
        elif "dataset" in source_type.lower() and "collection" in target_type.lower():
            return "isPartOf"

        # Check for version relationships
        source_title = source_metadata.get("title", "").lower()
        target_title = target_metadata.get("title", "").lower()

        version_indicators = ["v1", "v2", "version", "draft", "final", "revised"]
        if any(indicator in source_title for indicator in version_indicators) or any(
            indicator in target_title for indicator in version_indicators
        ):
            return "isVersionOf"

        # Check for same creator (might indicate related works)
        source_creator = source_metadata.get("creator", "")
        target_creator = target_metadata.get("creator", "")

        if source_creator and target_creator and source_creator == target_creator:
            # Same creator might indicate a series or related works
            return "relation"

        return None


class RelationshipDiscoveryService:
    """Main service for discovering relationships between resources."""

    def __init__(self, user_client: NakalaUserInfoClient):
        self.user_client = user_client
        self.utils = NakalaCommonUtils()
        self.similarity_analyzer = ContentSimilarityAnalyzer()
        self.relationship_classifier = RelationshipTypeClassifier()

    async def discover_relationships(
        self,
        source_metadata: Dict[str, Any],
        source_id: str = None,
        max_suggestions: int = 10,
        min_confidence: float = 0.3,
    ) -> RelationshipAnalysis:
        """Discover relationships for a given resource."""
        start_time = datetime.now()

        logger.info(f"Discovering relationships for resource: {source_id or 'unknown'}")

        # Get user's resources for comparison
        try:
            user_profile = self.user_client.get_complete_user_profile()
            all_resources = user_profile.get("datasets", []) + user_profile.get(
                "collections", []
            )
        except Exception as e:
            logger.warning(
                f"Could not get user profile for relationship discovery: {e}"
            )
            all_resources = []

        # Filter out the source resource itself
        if source_id:
            all_resources = [
                r for r in all_resources if r.get("identifier") != source_id
            ]

        suggestions = []
        similarity_matrix = {}
        analysis_notes = []

        if not all_resources:
            analysis_notes.append(
                "No user resources available for relationship discovery"
            )
        else:
            analysis_notes.append(
                f"Analyzing relationships with {len(all_resources)} user resources"
            )

            # Calculate similarities and generate suggestions
            for resource in all_resources:
                target_id = resource.get("identifier", "")
                target_metadata = self._extract_resource_metadata(resource)

                # Calculate overall similarity
                similarity = await self._calculate_resource_similarity(
                    source_metadata, target_metadata
                )
                similarity_matrix[target_id] = similarity

                # Only suggest if similarity is above threshold
                if similarity >= min_confidence:
                    # Classify relationship type
                    rel_type, confidence, reason = (
                        self.relationship_classifier.classify_relationship(
                            source_metadata, target_metadata, similarity
                        )
                    )

                    # Adjust confidence based on similarity
                    final_confidence = (confidence + similarity) / 2

                    suggestion = RelationshipSuggestion(
                        target_id=target_id,
                        target_title=self._extract_meta_value(
                            resource.get("metas", []), "title"
                        ),
                        relationship_type=rel_type,
                        confidence=final_confidence,
                        reason=reason,
                        target_metadata=target_metadata,
                    )

                    suggestions.append(suggestion)

            # Sort suggestions by confidence
            suggestions.sort(key=lambda x: x.confidence, reverse=True)

            # Limit to max suggestions
            suggestions = suggestions[:max_suggestions]

            analysis_notes.append(f"Found {len(suggestions)} relationship suggestions")

        processing_time = (datetime.now() - start_time).total_seconds()

        return RelationshipAnalysis(
            source_id=source_id or "unknown",
            source_title=source_metadata.get("title", "Unknown"),
            suggestions=suggestions,
            processing_time=processing_time,
            analysis_notes=analysis_notes,
            similarity_matrix=similarity_matrix,
        )

    async def _calculate_resource_similarity(
        self, source_metadata: Dict[str, Any], target_metadata: Dict[str, Any]
    ) -> float:
        """Calculate overall similarity between two resources."""

        # Text similarity (title + description)
        source_text = f"{source_metadata.get('title', '')} {source_metadata.get('description', '')}"
        target_text = f"{target_metadata.get('title', '')} {target_metadata.get('description', '')}"

        text_similarity = self.similarity_analyzer.calculate_text_similarity(
            source_text, target_text
        )

        # Metadata similarity
        metadata_similarity = self.similarity_analyzer.calculate_metadata_similarity(
            source_metadata, target_metadata
        )

        # Weighted combination
        overall_similarity = text_similarity * 0.7 + metadata_similarity * 0.3

        return overall_similarity

    def _extract_resource_metadata(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized metadata from a resource."""
        metas = resource.get("metas", [])

        metadata = {
            "title": self._extract_meta_value(metas, "title"),
            "description": self._extract_meta_value(metas, "description"),
            "keywords": self._extract_meta_value(metas, "subject"),
            "creator": self._extract_meta_value(metas, "creator"),
            "language": self._extract_meta_value(metas, "language"),
            "type": self._extract_meta_value(metas, "type"),
            "date": self._extract_meta_value(metas, "date"),
            "temporal": self._extract_meta_value(metas, "temporal"),
            "spatial": self._extract_meta_value(metas, "spatial"),
        }

        return metadata

    def _extract_meta_value(
        self, metas: List[Dict], property_name: str, language: str = "fr"
    ) -> str:
        """Extract metadata value by property name."""
        if not metas:
            return ""

        # Try to find exact property match
        for meta in metas:
            property_uri = meta.get("propertyUri", "").lower()
            if property_name.lower() in property_uri:
                # Prefer specified language
                meta_lang = meta.get("lang", "")
                if meta_lang == language:
                    return meta.get("value", "")

        # Fall back to any language
        for meta in metas:
            property_uri = meta.get("propertyUri", "").lower()
            if property_name.lower() in property_uri:
                return meta.get("value", "")

        return ""

    def suggest_relationship_fields(
        self, relationship_analysis: RelationshipAnalysis, template_fields: List[str]
    ) -> Dict[str, List[str]]:
        """Suggest values for relationship fields in templates."""
        suggestions = {}

        # Check if template has relationship fields
        relation_fields = ["relation", "source", "isPartOf", "references"]

        for field in relation_fields:
            if field in template_fields and relationship_analysis.suggestions:
                field_suggestions = []

                # Add top suggestions as relation field values
                for suggestion in relationship_analysis.suggestions[:3]:
                    if suggestion.confidence > 0.5:
                        relation_text = (
                            f"{suggestion.relationship_type}: {suggestion.target_title} "
                            f"({suggestion.target_id})"
                        )
                        field_suggestions.append(relation_text)

                if field_suggestions:
                    suggestions[field] = field_suggestions

        return suggestions

    def generate_relationship_report(self, analysis: RelationshipAnalysis) -> str:
        """Generate a human-readable report of relationship analysis."""
        doc = []
        doc.append("# Relationship Discovery Report")
        doc.append(f"**Source:** {analysis.source_title} ({analysis.source_id})")
        doc.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"**Processing time:** {analysis.processing_time:.3f} seconds")

        doc.append("\n## Summary")
        doc.append(f"- **Suggestions found:** {len(analysis.suggestions)}")

        if analysis.suggestions:
            avg_confidence = sum(s.confidence for s in analysis.suggestions) / len(
                analysis.suggestions
            )
            doc.append(f"- **Average confidence:** {avg_confidence:.1%}")

            highest_confidence = max(s.confidence for s in analysis.suggestions)
            doc.append(f"- **Highest confidence:** {highest_confidence:.1%}")

        # List suggestions
        if analysis.suggestions:
            doc.append("\n## Relationship Suggestions")

            for i, suggestion in enumerate(analysis.suggestions, 1):
                doc.append(f"\n### {i}. {suggestion.target_title}")
                doc.append(f"- **Target ID:** {suggestion.target_id}")
                doc.append(f"- **Relationship Type:** {suggestion.relationship_type}")
                doc.append(f"- **Confidence:** {suggestion.confidence:.1%}")
                doc.append(f"- **Reason:** {suggestion.reason}")
        else:
            doc.append("\n## No Relationships Found")
            doc.append("No similar resources found in user's data.")

        # Analysis notes
        if analysis.analysis_notes:
            doc.append("\n## Analysis Notes")
            for note in analysis.analysis_notes:
                doc.append(f"- {note}")

        return "\n".join(doc)


# Factory function
def create_relationship_discovery_service(
    user_client: NakalaUserInfoClient,
) -> RelationshipDiscoveryService:
    """Create a relationship discovery service with required dependencies."""
    return RelationshipDiscoveryService(user_client)
