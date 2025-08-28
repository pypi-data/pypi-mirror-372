"""
Nakala Curator Client

Provides data curation and quality management tools including batch modifications,
metadata validation, duplicate detection, and data consistency checking.
"""

import csv
import json
import logging
import argparse
import time
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Import common utilities
from .common.config import NakalaConfig
from .common.utils import NakalaCommonUtils, setup_common_logging

from .user_info import NakalaUserInfoClient
from .vocabulary import create_vocabulary_service, MetadataSchemaGenerator
from .templates import create_template_generator, MetadataTemplate
from .prepopulation import create_prepopulation_assistant, PrePopulationResult
from .relationships import create_relationship_discovery_service, RelationshipAnalysis
from .autonomous_generator import (
    create_autonomous_generator,
    AutonomousGenerationResult,
)
from .predictive_analytics import create_predictive_analytics, PredictiveAnalysisResult

logger = logging.getLogger(__name__)


# Comprehensive field mapping for CSV parsing
CSV_FIELD_MAPPINGS = {
    "new_title": {
        "api_field": "title",
        "property_uri": "http://nakala.fr/terms#title",
        "multilingual": True,
        "required": True,
    },
    "new_description": {
        "api_field": "description",
        "property_uri": "http://purl.org/dc/terms/description",
        "multilingual": True,
        "required": True,
    },
    "new_keywords": {
        "api_field": "keywords",
        "property_uri": "http://purl.org/dc/terms/subject",
        "multilingual": True,
        "required": False,
    },
    "new_author": {
        "api_field": "creator",
        "property_uri": "http://purl.org/dc/terms/creator",
        "multilingual": False,
        "required": True,
        "format": "semicolon_split",
    },
    "new_contributor": {
        "api_field": "contributor",
        "property_uri": "http://purl.org/dc/terms/contributor",
        "multilingual": False,
        "required": False,
        "format": "array",
    },
    "new_license": {
        "api_field": "license",
        "property_uri": "http://nakala.fr/terms#license",
        "multilingual": False,
        "required": True,
    },
    "new_type": {
        "api_field": "type",
        "property_uri": "http://nakala.fr/terms#type",
        "multilingual": False,
        "required": True,
    },
    "new_date": {
        "api_field": "date",
        "property_uri": "http://nakala.fr/terms#created",
        "multilingual": False,
        "required": True,
    },
    "new_language": {
        "api_field": "language",
        "property_uri": "http://purl.org/dc/terms/language",
        "multilingual": False,
        "required": False,
    },
    "new_temporal": {
        "api_field": "temporal",
        "property_uri": "http://purl.org/dc/terms/coverage",
        "multilingual": False,
        "required": False,
    },
    "new_spatial": {
        "api_field": "spatial",
        "property_uri": "http://purl.org/dc/terms/coverage",
        "multilingual": False,
        "required": False,
    },
    "new_relation": {
        "api_field": "relation",
        "property_uri": "http://purl.org/dc/terms/relation",
        "multilingual": False,
        "required": False,
    },
    "new_source": {
        "api_field": "source",
        "property_uri": "http://purl.org/dc/terms/source",
        "multilingual": False,
        "required": False,
    },
    "new_identifier": {
        "api_field": "identifier",
        "property_uri": "http://purl.org/dc/terms/identifier",
        "multilingual": False,
        "required": False,
    },
    "new_alternative": {
        "api_field": "alternative",
        "property_uri": "http://purl.org/dc/terms/alternative",
        "multilingual": True,
        "required": False,
    },
    "new_publisher": {
        "api_field": "publisher",
        "property_uri": "http://purl.org/dc/terms/publisher",
        "multilingual": False,
        "required": False,
    },
    "new_creator": {
        "api_field": "creator",
        "property_uri": "http://purl.org/dc/terms/creator",
        "multilingual": False,
        "required": False,
        "format": "semicolon_split",
    },
    # Access Control Fields
    "rights": {
        "api_field": "rights",
        "property_uri": "http://purl.org/dc/terms/rights",
        "multilingual": False,
        "required": False,
        "format": "rights_list",
    },
    "new_rights": {
        "api_field": "rights",
        "property_uri": "http://purl.org/dc/terms/rights",
        "multilingual": False,
        "required": False,
        "format": "rights_list",
    },
    "accessRights": {
        "api_field": "accessRights",
        "property_uri": "http://purl.org/dc/terms/accessRights",
        "multilingual": False,
        "required": False,
    },
    "new_accessRights": {
        "api_field": "accessRights",
        "property_uri": "http://purl.org/dc/terms/accessRights",
        "multilingual": False,
        "required": False,
    },
    # Status and Technical Fields
    "status": {
        "api_field": "status",
        "property_uri": "http://nakala.fr/terms#status",
        "multilingual": False,
        "required": False,
        "controlled_vocabulary": ["draft", "pending", "published", "embargoed"],
    },
    "new_status": {
        "api_field": "status",
        "property_uri": "http://nakala.fr/terms#status",
        "multilingual": False,
        "required": False,
        "controlled_vocabulary": ["draft", "pending", "published", "embargoed"],
    },
    # File and Collection Fields
    "file": {
        "api_field": "file",
        "property_uri": "http://nakala.fr/terms#file",
        "multilingual": False,
        "required": False,
        "format": "file_reference",
    },
    "data_items": {
        "api_field": "dataItems",
        "property_uri": "http://nakala.fr/terms#dataItems",
        "multilingual": False,
        "required": False,
        "format": "folder_patterns",
    },
    # Direct field name mappings (for compatibility with sample datasets)
    "title": {
        "api_field": "title",
        "property_uri": "http://nakala.fr/terms#title",
        "multilingual": True,
        "required": True,
    },
    "description": {
        "api_field": "description",
        "property_uri": "http://purl.org/dc/terms/description",
        "multilingual": True,
        "required": True,
    },
    "keywords": {
        "api_field": "keywords",
        "property_uri": "http://purl.org/dc/terms/subject",
        "multilingual": True,
        "required": False,
    },
    "author": {
        "api_field": "creator",
        "property_uri": "http://purl.org/dc/terms/creator",
        "multilingual": False,
        "required": True,
        "format": "semicolon_split",
    },
    "creator": {
        "api_field": "creator",
        "property_uri": "http://purl.org/dc/terms/creator",
        "multilingual": False,
        "required": False,
        "format": "semicolon_split",
    },
    "contributor": {
        "api_field": "contributor",
        "property_uri": "http://purl.org/dc/terms/contributor",
        "multilingual": False,
        "required": False,
        "format": "semicolon_split",
    },
    "license": {
        "api_field": "license",
        "property_uri": "http://nakala.fr/terms#license",
        "multilingual": False,
        "required": True,
    },
    "type": {
        "api_field": "type",
        "property_uri": "http://nakala.fr/terms#type",
        "multilingual": False,
        "required": True,
    },
    "date": {
        "api_field": "date",
        "property_uri": "http://nakala.fr/terms#created",
        "multilingual": False,
        "required": True,
    },
    "language": {
        "api_field": "language",
        "property_uri": "http://purl.org/dc/terms/language",
        "multilingual": False,
        "required": False,
    },
    "temporal": {
        "api_field": "temporal",
        "property_uri": "http://purl.org/dc/terms/coverage",
        "multilingual": False,
        "required": False,
    },
    "spatial": {
        "api_field": "spatial",
        "property_uri": "http://purl.org/dc/terms/coverage",
        "multilingual": False,
        "required": False,
    },
    "relation": {
        "api_field": "relation",
        "property_uri": "http://purl.org/dc/terms/relation",
        "multilingual": False,
        "required": False,
    },
    "source": {
        "api_field": "source",
        "property_uri": "http://purl.org/dc/terms/source",
        "multilingual": False,
        "required": False,
    },
    "identifier": {
        "api_field": "identifier",
        "property_uri": "http://purl.org/dc/terms/identifier",
        "multilingual": False,
        "required": False,
    },
    "alternative": {
        "api_field": "alternative",
        "property_uri": "http://purl.org/dc/terms/alternative",
        "multilingual": True,
        "required": False,
    },
    "publisher": {
        "api_field": "publisher",
        "property_uri": "http://purl.org/dc/terms/publisher",
        "multilingual": False,
        "required": False,
    },
    # Coverage field for collections
    "coverage": {
        "api_field": "coverage",
        "property_uri": "http://purl.org/dc/terms/coverage",
        "multilingual": True,
        "required": False,
    },
}


class CuratorConfig:
    """Extended configuration for curator operations."""

    def __init__(self, **kwargs):
        # Extract curator-specific settings
        self.batch_size = kwargs.pop("batch_size", 50)
        self.concurrent_operations = kwargs.pop("concurrent_operations", 3)
        self.validation_batch_size = kwargs.pop("validation_batch_size", 100)
        self.skip_existing = kwargs.pop("skip_existing", True)
        self.validate_before_modification = kwargs.pop(
            "validate_before_modification", True
        )
        self.backup_before_changes = kwargs.pop("backup_before_changes", True)
        self.duplicate_threshold = kwargs.pop("duplicate_threshold", 0.85)
        self.max_modifications_per_batch = kwargs.pop(
            "max_modifications_per_batch", 100
        )
        self.require_confirmation = kwargs.pop("require_confirmation", True)
        self.dry_run_default = kwargs.pop("dry_run_default", True)

        # Initialize base config with remaining kwargs
        self.base_config = NakalaConfig(**kwargs)

    def __getattr__(self, name):
        """Delegate attribute access to base config."""
        return getattr(self.base_config, name)


