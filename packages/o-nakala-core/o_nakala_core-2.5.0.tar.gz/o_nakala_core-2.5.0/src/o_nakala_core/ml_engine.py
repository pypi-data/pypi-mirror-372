"""
NAKALA Automated Enhancement Engine

Advanced pattern recognition and semantic analysis for metadata management
with intelligent suggestions and community insights.
"""

import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# Optional ML dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
import pickle
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class MetadataPattern:
    """Represents a learned metadata pattern."""

    pattern_id: str
    pattern_type: (
        str  # 'field_correlation', 'content_type', 'user_behavior', 'temporal'
    )
    confidence: float
    frequency: int
    last_seen: datetime
    context: Dict[str, Any]
    features: Dict[str, float]

    def __post_init__(self):
        if not hasattr(self, "last_seen") or self.last_seen is None:
            self.last_seen = datetime.now()


@dataclass
class SemanticEmbedding:
    """Represents semantic embedding for content analysis."""

    content_id: str
    content_type: str
    embedding_vector: List[float]
    semantic_features: Dict[str, float]
    language: str
    created_at: datetime

    def cosine_similarity(self, other: "SemanticEmbedding") -> float:
        """Calculate cosine similarity with another embedding."""
        if not HAS_NUMPY:
            # Fallback to basic dot product calculation without numpy
            return self._basic_cosine_similarity(other)

        if len(self.embedding_vector) != len(other.embedding_vector):
            return 0.0

        # Convert to numpy arrays for efficient computation
        vec1 = np.array(self.embedding_vector)
        vec2 = np.array(other.embedding_vector)

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _basic_cosine_similarity(self, other: "SemanticEmbedding") -> float:
        """Basic cosine similarity calculation without numpy."""
        if len(self.embedding_vector) != len(other.embedding_vector):
            return 0.0

        # Calculate dot product
        dot_product = sum(
            a * b for a, b in zip(self.embedding_vector, other.embedding_vector)
        )

        # Calculate norms
        norm1 = sum(a * a for a in self.embedding_vector) ** 0.5
        norm2 = sum(b * b for b in other.embedding_vector) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


@dataclass
class PredictionResult:
    """Result of automated prediction for metadata suggestions."""

    field_name: str
    predicted_value: str
    confidence: float
    reasoning: str
    evidence: List[str]
    alternatives: List[Tuple[str, float]]  # (value, confidence) pairs

    def __post_init__(self):
        if not hasattr(self, "alternatives") or self.alternatives is None:
            self.alternatives = []


