"""
NAKALA Template Generator

Provides intelligent metadata template generation with vocabulary integration.
Part of the Complete Metadata Management System - Foundation Phase.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .vocabulary import NakalaVocabularyService

logger = logging.getLogger(__name__)


@dataclass
class TemplateField:
    """Represents a field in a metadata template."""

    name: str
    property_uri: str
    data_type: str
    required: bool = False
    multilingual: bool = False
    controlled_vocabulary: Optional[str] = None
    validation_pattern: Optional[str] = None
    examples: List[str] = None
    help_text: str = ""
    default_value: Optional[str] = None
    priority: int = 1  # 1=high, 2=medium, 3=low
    section: str = "basic"  # grouping for UI

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class MetadataTemplate:
    """Complete metadata template with fields and configuration."""

    name: str
    description: str
    resource_type: str
    fields: List[TemplateField]
    created_at: datetime
    version: str = "1.0"
    context: Dict[str, Any] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.tags is None:
            self.tags = []

    def get_required_fields(self) -> List[TemplateField]:
        """Get all required fields."""
        return [field for field in self.fields if field.required]

    def get_fields_by_section(self, section: str) -> List[TemplateField]:
        """Get fields for a specific section."""
        return [field for field in self.fields if field.section == section]

    def get_field_by_name(self, name: str) -> Optional[TemplateField]:
        """Get a specific field by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None


