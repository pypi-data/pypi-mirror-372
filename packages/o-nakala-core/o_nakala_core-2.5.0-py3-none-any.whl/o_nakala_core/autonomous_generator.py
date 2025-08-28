"""
NAKALA Autonomous Metadata Generation

Advanced AI-driven system for automatically generating complete metadata from file content analysis.
Part of the Complete Metadata Management System - Phase 3 (Advanced Intelligence).
"""

import logging
import mimetypes
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

from .ml_engine import MLPatternLearner, SemanticAnalyzer, PredictionResult
from .collaborative_intelligence import CollaborativeIntelligenceEngine
from .templates import MetadataTemplate, TemplateField
from .user_info import NakalaUserInfoClient

logger = logging.getLogger(__name__)


@dataclass
class ContentAnalysisResult:
    """Result of autonomous content analysis."""

    content_type: str
    detected_language: str
    confidence_score: float
    extracted_features: Dict[str, Any]
    generated_metadata: Dict[str, str]
    analysis_time: float
    processing_notes: List[str]

    def __post_init__(self):
        if not hasattr(self, "processing_notes") or self.processing_notes is None:
            self.processing_notes = []


@dataclass
class AutonomousGenerationResult:
    """Complete result of autonomous metadata generation."""

    file_path: str
    template: MetadataTemplate
    generated_metadata: Dict[str, str]
    confidence_scores: Dict[str, float]
    content_analysis: ContentAnalysisResult
    ml_predictions: List[PredictionResult]
    collaborative_insights: List[Dict[str, Any]]
    processing_time: float
    completeness_score: float
    quality_score: float
    recommendations: List[str]

    def __post_init__(self):
        if not hasattr(self, "recommendations") or self.recommendations is None:
            self.recommendations = []


class ContentTypeDetector:
    """Advanced content type detection and analysis."""

    def __init__(self):
        self.content_patterns = {
            "research_paper": {
                "patterns": [
                    r"abstract",
                    r"introduction",
                    r"methodology",
                    r"results",
                    r"conclusion",
                    r"references",
                ],
                "file_extensions": [".pdf", ".tex", ".md", ".docx"],
                "keywords": [
                    "research",
                    "study",
                    "analysis",
                    "method",
                    "data",
                    "experiment",
                ],
            },
            "dataset": {
                "patterns": [r"\.csv$", r"\.xlsx?$", r"\.json$", r"\.xml$"],
                "file_extensions": [".csv", ".xlsx", ".xls", ".json", ".xml", ".tsv"],
                "keywords": [
                    "data",
                    "measurements",
                    "observations",
                    "records",
                    "samples",
                ],
            },
            "code": {
                "patterns": [
                    r"def\s+",
                    r"function\s+",
                    r"class\s+",
                    r"import\s+",
                    r"#include",
                ],
                "file_extensions": [".py", ".r", ".js", ".java", ".cpp", ".c", ".h"],
                "keywords": [
                    "algorithm",
                    "implementation",
                    "script",
                    "program",
                    "software",
                ],
            },
            "image": {
                "patterns": [],
                "file_extensions": [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".tiff",
                    ".tif",
                    ".bmp",
                    ".gif",
                ],
                "keywords": ["photo", "image", "picture", "visualization", "figure"],
            },
            "document": {
                "patterns": [r"chapter", r"section", r"paragraph"],
                "file_extensions": [".pdf", ".doc", ".docx", ".txt", ".md"],
                "keywords": ["document", "text", "report", "manual", "guide"],
            },
            "presentation": {
                "patterns": [r"slide", r"presentation"],
                "file_extensions": [".ppt", ".pptx", ".pdf"],
                "keywords": ["presentation", "slides", "lecture", "talk", "conference"],
            },
            "multimedia": {
                "patterns": [],
                "file_extensions": [".mp4", ".avi", ".mov", ".mp3", ".wav"],
                "keywords": ["video", "audio", "media", "recording", "sound"],
            },
        }

    def detect_content_type(
        self, file_path: str, content: str = None
    ) -> Tuple[str, float]:
        """Detect content type from file path and optional content."""
        path = Path(file_path)
        file_ext = path.suffix.lower()
        filename = path.name.lower()

        scores = {}

        # File extension analysis
        for content_type, config in self.content_patterns.items():
            score = 0.0

            # Extension matching
            if file_ext in config["file_extensions"]:
                score += 0.6

            # Filename keyword matching
            for keyword in config["keywords"]:
                if keyword in filename:
                    score += 0.2

            # Content pattern matching
            if content:
                content_lower = content.lower()
                for pattern in config["patterns"]:
                    if re.search(pattern, content_lower):
                        score += 0.3

                # Keyword density in content
                keyword_count = sum(
                    1 for keyword in config["keywords"] if keyword in content_lower
                )
                if keyword_count > 0:
                    score += min(0.4, keyword_count * 0.1)

            scores[content_type] = min(score, 1.0)

        # Find best match
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            return best_type[0], best_type[1]

        return "document", 0.3  # Default fallback