class BatchModificationResult:
    """Container for batch modification results."""

    def __init__(self):
        self.successful: List[Dict[str, Any]] = []
        self.failed: List[Dict[str, Any]] = []
        self.skipped: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None

    def add_success(self, item_id: str, changes: Dict[str, Any]):
        """Record successful modification."""
        self.successful.append(
            {"id": item_id, "changes": changes, "timestamp": datetime.now().isoformat()}
        )

    def add_failure(self, item_id: str, error: str, attempted_changes: Dict[str, Any]):
        """Record failed modification."""
        self.failed.append(
            {
                "id": item_id,
                "error": error,
                "attempted_changes": attempted_changes,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_skip(self, item_id: str, reason: str):
        """Record skipped modification."""
        self.skipped.append(
            {"id": item_id, "reason": reason, "timestamp": datetime.now().isoformat()}
        )

    def add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(f"{datetime.now().isoformat()}: {message}")

    def finalize(self):
        """Mark operation as complete."""
        self.end_time = datetime.now()

    def get_summary(self) -> Dict[str, Any]:
        """Get operation summary."""
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            "total_processed": len(self.successful)
            + len(self.failed)
            + len(self.skipped),
            "successful": len(self.successful),
            "failed": len(self.failed),
            "skipped": len(self.skipped),
            "warnings": len(self.warnings),
            "duration_seconds": duration,
            "success_rate": len(self.successful)
            / max(1, len(self.successful) + len(self.failed))
            * 100,
        }


class NakalaMetadataValidator:
    """Validates metadata against Nakala requirements and best practices."""

    def __init__(self, config: CuratorConfig):
        self.config = config
        self.utils = NakalaCommonUtils()

        # Initialize vocabulary service for validation
        try:
            self.vocab_service = create_vocabulary_service(config.base_config)
            self.schema_generator = MetadataSchemaGenerator(self.vocab_service)
            self.vocabulary_enabled = True
            logger.info("Vocabulary service initialized for validation")
        except Exception as e:
            logger.warning(f"Vocabulary service unavailable: {e}")
            self.vocab_service = None
            self.schema_generator = None
            self.vocabulary_enabled = False

    def validate_required_fields(
        self, metadata: Dict[str, Any], validation_mode: str = "creation"
    ) -> List[str]:
        """Validate required metadata fields with different modes for creation vs modification.

        Args:
            metadata: The metadata to validate
            validation_mode: 'creation' (strict) or 'modification' (permissive)
        """
        errors = []

        if validation_mode == "creation":
            # Strict validation for new resources
            required_fields = ["title", "creator", "description"]
            for field in required_fields:
                if not metadata.get(field):
                    errors.append(f"Required field '{field}' is missing or empty")

        elif validation_mode == "modification":
            # Permissive validation for modifications - only validate fields that are present
            # This allows partial updates without requiring all fields

            # Only validate structure/format of fields that are provided
            if "title" in metadata:
                title = metadata.get("title", "").strip()
                if not title:
                    errors.append("Title cannot be empty when provided")

            if "description" in metadata:
                desc = metadata.get("description", "").strip()
                if not desc:
                    errors.append("Description cannot be empty when provided")

            # Note: 'creator' is not required for modifications as it might be inherited
            # from existing metadata or handled at the API level

        return errors

    def validate_controlled_vocabularies(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate controlled vocabulary values using dynamic vocabulary service."""
        warnings = []

        if not self.vocabulary_enabled:
            # Fallback to static validation
            return self._validate_static_vocabularies(metadata)

        # Dynamic vocabulary validation
        vocabulary_fields = {
            "language": "languages",
            "license": "licenses",
            "type": "datatypes",
        }

        for field_name, vocab_name in vocabulary_fields.items():
            if field_name in metadata:
                value = metadata[field_name]
                if not self.vocab_service.validate_vocabulary_value(vocab_name, value):
                    # Get suggestions for correction
                    suggestions = self.vocab_service.get_vocabulary_suggestions(
                        vocab_name, value, limit=3
                    )
                    suggestion_text = (
                        ", ".join([s.value for s in suggestions])
                        if suggestions
                        else "None available"
                    )
                    warnings.append(
                        f"{field_name.title()} '{value}' not found in vocabulary. "
                        f"Suggestions: {suggestion_text}"
                    )

        return warnings

    def _validate_static_vocabularies(self, metadata: Dict[str, Any]) -> List[str]:
        """Fallback static vocabulary validation."""
        warnings = []

        # Language validation
        if "language" in metadata:
            lang = metadata["language"]
            if lang not in ["fr", "en", "de", "es", "it"]:
                warnings.append(f"Language '{lang}' might not be supported")

        # License validation
        if "license" in metadata:
            license_val = metadata["license"]
            valid_licenses = ["CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0", "CC0-1.0"]
            if license_val not in valid_licenses:
                warnings.append(f"License '{license_val}' is not in recommended list")

        return warnings

    def validate_metadata_quality(
        self, metadata: Dict[str, Any], validation_mode: str = "creation"
    ) -> Dict[str, List[str]]:
        """Comprehensive metadata quality validation.

        Args:
            metadata: The metadata to validate
            validation_mode: 'creation' (strict) or 'modification' (permissive)
        """
        results = {
            "errors": self.validate_required_fields(metadata, validation_mode),
            "warnings": self.validate_controlled_vocabularies(metadata),
            "suggestions": [],
        }

        # Quality suggestions
        if metadata.get("title") and len(metadata["title"]) < 10:
            results["suggestions"].append("Title is very short, consider expanding")

        if metadata.get("description") and len(metadata["description"]) < 50:
            results["suggestions"].append(
                "Description is brief, consider adding more detail"
            )

        if not metadata.get("keywords"):
            results["suggestions"].append(
                "Consider adding keywords for better discoverability"
            )

        return results


class NakalaDuplicateDetector:
    """Detects potential duplicates in datasets and collections."""

    def __init__(self, config: CuratorConfig):
        self.config = config
        self.threshold = config.duplicate_threshold

    def calculate_similarity(
        self, item1: Dict[str, Any], item2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two items based on metadata."""
        # Simple text-based similarity for now
        text1 = f"{item1.get('title', '')} {item1.get('description', '')}"
        text2 = f"{item2.get('title', '')} {item2.get('description', '')}"

        # Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def find_duplicates(
        self, items: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """Find potential duplicates in a list of items."""
        duplicates = []

        for i, item1 in enumerate(items):
            for item2 in items[i + 1 :]:
                similarity = self.calculate_similarity(item1, item2)
                if similarity >= self.threshold:
                    duplicates.append((item1, item2, similarity))

        return duplicates


class NakalaCuratorClient:
    """Main curator client for batch operations and quality management."""

    def __init__(self, config):
        # Handle both NakalaConfig and CuratorConfig for backward compatibility
        if isinstance(config, NakalaConfig):
            # Auto-wrap NakalaConfig in CuratorConfig
            self.config = CuratorConfig(
                api_url=config.api_url,
                api_key=config.api_key,
                timeout=getattr(config, "timeout", 30),
            )
        elif isinstance(config, CuratorConfig):
            self.config = config
        else:
            raise TypeError(
                f"Expected NakalaConfig or CuratorConfig, got {type(config)}"
            )

        self.utils = NakalaCommonUtils()
        self.validator = NakalaMetadataValidator(self.config)
        self.duplicate_detector = NakalaDuplicateDetector(self.config)
        self.user_client = NakalaUserInfoClient(self.config)

        # Initialize vocabulary discovery for this curator instance
        self._initialize_vocabulary_discovery()

        # Initialize template generator and intelligence services
        if self.validator.vocabulary_enabled:
            self.template_generator = create_template_generator(
                self.validator.vocab_service
            )
            self.prepopulation_assistant = create_prepopulation_assistant(
                self.user_client, self.validator.vocab_service
            )
            self.relationship_service = create_relationship_discovery_service(
                self.user_client
            )
            self.autonomous_generator = create_autonomous_generator(self.user_client)
            self.predictive_analytics = create_predictive_analytics(self.user_client)
            logger.info(
                "All intelligence services initialized: template generator, "
                "pre-population, relationships, autonomous generation, and predictive analytics"
            )
        else:
            self.template_generator = None
            self.prepopulation_assistant = None
            self.relationship_service = None
            self.autonomous_generator = None
            self.predictive_analytics = None
            logger.warning(
                "Intelligence services unavailable without vocabulary service"
            )

    def _initialize_vocabulary_discovery(self):
        """Initialize vocabulary discovery in the background."""
        if self.validator.vocabulary_enabled:
            logger.info("Starting background vocabulary discovery...")
            # In a real implementation, this would run asynchronously
            # For now, we'll note that vocabularies will be loaded on first use

    async def get_field_suggestions(
        self, field_name: str, partial_value: str, limit: int = 5
    ) -> List[str]:
        """Get vocabulary suggestions for a field."""
        if not self.validator.vocabulary_enabled:
            return []

        # Map field names to vocabulary categories
        field_vocab_mapping = {
            "language": "languages",
            "license": "licenses",
            "type": "datatypes",
            "spatial": "countries",
        }

        vocab_name = field_vocab_mapping.get(field_name)
        if not vocab_name:
            return []

        suggestions = self.validator.vocab_service.get_vocabulary_suggestions(
            vocab_name, partial_value, limit
        )
        return [s.value for s in suggestions]

    async def get_field_schema(self, property_uri: str) -> Optional[Dict[str, Any]]:
        """Get schema information for a metadata field."""
        if not self.validator.schema_generator:
            return None

        try:
            # Find field config from our mappings
            field_config = None
            for mapping in CSV_FIELD_MAPPINGS.values():
                if mapping["property_uri"] == property_uri:
                    field_config = mapping
                    break

            schema = self.validator.schema_generator.generate_field_schema(
                property_uri, field_config
            )

            return {
                "field_name": schema.field_name,
                "data_type": schema.data_type,
                "required": schema.required,
                "multilingual": schema.multilingual,
                "controlled_vocabulary": schema.controlled_vocabulary,
                "examples": schema.examples,
                "help_text": schema.help_text,
            }
        except Exception as e:
            logger.warning(f"Failed to generate schema for {property_uri}: {e}")
            return None

    async def generate_metadata_template(
        self,
        resource_type: str,
        template_name: str = None,
        user_context: Dict[str, Any] = None,
        include_optional: bool = True,
    ) -> Optional[MetadataTemplate]:
        """Generate an automated metadata template."""
        if not self.template_generator:
            logger.warning("Template generation unavailable without vocabulary service")
            return None

        try:
            logger.info(f"Generating metadata template for {resource_type}")

            # Add user profile information to context if available
            if not user_context:
                user_context = {}

            # Try to get user information for better context
            try:
                user_profile = self.user_client.get_complete_user_profile()
                if user_profile:
                    user_context.update(
                        {
                            "user_collections_count": len(
                                user_profile.get("collections", [])
                            ),
                            "user_datasets_count": len(
                                user_profile.get("datasets", [])
                            ),
                            "has_existing_data": len(user_profile.get("datasets", []))
                            > 0,
                        }
                    )
            except Exception as e:
                logger.debug(f"Could not get user profile for template context: {e}")

            template = await self.template_generator.generate_template(
                resource_type=resource_type,
                template_name=template_name,
                user_context=user_context,
                include_optional=include_optional,
            )

            logger.info(
                f"Generated template with {len(template.fields)} fields "
                f"({len(template.get_required_fields())} required)"
            )
            return template

        except Exception as e:
            logger.error(f"Failed to generate template: {e}")
            return None

    def export_template_to_csv(
        self, template: MetadataTemplate, output_path: str, mode: str = "create"
    ) -> None:
        """Export template as CSV for easy data entry."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if mode == "create":
                    # Creation mode CSV header (direct field names)
                    headers = []
                    for field in template.fields:
                        headers.append(field.name)

                    # Add file field for creation mode
                    if "file" not in headers:
                        headers.insert(0, "file")

                    writer.writerow(headers)

                    # Write example row with defaults and examples
                    example_row = []
                    for i, header in enumerate(headers):
                        if header == "file":
                            example_row.append("path/to/file_or_folder/")
                        else:
                            field = template.get_field_by_name(header)
                            if field:
                                if field.default_value:
                                    example_row.append(field.default_value)
                                elif field.examples:
                                    example_row.append(field.examples[0])
                                else:
                                    example_row.append(f"example_{field.name}")
                            else:
                                example_row.append("")

                    writer.writerow(example_row)

                elif mode == "modify":
                    # Modification mode CSV header (new_ prefixes)
                    headers = ["id", "action"]
                    for field in template.fields:
                        headers.extend([f"current_{field.name}", f"new_{field.name}"])

                    writer.writerow(headers)

                    # Write example row
                    example_row = ["10.34847/nkl.example123", "modify"]
                    for field in template.fields:
                        example_row.extend(
                            [
                                "current_value",
                                field.examples[0] if field.examples else "new_value",
                            ]
                        )

                    writer.writerow(example_row)

            logger.info(f"Template exported as {mode} CSV to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to export template to CSV: {e}")
            raise

    def generate_template_documentation(self, template: MetadataTemplate) -> str:
        """Generate human-readable documentation for a template."""
        doc = []
        doc.append(f"# {template.name}")
        doc.append(f"\n{template.description}")
        doc.append(f"\n**Resource Type:** {template.resource_type}")
        doc.append(f"**Created:** {template.created_at.strftime('%Y-%m-%d %H:%M')}")
        doc.append(f"**Version:** {template.version}")

        if template.tags:
            doc.append(f"**Tags:** {', '.join(template.tags)}")

        doc.append("\n## Fields Summary")
        doc.append(f"- **Total fields:** {len(template.fields)}")
        doc.append(f"- **Required fields:** {len(template.get_required_fields())}")

        # Group by section
        sections = {}
        for field in template.fields:
            if field.section not in sections:
                sections[field.section] = []
            sections[field.section].append(field)

        for section_name in sorted(sections.keys()):
            section_fields = sections[section_name]
            doc.append(f"\n### {section_name.title()} ({len(section_fields)} fields)")

            for field in sorted(section_fields, key=lambda f: (f.priority, f.name)):
                required_marker = "**Required**" if field.required else "Optional"
                multilingual_marker = " (Multilingual)" if field.multilingual else ""

                doc.append(
                    f"\n#### {field.name} - {required_marker}{multilingual_marker}"
                )
                doc.append(f"- **Type:** {field.data_type}")
                doc.append(f"- **URI:** {field.property_uri}")

                if field.controlled_vocabulary:
                    doc.append(f"- **Vocabulary:** {field.controlled_vocabulary}")

                if field.examples:
                    doc.append(f"- **Examples:** {', '.join(field.examples[:3])}")

                if field.help_text:
                    doc.append(f"- **Help:** {field.help_text}")

                if field.default_value:
                    doc.append(f"- **Default:** {field.default_value}")

        return "\n".join(doc)

    async def generate_autonomous_metadata(
        self,
        file_path: str,
        resource_type: str = None,
        target_template: MetadataTemplate = None,
        user_context: Dict[str, Any] = None,
    ) -> Optional[AutonomousGenerationResult]:
        """Generate complete metadata autonomously from file analysis."""
        if not self.autonomous_generator:
            logger.warning(
                "Autonomous generation unavailable without vocabulary service"
            )
            return None

        try:
            logger.info(f"Generating autonomous metadata for: {file_path}")

            # Add user profile information to context if available
            if not user_context:
                user_context = {}

            # Try to get user information for better context
            try:
                user_profile = self.user_client.get_complete_user_profile()
                if user_profile:
                    user_context.update(
                        {
                            "user_collections_count": len(
                                user_profile.get("collections", [])
                            ),
                            "user_datasets_count": len(
                                user_profile.get("datasets", [])
                            ),
                            "has_existing_data": len(user_profile.get("datasets", []))
                            > 0,
                            "primary_language": "fr",  # Default for French institutions
                        }
                    )
            except Exception as e:
                logger.debug(
                    f"Could not get user profile for autonomous generation: {e}"
                )

            result = await self.autonomous_generator.generate_autonomous_metadata(
                file_path=file_path,
                resource_type=resource_type,
                target_template=target_template,
                user_context=user_context,
            )

            logger.info(
                f"Autonomous generation completed: {len(result.generated_metadata)} fields, "
                f"{result.quality_score:.1%} quality, {result.completeness_score:.1%} completeness"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to generate autonomous metadata: {e}")
            return None

    def export_autonomous_result_csv(
        self,
        result: AutonomousGenerationResult,
        output_path: str,
        mode: str = "create",
        include_analysis: bool = True,
    ) -> None:
        """Export autonomous generation result as CSV for upload or modification."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if mode == "create":
                    # Creation mode CSV header
                    headers = ["file"] + [
                        field.name for field in result.template.fields
                    ]
                    writer.writerow(headers)

                    # Generated metadata row
                    metadata_row = [result.file_path]
                    for field in result.template.fields:
                        value = result.generated_metadata.get(field.name, "")
                        metadata_row.append(value)

                    writer.writerow(metadata_row)

                    # Add analysis information as comments if requested
                    if include_analysis:
                        writer.writerow(
                            [
                                f"# Autonomous generation analysis for "
                                f"{Path(result.file_path).name}"
                            ]
                        )
                        writer.writerow(
                            [f"# Content type: {result.content_analysis.content_type}"]
                        )
                        writer.writerow(
                            [
                                f"# Detection confidence: "
                                f"{result.content_analysis.confidence_score:.1%}"
                            ]
                        )
                        writer.writerow(
                            [f"# Quality score: {result.quality_score:.1%}"]
                        )
                        writer.writerow(
                            [f"# Completeness: {result.completeness_score:.1%}"]
                        )

                        if result.recommendations:
                            writer.writerow(["# Recommendations:"])
                            for rec in result.recommendations:
                                writer.writerow([f"#   - {rec}"])

                elif mode == "modify":
                    # Modification mode CSV header
                    headers = ["id", "action"]
                    for field in result.template.fields:
                        headers.extend([f"current_{field.name}", f"new_{field.name}"])

                    writer.writerow(headers)

                    # Example modification row
                    modify_row = ["10.34847/nkl.your_id", "modify"]
                    for field in result.template.fields:
                        current_value = "current_value"
                        new_value = result.generated_metadata.get(
                            field.name, "new_value"
                        )
                        modify_row.extend([current_value, new_value])

                    writer.writerow(modify_row)

            logger.info(f"Autonomous result exported as {mode} CSV to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to export autonomous result to CSV: {e}")
            raise

    def generate_autonomous_metadata_report(
        self, result: AutonomousGenerationResult
    ) -> str:
        """Generate a comprehensive report for autonomous metadata generation."""
        doc = []
        doc.append("# Autonomous Metadata Generation Report")
        doc.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"File: {result.file_path}")
        doc.append(f"Processing time: {result.processing_time:.3f} seconds")

        doc.append("\n## Content Analysis")
        doc.append(f"- **Content Type:** {result.content_analysis.content_type}")
        doc.append(
            f"- **Detected Language:** {result.content_analysis.detected_language}"
        )
        doc.append(
            f"- **Detection Confidence:** {result.content_analysis.confidence_score:.1%}"
        )
        doc.append(
            f"- **Analysis Time:** {result.content_analysis.analysis_time:.3f} seconds"
        )

        if result.content_analysis.extracted_features:
            doc.append("\n### Extracted Features")
            for feature, value in result.content_analysis.extracted_features.items():
                doc.append(f"- **{feature.replace('_', ' ').title()}:** {value}")

        doc.append("\n## Generated Metadata")
        doc.append(f"- **Fields Generated:** {len(result.generated_metadata)}")
        doc.append(f"- **Quality Score:** {result.quality_score:.1%}")
        doc.append(f"- **Completeness Score:** {result.completeness_score:.1%}")

        # Generated fields with confidence scores
        for field_name, value in result.generated_metadata.items():
            confidence = result.confidence_scores.get(field_name, 0.0)
            doc.append(f"\n### {field_name}")
            doc.append(f"- **Value:** {value}")
            doc.append(f"- **Confidence:** {confidence:.1%}")

        # Automated Predictions
        if result.ml_predictions:
            doc.append("\n## Automated Metadata Enhancements")
            for prediction in result.ml_predictions:
                doc.append(f"\n### {prediction.field_name}")
                doc.append(f"- **Predicted Value:** {prediction.predicted_value}")
                doc.append(f"- **Confidence:** {prediction.confidence:.1%}")
                doc.append(f"- **Reasoning:** {prediction.reasoning}")

        # Collaborative Insights
        if result.collaborative_insights:
            doc.append("\n## Collaborative Intelligence")
            # Show top 3 insights
            for insight in result.collaborative_insights[:3]:
                doc.append(
                    f"- **{insight.get('insight_type', 'insight').title()}:** "
                    f"{insight.get('recommendation', 'N/A')}"
                )

        # Recommendations
        if result.recommendations:
            doc.append("\n## Recommendations")
            for rec in result.recommendations:
                doc.append(f"- {rec}")

        # Processing notes
        if result.content_analysis.processing_notes:
            doc.append("\n## Processing Notes")
            for note in result.content_analysis.processing_notes:
                doc.append(f"- {note}")

        return "\n".join(doc)

    async def generate_predictive_analysis_report(
        self,
        custom_timeframes: List[str] = None,
        include_quality: bool = True,
        include_completeness: bool = True,
        include_usage: bool = True,
        output_path: str = None,
    ) -> Optional[PredictiveAnalysisResult]:
        """Generate comprehensive predictive analysis report."""
        if not self.predictive_analytics:
            logger.warning(
                "Predictive analytics unavailable without vocabulary service"
            )
            return None

        try:
            logger.info("Generating predictive analysis report...")

            result = await self.predictive_analytics.generate_predictive_analysis(
                custom_timeframes=custom_timeframes,
                include_quality=include_quality,
                include_completeness=include_completeness,
                include_usage=include_usage,
            )

            logger.info(
                f"Predictive analysis completed: health score "
                f"{result.overall_health_score:.1%}, {len(result.key_insights)} insights, "
                f"{len(result.strategic_recommendations)} recommendations"
            )

            # Export to file if requested
            if output_path:
                report_text = self.generate_predictive_analysis_report_text(result)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(report_text)
                logger.info(f"Predictive analysis report exported to: {output_path}")

            return result

        except Exception as e:
            logger.error(f"Failed to generate predictive analysis: {e}")
            return None

    def generate_predictive_analysis_report_text(
        self, result: PredictiveAnalysisResult
    ) -> str:
        """Generate text report for predictive analysis."""
        doc = []
        doc.append("# Predictive Analytics Report")
        doc.append(f"Generated: {result.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"Processing time: {result.processing_time:.3f} seconds")
        doc.append(f"Data quality score: {result.data_quality_score:.1%}")

        doc.append("\n## Executive Summary")
        doc.append(f"- **Overall Health Score:** {result.overall_health_score:.1%}")
        doc.append(
            f"- **Prediction Timeframes:** {', '.join(result.prediction_timeframes)}"
        )
        doc.append(f"- **Quality Predictions:** {len(result.quality_predictions)}")
        doc.append(
            f"- **Completeness Predictions:** {len(result.completeness_predictions)}"
        )
        doc.append(f"- **Usage Predictions:** {len(result.usage_predictions)}")

        # Key Insights
        if result.key_insights:
            doc.append("\n## Key Insights")
            for insight in result.key_insights:
                doc.append(f"- {insight}")

        # Strategic Recommendations
        if result.strategic_recommendations:
            doc.append("\n## Strategic Recommendations")
            for rec in result.strategic_recommendations:
                doc.append(f"- {rec}")

        # Quality Predictions
        if result.quality_predictions:
            doc.append("\n## Quality Predictions")
            for pred in result.quality_predictions:
                doc.append(f"\n### {pred.metric_name} ({pred.prediction_timeframe})")
                doc.append(f"- **Current:** {pred.current_value:.1%}")
                doc.append(f"- **Predicted:** {pred.predicted_value:.1%}")
                doc.append(f"- **Trend:** {pred.trend_direction}")
                doc.append(f"- **Confidence:** {pred.confidence:.1%}")

                if pred.recommendations:
                    doc.append(
                        f"- **Recommendations:** {'; '.join(pred.recommendations[:2])}"
                    )

        # Completeness Predictions
        if result.completeness_predictions:
            doc.append("\n## Completeness Predictions")
            high_priority = [
                p for p in result.completeness_predictions if p.priority_level == "high"
            ]

            for pred in high_priority[:5]:  # Show top 5 high-priority fields
                doc.append(f"\n### {pred.field_name} ({pred.prediction_timeframe})")
                doc.append(
                    f"- **Current Completion:** {pred.current_completion_rate:.1%}"
                )
                doc.append(
                    f"- **Predicted Completion:** {pred.predicted_completion_rate:.1%}"
                )
                doc.append(f"- **Priority:** {pred.priority_level}")
                doc.append(f"- **Confidence:** {pred.confidence:.1%}")

                if pred.suggested_actions:
                    doc.append(
                        f"- **Actions:** {'; '.join(pred.suggested_actions[:2])}"
                    )

        # Usage Predictions
        if result.usage_predictions:
            doc.append("\n## Usage Predictions")
            for pred in result.usage_predictions:
                doc.append(f"\n### {pred.usage_metric} ({pred.prediction_timeframe})")
                doc.append(f"- **Current:** {pred.current_value:,}")
                doc.append(f"- **Predicted:** {pred.predicted_value:,}")
                growth_rate = (pred.predicted_value - pred.current_value) / max(
                    pred.current_value, 1
                )
                doc.append(f"- **Growth Rate:** {growth_rate:.1%}")
                doc.append(f"- **Confidence:** {pred.confidence:.1%}")

                if pred.capacity_recommendations:
                    doc.append(
                        f"- **Capacity Recommendations:** "
                        f"{'; '.join(pred.capacity_recommendations[:2])}"
                    )

        return "\n".join(doc)

    async def discover_relationships_for_metadata(
        self,
        metadata: Dict[str, Any],
        resource_id: str = None,
        max_suggestions: int = 5,
    ) -> Optional[RelationshipAnalysis]:
        """Discover relationships for given metadata."""
        if not self.relationship_service:
            logger.warning(
                "Relationship discovery unavailable without vocabulary service"
            )
            return None

        try:
            analysis = await self.relationship_service.discover_relationships(
                source_metadata=metadata,
                source_id=resource_id,
                max_suggestions=max_suggestions,
                min_confidence=0.3,
            )

            logger.info(
                f"Discovered {len(analysis.suggestions)} relationship suggestions"
            )
            return analysis

        except Exception as e:
            logger.error(f"Failed to discover relationships: {e}")
            return None

    async def generate_automated_template(
        self,
        resource_type: str,
        file_path: str = None,
        template_name: str = None,
        additional_context: Dict[str, Any] = None,
        include_optional: bool = True,
        include_relationships: bool = True,
    ) -> Optional[
        Tuple[MetadataTemplate, PrePopulationResult, Optional[RelationshipAnalysis]]
    ]:
        """Generate an automated template with pre-populated values and
        relationship suggestions."""
        if not self.template_generator or not self.prepopulation_assistant:
            logger.warning(
                "Intelligent template generation unavailable without vocabulary service"
            )
            return None

        try:
            logger.info(
                f"Generating comprehensive automated template for {resource_type}"
            )

            # Generate base template
            template = await self.generate_metadata_template(
                resource_type=resource_type,
                template_name=template_name,
                include_optional=include_optional,
            )

            if not template:
                logger.error("Failed to generate base template")
                return None

            # Pre-populate the template
            prepop_result = await self.prepopulation_assistant.pre_populate_template(
                template=template,
                api_key=self.config.api_key,
                file_path=file_path,
                additional_context=additional_context,
            )

            # Discover relationships if requested and we have populated metadata
            relationship_analysis = None
            if include_relationships and prepop_result.populated_fields:
                try:
                    relationship_analysis = (
                        await self.discover_relationships_for_metadata(
                            metadata=prepop_result.populated_fields, max_suggestions=5
                        )
                    )

                    # Enhance pre-population with relationship suggestions
                    if relationship_analysis and relationship_analysis.suggestions:
                        template_field_names = [f.name for f in template.fields]
                        rel_suggestions = (
                            self.relationship_service.suggest_relationship_fields(
                                relationship_analysis, template_field_names
                            )
                        )

                        # Add relationship suggestions to prepop suggestions
                        for field_name, suggestions in rel_suggestions.items():
                            if field_name in prepop_result.suggestions:
                                prepop_result.suggestions[field_name].extend(
                                    suggestions
                                )
                            else:
                                prepop_result.suggestions[field_name] = suggestions

                        prepop_result.analysis_notes.append(
                            f"Added {len(rel_suggestions)} relationship field suggestions"
                        )

                except Exception as e:
                    logger.warning(f"Relationship discovery failed: {e}")

            rel_suffix = ""
            if relationship_analysis:
                rel_suffix = (
                    f" and {len(relationship_analysis.suggestions)} "
                    f"relationship suggestions"
                )

            logger.info(
                f"Generated comprehensive automated template with "
                f"{len(prepop_result.populated_fields)} pre-populated fields{rel_suffix}"
            )

            return template, prepop_result, relationship_analysis

        except Exception as e:
            logger.error(f"Failed to generate automated template: {e}")
            return None

    def export_automated_template_csv(
        self,
        template: MetadataTemplate,
        prepop_result: PrePopulationResult,
        output_path: str,
        mode: str = "create",
        include_suggestions: bool = True,
    ) -> None:
        """Export automated template with pre-populated values as CSV."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                if mode == "create":
                    # Creation mode CSV header
                    headers = ["file"] + [field.name for field in template.fields]
                    writer.writerow(headers)

                    # Pre-populated example row
                    example_row = ["path/to/your/file_or_folder/"]
                    for field in template.fields:
                        # Use pre-populated value if available, otherwise use example
                        if field.name in prepop_result.populated_fields:
                            example_row.append(
                                prepop_result.populated_fields[field.name]
                            )
                        elif field.examples:
                            example_row.append(field.examples[0])
                        else:
                            example_row.append(f"example_{field.name}")

                    writer.writerow(example_row)

                    # Add suggestions as comments if requested
                    if include_suggestions:
                        for (
                            field_name,
                            suggestions,
                        ) in prepop_result.suggestions.items():
                            if suggestions:
                                comment_row = [f"# {field_name} suggestions:"] + [
                                    ""
                                ] * (len(headers) - 1)
                                writer.writerow(comment_row)
                                for suggestion in suggestions[:3]:
                                    suggestion_row = [f"#   {suggestion}"] + [""] * (
                                        len(headers) - 1
                                    )
                                    writer.writerow(suggestion_row)

                elif mode == "modify":
                    # Modification mode CSV header
                    headers = ["id", "action"]
                    for field in template.fields:
                        headers.extend([f"current_{field.name}", f"new_{field.name}"])

                    writer.writerow(headers)

                    # Pre-populated example row
                    example_row = ["10.34847/nkl.example123", "modify"]
                    for field in template.fields:
                        current_value = "current_value"
                        # Use pre-populated value if available
                        if field.name in prepop_result.populated_fields:
                            new_value = prepop_result.populated_fields[field.name]
                        elif field.examples:
                            new_value = field.examples[0]
                        else:
                            new_value = "new_value"

                        example_row.extend([current_value, new_value])

                    writer.writerow(example_row)

            logger.info(
                f"Intelligent template exported as {mode} CSV to: {output_path}"
            )

        except Exception as e:
            logger.error(f"Failed to export automated template to CSV: {e}")
            raise

    def generate_automated_template_report(
        self,
        template: MetadataTemplate,
        prepop_result: PrePopulationResult,
        relationship_analysis: Optional[RelationshipAnalysis] = None,
    ) -> str:
        """Generate a comprehensive report for the automated template."""
        doc = []
        doc.append(f"# Comprehensive Intelligent Template Report: {template.name}")
        doc.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append(f"Processing time: {prepop_result.processing_time:.3f} seconds")

        doc.append("\n## Intelligence Summary")
        doc.append(
            f"- **Fields populated:** {len(prepop_result.populated_fields)}/{len(template.fields)}"
        )
        doc.append(f"- **Fields with suggestions:** {len(prepop_result.suggestions)}")
        doc.append(f"- **Analysis notes:** {len(prepop_result.analysis_notes)}")

        if relationship_analysis:
            doc.append(
                f"- **Relationship suggestions:** {len(relationship_analysis.suggestions)}"
            )
            doc.append(
                f"- **Relationship processing time:** "
                f"{relationship_analysis.processing_time:.3f} seconds"
            )

        # Average confidence score
        if prepop_result.confidence_scores:
            avg_confidence = sum(prepop_result.confidence_scores.values()) / len(
                prepop_result.confidence_scores
            )
            doc.append(f"- **Average confidence:** {avg_confidence:.1%}")

        doc.append("\n## Populated Fields")
        for field_name, value in prepop_result.populated_fields.items():
            confidence = prepop_result.confidence_scores.get(field_name, 0.0)
            field = template.get_field_by_name(field_name)

            doc.append(f"\n### {field_name}")
            doc.append(f"- **Value:** {value}")
            doc.append(f"- **Confidence:** {confidence:.1%}")
            if field:
                doc.append(f"- **Required:** {'Yes' if field.required else 'No'}")
                doc.append(f"- **Type:** {field.data_type}")

        # Relationship suggestions
        if relationship_analysis and relationship_analysis.suggestions:
            doc.append("\n## Relationship Suggestions")
            for i, suggestion in enumerate(relationship_analysis.suggestions, 1):
                doc.append(f"\n### {i}. {suggestion.target_title}")
                doc.append(f"- **Target ID:** {suggestion.target_id}")
                doc.append(f"- **Relationship Type:** {suggestion.relationship_type}")
                doc.append(f"- **Confidence:** {suggestion.confidence:.1%}")
                doc.append(f"- **Reason:** {suggestion.reason}")

        # All suggestions (including relationships)
        if prepop_result.suggestions:
            doc.append("\n## All Available Suggestions")
            for field_name, suggestions in prepop_result.suggestions.items():
                if suggestions:
                    doc.append(f"\n### {field_name}")
                    for suggestion in suggestions[:5]:
                        doc.append(f"- {suggestion}")

        # Analysis notes
        if prepop_result.analysis_notes:
            doc.append("\n## Analysis Notes")
            for note in prepop_result.analysis_notes:
                doc.append(f"- {note}")

        if relationship_analysis and relationship_analysis.analysis_notes:
            doc.append("\n## Relationship Analysis Notes")
            for note in relationship_analysis.analysis_notes:
                doc.append(f"- {note}")

        # Template information
        doc.append("\n## Template Information")
        doc.append(f"- **Resource type:** {template.resource_type}")
        doc.append(f"- **Total fields:** {len(template.fields)}")
        doc.append(f"- **Required fields:** {len(template.get_required_fields())}")

        required_fields = [f.name for f in template.get_required_fields()]
        populated_required = [
            f for f in required_fields if f in prepop_result.populated_fields
        ]

        doc.append(
            f"- **Required fields populated:** {len(populated_required)}/{len(required_fields)}"
        )

        if len(populated_required) < len(required_fields):
            missing_required = [
                f for f in required_fields if f not in prepop_result.populated_fields
            ]
            doc.append(f"- **Missing required fields:** {', '.join(missing_required)}")

        # Intelligence capabilities summary
        doc.append("\n## Intelligence Capabilities Applied")
        doc.append(
            "- ✅ **Dynamic Field Discovery:** Vocabulary-based field generation"
        )
        doc.append("- ✅ **Template Generation:** Context-aware metadata templates")
        doc.append("- ✅ **Pre-population:** User context and file analysis")
        doc.append(
            f"- {'✅' if relationship_analysis else '⏸️'} **Relationship Discovery:** "
            f"{'Connected resource analysis' if relationship_analysis else 'Not applied'}"
        )

        return "\n".join(doc)

    def parse_csv_modifications(
        self, csv_path: str, mode="auto"
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Enhanced CSV parser supporting both creation and modification formats.

        Args:
            csv_path: Path to CSV file
            mode: 'auto', 'modify', or 'create'

        Returns:
            Tuple of (modifications_list, unsupported_fields_list)
        """
        modifications = []
        unsupported_fields = set()

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                # Auto-detect mode if not specified
                if mode == "auto":
                    mode = self._detect_csv_mode(reader.fieldnames)
                    logger.info(f"Auto-detected CSV mode: {mode}")

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 for line numbers (header is line 1)

                    if mode == "modify":
                        # Modification mode (requires action column)
                        if row.get("action") == "modify":
                            changes = self._parse_modification_row(
                                row, row_num, unsupported_fields
                            )
                            if changes:
                                modifications.append(
                                    {
                                        "id": row["id"],
                                        "changes": changes,
                                        "row_number": row_num,
                                        "mode": "modify",
                                    }
                                )

                    elif mode == "create":
                        # Creation mode (direct field names from sample datasets)
                        changes = self._parse_creation_row(
                            row, row_num, unsupported_fields
                        )
                        if changes:
                            modifications.append(
                                {
                                    "file_or_folder": row.get(
                                        "file", row.get("folder", "")
                                    ),
                                    "metadata": changes,
                                    "row_number": row_num,
                                    "mode": "create",
                                }
                            )

        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        except Exception as e:
            raise Exception(f"Error parsing CSV file {csv_path}: {e}")

        # Log warnings for unsupported fields
        if unsupported_fields:
            logger.warning(
                f"Unsupported CSV fields ignored: {sorted(unsupported_fields)}"
            )
            logger.info(f"Supported fields: {sorted(CSV_FIELD_MAPPINGS.keys())}")

        return modifications, list(unsupported_fields)

    def _detect_csv_mode(self, fieldnames):
        """Auto-detect CSV format based on column names."""
        if "action" in fieldnames and any(f.startswith("new_") for f in fieldnames):
            return "modify"
        elif (
            "file" in fieldnames or "folder" in fieldnames or "data_items" in fieldnames
        ):
            return "create"
        else:
            return "modify"  # Default to modification mode

    def _parse_modification_row(self, row, row_num, unsupported_fields):
        """Parse row with new_ prefixes (modification format)."""
        changes = {}

        # Process all potential modification fields
        for csv_field, value in row.items():
            if (
                csv_field
                and csv_field.startswith("new_")
                and value
                and str(value).strip()
            ):
                if csv_field in CSV_FIELD_MAPPINGS:
                    field_config = CSV_FIELD_MAPPINGS[csv_field]
                    api_field = field_config["api_field"]

                    # Store the raw value - processing happens in _apply_modification
                    changes[api_field] = str(value).strip()
                    logger.debug(
                        f"Row {row_num}: Mapped {csv_field} -> {api_field} = {changes[api_field]}"
                    )
                else:
                    unsupported_fields.add(csv_field)

        return changes

    def _parse_creation_row(self, row, row_num, unsupported_fields):
        """Parse row with direct field names (creation format from sample datasets)."""
        changes = {}

        for csv_field, value in row.items():
            if csv_field and value and str(value).strip():
                # Skip file/folder fields but allow data_items for collections
                if csv_field in ["file", "folder"]:
                    continue

                # Map direct field names to API fields
                if csv_field in CSV_FIELD_MAPPINGS:
                    field_config = CSV_FIELD_MAPPINGS[csv_field]
                    api_field = field_config["api_field"]

                    # Store the raw value - processing happens in _apply_modification
                    changes[api_field] = str(value).strip()
                    logger.debug(
                        f"Row {row_num}: Mapped {csv_field} -> {api_field} = {changes[api_field]}"
                    )
                else:
                    unsupported_fields.add(csv_field)

        return changes

    def _format_field_value(self, value: str, field_config: Dict[str, Any]) -> Any:
        """Format field value according to its configuration."""
        if field_config.get("format") == "array":
            # Convert semicolon-separated values to array
            return [v.strip() for v in value.split(";") if v.strip()]
        return value.strip()

    def batch_validate_metadata(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate metadata for multiple items."""
        logger.info(f"Validating metadata for {len(items)} items...")

        results = {
            "total_items": len(items),
            "valid_items": 0,
            "items_with_errors": 0,
            "items_with_warnings": 0,
            "validation_details": [],
        }

        for item in items:
            item_id = item.get("id", "unknown")
            validation = self.validator.validate_metadata_quality(item)

            has_errors = len(validation["errors"]) > 0
            has_warnings = len(validation["warnings"]) > 0

            if not has_errors:
                results["valid_items"] += 1
            else:
                results["items_with_errors"] += 1

            if has_warnings:
                results["items_with_warnings"] += 1

            results["validation_details"].append(
                {
                    "id": item_id,
                    "title": item.get("title", ""),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                    "suggestions": validation["suggestions"],
                }
            )

        return results

    def batch_modify_metadata(
        self, modifications: List[Dict[str, Any]], dry_run: bool = True
    ) -> BatchModificationResult:
        """Apply metadata modifications in batches."""
        logger.info(
            f"{'DRY RUN: ' if dry_run else ''}Processing "
            f"{len(modifications)} metadata modifications..."
        )

        result = BatchModificationResult()

        # Process in batches
        for batch_start in range(0, len(modifications), self.config.batch_size):
            batch_end = min(batch_start + self.config.batch_size, len(modifications))
            batch = modifications[batch_start:batch_end]

            logger.info(
                f"Processing batch {batch_start//self.config.batch_size + 1}: "
                f"items {batch_start+1}-{batch_end}"
            )

            self._process_modification_batch(batch, result, dry_run)

            # Small delay between batches to avoid overwhelming API
            time.sleep(0.5)

        result.finalize()
        return result

    def _process_modification_batch(
        self,
        batch: List[Dict[str, Any]],
        result: BatchModificationResult,
        dry_run: bool,
    ):
        """Process a single batch of modifications."""
        for modification in batch:
            item_id = modification.get("id", "unknown")
            changes = modification.get("changes", {})

            try:
                # Validate before modification if enabled
                if self.config.validate_before_modification:
                    # Use modification-specific validation (more permissive than creation)
                    # Only validate the changes being made, not the complete metadata
                    validation = self.validator.validate_metadata_quality(
                        changes, validation_mode="modification"
                    )

                    if validation["errors"]:
                        result.add_failure(
                            item_id,
                            f"Validation failed: {validation['errors']}",
                            changes,
                        )
                        continue

                # Apply modification (or simulate in dry run)
                if dry_run:
                    logger.debug(
                        f"DRY RUN: Would modify {item_id} with changes: {changes}"
                    )
                    result.add_success(item_id, changes)
                else:
                    # Here you would make actual API calls to modify the item
                    success = self._apply_modification(item_id, changes)
                    if success:
                        result.add_success(item_id, changes)
                    else:
                        result.add_failure(item_id, "API modification failed", changes)

            except Exception as e:
                result.add_failure(item_id, str(e), changes)

    def _determine_item_type(self, item_id: str) -> str:
        """Determine if an item is a collection or dataset by trying both endpoints."""
        headers = {"X-API-KEY": self.config.api_key}

        # Try collections endpoint first
        try:
            url = f"{self.config.api_url}/collections/{item_id}"
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            if response.status_code == 200:
                return "collection"
        except Exception:
            pass

        # Try datasets endpoint
        try:
            url = f"{self.config.api_url}/datas/{item_id}"
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            if response.status_code == 200:
                return "dataset"
        except Exception:
            pass

        return "unknown"

    def _apply_modification(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """Apply actual modification via API with comprehensive field support."""
        try:
            headers = {"X-API-KEY": self.config.api_key}

            # Try datasets first (most common), then collections if 404
            dataset_url = f"{self.config.api_url}/datas/{item_id}"
            collection_url = f"{self.config.api_url}/collections/{item_id}"

            # Single API call to get current data
            response = requests.get(
                dataset_url, headers=headers, timeout=self.config.timeout
            )

            if response.status_code == 404:
                # Try collections endpoint
                response = requests.get(
                    collection_url, headers=headers, timeout=self.config.timeout
                )
                if response.status_code == 404:
                    logger.error(f"Item {item_id} not found in datasets or collections")
                    return False
                url = collection_url
            else:
                response.raise_for_status()
                url = dataset_url

            current_data = response.json()
            current_metas = current_data.get("metas", [])

            # Build new metadata array
            new_metas = []

            # Find field configurations for the changes being made
            changing_uris = set()
            for field_name in changes.keys():
                field_config = self._find_field_config_by_api_name(field_name)
                if field_config:
                    changing_uris.add(field_config["property_uri"])

            # Keep existing metas that we're not changing
            for meta in current_metas:
                property_uri = meta.get("propertyUri", "")
                if property_uri not in changing_uris:
                    new_metas.append(meta)

            # Add new/modified metadata using comprehensive field mapping
            for field_name, new_value in changes.items():
                field_config = self._find_field_config_by_api_name(field_name)
                if not field_config:
                    logger.warning(
                        f"No configuration found for field {field_name}, skipping"
                    )
                    continue

                property_uri = field_config["property_uri"]
                is_multilingual = field_config.get("multilingual", False)
                is_array = field_config.get("format") == "array"

                if is_array:
                    # Handle array fields like contributor (real arrays)
                    if isinstance(new_value, list):
                        new_metas.append(
                            {
                                "value": new_value,
                                "propertyUri": property_uri,
                                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            }
                        )
                    else:
                        # Convert string to array if needed
                        array_value = [
                            v.strip() for v in str(new_value).split(";") if v.strip()
                        ]
                        new_metas.append(
                            {
                                "value": array_value,
                                "propertyUri": property_uri,
                                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            }
                        )
                elif field_config.get("format") == "semicolon_split":
                    # Handle semicolon-separated fields like creator - each as separate
                    # metadata entry
                    if isinstance(new_value, list):
                        creators = new_value
                    else:
                        creators = [
                            v.strip() for v in str(new_value).split(";") if v.strip()
                        ]

                    for creator in creators:
                        new_metas.append(
                            {
                                "value": creator,
                                "propertyUri": property_uri,
                                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            }
                        )
                elif field_config.get("format") == "rights_list":
                    # Enhanced rights and access control processing
                    rights_entries = self._process_rights_value(
                        str(new_value), field_name
                    )
                    for rights_entry in rights_entries:
                        new_metas.append(
                            {
                                "value": rights_entry["value"],
                                "propertyUri": property_uri,
                                "typeUri": rights_entry.get(
                                    "typeUri", "http://www.w3.org/2001/XMLSchema#string"
                                ),
                            }
                        )
                elif field_config.get("format") == "file_reference":
                    # Handle file references for folder-based uploads
                    new_metas.append(
                        {
                            "value": str(new_value),
                            "propertyUri": property_uri,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                        }
                    )
                elif field_config.get("format") == "folder_patterns":
                    # Handle data_items field with folder patterns
                    if isinstance(new_value, list):
                        folder_patterns = new_value
                    else:
                        folder_patterns = [
                            v.strip() for v in str(new_value).split(";") if v.strip()
                        ]

                    for pattern in folder_patterns:
                        new_metas.append(
                            {
                                "value": pattern,
                                "propertyUri": property_uri,
                                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            }
                        )
                elif is_multilingual:
                    # Enhanced multilingual fields processing with complex format support
                    processed_values = self._process_multilingual_value(
                        str(new_value), field_name
                    )
                    for lang_entry in processed_values:
                        new_metas.append(
                            {
                                "value": lang_entry["value"],
                                "lang": lang_entry["lang"],
                                "propertyUri": property_uri,
                            }
                        )
                else:
                    # Handle simple non-multilingual fields
                    meta_entry = {
                        "value": str(new_value),
                        "propertyUri": property_uri,
                    }

                    # Add typeUri for certain fields
                    if field_name == "type":
                        meta_entry["typeUri"] = "http://purl.org/dc/terms/URI"

                    new_metas.append(meta_entry)

            # Prepare update payload
            update_payload = {"metas": new_metas}

            # Debug: Log the payload being sent
            logger.debug(f"Sending payload for {item_id}: {update_payload}")

            # Apply the modification
            headers["Content-Type"] = "application/json"
            response = requests.put(
                url, headers=headers, json=update_payload, timeout=self.config.timeout
            )

            # Log error details for debugging
            if response.status_code != 204:
                logger.error(f"API Error {response.status_code}: {response.text}")

            response.raise_for_status()

            logger.info(f"Successfully applied changes to {item_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to apply modification to {item_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing modification for {item_id}: {e}")
            return False

    def _process_multilingual_value(
        self, value: str, field_name: str
    ) -> List[Dict[str, str]]:
        """Enhanced multilingual value processing supporting complex formats.

        Supports formats:
        - Simple: "Simple text" (defaults to French)
        - Basic multilingual: "fr:Français|en:English"
        - Complex with semicolons: "fr:mot1;mot2;mot3|en:word1;word2;word3"
        - Language codes: "fr-FR:Français|en-US:English"
        - Mixed separators: "fr:text1,text2|en:text3;text4"
        - Unicode support: "fr:café;résumé|en:coffee;resume"
        """
        import re

        processed_values = []

        # Handle complex multilingual patterns
        if "|" in value:
            # Split by language separator
            language_parts = value.split("|")
            for part in language_parts:
                part = part.strip()
                if not part:
                    continue

                # Enhanced language code pattern matching
                lang_match = re.match(r"^([a-z]{2}(?:-[A-Z]{2})?):(.+)$", part)
                if lang_match:
                    lang_code = lang_match.group(1)
                    content = lang_match.group(2).strip()

                    # Normalize language codes (fr-FR -> fr, en-US -> en)
                    normalized_lang = lang_code.split("-")[0].lower()

                    if field_name == "keywords":
                        # Enhanced keyword parsing with multiple separators
                        keywords = self._parse_keywords(content)
                        for keyword in keywords:
                            if keyword.strip():
                                processed_values.append(
                                    {"value": keyword.strip(), "lang": normalized_lang}
                                )
                    else:
                        # Handle regular multilingual text
                        processed_values.append(
                            {"value": content, "lang": normalized_lang}
                        )
                else:
                    # Fallback for malformed language prefixes
                    logger.warning(f"Malformed multilingual pattern: {part}")
                    processed_values.append(
                        {"value": part, "lang": "fr"}  # Default to French
                    )
        else:
            # Single language or no language specified
            if field_name == "keywords":
                keywords = self._parse_keywords(value)
                for keyword in keywords:
                    if keyword.strip():
                        processed_values.append(
                            {
                                "value": keyword.strip(),
                                "lang": "fr",  # Default to French
                            }
                        )
            else:
                processed_values.append(
                    {"value": value, "lang": "fr"}  # Default to French
                )

        return processed_values

    def _parse_keywords(self, content: str) -> List[str]:
        """Enhanced keyword parsing supporting multiple separators and formats."""
        import re

        # Handle multiple keyword separators: semicolon, comma, pipe, newline
        # Split by any of these separators
        keywords = re.split(r"[;,\|\n]+", content)

        # Clean and normalize keywords
        cleaned_keywords = []
        for keyword in keywords:
            # Remove extra whitespace and special characters
            cleaned = keyword.strip().strip("\"'")
            if cleaned and len(cleaned) > 1:  # Ignore single characters
                cleaned_keywords.append(cleaned)

        return cleaned_keywords

    def _process_rights_value(
        self, value: str, field_name: str
    ) -> List[Dict[str, str]]:
        """Enhanced rights and access control processing supporting complex formats.

        Supports formats:
        - Simple text: "Open access"
        - Group permissions: "group_uuid,ROLE_READER"
        - Multiple groups: "group1,ROLE_ADMIN;group2,ROLE_READER"
        - User permissions: "user:john.doe@example.com,ROLE_EDITOR"
        - Access dates: "embargo:2025-12-31"
        - Complex rights: "license:CC-BY-4.0|access:open|embargo:2025-01-01"
        """
        from datetime import datetime

        rights_entries = []

        # Handle complex rights expressions
        if "|" in value:
            # Split complex rights by pipe separator
            parts = value.split("|")
            for part in parts:
                part = part.strip()
                if ":" in part:
                    rights_type, rights_value = part.split(":", 1)
                    rights_entries.append(
                        {
                            "value": f"{rights_type.strip()}:{rights_value.strip()}",
                            "typeUri": "http://purl.org/dc/terms/RightsStatement",
                        }
                    )
                else:
                    rights_entries.append(
                        {
                            "value": part,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                        }
                    )
        elif ";" in value:
            # Handle multiple group/user permissions separated by semicolons
            permissions = value.split(";")
            for permission in permissions:
                permission = permission.strip()
                if "," in permission:
                    # Group or user permission format
                    entity, role = permission.split(",", 1)
                    entity = entity.strip()
                    role = role.strip()

                    # Validate role format
                    if role.startswith("ROLE_"):
                        rights_entries.append(
                            {
                                "value": f"{entity},{role}",
                                "typeUri": "http://nakala.fr/terms#permission",
                            }
                        )
                    else:
                        # Invalid role format, treat as simple text
                        rights_entries.append(
                            {
                                "value": permission,
                                "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                            }
                        )
                else:
                    rights_entries.append(
                        {
                            "value": permission,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                        }
                    )
        elif "," in value:
            # Single group/user permission
            parts = value.split(",", 1)
            if len(parts) == 2:
                entity, role = parts
                entity = entity.strip()
                role = role.strip()

                # Enhanced entity type detection
                if entity.startswith("user:"):
                    # User permission
                    rights_entries.append(
                        {
                            "value": f"{entity},{role}",
                            "typeUri": "http://nakala.fr/terms#userPermission",
                        }
                    )
                elif "@" in entity:
                    # Email-based user permission
                    rights_entries.append(
                        {
                            "value": f"user:{entity},{role}",
                            "typeUri": "http://nakala.fr/terms#userPermission",
                        }
                    )
                elif len(entity) == 36 and "-" in entity:
                    # UUID-based group permission
                    rights_entries.append(
                        {
                            "value": f"group:{entity},{role}",
                            "typeUri": "http://nakala.fr/terms#groupPermission",
                        }
                    )
                else:
                    # Generic group permission
                    rights_entries.append(
                        {
                            "value": f"{entity},{role}",
                            "typeUri": "http://nakala.fr/terms#permission",
                        }
                    )
            else:
                # Malformed permission, treat as simple text
                rights_entries.append(
                    {
                        "value": value,
                        "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                    }
                )
        elif ":" in value:
            # Special rights format (embargo, license, etc.)
            rights_type, rights_value = value.split(":", 1)
            rights_type = rights_type.strip().lower()
            rights_value = rights_value.strip()

            if rights_type == "embargo":
                # Validate embargo date format
                try:
                    datetime.strptime(rights_value, "%Y-%m-%d")
                    rights_entries.append(
                        {
                            "value": f"embargo:{rights_value}",
                            "typeUri": "http://nakala.fr/terms#embargoDate",
                        }
                    )
                except ValueError:
                    # Invalid date format
                    logger.warning(f"Invalid embargo date format: {rights_value}")
                    rights_entries.append(
                        {
                            "value": value,
                            "typeUri": "http://www.w3.org/2001/XMLSchema#string",
                        }
                    )
            elif rights_type == "license":
                # License specification
                rights_entries.append(
                    {"value": rights_value, "typeUri": "http://nakala.fr/terms#license"}
                )
            elif rights_type in ["access", "availability"]:
                # Access control specification
                rights_entries.append(
                    {
                        "value": f"{rights_type}:{rights_value}",
                        "typeUri": "http://purl.org/dc/terms/accessRights",
                    }
                )
            else:
                # Generic typed rights
                rights_entries.append(
                    {
                        "value": value,
                        "typeUri": "http://purl.org/dc/terms/RightsStatement",
                    }
                )
        else:
            # Simple rights statement
            # Check for common access control terms
            value_lower = value.lower()
            if value_lower in ["open", "open access", "public"]:
                rights_entries.append(
                    {"value": value, "typeUri": "http://purl.org/dc/terms/accessRights"}
                )
            elif value_lower in ["restricted", "private", "confidential"]:
                rights_entries.append(
                    {"value": value, "typeUri": "http://purl.org/dc/terms/accessRights"}
                )
            elif value_lower.startswith("cc-") or "creative commons" in value_lower:
                # Creative Commons license
                rights_entries.append(
                    {"value": value, "typeUri": "http://nakala.fr/terms#license"}
                )
            else:
                # Generic rights statement
                rights_entries.append(
                    {
                        "value": value,
                        "typeUri": "http://purl.org/dc/terms/RightsStatement",
                    }
                )

        return rights_entries

    def _find_field_config_by_api_name(
        self, api_field_name: str
    ) -> Optional[Dict[str, Any]]:
        """Find field configuration by API field name."""
        for config in CSV_FIELD_MAPPINGS.values():
            if config["api_field"] == api_field_name:
                return config
        return None

    def detect_duplicates_in_collections(
        self, collection_ids: List[str]
    ) -> Dict[str, Any]:
        """Detect duplicates across multiple collections."""
        logger.info(f"Analyzing {len(collection_ids)} collections for duplicates...")

        all_items = []
        collection_items = {}

        # Gather all items from collections
        for collection_id in collection_ids:
            try:
                # Here you would fetch collection items via API
                items = self._get_collection_items(collection_id)
                collection_items[collection_id] = items
                all_items.extend(items)
            except Exception as e:
                logger.error(
                    f"Failed to get items from collection {collection_id}: {e}"
                )

        # Find duplicates
        duplicates = self.duplicate_detector.find_duplicates(all_items)

        return {
            "total_items_analyzed": len(all_items),
            "duplicate_pairs_found": len(duplicates),
            "collections_analyzed": collection_ids,
            "duplicates": [
                {
                    "item1": {"id": dup[0].get("id"), "title": dup[0].get("title")},
                    "item2": {"id": dup[1].get("id"), "title": dup[1].get("title")},
                    "similarity": dup[2],
                }
                for dup in duplicates
            ],
        }

    def _get_collection_items(self, collection_id: str) -> List[Dict[str, Any]]:
        """Get items from a collection via API."""
        try:
            url = f"{self.config.api_url}/collections/{collection_id}/datas"
            headers = {"X-API-KEY": self.config.api_key}

            response = requests.get(url, headers=headers, timeout=self.config.timeout)

            # Handle access denied for private collections
            if response.status_code == 403:
                logger.warning(
                    f"Access denied to collection {collection_id} - may be private or "
                    f"require special permissions"
                )
                return []

            response.raise_for_status()

            result = response.json()
            items = []

            if "data" in result:
                for item in result["data"]:
                    # Extract metadata for duplicate detection
                    title = self._extract_meta_value(item.get("metas", []), "title")
                    description = self._extract_meta_value(
                        item.get("metas", []), "description"
                    )

                    items.append(
                        {
                            "id": item.get("identifier"),
                            "title": title,
                            "description": description,
                            "status": item.get("status", ""),
                            "files": item.get("files", []),
                            "metas": item.get("metas", []),
                        }
                    )

            logger.info(f"Retrieved {len(items)} items from collection {collection_id}")
            return items

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get items from collection {collection_id}: {e}")
            return []

    def _extract_meta_value(
        self, metas: List[Dict], property_name: str, language: str = "fr"
    ) -> str:
        """Extract metadata value by property name."""
        if not metas:
            return ""

        for meta in metas:
            property_uri = meta.get("propertyUri", "")
            meta_lang = meta.get("lang", "")

            if property_name in property_uri.lower() and meta_lang == language:
                return meta.get("value", "")

        # Fall back to any language
        for meta in metas:
            property_uri = meta.get("propertyUri", "")
            if property_name in property_uri.lower():
                return meta.get("value", "")

        return ""

    def generate_quality_report(self, scope: str = "all") -> Dict[str, Any]:
        """Generate comprehensive quality report for user's data."""
        logger.info("Generating data quality report...")

        # Get user's data
        user_profile = self.user_client.get_complete_user_profile()

        report = {
            "generated_at": datetime.now().isoformat(),
            "scope": scope,
            "summary": user_profile["summary"],
            "collections_analysis": {},
            "datasets_analysis": {},
            "overall_quality_score": 0.0,
            "recommendations": [],
        }

        # Analyze collections
        if user_profile["collections"]:
            validation_result = self.batch_validate_metadata(
                user_profile["collections"]
            )
            report["collections_analysis"] = validation_result

        # Analyze datasets
        if user_profile["datasets"]:
            validation_result = self.batch_validate_metadata(user_profile["datasets"])
            report["datasets_analysis"] = validation_result

        # Calculate overall quality score
        total_items = len(user_profile["collections"]) + len(user_profile["datasets"])
        if total_items > 0:
            valid_collections = report["collections_analysis"].get("valid_items", 0)
            valid_datasets = report["datasets_analysis"].get("valid_items", 0)
            report["overall_quality_score"] = (
                (valid_collections + valid_datasets) / total_items * 100
            )

        # Generate recommendations
        self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]):
        """Generate quality improvement recommendations."""
        recommendations = []

        collections_analysis = report.get("collections_analysis", {})
        datasets_analysis = report.get("datasets_analysis", {})

        # Check for metadata quality issues
        if collections_analysis.get("items_with_errors", 0) > 0:
            recommendations.append(
                f"Fix metadata errors in {collections_analysis['items_with_errors']} collections"
            )

        if datasets_analysis.get("items_with_errors", 0) > 0:
            recommendations.append(
                f"Fix metadata errors in {datasets_analysis['items_with_errors']} datasets"
            )

        # Check overall quality score
        quality_score = report.get("overall_quality_score", 0)
        if quality_score < 80:
            recommendations.append(
                "Consider improving metadata quality - current score is below 80%"
            )

        if quality_score < 60:
            recommendations.append(
                "Urgent: Metadata quality is critically low - review and update metadata"
            )

        report["recommendations"] = recommendations

    def get_collection_data_items(self, collection_id: str) -> List[Dict[str, Any]]:
        """Get data items from a collection via API.

        Args:
            collection_id: The identifier of the collection

        Returns:
            List of data items with their metadata
        """
        return self._get_collection_items(collection_id)

    def export_modifications_template(
        self, items: List[Dict[str, Any]], output_path: str
    ):
        """Export a CSV template for batch modifications."""
        logger.info(
            f"Exporting modification template for {len(items)} items to {output_path}"
        )

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "id",
                    "current_title",
                    "new_title",
                    "current_description",
                    "new_description",
                    "current_keywords",
                    "new_keywords",
                    "current_license",
                    "new_license",
                    "current_language",
                    "new_language",
                    "action",
                ]
            )

            # Data rows
            for item in items:
                writer.writerow(
                    [
                        item.get("id", ""),
                        item.get("title", ""),
                        "",  # new_title - to be filled
                        item.get("description", ""),
                        "",  # new_description - to be filled
                        item.get("keywords", ""),
                        "",  # new_keywords - to be filled
                        item.get("license", ""),
                        "",  # new_license - to be filled
                        item.get("language", ""),
                        "",  # new_language - to be filled
                        "modify",  # action
                    ]
                )

        logger.info(f"Template exported to {output_path}")


