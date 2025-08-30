"""
NAKALA Vocabulary Service

Provides dynamic field discovery and vocabulary management for the NAKALA API.
Part of the Complete Metadata Management System - Foundation Phase.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import requests
from dataclasses import dataclass, asdict

from .common.config import NakalaConfig
from .common.exceptions import NakalaAPIError
from .common.utils import NakalaCommonUtils

logger = logging.getLogger(__name__)


@dataclass
class VocabularyEntry:
    """Represents a vocabulary entry with metadata."""

    value: str
    label: str
    description: Optional[str] = None
    uri: Optional[str] = None
    category: Optional[str] = None
    language: str = "en"
    last_updated: Optional[datetime] = None


@dataclass
class FieldSchema:
    """Represents the schema for a metadata field."""

    property_uri: str
    field_name: str
    data_type: str
    required: bool = False
    multilingual: bool = False
    controlled_vocabulary: Optional[str] = None
    validation_pattern: Optional[str] = None
    examples: List[str] = None
    help_text: str = ""
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


class NakalaVocabularyCache:
    """Manages caching of vocabulary data with expiration."""

    def __init__(self, cache_dir: str = None, cache_ttl_hours: int = 24):
        self.cache_dir = (
            Path(cache_dir) if cache_dir else Path.home() / ".nakala" / "cache"
        )
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for a given key."""
        return self.cache_dir / f"{cache_key}.json"

    def is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and not expired."""
        cache_file = self._get_cache_file(cache_key)
        if not cache_file.exists():
            return False

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get("cached_at", ""))
                return datetime.now() - cached_time < self.cache_ttl
        except Exception as e:
            logger.warning(f"Error checking cache for {cache_key}: {e}")
            return False

    def get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached data if available and not expired."""
        if not self.is_cached(cache_key):
            return None

        cache_file = self._get_cache_file(cache_key)
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("data")
        except Exception as e:
            logger.warning(f"Error reading cache for {cache_key}: {e}")
            return None

    def set_cached(self, cache_key: str, data: Any) -> None:
        """Cache data with timestamp."""
        cache_file = self._get_cache_file(cache_key)
        try:
            cache_data = {"cached_at": datetime.now().isoformat(), "data": data}
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"Cached data for {cache_key}")
        except Exception as e:
            logger.warning(f"Error caching data for {cache_key}: {e}")

    def clear_cache(self, cache_key: str = None) -> None:
        """Clear specific cache or all caches."""
        if cache_key:
            cache_file = self._get_cache_file(cache_key)
            if cache_file.exists():
                cache_file.unlink()
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()