class LanguageDetector:
    """Simple language detection for multilingual metadata generation."""

    def __init__(self):
        self.language_patterns = {
            "fr": {
                "common_words": [
                    "le",
                    "de",
                    "et",
                    "à",
                    "un",
                    "il",
                    "être",
                    "et",
                    "en",
                    "avoir",
                    "que",
                    "pour",
                ],
                "patterns": [r"[àâäéèêëïîôöùûüÿç]"],
                "stopwords": [
                    "le",
                    "la",
                    "les",
                    "un",
                    "une",
                    "des",
                    "du",
                    "de",
                    "dans",
                    "sur",
                    "avec",
                    "par",
                ],
            },
            "en": {
                "common_words": [
                    "the",
                    "of",
                    "and",
                    "to",
                    "a",
                    "in",
                    "is",
                    "it",
                    "you",
                    "that",
                    "he",
                    "was",
                ],
                "patterns": [r"\b(the|and|of|to|in|is|it)\b"],
                "stopwords": [
                    "the",
                    "of",
                    "and",
                    "to",
                    "a",
                    "in",
                    "is",
                    "it",
                    "you",
                    "that",
                    "he",
                    "was",
                ],
            },
            "de": {
                "common_words": [
                    "der",
                    "die",
                    "und",
                    "in",
                    "den",
                    "von",
                    "zu",
                    "das",
                    "mit",
                    "sich",
                    "des",
                    "auf",
                ],
                "patterns": [r"[äöüß]"],
                "stopwords": [
                    "der",
                    "die",
                    "und",
                    "in",
                    "den",
                    "von",
                    "zu",
                    "das",
                    "mit",
                    "sich",
                ],
            },
            "es": {
                "common_words": [
                    "el",
                    "la",
                    "de",
                    "que",
                    "y",
                    "a",
                    "en",
                    "un",
                    "es",
                    "se",
                    "no",
                    "te",
                ],
                "patterns": [r"[ñáéíóúü]"],
                "stopwords": [
                    "el",
                    "la",
                    "de",
                    "que",
                    "y",
                    "a",
                    "en",
                    "un",
                    "es",
                    "se",
                    "no",
                ],
            },
        }

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text content."""
        if not text or len(text.strip()) < 10:
            return "fr", 0.3  # Default to French with low confidence

        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)

        if len(words) < 5:
            return "fr", 0.3

        scores = {}

        for lang, config in self.language_patterns.items():
            score = 0.0

            # Common word matching
            common_word_count = sum(
                1 for word in words if word in config["common_words"]
            )
            score += (common_word_count / len(words)) * 0.6

            # Pattern matching (accents, special characters)
            pattern_matches = sum(
                1 for pattern in config["patterns"] if re.search(pattern, text_lower)
            )
            score += min(0.4, pattern_matches * 0.1)

            scores[lang] = score

        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])
            return best_lang[0], min(best_lang[1], 1.0)

        return "fr", 0.3


class MetadataGenerator:
    """Core autonomous metadata generation engine."""

    def __init__(self):
        self.content_detector = ContentTypeDetector()
        self.language_detector = LanguageDetector()

        # Metadata generation templates by content type
        self.generation_templates = {
            "research_paper": {
                "title_patterns": [
                    "{filename} - Research Paper",
                    "Academic Study: {filename}",
                ],
                "description_template": (
                    "Research paper containing {content_summary}. "
                    "This academic document includes {detected_sections}."
                ),
                "keywords": ["research", "academic", "study", "paper", "analysis"],
                "type": "http://purl.org/coar/resource_type/c_6501",
                "default_license": "CC-BY-4.0",
            },
            "dataset": {
                "title_patterns": ["{filename} Dataset", "Data Collection: {filename}"],
                "description_template": (
                    "Dataset containing {content_summary}. The data includes {detected_features} "
                    "and is suitable for {analysis_type} analysis."
                ),
                "keywords": [
                    "dataset",
                    "data",
                    "collection",
                    "measurements",
                    "observations",
                ],
                "type": "http://purl.org/coar/resource_type/c_ddb1",
                "default_license": "CC-BY-4.0",
            },
            "code": {
                "title_patterns": [
                    "{filename} - Source Code",
                    "Implementation: {filename}",
                ],
                "description_template": (
                    "Source code implementation for {content_summary}. "
                    "This {programming_language} code includes {detected_functions}."
                ),
                "keywords": [
                    "code",
                    "software",
                    "implementation",
                    "algorithm",
                    "programming",
                ],
                "type": "http://purl.org/coar/resource_type/c_5ce6",
                "default_license": "MIT",
            },
            "image": {
                "title_patterns": ["{filename} - Image", "Visual Content: {filename}"],
                "description_template": (
                    "Image file containing {content_summary}. "
                    "This visual resource shows {detected_content}."
                ),
                "keywords": ["image", "visual", "photo", "picture", "graphic"],
                "type": "http://purl.org/coar/resource_type/c_ecc8",
                "default_license": "CC-BY-4.0",
            },
            "document": {
                "title_patterns": [
                    "{filename} - Document",
                    "Text Document: {filename}",
                ],
                "description_template": (
                    "Document containing {content_summary}. "
                    "This text resource includes {detected_sections}."
                ),
                "keywords": ["document", "text", "information", "content"],
                "type": "http://purl.org/coar/resource_type/c_6501",
                "default_license": "CC-BY-4.0",
            },
        }

    def analyze_file_content(self, file_path: str) -> ContentAnalysisResult:
        """Analyze file content for metadata generation."""
        start_time = datetime.now()
        path = Path(file_path)

        # Initialize result
        result = ContentAnalysisResult(
            content_type="unknown",
            detected_language="fr",
            confidence_score=0.0,
            extracted_features={},
            generated_metadata={},
            analysis_time=0.0,
            processing_notes=[],
        )

        try:
            # Basic file analysis
            result.extracted_features = {
                "filename": path.name,
                "file_extension": path.suffix.lower(),
                "file_size": path.stat().st_size if path.exists() else 0,
                "mime_type": mimetypes.guess_type(str(path))[0]
                or "application/octet-stream",
            }

            # Try to read file content for text files
            content = None
            if path.exists() and path.is_file():
                try:
                    # Try reading as text
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(5000)  # Read first 5KB for analysis
                except (UnicodeDecodeError, IOError):
                    # If text reading fails, it's likely binary
                    result.processing_notes.append(
                        "Binary file - content analysis limited to filename and extension"
                    )
            else:
                result.processing_notes.append(
                    "File not accessible - analysis based on path only"
                )

            # Detect content type
            content_type, type_confidence = self.content_detector.detect_content_type(
                str(path), content
            )
            result.content_type = content_type
            result.confidence_score = type_confidence

            # Detect language if content available
            if content:
                language, lang_confidence = self.language_detector.detect_language(
                    content
                )
                result.detected_language = language
                result.confidence_score = (
                    result.confidence_score + lang_confidence
                ) / 2

                # Extract additional features from content
                result.extracted_features.update(
                    {
                        "content_length": len(content),
                        "word_count": len(content.split()),
                        "has_code_patterns": bool(
                            re.search(r"(def |function |class |import )", content)
                        ),
                        "has_data_patterns": bool(
                            re.search(r"(\d+[,.]?\d*[,;]\s*){3,}", content)
                        ),
                        "has_academic_patterns": bool(
                            re.search(
                                r"(abstract|introduction|methodology|conclusion)",
                                content,
                                re.I,
                            )
                        ),
                    }
                )

            # Generate basic metadata
            result.generated_metadata = self._generate_basic_metadata(
                path, content_type, content
            )

            processing_time = (datetime.now() - start_time).total_seconds()
            result.analysis_time = processing_time

            logger.info(
                f"Content analysis completed for {path.name}: {content_type} "
                f"({result.confidence_score:.1%} confidence)"
            )

        except Exception as e:
            logger.error(f"Content analysis failed for {file_path}: {e}")
            result.processing_notes.append(f"Analysis error: {str(e)}")

        return result

    def _generate_basic_metadata(
        self, path: Path, content_type: str, content: str = None
    ) -> Dict[str, str]:
        """Generate basic metadata from file analysis."""
        metadata = {}

        template = self.generation_templates.get(
            content_type, self.generation_templates["document"]
        )

        # Generate title
        filename_clean = path.stem.replace("_", " ").replace("-", " ").title()
        title_pattern = template["title_patterns"][0]
        metadata["title"] = title_pattern.format(filename=filename_clean)

        # Generate description
        content_summary = self._extract_content_summary(content, content_type)
        detected_features = self._detect_content_features(content, content_type)

        description = template["description_template"].format(
            content_summary=content_summary,
            detected_sections=detected_features.get("sections", "various sections"),
            detected_features=detected_features.get("features", "data elements"),
            analysis_type=detected_features.get("analysis_type", "statistical"),
            programming_language=detected_features.get(
                "programming_language", "general"
            ),
            detected_functions=detected_features.get(
                "functions", "implementation logic"
            ),
            detected_content=detected_features.get(
                "visual_content", "visual information"
            ),
        )
        metadata["description"] = description

        # Generate keywords
        keywords = template["keywords"].copy()
        if content:
            extracted_keywords = self._extract_keywords_from_content(content)
            keywords.extend(extracted_keywords[:3])  # Add top 3 extracted keywords
        metadata["keywords"] = ";".join(keywords[:5])  # Limit to 5 keywords

        # Set type and license
        metadata["type"] = template["type"]
        metadata["license"] = template["default_license"]

        # Add date
        metadata["date"] = datetime.now().strftime("%Y-%m-%d")

        return metadata

    def _extract_content_summary(self, content: str, content_type: str) -> str:
        """Extract a brief summary of content."""
        if not content:
            return f"structured {content_type} content"

        # Simple content summarization
        if content_type == "research_paper":
            if "abstract" in content.lower():
                return "academic research with abstract and methodology"
            return "academic research and analysis"
        elif content_type == "dataset":
            if re.search(r"\d+[,.]?\d*", content):
                return "numerical data and measurements"
            return "structured data records"
        elif content_type == "code":
            if "def " in content or "function" in content:
                return "functions and algorithms"
            return "program implementation"
        elif content_type == "image":
            return "visual information and graphics"
        else:
            return "informational content"

    def _detect_content_features(
        self, content: str, content_type: str
    ) -> Dict[str, str]:
        """Detect specific features based on content type."""
        features = {}

        if not content:
            return features

        if content_type == "research_paper":
            sections = []
            for section in [
                "abstract",
                "introduction",
                "methodology",
                "results",
                "conclusion",
            ]:
                if section in content.lower():
                    sections.append(section)
            features["sections"] = (
                ", ".join(sections) if sections else "research sections"
            )

        elif content_type == "dataset":
            if "," in content and "\n" in content:
                features["features"] = "comma-separated values"
                features["analysis_type"] = "tabular data"
            elif "{" in content and "}" in content:
                features["features"] = "JSON structured data"
                features["analysis_type"] = "structured object"
            else:
                features["features"] = "data records"
                features["analysis_type"] = "general"

        elif content_type == "code":
            if "python" in content.lower() or "import " in content:
                features["programming_language"] = "Python"
            elif "#include" in content or "iostream" in content:
                features["programming_language"] = "C++"
            elif "library(" in content or "<-" in content:
                features["programming_language"] = "R"
            else:
                features["programming_language"] = "general purpose"

            if "def " in content:
                features["functions"] = "function definitions and logic"
            elif "class " in content:
                features["functions"] = "class definitions and methods"
            else:
                features["functions"] = "programming logic"

        return features

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract meaningful keywords from content."""
        if not content:
            return []

        # Simple keyword extraction
        words = re.findall(r"\b[a-zA-Z]{4,15}\b", content.lower())

        # Filter out common stop words
        stop_words = {
            "this",
            "that",
            "with",
            "have",
            "will",
            "been",
            "from",
            "they",
            "know",
            "want",
            "were",
            "said",
            "each",
            "which",
            "their",
            "time",
            "would",
            "about",
            "there",
            "could",
            "other",
            "more",
            "very",
            "what",
            "make",
            "than",
            "first",
            "been",
            "call",
            "who",
            "its",
            "now",
            "find",
            "long",
            "down",
            "day",
            "did",
            "get",
            "come",
            "made",
            "may",
            "part",
        }

        filtered_words = [
            word for word in words if word not in stop_words and len(word) >= 4
        ]

        # Count frequency and return most common
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10] if freq > 1]