def print_field_reference():
    """Print comprehensive field reference for curator operations."""
    print("\n" + "=" * 80)
    print("NAKALA CURATOR - FIELD REFERENCE")
    print("=" * 80)

    print("\n📋 DATA ITEM FIELDS")
    print("-" * 40)

    data_fields = [
        (
            "title",
            "http://nakala.fr/terms#title",
            "Yes",
            "Required",
            '"fr:French|en:English"',
        ),
        (
            "description",
            "http://purl.org/dc/terms/description",
            "Yes",
            "Required",
            '"fr:Description|en:Description"',
        ),
        (
            "keywords",
            "http://purl.org/dc/terms/subject",
            "Yes",
            "Optional",
            '"fr:mot1;mot2|en:word1;word2"',
        ),
        (
            "author",
            "http://nakala.fr/terms#creator",
            "No",
            "Required",
            '"Surname,Givenname"',
        ),
        (
            "contributor",
            "http://purl.org/dc/terms/contributor",
            "No",
            "Optional",
            '"Smith,John;Martin,Alice"',
        ),
        (
            "type",
            "http://nakala.fr/terms#type",
            "No",
            "Required",
            "COAR Resource Type URI",
        ),
        ("license", "http://nakala.fr/terms#license", "No", "Required", '"CC-BY-4.0"'),
        (
            "date",
            "http://nakala.fr/terms#created",
            "No",
            "Required",
            '"2024-01-15" or "2024"',
        ),
        (
            "language",
            "http://purl.org/dc/terms/language",
            "No",
            "Optional",
            '"fr" or "en"',
        ),
        (
            "temporal",
            "http://purl.org/dc/terms/coverage",
            "No",
            "Optional",
            '"2020/2023"',
        ),
        ("spatial", "http://purl.org/dc/terms/coverage", "No", "Optional", '"France"'),
        (
            "relation",
            "http://purl.org/dc/terms/relation",
            "No",
            "Optional",
            "URI or text",
        ),
        (
            "source",
            "http://purl.org/dc/terms/source",
            "No",
            "Optional",
            "Source reference",
        ),
        (
            "identifier",
            "http://purl.org/dc/terms/identifier",
            "No",
            "Optional",
            '"DOI:10.1234/example"',
        ),
    ]

    print(f"{'Field':<12} {'Multilingual':<12} {'Required':<10} {'Example':<25}")
    print("-" * 70)
    for field, _, multilingual, required, example in data_fields:
        print(f"{field:<12} {multilingual:<12} {required:<10} {example:<25}")

    print("\n📚 COLLECTION FIELDS")
    print("-" * 40)

    collection_fields = [
        ("title", "Required", '"fr:Collection|en:Collection"'),
        ("status", "Required", '"private" or "public"'),
        ("description", "Optional", '"fr:Description|en:Description"'),
        ("keywords", "Optional", '"fr:mot1;mot2|en:word1;word2"'),
        ("creator", "Optional", '"Surname,Givenname"'),
        ("data_items", "Optional", "Folder patterns or IDs"),
    ]

    print(f"{'Field':<12} {'Required':<10} {'Example':<30}")
    print("-" * 55)
    for field, required, example in collection_fields:
        print(f"{field:<12} {required:<10} {example:<30}")

    print("\n🔧 BATCH MODIFICATION CSV FORMAT")
    print("-" * 40)
    print("id,action,current_title,new_title,current_description,new_description")
    print(
        '10.34847/nkl.abc123,update,"Old Title","fr:New|en:Title","Old desc",'
        '"fr:New|en:Description"'
    )

    print("\n🌐 MULTILINGUAL FORMAT")
    print("-" * 40)
    print('Format: "language_code:content|language_code:content"')
    print("Examples:")
    print('  Single:   "Simple English Title"')
    print('  Multiple: "fr:Titre français|en:English Title"')
    print('  Keywords: "fr:mot1;mot2|en:word1;word2"')

    print("\n⚡ QUICK COMMANDS")
    print("-" * 40)
    print("# Show this reference")
    print("o-nakala-curator --list-fields")
    print("")
    print("# Generate quality report")
    print("o-nakala-curator --quality-report --api-key YOUR_KEY")
    print("")
    print("# Batch modify from CSV (dry run)")
    print("o-nakala-curator --batch-modify changes.csv --dry-run --api-key YOUR_KEY")
    print("")
    print("# Validate metadata")
    print("o-nakala-curator --validate-metadata --scope datasets --api-key YOUR_KEY")

    print("\n📖 COMPLETE REFERENCE")
    print("-" * 40)
    print("For detailed documentation with all fields, formats, and examples:")
    print("See: docs/curator-field-reference.md")

    print("\n" + "=" * 80)