class NakalaVocabularyService:
    """Service for discovering and managing NAKALA vocabularies."""

    def __init__(self, config: NakalaConfig, cache_ttl_hours: int = 24):
        self.config = config
        self.utils = NakalaCommonUtils()
        self.cache = NakalaVocabularyCache(cache_ttl_hours=cache_ttl_hours)
        self.vocabularies: Dict[str, List[VocabularyEntry]] = {}
        self.field_schemas: Dict[str, FieldSchema] = {}

    async def discover_vocabularies(
        self, force_refresh: bool = False
    ) -> Dict[str, List[VocabularyEntry]]:
        """Discover all available vocabularies from NAKALA API."""
        logger.info("Discovering NAKALA vocabularies...")

        vocabulary_endpoints = {
            "languages": "/vocabularies/languages",
            "licenses": "/vocabularies/licenses",
            "datatypes": "/vocabularies/datatypes",
            "countries": "/vocabularies/countryCodes",
            "data_statuses": "/vocabularies/dataStatuses",
            "collection_statuses": "/vocabularies/collectionStatuses",
        }

        discovered_vocabularies = {}

        for vocab_name, endpoint in vocabulary_endpoints.items():
            cache_key = f"vocabulary_{vocab_name}"

            # Check cache first unless force refresh
            if not force_refresh:
                cached_data = self.cache.get_cached(cache_key)
                if cached_data:
                    logger.debug(f"Using cached vocabulary: {vocab_name}")
                    discovered_vocabularies[vocab_name] = [
                        VocabularyEntry(**entry) for entry in cached_data
                    ]
                    continue

            # Fetch from API
            try:
                vocab_data = await self._fetch_vocabulary(endpoint)
                vocabulary_entries = self._parse_vocabulary_response(
                    vocab_data, vocab_name
                )
                discovered_vocabularies[vocab_name] = vocabulary_entries

                # Cache the results
                serializable_data = [asdict(entry) for entry in vocabulary_entries]
                self.cache.set_cached(cache_key, serializable_data)

                logger.info(
                    f"Discovered {len(vocabulary_entries)} entries for {vocab_name}"
                )

            except Exception as e:
                logger.error(f"Failed to fetch vocabulary {vocab_name}: {e}")
                # Try to use expired cache as fallback
                cached_data = self.cache.get_cached(cache_key)
                if cached_data:
                    logger.warning(f"Using expired cache for {vocab_name}")
                    discovered_vocabularies[vocab_name] = [
                        VocabularyEntry(**entry) for entry in cached_data
                    ]
                else:
                    discovered_vocabularies[vocab_name] = []

        self.vocabularies = discovered_vocabularies
        return discovered_vocabularies

    async def _fetch_vocabulary(self, endpoint: str) -> Dict[str, Any]:
        """Fetch vocabulary data from NAKALA API."""
        url = f"{self.config.api_url}{endpoint}"
        headers = {"X-API-KEY": self.config.api_key}

        try:
            # Use asyncio to run the blocking request in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=headers, timeout=self.config.timeout),
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise NakalaAPIError(f"Failed to fetch vocabulary from {endpoint}: {e}")

    def _parse_vocabulary_response(
        self, response_data: Dict[str, Any], vocab_name: str
    ) -> List[VocabularyEntry]:
        """Parse vocabulary response into VocabularyEntry objects."""
        entries = []

        # Handle different response formats
        if isinstance(response_data, list):
            data_list = response_data
        elif "data" in response_data:
            data_list = response_data["data"]
        else:
            data_list = [response_data]

        for item in data_list:
            if isinstance(item, dict):
                entry = VocabularyEntry(
                    value=item.get("value", item.get("code", item.get("id", ""))),
                    label=item.get("label", item.get("name", item.get("title", ""))),
                    description=item.get("description", item.get("comment")),
                    uri=item.get("uri", item.get("@id")),
                    category=vocab_name,
                    language=item.get("lang", "en"),
                    last_updated=datetime.now(),
                )
                entries.append(entry)
            elif isinstance(item, str):
                # Handle simple string lists
                entry = VocabularyEntry(
                    value=item,
                    label=item,
                    category=vocab_name,
                    last_updated=datetime.now(),
                )
                entries.append(entry)

        return entries

    def get_vocabulary(self, vocab_name: str) -> List[VocabularyEntry]:
        """Get a specific vocabulary by name."""
        return self.vocabularies.get(vocab_name, [])

    def search_vocabulary(
        self, vocab_name: str, query: str, limit: int = 10
    ) -> List[VocabularyEntry]:
        """Search within a specific vocabulary."""
        vocabulary = self.get_vocabulary(vocab_name)
        query_lower = query.lower()

        matches = []
        for entry in vocabulary:
            if (
                query_lower in entry.label.lower()
                or query_lower in entry.value.lower()
                or (entry.description and query_lower in entry.description.lower())
            ):
                matches.append(entry)

            if len(matches) >= limit:
                break

        return matches

    def validate_vocabulary_value(self, vocab_name: str, value: str) -> bool:
        """Validate if a value exists in a vocabulary."""
        vocabulary = self.get_vocabulary(vocab_name)
        return any(entry.value == value for entry in vocabulary)

    def get_vocabulary_suggestions(
        self, vocab_name: str, partial_value: str, limit: int = 5
    ) -> List[VocabularyEntry]:
        """Get suggestions for partial vocabulary values."""
        vocabulary = self.get_vocabulary(vocab_name)
        partial_lower = partial_value.lower()

        suggestions = []

        # Exact prefix matches first
        for entry in vocabulary:
            if entry.value.lower().startswith(partial_lower):
                suggestions.append(entry)

        # Then label matches
        for entry in vocabulary:
            if entry not in suggestions and entry.label.lower().startswith(
                partial_lower
            ):
                suggestions.append(entry)

        # Finally fuzzy matches
        for entry in vocabulary:
            if entry not in suggestions and (
                partial_lower in entry.value.lower()
                or partial_lower in entry.label.lower()
            ):
                suggestions.append(entry)

            if len(suggestions) >= limit:
                break

        return suggestions[:limit]