class MLPatternLearner:
    """Automated component for discovering and learning metadata patterns."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = (
            Path(cache_dir) if cache_dir else Path.home() / ".nakala" / "ml_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Pattern storage
        self.learned_patterns: Dict[str, MetadataPattern] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(
            list
        )  # type -> pattern_ids

        # Feature extractors
        self.field_correlations: Dict[Tuple[str, str], float] = {}
        self.content_type_patterns: Dict[str, Dict[str, float]] = {}
        self.user_behavior_patterns: Dict[str, Dict[str, Any]] = {}

        # Learning parameters
        self.min_pattern_frequency = 3
        self.min_confidence_threshold = 0.6
        self.pattern_decay_factor = 0.95  # Daily decay for pattern relevance

        self._load_patterns()

    def _load_patterns(self):
        """Load previously learned patterns from cache."""
        patterns_file = self.cache_dir / "learned_patterns.pkl"
        if patterns_file.exists():
            try:
                with open(patterns_file, "rb") as f:
                    data = pickle.load(f)
                    self.learned_patterns = data.get("patterns", {})
                    self.field_correlations = data.get("correlations", {})
                    self.content_type_patterns = data.get("content_patterns", {})
                    self.user_behavior_patterns = data.get("user_patterns", {})

                # Rebuild pattern index
                for pattern_id, pattern in self.learned_patterns.items():
                    self.pattern_index[pattern.pattern_type].append(pattern_id)

                logger.info(f"Loaded {len(self.learned_patterns)} learned patterns")
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save learned patterns to cache."""
        patterns_file = self.cache_dir / "learned_patterns.pkl"
        try:
            data = {
                "patterns": self.learned_patterns,
                "correlations": self.field_correlations,
                "content_patterns": self.content_type_patterns,
                "user_patterns": self.user_behavior_patterns,
                "saved_at": datetime.now(),
            }
            with open(patterns_file, "wb") as f:
                pickle.dump(data, f)
            logger.debug("Saved learned patterns to cache")
        except Exception as e:
            logger.warning(f"Failed to save patterns: {e}")

    def learn_from_metadata(self, metadata_items: List[Dict[str, Any]]) -> int:
        """Learn patterns from a collection of metadata items."""
        patterns_learned = 0

        logger.info(f"Learning patterns from {len(metadata_items)} metadata items")

        # Extract field correlations
        patterns_learned += self._learn_field_correlations(metadata_items)

        # Learn content type patterns
        patterns_learned += self._learn_content_type_patterns(metadata_items)

        # Learn user behavior patterns
        patterns_learned += self._learn_user_behavior_patterns(metadata_items)

        # Learn temporal patterns
        patterns_learned += self._learn_temporal_patterns(metadata_items)

        # Save learned patterns
        self._save_patterns()

        logger.info(f"Learned {patterns_learned} new patterns")
        return patterns_learned

    def _learn_field_correlations(self, metadata_items: List[Dict[str, Any]]) -> int:
        """Learn correlations between metadata fields."""
        field_co_occurrences = defaultdict(int)
        field_counts = defaultdict(int)
        patterns_learned = 0

        for item in metadata_items:
            # Extract all present fields
            present_fields = []
            for key, value in item.items():
                if value and str(value).strip():
                    present_fields.append(key)

            # Count field co-occurrences
            for i, field1 in enumerate(present_fields):
                field_counts[field1] += 1
                for field2 in present_fields[i + 1 :]:
                    pair = tuple(sorted([field1, field2]))
                    field_co_occurrences[pair] += 1

        # Calculate correlation coefficients
        for (field1, field2), co_count in field_co_occurrences.items():
            if co_count >= self.min_pattern_frequency:
                # Calculate correlation using Jaccard similarity
                count1 = field_counts[field1]
                count2 = field_counts[field2]
                correlation = co_count / (count1 + count2 - co_count)

                if correlation >= self.min_confidence_threshold:
                    self.field_correlations[(field1, field2)] = correlation

                    # Create pattern
                    pattern_id = f"field_corr_{field1}_{field2}"
                    pattern = MetadataPattern(
                        pattern_id=pattern_id,
                        pattern_type="field_correlation",
                        confidence=correlation,
                        frequency=co_count,
                        last_seen=datetime.now(),
                        context={"field1": field1, "field2": field2},
                        features={"correlation": correlation, "frequency": co_count},
                    )

                    self.learned_patterns[pattern_id] = pattern
                    patterns_learned += 1

        return patterns_learned

    def _learn_content_type_patterns(self, metadata_items: List[Dict[str, Any]]) -> int:
        """Learn patterns specific to content types."""
        type_field_patterns = defaultdict(lambda: defaultdict(int))
        patterns_learned = 0

        for item in metadata_items:
            content_type = item.get("type", "unknown")

            # Count field usage per content type
            for field, value in item.items():
                if value and str(value).strip():
                    type_field_patterns[content_type][field] += 1

        # Create patterns for significant field-type associations
        for content_type, field_counts in type_field_patterns.items():
            total_items = sum(field_counts.values())
            if total_items >= self.min_pattern_frequency:

                for field, count in field_counts.items():
                    usage_rate = count / total_items
                    if usage_rate >= self.min_confidence_threshold:

                        pattern_id = f"content_type_{content_type}_{field}"
                        pattern = MetadataPattern(
                            pattern_id=pattern_id,
                            pattern_type="content_type",
                            confidence=usage_rate,
                            frequency=count,
                            last_seen=datetime.now(),
                            context={"content_type": content_type, "field": field},
                            features={
                                "usage_rate": usage_rate,
                                "total_items": total_items,
                            },
                        )

                        self.learned_patterns[pattern_id] = pattern
                        self.content_type_patterns[content_type] = (
                            self.content_type_patterns.get(content_type, {})
                        )
                        self.content_type_patterns[content_type][field] = usage_rate
                        patterns_learned += 1

        return patterns_learned

    def _learn_user_behavior_patterns(
        self, metadata_items: List[Dict[str, Any]]
    ) -> int:
        """Learn user behavior patterns from metadata creation."""
        user_patterns = defaultdict(lambda: defaultdict(list))
        patterns_learned = 0

        for item in metadata_items:
            creator = item.get("creator", "unknown")

            # Collect user's metadata patterns
            for field, value in item.items():
                if value and str(value).strip():
                    user_patterns[creator][field].append(value)

        # Analyze patterns for each user
        for user, field_values in user_patterns.items():
            if len(field_values) >= self.min_pattern_frequency:

                # Find most common values per field
                user_preferences = {}
                for field, values in field_values.items():
                    value_counts = Counter(values)
                    most_common = value_counts.most_common(1)
                    if most_common:
                        preference_strength = most_common[0][1] / len(values)
                        if preference_strength >= self.min_confidence_threshold:
                            user_preferences[field] = {
                                "preferred_value": most_common[0][0],
                                "strength": preference_strength,
                            }

                if user_preferences:
                    pattern_id = (
                        f"user_behavior_{hashlib.md5(user.encode()).hexdigest()[:12]}"
                    )
                    pattern = MetadataPattern(
                        pattern_id=pattern_id,
                        pattern_type="user_behavior",
                        confidence=sum(p["strength"] for p in user_preferences.values())
                        / len(user_preferences),
                        frequency=len(field_values),
                        last_seen=datetime.now(),
                        context={"user": user, "preferences": user_preferences},
                        features={"field_count": len(user_preferences)},
                    )

                    self.learned_patterns[pattern_id] = pattern
                    self.user_behavior_patterns[user] = user_preferences
                    patterns_learned += 1

        return patterns_learned

    def _learn_temporal_patterns(self, metadata_items: List[Dict[str, Any]]) -> int:
        """Learn temporal patterns in metadata creation."""
        temporal_patterns = defaultdict(lambda: defaultdict(int))
        patterns_learned = 0

        current_year = datetime.now().year

        for item in metadata_items:
            # Extract temporal information
            created_date = item.get("created", item.get("date"))
            if created_date:
                try:
                    if isinstance(created_date, str):
                        # Try to parse date
                        if len(created_date) == 4:  # Year only
                            year = int(created_date)
                        else:
                            date_obj = datetime.fromisoformat(
                                created_date.replace("Z", "+00:00")
                            )
                            year = date_obj.year
                    else:
                        year = current_year

                    # Group by time periods
                    if year >= current_year - 1:
                        period = "recent"
                    elif year >= current_year - 5:
                        period = "medium_term"
                    else:
                        period = "historical"

                    # Count field usage by time period
                    for field, value in item.items():
                        if value and str(value).strip():
                            temporal_patterns[period][field] += 1

                except (ValueError, TypeError):
                    continue

        # Create temporal patterns
        for period, field_counts in temporal_patterns.items():
            total_items = sum(field_counts.values())
            if total_items >= self.min_pattern_frequency:

                for field, count in field_counts.items():
                    usage_rate = count / total_items
                    if usage_rate >= self.min_confidence_threshold:

                        pattern_id = f"temporal_{period}_{field}"
                        pattern = MetadataPattern(
                            pattern_id=pattern_id,
                            pattern_type="temporal",
                            confidence=usage_rate,
                            frequency=count,
                            last_seen=datetime.now(),
                            context={"period": period, "field": field},
                            features={"usage_rate": usage_rate, "period": period},
                        )

                        self.learned_patterns[pattern_id] = pattern
                        patterns_learned += 1

        return patterns_learned

    def predict_field_value(
        self, context: Dict[str, Any], field_name: str
    ) -> Optional[PredictionResult]:
        """Predict a field value based on learned patterns and context."""
        predictions = []
        evidence = []

        # Check field correlations
        for (field1, field2), correlation in self.field_correlations.items():
            if field1 == field_name and field2 in context:
                predictions.append(
                    (context[field2], correlation * 0.7)
                )  # Reduced confidence for correlation
                evidence.append(f"Field correlation with {field2}")
            elif field2 == field_name and field1 in context:
                predictions.append((context[field1], correlation * 0.7))
                evidence.append(f"Field correlation with {field1}")

        # Check content type patterns
        content_type = context.get("type")
        if content_type and content_type in self.content_type_patterns:
            type_patterns = self.content_type_patterns[content_type]
            if field_name in type_patterns:
                # Find most common value for this field-type combination
                for pattern in self.learned_patterns.values():
                    if (
                        pattern.pattern_type == "content_type"
                        and pattern.context.get("content_type") == content_type
                        and pattern.context.get("field") == field_name
                    ):
                        # This would need enhancement to store actual values, not just usage rates
                        evidence.append(f"Content type pattern for {content_type}")

        # Check user behavior patterns
        user = context.get("creator", context.get("user"))
        if user and user in self.user_behavior_patterns:
            user_prefs = self.user_behavior_patterns[user]
            if field_name in user_prefs:
                pref = user_prefs[field_name]
                predictions.append((pref["preferred_value"], pref["strength"]))
                evidence.append("User preference pattern")

        # Select best prediction
        if predictions:
            # Sort by confidence
            predictions.sort(key=lambda x: x[1], reverse=True)
            best_prediction = predictions[0]
            alternatives = predictions[1:3]  # Top 2 alternatives

            return PredictionResult(
                field_name=field_name,
                predicted_value=best_prediction[0],
                confidence=best_prediction[1],
                reasoning=f"Automated prediction based on {len(evidence)} evidence sources",
                evidence=evidence,
                alternatives=alternatives,
            )

        return None

    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns."""
        summary = {
            "total_patterns": len(self.learned_patterns),
            "pattern_types": {},
            "high_confidence_patterns": 0,
            "recent_patterns": 0,
        }

        # Count patterns by type
        for pattern in self.learned_patterns.values():
            pattern_type = pattern.pattern_type
            summary["pattern_types"][pattern_type] = (
                summary["pattern_types"].get(pattern_type, 0) + 1
            )

            if pattern.confidence >= 0.8:
                summary["high_confidence_patterns"] += 1

            if pattern.last_seen >= datetime.now() - timedelta(days=30):
                summary["recent_patterns"] += 1

        return summary


class SemanticAnalyzer:
    """Semantic content analysis engine for advanced understanding."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = (
            Path(cache_dir) if cache_dir else Path.home() / ".nakala" / "semantic_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Semantic storage
        self.embeddings: Dict[str, SemanticEmbedding] = {}
        self.semantic_clusters: Dict[str, List[str]] = {}
        self.domain_vocabularies: Dict[str, Set[str]] = defaultdict(set)

        # Analysis parameters
        self.similarity_threshold = 0.7
        self.cluster_min_size = 3

        self._load_embeddings()

    def _load_embeddings(self):
        """Load previously computed embeddings from cache."""
        embeddings_file = self.cache_dir / "semantic_embeddings.pkl"
        if embeddings_file.exists():
            try:
                with open(embeddings_file, "rb") as f:
                    data = pickle.load(f)
                    self.embeddings = data.get("embeddings", {})
                    self.semantic_clusters = data.get("clusters", {})
                    self.domain_vocabularies = data.get(
                        "vocabularies", defaultdict(set)
                    )

                logger.info(f"Loaded {len(self.embeddings)} semantic embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embeddings: {e}")

    def _save_embeddings(self):
        """Save computed embeddings to cache."""
        embeddings_file = self.cache_dir / "semantic_embeddings.pkl"
        try:
            data = {
                "embeddings": self.embeddings,
                "clusters": self.semantic_clusters,
                "vocabularies": self.domain_vocabularies,
                "saved_at": datetime.now(),
            }
            with open(embeddings_file, "wb") as f:
                pickle.dump(data, f)
            logger.debug("Saved semantic embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save embeddings: {e}")

    def analyze_content(
        self, content: str, content_id: str, content_type: str, language: str = "en"
    ) -> SemanticEmbedding:
        """Analyze content and create semantic embedding."""
        # Simple semantic feature extraction (would use real NLP models in production)
        semantic_features = self._extract_semantic_features(content, language)

        # Create embedding vector (simplified - would use actual embedding models)
        embedding_vector = self._create_embedding_vector(content, semantic_features)

        # Create semantic embedding
        embedding = SemanticEmbedding(
            content_id=content_id,
            content_type=content_type,
            embedding_vector=embedding_vector,
            semantic_features=semantic_features,
            language=language,
            created_at=datetime.now(),
        )

        # Store embedding
        self.embeddings[content_id] = embedding

        # Update domain vocabularies
        self._update_domain_vocabulary(content, content_type, language)

        # Save changes
        self._save_embeddings()

        return embedding

    def _extract_semantic_features(
        self, content: str, language: str
    ) -> Dict[str, float]:
        """Extract semantic features from content."""
        import re

        features = {}
        content_lower = content.lower()

        # Content length features
        features["content_length"] = len(content)
        features["word_count"] = len(content.split())
        features["sentence_count"] = len(re.split(r"[.!?]+", content))

        # Language-specific features
        features["language_complexity"] = self._calculate_language_complexity(
            content, language
        )

        # Domain indicators
        academic_terms = {
            "research",
            "study",
            "analysis",
            "methodology",
            "data",
            "results",
            "conclusion",
        }
        features["academic_score"] = sum(
            1 for term in academic_terms if term in content_lower
        ) / len(academic_terms)

        technical_terms = {
            "algorithm",
            "system",
            "method",
            "process",
            "implementation",
            "framework",
        }
        features["technical_score"] = sum(
            1 for term in technical_terms if term in content_lower
        ) / len(technical_terms)

        # Content type indicators
        features["has_numbers"] = 1.0 if re.search(r"\d+", content) else 0.0
        features["has_dates"] = (
            1.0 if re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", content) else 0.0
        )
        features["has_urls"] = 1.0 if re.search(r"https?://", content) else 0.0

        return features

    def _calculate_language_complexity(self, content: str, language: str) -> float:
        """Calculate language complexity score."""
        words = content.split()
        if not words:
            return 0.0

        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Complexity heuristics
        complexity = min(avg_word_length / 10.0, 1.0)  # Normalize to 0-1

        return complexity

    def _create_embedding_vector(
        self, content: str, features: Dict[str, float]
    ) -> List[float]:
        """Create embedding vector (simplified implementation)."""
        # In a real implementation, this would use pre-trained models like BERT, Word2Vec, etc.
        # For now, we'll create a simple feature-based vector

        import re
        from collections import Counter

        # Text preprocessing
        words = re.findall(r"\w+", content.lower())
        word_counts = Counter(words)

        # Create fixed-size vector (128 dimensions)
        vector = [0.0] * 128

        # Fill with feature values
        feature_values = list(features.values())
        for i, value in enumerate(
            feature_values[:64]
        ):  # First 64 dimensions for features
            vector[i] = float(value)

        # Fill remaining dimensions with word frequency features
        common_words = [
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
            "be",
            "been",
            "have",
            "has",
        ]

        for i, word in enumerate(common_words):
            if i + 64 < 128:
                vector[i + 64] = word_counts.get(word, 0) / max(len(words), 1)

        return vector

    def _update_domain_vocabulary(self, content: str, content_type: str, language: str):
        """Update domain-specific vocabulary."""
        import re

        words = re.findall(r"\w+", content.lower())
        # Filter out common words and keep domain-specific terms
        domain_words = [word for word in words if len(word) > 4 and word.isalpha()]

        # Add to domain vocabulary
        domain_key = f"{content_type}_{language}"
        self.domain_vocabularies[domain_key].update(
            domain_words[:20]
        )  # Limit vocabulary growth

    def find_similar_content(
        self, content_id: str, limit: int = 10
    ) -> List[Tuple[str, float]]:
        """Find content similar to the given content."""
        if content_id not in self.embeddings:
            return []

        target_embedding = self.embeddings[content_id]
        similarities = []

        for other_id, other_embedding in self.embeddings.items():
            if other_id != content_id:
                similarity = target_embedding.cosine_similarity(other_embedding)
                if similarity >= self.similarity_threshold:
                    similarities.append((other_id, similarity))

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def analyze_semantic_trends(self) -> Dict[str, Any]:
        """Analyze semantic trends across content."""
        trends = {
            "content_types": defaultdict(int),
            "languages": defaultdict(int),
            "average_similarity": 0.0,
            "domain_vocabularies_size": {
                k: len(v) for k, v in self.domain_vocabularies.items()
            },
            "semantic_clusters": len(self.semantic_clusters),
        }

        # Count content types and languages
        similarities = []
        for embedding in self.embeddings.values():
            trends["content_types"][embedding.content_type] += 1
            trends["languages"][embedding.language] += 1

        # Calculate average pairwise similarity (sample for performance)
        embedding_list = list(self.embeddings.values())
        if len(embedding_list) > 1:
            sample_size = min(100, len(embedding_list))
            import random

            sample = random.sample(embedding_list, sample_size)

            for i, emb1 in enumerate(sample):
                for emb2 in sample[i + 1 :]:
                    similarities.append(emb1.cosine_similarity(emb2))

            if similarities:
                trends["average_similarity"] = sum(similarities) / len(similarities)

        return dict(trends)


# Factory functions
def create_ml_pattern_learner(cache_dir: str = None) -> MLPatternLearner:
    """Create automated pattern learner with caching."""
    return MLPatternLearner(cache_dir)


def create_semantic_analyzer(cache_dir: str = None) -> SemanticAnalyzer:
    """Create semantic analyzer with caching."""
    return SemanticAnalyzer(cache_dir)