class TemplateGenerator:
    """Generates intelligent metadata templates based on resource type and context."""

    def __init__(self, vocabulary_service: NakalaVocabularyService):
        self.vocab_service = vocabulary_service
        self.template_cache: Dict[str, MetadataTemplate] = {}

        # Define field priorities and sections
        self.field_priorities = {
            "title": (1, "basic"),
            "description": (1, "basic"),
            "type": (1, "basic"),
            "creator": (1, "creators"),
            "date": (1, "basic"),
            "license": (1, "rights"),
            "language": (2, "content"),
            "keywords": (2, "content"),
            "contributor": (2, "creators"),
            "publisher": (2, "creators"),
            "alternative": (3, "content"),
            "identifier": (2, "technical"),
            "source": (3, "relations"),
            "relation": (3, "relations"),
            "temporal": (3, "coverage"),
            "spatial": (3, "coverage"),
            "rights": (2, "rights"),
            "accessRights": (2, "rights"),
            "status": (1, "technical"),
        }

    async def generate_template(
        self,
        resource_type: str,
        template_name: str = None,
        user_context: Dict[str, Any] = None,
        include_optional: bool = True,
    ) -> MetadataTemplate:
        """Generate a metadata template for a specific resource type."""

        if template_name is None:
            template_name = f"{resource_type}_template"

        logger.info(f"Generating template: {template_name} for {resource_type}")

        # Check cache first
        cache_key = f"{template_name}_{resource_type}_{include_optional}"
        if cache_key in self.template_cache:
            logger.debug(f"Using cached template: {cache_key}")
            return self.template_cache[cache_key]

        # Get required and recommended fields
        required_fields = self._get_required_fields(resource_type)
        recommended_fields = self._get_recommended_fields(resource_type, user_context)

        # Combine field sets
        all_fields = required_fields.copy()
        if include_optional:
            all_fields.extend(
                [f for f in recommended_fields if f not in required_fields]
            )

        # Generate template fields
        template_fields = []
        for field_name in all_fields:
            field = await self._generate_template_field(
                field_name, resource_type, user_context
            )
            if field:
                template_fields.append(field)

        # Sort fields by priority and section
        template_fields.sort(key=lambda f: (f.priority, f.section, f.name))

        # Create template
        template = MetadataTemplate(
            name=template_name,
            description=self._generate_template_description(resource_type),
            resource_type=resource_type,
            fields=template_fields,
            created_at=datetime.now(),
            context=user_context or {},
            tags=self._generate_template_tags(resource_type),
        )

        # Cache the template
        self.template_cache[cache_key] = template

        logger.info(f"Generated template with {len(template_fields)} fields")
        return template

    def _get_required_fields(self, resource_type: str) -> List[str]:
        """Get required fields for a resource type."""
        # Base required fields for all resource types
        base_required = ["title", "description", "creator", "date", "license", "type"]

        # Resource-type specific requirements
        type_specific = {
            "dataset": ["language"],
            "image": ["format"],
            "collection": ["status"],
            "document": ["language"],
            "software": ["identifier"],
        }

        required = base_required.copy()
        if resource_type in type_specific:
            required.extend(type_specific[resource_type])

        return list(set(required))  # Remove duplicates

    def _get_recommended_fields(
        self, resource_type: str, user_context: Dict[str, Any] = None
    ) -> List[str]:
        """Get recommended fields based on resource type and context."""
        recommended = [
            "keywords",
            "contributor",
            "alternative",
            "identifier",
            "temporal",
            "spatial",
            "rights",
            "accessRights",
        ]

        # Add context-specific recommendations
        if user_context:
            # If user has geographic focus, prioritize spatial
            if user_context.get("geographic_focus"):
                if "spatial" not in recommended:
                    recommended.append("spatial")

            # If user works with historical data, prioritize temporal
            if user_context.get("historical_focus"):
                if "temporal" not in recommended:
                    recommended.append("temporal")

        return recommended

    async def _generate_template_field(
        self, field_name: str, resource_type: str, user_context: Dict[str, Any] = None
    ) -> Optional[TemplateField]:
        """Generate a template field with all metadata."""

        # Get property URI for field
        property_uri = self._get_property_uri(field_name)
        if not property_uri:
            logger.warning(f"No property URI found for field: {field_name}")
            return None

        # Get priority and section
        priority, section = self.field_priorities.get(field_name, (2, "other"))

        # Determine data type
        data_type = self._determine_data_type(field_name, property_uri)

        # Check if required
        required = field_name in self._get_required_fields(resource_type)

        # Check if multilingual
        multilingual = self._is_multilingual_field(field_name)

        # Get controlled vocabulary
        controlled_vocab = self._get_controlled_vocabulary(field_name)

        # Generate examples
        examples = await self._generate_examples(
            field_name, controlled_vocab, user_context
        )

        # Generate help text
        help_text = self._generate_help_text(field_name, data_type, controlled_vocab)

        # Get default value if available
        default_value = self._get_default_value(field_name, user_context)

        return TemplateField(
            name=field_name,
            property_uri=property_uri,
            data_type=data_type,
            required=required,
            multilingual=multilingual,
            controlled_vocabulary=controlled_vocab,
            examples=examples,
            help_text=help_text,
            default_value=default_value,
            priority=priority,
            section=section,
        )

    def _get_property_uri(self, field_name: str) -> Optional[str]:
        """Get the property URI for a field name."""
        # Map common field names to property URIs
        uri_mappings = {
            "title": "http://nakala.fr/terms#title",
            "description": "http://purl.org/dc/terms/description",
            "creator": "http://purl.org/dc/terms/creator",
            "contributor": "http://purl.org/dc/terms/contributor",
            "date": "http://nakala.fr/terms#created",
            "license": "http://nakala.fr/terms#license",
            "type": "http://nakala.fr/terms#type",
            "language": "http://purl.org/dc/terms/language",
            "keywords": "http://purl.org/dc/terms/subject",
            "alternative": "http://purl.org/dc/terms/alternative",
            "identifier": "http://purl.org/dc/terms/identifier",
            "source": "http://purl.org/dc/terms/source",
            "relation": "http://purl.org/dc/terms/relation",
            "temporal": "http://purl.org/dc/terms/coverage",
            "spatial": "http://purl.org/dc/terms/coverage",
            "rights": "http://purl.org/dc/terms/rights",
            "accessRights": "http://purl.org/dc/terms/accessRights",
            "publisher": "http://purl.org/dc/terms/publisher",
            "status": "http://nakala.fr/terms#status",
        }

        return uri_mappings.get(field_name)

    def _determine_data_type(self, field_name: str, property_uri: str) -> str:
        """Determine the data type for a field."""
        type_mappings = {
            "date": "date",
            "language": "language_code",
            "license": "license_uri",
            "type": "resource_type_uri",
            "identifier": "identifier",
            "rights": "rights_expression",
            "status": "status_value",
        }

        return type_mappings.get(field_name, "string")

    def _is_multilingual_field(self, field_name: str) -> bool:
        """Check if a field supports multiple languages."""
        multilingual_fields = {"title", "description", "keywords", "alternative"}
        return field_name in multilingual_fields

    def _get_controlled_vocabulary(self, field_name: str) -> Optional[str]:
        """Get the controlled vocabulary for a field."""
        vocab_mappings = {
            "language": "languages",
            "license": "licenses",
            "type": "datatypes",
            "spatial": "countries",
            "status": "data_statuses",
        }

        return vocab_mappings.get(field_name)

    async def _generate_examples(
        self,
        field_name: str,
        controlled_vocab: Optional[str],
        user_context: Dict[str, Any] = None,
    ) -> List[str]:
        """Generate example values for a field."""
        examples = []

        # Get examples from vocabulary if available
        if controlled_vocab and self.vocab_service:
            vocab_entries = self.vocab_service.get_vocabulary(controlled_vocab)
            if vocab_entries:
                examples = [entry.value for entry in vocab_entries[:3]]

        # Generate contextual examples if no vocabulary
        if not examples:
            contextual_examples = {
                "title": [
                    "Research Dataset on Climate Change",
                    "fr:Données de recherche|en:Research Data",
                ],
                "description": [
                    "Comprehensive description of the research data and methodology",
                    "fr:Description détaillée|en:Detailed description",
                ],
                "creator": ["Surname,Givenname", "Doe,John;Smith,Jane"],
                "date": ["2024-01-15", "2024", "2020/2023"],
                "keywords": [
                    "research, data, analysis",
                    "fr:recherche;données|en:research;data",
                ],
                "identifier": ["DOI:10.1234/example", "ISBN:978-0123456789"],
                "temporal": ["2020/2023", "2024-01-01/2024-12-31"],
                "spatial": ["France", "Europe", "Global"],
            }

            examples = contextual_examples.get(
                field_name, [f"Example {field_name} value"]
            )

        # Add user context examples
        if user_context:
            context_examples = self._get_context_examples(field_name, user_context)
            examples.extend(context_examples)

        return examples[:5]  # Limit to 5 examples

    def _get_context_examples(
        self, field_name: str, user_context: Dict[str, Any]
    ) -> List[str]:
        """Get examples based on user context."""
        examples = []

        if field_name == "creator" and user_context.get("user_name"):
            examples.append(user_context["user_name"])

        if field_name == "language" and user_context.get("default_language"):
            examples.append(user_context["default_language"])

        if field_name == "publisher" and user_context.get("affiliation"):
            examples.append(user_context["affiliation"])

        return examples

    def _generate_help_text(
        self, field_name: str, data_type: str, controlled_vocab: Optional[str]
    ) -> str:
        """Generate helpful guidance text for a field."""
        base_help = {
            "title": (
                "The main title of the resource. Use multilingual format "
                "for international content."
            ),
            "description": (
                "A comprehensive description of the resource content, purpose, "
                "and methodology."
            ),
            "creator": (
                'Primary authors or creators. Use format "Surname,Givenname" '
                "and separate multiple creators with semicolons."
            ),
            "contributor": "Additional people who contributed to creating the resource.",
            "date": "Date of creation, publication, or coverage in YYYY-MM-DD format.",
            "license": "License under which the resource is made available (e.g., CC-BY-4.0).",
            "type": "Resource type from COAR vocabulary indicating what kind of resource this is.",
            "language": "Primary language of the resource content using ISO 639-1 codes.",
            "keywords": (
                "Descriptive keywords or subject terms. Use multilingual format "
                "if applicable."
            ),
            "identifier": "Persistent identifier such as DOI, ISBN, or other standard identifier.",
            "rights": "Rights statement or access permissions for the resource.",
            "status": "Publication status of the resource (draft, pending, published, etc.)",
        }

        help_text = base_help.get(field_name, f"Value for the {field_name} field.")

        # Add vocabulary-specific help
        if controlled_vocab:
            help_text += (
                f" This field uses controlled vocabulary from {controlled_vocab}."
            )

        # Add data type specific help
        if data_type == "date":
            help_text += " Use ISO 8601 date format (YYYY-MM-DD)."
        elif data_type == "language_code":
            help_text += " Use ISO 639-1 two-letter language codes."

        return help_text

    def _get_default_value(
        self, field_name: str, user_context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Get default value for a field based on context."""
        if not user_context:
            return None

        defaults = {
            "creator": user_context.get("user_name"),
            "language": user_context.get("default_language", "en"),
            "publisher": user_context.get("affiliation"),
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        return defaults.get(field_name)

    def _generate_template_description(self, resource_type: str) -> str:
        """Generate a description for the template."""
        descriptions = {
            "dataset": "Template for research datasets with comprehensive metadata fields.",
            "image": "Template for image resources with visual content metadata.",
            "collection": "Template for collections containing multiple related resources.",
            "document": "Template for text documents and publications.",
            "software": "Template for software and code resources.",
        }

        return descriptions.get(
            resource_type, f"Metadata template for {resource_type} resources."
        )

    def _generate_template_tags(self, resource_type: str) -> List[str]:
        """Generate tags for the template."""
        base_tags = ["nakala", "metadata", "template"]
        type_tags = [resource_type, f"{resource_type}_template"]

        return base_tags + type_tags

    def export_template(self, template: MetadataTemplate, file_path: str) -> None:
        """Export template to JSON file."""
        template_data = asdict(template)

        # Convert datetime to string for JSON serialization
        template_data["created_at"] = template.created_at.isoformat()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Template exported to: {file_path}")

    def import_template(self, file_path: str) -> MetadataTemplate:
        """Import template from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            template_data = json.load(f)

        # Convert string back to datetime
        template_data["created_at"] = datetime.fromisoformat(
            template_data["created_at"]
        )

        # Convert field dictionaries back to TemplateField objects
        fields = []
        for field_data in template_data["fields"]:
            fields.append(TemplateField(**field_data))
        template_data["fields"] = fields

        template = MetadataTemplate(**template_data)

        logger.info(f"Template imported from: {file_path}")
        return template


# Factory function
def create_template_generator(
    vocabulary_service: NakalaVocabularyService,
) -> TemplateGenerator:
    """Create a template generator with vocabulary service."""
    return TemplateGenerator(vocabulary_service)


# Convenience function for quick template generation
async def generate_quick_template(
    resource_type: str,
    api_url: str = "https://apitest.nakala.fr",
    api_key: str = None,
    user_context: Dict[str, Any] = None,
) -> MetadataTemplate:
    """Quick template generation with minimal setup."""
    from .vocabulary import create_vocabulary_service
    from .common.config import NakalaConfig

    config = NakalaConfig(api_url=api_url, api_key=api_key)
    vocab_service = create_vocabulary_service(config)
    generator = create_template_generator(vocab_service)

    return await generator.generate_template(resource_type, user_context=user_context)