class MetadataSchemaGenerator:
    """Generates JSON schemas for metadata fields based on NAKALA vocabularies."""

    def __init__(self, vocabulary_service: NakalaVocabularyService):
        self.vocab_service = vocabulary_service

    def generate_field_schema(
        self, property_uri: str, field_config: Dict[str, Any] = None
    ) -> FieldSchema:
        """Generate schema for a specific metadata field."""
        if field_config is None:
            field_config = {}

        # Extract field name from URI
        field_name = property_uri.split("#")[-1].split("/")[-1]

        # Determine data type
        data_type = self._determine_data_type(property_uri, field_config)

        # Check if field has controlled vocabulary
        controlled_vocab = self._get_controlled_vocabulary(property_uri)

        # Generate examples
        examples = self._generate_examples(property_uri, controlled_vocab)

        # Generate help text
        help_text = self._generate_help_text(property_uri, field_config)

        schema = FieldSchema(
            property_uri=property_uri,
            field_name=field_name,
            data_type=data_type,
            required=field_config.get("required", False),
            multilingual=field_config.get("multilingual", False),
            controlled_vocabulary=controlled_vocab,
            validation_pattern=field_config.get("validation_pattern"),
            examples=examples,
            help_text=help_text,
            last_updated=datetime.now(),
        )

        return schema

    def _determine_data_type(
        self, property_uri: str, field_config: Dict[str, Any]
    ) -> str:
        """Determine appropriate data type for field."""
        # Check explicit configuration first
        if "data_type" in field_config:
            return field_config["data_type"]

        # Infer from property URI
        if "date" in property_uri.lower() or "created" in property_uri.lower():
            return "date"
        elif "language" in property_uri.lower():
            return "language_code"
        elif "license" in property_uri.lower():
            return "license_uri"
        elif "type" in property_uri.lower():
            return "resource_type_uri"
        else:
            return "string"

    def _get_controlled_vocabulary(self, property_uri: str) -> Optional[str]:
        """Determine if field uses controlled vocabulary."""
        if "language" in property_uri.lower():
            return "languages"
        elif "license" in property_uri.lower():
            return "licenses"
        elif "type" in property_uri.lower():
            return "datatypes"
        elif "coverage" in property_uri.lower() and "spatial" in property_uri.lower():
            return "countries"
        return None

    def _generate_examples(
        self, property_uri: str, controlled_vocab: Optional[str]
    ) -> List[str]:
        """Generate example values for the field."""
        examples = []

        if controlled_vocab:
            # Get examples from vocabulary
            vocab_entries = self.vocab_service.get_vocabulary(controlled_vocab)
            if vocab_entries:
                examples = [entry.value for entry in vocab_entries[:3]]
        else:
            # Generate contextual examples
            if "title" in property_uri.lower():
                examples = [
                    "Research Dataset Title",
                    "fr:Titre en français|en:English Title",
                ]
            elif "description" in property_uri.lower():
                examples = [
                    "Detailed description of the resource",
                    "fr:Description|en:Description",
                ]
            elif "creator" in property_uri.lower():
                examples = ["Surname,Givenname", "Doe,John;Smith,Jane"]
            elif "date" in property_uri.lower():
                examples = ["2024-01-15", "2024", "2020/2023"]
            elif "identifier" in property_uri.lower():
                examples = ["DOI:10.1234/example", "ISBN:978-0123456789"]

        return examples

    def _generate_help_text(
        self, property_uri: str, field_config: Dict[str, Any]
    ) -> str:
        """Generate helpful guidance text for the field."""
        if "help_text" in field_config:
            return field_config["help_text"]

        field_name = property_uri.split("#")[-1].split("/")[-1]

        help_texts = {
            "title": (
                "The main title of the resource. For multilingual titles, "
                'use format: "fr:French title|en:English title"'
            ),
            "description": "A detailed description of the resource content and purpose.",
            "creator": (
                'Primary authors/creators in format "Surname,Givenname". '
                "Separate multiple creators with semicolons."
            ),
            "contributor": "Additional contributors who helped create the resource.",
            "license": "License under which the resource is made available (e.g., CC-BY-4.0).",
            "type": (
                "Resource type from COAR vocabulary "
                "(e.g., http://purl.org/coar/resource_type/c_ddb1)."
            ),
            "date": "Date of creation or publication in YYYY-MM-DD format.",
            "language": 'Primary language of the resource (ISO 639-1 code, e.g., "fr", "en").',
            "keywords": (
                "Keywords describing the resource. For multilingual: "
                '"fr:mot1;mot2|en:word1;word2"'
            ),
            "rights": "Rights information or access permissions.",
            "identifier": "Persistent identifier like DOI, ISBN, etc.",
        }

        return help_texts.get(field_name, f"Value for {field_name} field.")


# Factory function for easy instantiation
def create_vocabulary_service(
    config: NakalaConfig, cache_ttl_hours: int = 24
) -> NakalaVocabularyService:
    """Create a configured vocabulary service."""
    return NakalaVocabularyService(config, cache_ttl_hours)


# Async helper for running sync code
async def discover_nakala_vocabularies(
    api_url: str = "https://apitest.nakala.fr",
    api_key: str = None,
    force_refresh: bool = False,
) -> Dict[str, List[VocabularyEntry]]:
    """Convenience function to discover vocabularies."""
    config = NakalaConfig(api_url=api_url, api_key=api_key)
    service = create_vocabulary_service(config)
    return await service.discover_vocabularies(force_refresh=force_refresh)