def main():
    """
    Main entry point for o-nakala-curator (v2.2.0).

    Examples:
        # Generate quality report (validated v2.2.0):
        o-nakala-curator --api-key "33170cfe-f53c-550b-5fb6-4814ce981293" \\
            --quality-report --scope collections

        # Results: Analyzes 207 collections with detailed validation reports
    """
    parser = argparse.ArgumentParser(
        description="Nakala Curator - Data curation and quality management tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate quality report
  python o-nakala-curator.py --quality-report

  # Validate metadata for all collections
  python o-nakala-curator.py --validate-metadata --scope collections

  # Detect duplicates
  python o-nakala-curator.py --detect-duplicates --collections col1,col2

  # Apply batch modifications from CSV
  python o-nakala-curator.py --batch-modify modifications.csv --dry-run
        """,
    )

    parser.add_argument(
        "--api-key", help="Nakala API key (or set NAKALA_API_KEY environment variable)"
    )

    parser.add_argument(
        "--api-url",
        default="https://apitest.nakala.fr",
        help="Nakala API URL (default: test API)",
    )

    parser.add_argument(
        "--quality-report",
        action="store_true",
        help="Generate comprehensive quality report",
    )

    parser.add_argument(
        "--validate-metadata",
        action="store_true",
        help="Validate metadata for specified scope",
    )

    parser.add_argument(
        "--detect-duplicates", action="store_true", help="Detect potential duplicates"
    )

    parser.add_argument(
        "--batch-modify", help="CSV file with batch modifications to apply"
    )

    parser.add_argument(
        "--export-template", help="Export modification template CSV for specified items"
    )

    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "collections", "datasets"],
        help="Scope for operations",
    )

    parser.add_argument("--collections", help="Comma-separated list of collection IDs")

    parser.add_argument(
        "--output", "-o", help="Output file path for reports and exports"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without making changes",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing (default: 50)",
    )

    parser.add_argument(
        "--list-fields",
        action="store_true",
        help="Display complete field reference with examples",
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip client-side validation before modifications (use with caution)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_common_logging(level=log_level)

    try:
        # Handle --list-fields before configuration validation
        if args.list_fields:
            print_field_reference()
            return 0

        # Create configuration
        config = CuratorConfig(
            api_url=args.api_url,
            api_key=args.api_key,
            batch_size=args.batch_size,
            dry_run_default=args.dry_run,
            validate_before_modification=not args.skip_validation,
        )

        if not config.validate():
            logger.error("Configuration validation failed")
            return 1

        # Create curator client
        curator = NakalaCuratorClient(config)

        # Execute requested operations
        if args.quality_report:
            report = curator.generate_quality_report(scope=args.scope)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Quality report exported to: {args.output}")
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

        elif args.validate_metadata:
            # Get user data for validation
            user_client = NakalaUserInfoClient(config)
            profile = user_client.get_complete_user_profile()

            items = []
            if args.scope == "collections":
                items = profile["collections"]
            elif args.scope == "datasets":
                items = profile["datasets"]
            else:
                items = profile["collections"] + profile["datasets"]

            validation_result = curator.batch_validate_metadata(items)
            print(json.dumps(validation_result, indent=2, ensure_ascii=False))

        elif args.detect_duplicates:
            if not args.collections:
                logger.error("--collections parameter required for duplicate detection")
                return 1

            collection_ids = [cid.strip() for cid in args.collections.split(",")]
            duplicates = curator.detect_duplicates_in_collections(collection_ids)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(duplicates, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Duplicate analysis exported to: {args.output}")
            else:
                print(json.dumps(duplicates, indent=2, ensure_ascii=False, default=str))

        elif args.export_template:
            # Export modification template
            user_client = NakalaUserInfoClient(config)
            profile = user_client.get_complete_user_profile()

            items = []
            if args.scope == "collections":
                items = profile["collections"]
            elif args.scope == "datasets":
                items = profile["datasets"]
            else:
                items = profile["collections"] + profile["datasets"]

            # Filter by specific collections if provided
            if args.collections:
                collection_ids = [cid.strip() for cid in args.collections.split(",")]
                if args.scope == "collections":
                    items = [item for item in items if item.get("id") in collection_ids]
                elif args.scope == "datasets":
                    # For datasets, get items from specified collections
                    collection_items = []
                    for collection_id in collection_ids:
                        collection_data = curator.get_collection_data_items(
                            collection_id
                        )
                        collection_items.extend(collection_data)
                    items = collection_items

            curator.export_modifications_template(items, args.export_template)
            logger.info(f"Modification template exported to: {args.export_template}")

        elif args.batch_modify:
            # Load modifications from CSV using comprehensive parser
            try:
                modifications, unsupported_fields = curator.parse_csv_modifications(
                    args.batch_modify
                )

                if unsupported_fields:
                    logger.warning(
                        f"Found {len(unsupported_fields)} unsupported fields: {unsupported_fields}"
                    )
                    logger.info("Continuing with supported fields only...")

                logger.info(f"Parsed {len(modifications)} modifications from CSV")

            except Exception as e:
                logger.error(f"Failed to parse CSV file: {e}")
                return 1

            if modifications:
                result = curator.batch_modify_metadata(
                    modifications, dry_run=args.dry_run
                )
                summary = result.get_summary()

                print(
                    f"Batch modification {'simulation' if args.dry_run else 'completed'}:"
                )
                print(f"  Total processed: {summary['total_processed']}")
                print(f"  Successful: {summary['successful']}")
                print(f"  Failed: {summary['failed']}")
                print(f"  Skipped: {summary['skipped']}")
                print(f"  Success rate: {summary['success_rate']:.1f}%")

                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        json.dump(
                            result.__dict__,
                            f,
                            indent=2,
                            ensure_ascii=False,
                            default=str,
                        )
            else:
                logger.error("No valid modifications found in CSV file")
                logger.info("Check that:")
                logger.info("- CSV has 'action' column with 'modify' values")
                logger.info("- CSV has 'id' column with valid item identifiers")
                logger.info(
                    f"- CSV has one or more supported fields: {list(CSV_FIELD_MAPPINGS.keys())}"
                )
                if unsupported_fields:
                    logger.info(f"- Remove unsupported fields: {unsupported_fields}")
                return 1

        else:
            parser.print_help()
            return 1

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