class AutonomousMetadataEngine:
    """Main engine for autonomous metadata generation."""

    def __init__(self, user_client: NakalaUserInfoClient, cache_dir: str = None):
        self.user_client = user_client
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path.home() / ".nakala" / "autonomous_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.metadata_generator = MetadataGenerator()
        self.ml_learner = MLPatternLearner(str(self.cache_dir))
        self.semantic_analyzer = SemanticAnalyzer(str(self.cache_dir))
        self.collaborative_engine = CollaborativeIntelligenceEngine(
            user_client, str(self.cache_dir)
        )

        # Generation settings
        self.min_confidence_threshold = 0.3
        self.enable_ml_enhancement = True
        self.enable_collaborative_insights = True

    async def generate_autonomous_metadata(
        self,
        file_path: str,
        resource_type: str = None,
        target_template: MetadataTemplate = None,
        user_context: Dict[str, Any] = None,
    ) -> AutonomousGenerationResult:
        """Generate complete metadata autonomously from file analysis."""
        start_time = datetime.now()

        logger.info(f"Starting autonomous metadata generation for: {file_path}")

        try:
            # 1. Analyze file content
            content_analysis = self.metadata_generator.analyze_file_content(file_path)

            # 2. Generate base metadata
            base_metadata = content_analysis.generated_metadata.copy()
            confidence_scores = {
                field: content_analysis.confidence_score
                for field in base_metadata.keys()
            }

            # 3. Enhance with ML predictions if enabled
            ml_predictions = []
            if self.enable_ml_enhancement and base_metadata:
                try:
                    context = {**base_metadata, **(user_context or {})}
                    for field in [
                        "creator",
                        "contributor",
                        "language",
                        "spatial",
                        "temporal",
                    ]:
                        prediction = self.ml_learner.predict_field_value(context, field)
                        if (
                            prediction
                            and prediction.confidence >= self.min_confidence_threshold
                        ):
                            ml_predictions.append(prediction)
                            base_metadata[field] = prediction.predicted_value
                            confidence_scores[field] = prediction.confidence
                except Exception as e:
                    logger.warning(f"ML enhancement failed: {e}")

            # 4. Get collaborative insights if enabled
            collaborative_insights = []
            if self.enable_collaborative_insights:
                try:
                    analysis_results = (
                        await self.collaborative_engine.analyze_and_learn()
                    )
                    if analysis_results.get("collaborative_insights"):
                        collaborative_insights = analysis_results[
                            "collaborative_insights"
                        ]

                        # Apply relevant insights to metadata
                        for insight in collaborative_insights:
                            if insight.get("insight_type") == "community_trend":
                                context = insight.get("context", {})
                                if (
                                    "keywords" in context
                                    and "keywords" in base_metadata
                                ):
                                    # Enhance keywords with community trends
                                    community_keywords = context["keywords"][:3]
                                    current_keywords = base_metadata["keywords"].split(
                                        ";"
                                    )
                                    updated_keywords = list(
                                        set(current_keywords + community_keywords)
                                    )
                                    base_metadata["keywords"] = ";".join(
                                        updated_keywords[:7]
                                    )
                except Exception as e:
                    logger.warning(f"Collaborative intelligence failed: {e}")

            # 5. Create or enhance template
            if target_template:
                template = target_template
            else:
                template = self._create_autonomous_template(
                    content_analysis, base_metadata
                )

            # 6. Calculate quality metrics
            completeness_score = self._calculate_completeness_score(
                base_metadata, template
            )
            quality_score = self._calculate_quality_score(
                base_metadata, content_analysis
            )

            # 7. Generate recommendations
            recommendations = self._generate_recommendations(
                base_metadata, content_analysis, quality_score
            )

            # 8. Create final result
            processing_time = (datetime.now() - start_time).total_seconds()

            result = AutonomousGenerationResult(
                file_path=file_path,
                template=template,
                generated_metadata=base_metadata,
                confidence_scores=confidence_scores,
                content_analysis=content_analysis,
                ml_predictions=ml_predictions,
                collaborative_insights=collaborative_insights,
                processing_time=processing_time,
                completeness_score=completeness_score,
                quality_score=quality_score,
                recommendations=recommendations,
            )

            logger.info(
                f"Autonomous generation completed in {processing_time:.2f}s: "
                f"{len(base_metadata)} fields, {quality_score:.1%} quality"
            )

            return result

        except Exception as e:
            logger.error(f"Autonomous metadata generation failed: {e}")
            raise

    def _create_autonomous_template(
        self, content_analysis: ContentAnalysisResult, metadata: Dict[str, str]
    ) -> MetadataTemplate:
        """Create a template based on autonomous analysis."""
        template_fields = []

        # Core fields always included
        core_fields = [
            ("title", "http://nakala.fr/terms#title", True, True),
            ("description", "http://purl.org/dc/terms/description", True, True),
            ("type", "http://nakala.fr/terms#type", False, True),
            ("license", "http://nakala.fr/terms#license", False, True),
            ("date", "http://nakala.fr/terms#created", False, True),
        ]

        # Add fields based on content type
        content_type = content_analysis.content_type
        if content_type in ["research_paper", "document"]:
            core_fields.extend(
                [
                    ("creator", "http://purl.org/dc/terms/creator", False, True),
                    ("keywords", "http://purl.org/dc/terms/subject", True, False),
                    ("language", "http://purl.org/dc/terms/language", False, False),
                ]
            )
        elif content_type == "dataset":
            core_fields.extend(
                [
                    ("creator", "http://purl.org/dc/terms/creator", False, True),
                    ("keywords", "http://purl.org/dc/terms/subject", True, False),
                    ("temporal", "http://purl.org/dc/terms/coverage", False, False),
                    ("spatial", "http://purl.org/dc/terms/coverage", False, False),
                ]
            )
        elif content_type == "code":
            core_fields.extend(
                [
                    ("creator", "http://purl.org/dc/terms/creator", False, True),
                    ("language", "http://purl.org/dc/terms/language", False, False),
                    ("relation", "http://purl.org/dc/terms/relation", False, False),
                ]
            )

        # Create template fields
        for i, (name, uri, multilingual, required) in enumerate(core_fields):
            field = TemplateField(
                name=name,
                property_uri=uri,
                data_type="string",
                required=required,
                multilingual=multilingual,
                section="basic" if required else "optional",
                priority=1 if required else 2,
                examples=[metadata.get(name, f"example_{name}")],
                help_text=f"Autonomous generated field for {name}",
                default_value=metadata.get(name),
            )
            template_fields.append(field)

        # Create template
        template = MetadataTemplate(
            name=f"Autonomous Template for {content_type}",
            description=f"Automatically generated template for {content_type} resources",
            resource_type=content_type,
            fields=template_fields,
            created_at=datetime.now(),
            version="1.0",
            tags=["autonomous", "generated", content_type],
        )

        return template

    def _calculate_completeness_score(
        self, metadata: Dict[str, str], template: MetadataTemplate
    ) -> float:
        """Calculate metadata completeness score."""
        required_fields = [f.name for f in template.fields if f.required]
        optional_fields = [f.name for f in template.fields if not f.required]

        required_filled = sum(
            1 for field in required_fields if field in metadata and metadata[field]
        )
        optional_filled = sum(
            1 for field in optional_fields if field in metadata and metadata[field]
        )

        if not required_fields:
            return 1.0

        required_score = required_filled / len(required_fields)
        optional_score = (
            optional_filled / len(optional_fields) if optional_fields else 1.0
        )

        # Weight required fields more heavily
        return (required_score * 0.8) + (optional_score * 0.2)

    def _calculate_quality_score(
        self, metadata: Dict[str, str], content_analysis: ContentAnalysisResult
    ) -> float:
        """Calculate metadata quality score."""
        quality_factors = []

        # Content analysis confidence
        quality_factors.append(content_analysis.confidence_score)

        # Title quality
        title = metadata.get("title", "")
        if title:
            title_score = min(1.0, len(title.split()) / 5)  # Normalize to 5 words
            quality_factors.append(title_score)

        # Description quality
        description = metadata.get("description", "")
        if description:
            desc_score = min(
                1.0, len(description.split()) / 20
            )  # Normalize to 20 words
            quality_factors.append(desc_score)

        # Keywords quality
        keywords = metadata.get("keywords", "")
        if keywords:
            keyword_count = len(keywords.split(";"))
            keyword_score = min(1.0, keyword_count / 5)  # Normalize to 5 keywords
            quality_factors.append(keyword_score)

        # Field coverage
        field_count = len([v for v in metadata.values() if v and v.strip()])
        coverage_score = min(1.0, field_count / 8)  # Normalize to 8 fields
        quality_factors.append(coverage_score)

        # Average quality score
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.3

    def _generate_recommendations(
        self,
        metadata: Dict[str, str],
        content_analysis: ContentAnalysisResult,
        quality_score: float,
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Quality-based recommendations
        if quality_score < 0.6:
            recommendations.append(
                "Consider manual review - autonomous quality score is below 60%"
            )

        if quality_score < 0.8:
            recommendations.append(
                "Add more descriptive keywords for better discoverability"
            )

        # Content-specific recommendations
        if content_analysis.content_type == "dataset":
            if "temporal" not in metadata:
                recommendations.append("Consider adding temporal coverage for dataset")
            if "spatial" not in metadata:
                recommendations.append("Consider adding spatial coverage for dataset")

        if content_analysis.content_type == "research_paper":
            if "creator" not in metadata:
                recommendations.append("Add author information for academic paper")

        # Confidence-based recommendations
        if content_analysis.confidence_score < 0.5:
            recommendations.append(
                "Low content analysis confidence - manual verification recommended"
            )

        # Missing field recommendations
        essential_fields = ["title", "description", "type", "license"]
        missing_essential = [
            field for field in essential_fields if field not in metadata
        ]
        if missing_essential:
            recommendations.append(
                f"Essential fields missing: {', '.join(missing_essential)}"
            )

        return recommendations


# Factory function
def create_autonomous_generator(
    user_client: NakalaUserInfoClient, cache_dir: str = None
) -> AutonomousMetadataEngine:
    """Create autonomous metadata generation engine."""
    return AutonomousMetadataEngine(user_client, cache_dir)
