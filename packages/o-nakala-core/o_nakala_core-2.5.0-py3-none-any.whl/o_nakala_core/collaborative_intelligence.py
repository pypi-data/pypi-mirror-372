"""
NAKALA Collaborative Intelligence System

Repository-wide pattern learning and collaborative metadata intelligence.
Part of the Complete Metadata Management System - Phase 3.
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Optional ML dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
from typing import Dict, Any, List, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics

from .ml_engine import (
    MLPatternLearner,
    SemanticAnalyzer,
    PredictionResult,
)
from .user_info import NakalaUserInfoClient

logger = logging.getLogger(__name__)


@dataclass
class CollaborativeInsight:
    """Represents insights learned from collaborative analysis."""

    insight_id: str
    insight_type: (
        str  # 'community_trend', 'best_practice', 'quality_pattern', 'domain_standard'
    )
    confidence: float
    impact_score: float
    evidence_count: int
    created_at: datetime
    context: Dict[str, Any]
    recommendation: str

    def __post_init__(self):
        if not hasattr(self, "created_at") or self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class CommunityMetrics:
    """Metrics about the research community's metadata practices."""

    total_resources: int
    total_users: int
    avg_metadata_completeness: float
    top_keywords: List[Tuple[str, int]]
    popular_licenses: List[Tuple[str, int]]
    common_resource_types: List[Tuple[str, int]]
    metadata_quality_distribution: Dict[str, int]
    temporal_trends: Dict[str, Any]
    collaboration_patterns: Dict[str, Any]


class CommunityAnalyzer:
    """Analyzes repository-wide patterns for collaborative intelligence."""

    def __init__(self, user_client: NakalaUserInfoClient, cache_dir: str = None):
        self.user_client = user_client
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path.home() / ".nakala" / "community_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Community data storage
        self.community_patterns: Dict[str, Any] = {}
        self.quality_benchmarks: Dict[str, float] = {}
        self.domain_standards: Dict[str, Dict[str, Any]] = {}
        self.collaboration_networks: Dict[str, Set[str]] = defaultdict(set)

        # Analysis parameters
        self.min_community_size = 10
        self.trend_window_days = 90
        self.quality_percentiles = [25, 50, 75, 90, 95]

        self._load_community_data()

    def _load_community_data(self):
        """Load community analysis data from cache."""
        community_file = self.cache_dir / "community_data.json"
        if community_file.exists():
            try:
                with open(community_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.community_patterns = data.get("patterns", {})
                    self.quality_benchmarks = data.get("benchmarks", {})
                    self.domain_standards = data.get("standards", {})

                logger.info("Loaded community analysis data")
            except Exception as e:
                logger.warning(f"Failed to load community data: {e}")

    def _save_community_data(self):
        """Save community analysis data to cache."""
        community_file = self.cache_dir / "community_data.json"
        try:
            data = {
                "patterns": self.community_patterns,
                "benchmarks": self.quality_benchmarks,
                "standards": self.domain_standards,
                "updated_at": datetime.now().isoformat(),
            }
            with open(community_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.debug("Saved community analysis data")
        except Exception as e:
            logger.warning(f"Failed to save community data: {e}")

    async def analyze_community_patterns(self) -> CommunityMetrics:
        """Analyze repository-wide patterns and community behavior."""
        logger.info("Analyzing community metadata patterns...")

        try:
            # Get comprehensive user profile (includes community data)
            user_profile = self.user_client.get_complete_user_profile()

            # Extract community data
            all_datasets = user_profile.get("datasets", [])
            all_collections = user_profile.get("collections", [])
            all_resources = all_datasets + all_collections

            if len(all_resources) < self.min_community_size:
                logger.warning(
                    f"Insufficient community data: {len(all_resources)} resources"
                )
                return self._create_minimal_metrics(all_resources)

            # Analyze patterns
            metrics = await self._compute_community_metrics(all_resources)

            # Update community patterns
            self._update_community_patterns(all_resources, metrics)

            # Save analysis results
            self._save_community_data()

            logger.info(f"Analyzed {len(all_resources)} community resources")
            return metrics

        except Exception as e:
            logger.error(f"Failed to analyze community patterns: {e}")
            return self._create_minimal_metrics([])

    async def _compute_community_metrics(
        self, resources: List[Dict[str, Any]]
    ) -> CommunityMetrics:
        """Compute comprehensive community metrics."""

        # Basic counts
        total_resources = len(resources)
        creators = set()

        # Metadata analysis
        metadata_completeness_scores = []
        all_keywords = []
        all_licenses = []
        all_types = []
        quality_scores = []

        # Temporal analysis
        creation_dates = []
        monthly_counts = defaultdict(int)

        # Collaboration analysis
        collaboration_pairs = []

        for resource in resources:
            # Extract creators
            resource_creators = self._extract_creators(resource)
            creators.update(resource_creators)

            # If multiple creators, it's a collaboration
            if len(resource_creators) > 1:
                for i, creator1 in enumerate(resource_creators):
                    for creator2 in resource_creators[i + 1 :]:
                        collaboration_pairs.append((creator1, creator2))

            # Analyze metadata completeness
            completeness = self._calculate_metadata_completeness(resource)
            metadata_completeness_scores.append(completeness)

            # Analyze quality
            quality = self._estimate_metadata_quality(resource)
            quality_scores.append(quality)

            # Extract field values
            keywords = self._extract_keywords(resource)
            all_keywords.extend(keywords)

            license_value = self._extract_meta_value(
                resource.get("metas", []), "license"
            )
            if license_value:
                all_licenses.append(license_value)

            type_value = self._extract_meta_value(resource.get("metas", []), "type")
            if type_value:
                all_types.append(type_value)

            # Temporal analysis
            created = resource.get("created", resource.get("date"))
            if created:
                try:
                    if isinstance(created, str):
                        date_obj = datetime.fromisoformat(
                            created.replace("Z", "+00:00")
                        )
                    else:
                        date_obj = datetime.now()

                    creation_dates.append(date_obj)
                    month_key = f"{date_obj.year}-{date_obj.month:02d}"
                    monthly_counts[month_key] += 1
                except (ValueError, TypeError):
                    pass

        # Compute aggregated metrics
        avg_completeness = (
            statistics.mean(metadata_completeness_scores)
            if metadata_completeness_scores
            else 0.0
        )

        # Top keywords (most frequent)
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(20)

        # Popular licenses
        license_counts = Counter(all_licenses)
        popular_licenses = license_counts.most_common(10)

        # Common resource types
        type_counts = Counter(all_types)
        common_types = type_counts.most_common(10)

        # Quality distribution
        quality_distribution = self._compute_quality_distribution(quality_scores)

        # Temporal trends
        temporal_trends = self._analyze_temporal_trends(creation_dates, monthly_counts)

        # Collaboration patterns
        collaboration_patterns = self._analyze_collaboration_patterns(
            collaboration_pairs, creators
        )

        return CommunityMetrics(
            total_resources=total_resources,
            total_users=len(creators),
            avg_metadata_completeness=avg_completeness,
            top_keywords=top_keywords,
            popular_licenses=popular_licenses,
            common_resource_types=common_types,
            metadata_quality_distribution=quality_distribution,
            temporal_trends=temporal_trends,
            collaboration_patterns=collaboration_patterns,
        )

    def _extract_creators(self, resource: Dict[str, Any]) -> List[str]:
        """Extract creator names from resource metadata."""
        creators = []

        # Try multiple fields for creator information
        creator_fields = ["creator", "author", "contributor"]
        for field in creator_fields:
            value = self._extract_meta_value(resource.get("metas", []), field)
            if value:
                # Handle multiple creators separated by semicolons
                if ";" in value:
                    creators.extend([c.strip() for c in value.split(";") if c.strip()])
                else:
                    creators.append(value.strip())

        return list(set(creators))  # Remove duplicates

    def _calculate_metadata_completeness(self, resource: Dict[str, Any]) -> float:
        """Calculate metadata completeness score (0-1)."""
        essential_fields = ["title", "description", "creator", "type", "license"]
        optional_fields = ["keywords", "language", "date", "identifier"]

        metas = resource.get("metas", [])
        present_fields = set()

        for meta in metas:
            property_uri = meta.get("propertyUri", "").lower()
            for field in essential_fields + optional_fields:
                if field in property_uri:
                    present_fields.add(field)

        # Weight essential fields more heavily
        essential_score = sum(
            1 for field in essential_fields if field in present_fields
        ) / len(essential_fields)
        optional_score = sum(
            1 for field in optional_fields if field in present_fields
        ) / len(optional_fields)

        # Weighted average: 70% essential, 30% optional
        completeness = (essential_score * 0.7) + (optional_score * 0.3)
        return completeness

    def _estimate_metadata_quality(self, resource: Dict[str, Any]) -> float:
        """Estimate metadata quality based on various factors."""
        quality_score = 0.0
        factors = 0

        metas = resource.get("metas", [])

        # Check title quality
        title = self._extract_meta_value(metas, "title")
        if title:
            if len(title) > 10:  # Substantial title
                quality_score += 0.2
            if len(title.split()) >= 3:  # Multi-word title
                quality_score += 0.1
            factors += 2

        # Check description quality
        description = self._extract_meta_value(metas, "description")
        if description:
            if len(description) > 50:  # Substantial description
                quality_score += 0.2
            if len(description.split()) >= 10:  # Detailed description
                quality_score += 0.1
            factors += 2

        # Check keywords presence and quality
        keywords = self._extract_keywords(resource)
        if keywords:
            if len(keywords) >= 3:  # Good keyword coverage
                quality_score += 0.2
            factors += 1

        # Check multilingual support
        has_multilingual = self._has_multilingual_metadata(metas)
        if has_multilingual:
            quality_score += 0.15
            factors += 1

        # Check identifier presence
        identifier = self._extract_meta_value(metas, "identifier")
        if identifier:
            quality_score += 0.1
            factors += 1

        # Normalize by number of factors checked
        if factors > 0:
            quality_score = quality_score / (factors * 0.1)  # Normalize to 0-1 range

        return min(quality_score, 1.0)

    def _extract_keywords(self, resource: Dict[str, Any]) -> List[str]:
        """Extract keywords from resource metadata."""
        keywords = []
        metas = resource.get("metas", [])

        for meta in metas:
            if "subject" in meta.get("propertyUri", "").lower():
                value = meta.get("value", "")
                if value:
                    # Handle various keyword separators
                    if ";" in value:
                        keywords.extend(
                            [k.strip() for k in value.split(";") if k.strip()]
                        )
                    elif "," in value:
                        keywords.extend(
                            [k.strip() for k in value.split(",") if k.strip()]
                        )
                    else:
                        keywords.append(value.strip())

        return keywords

    def _extract_meta_value(
        self, metas: List[Dict], property_name: str, language: str = None
    ) -> str:
        """Extract metadata value by property name."""
        for meta in metas:
            property_uri = meta.get("propertyUri", "").lower()
            if property_name.lower() in property_uri:
                if language:
                    if meta.get("lang") == language:
                        return meta.get("value", "")
                else:
                    return meta.get("value", "")
        return ""

    def _has_multilingual_metadata(self, metas: List[Dict]) -> bool:
        """Check if resource has multilingual metadata."""
        languages = set()
        for meta in metas:
            lang = meta.get("lang")
            if lang:
                languages.add(lang)
        return len(languages) > 1

    def _compute_quality_distribution(
        self, quality_scores: List[float]
    ) -> Dict[str, int]:
        """Compute quality score distribution."""
        distribution = {
            "excellent": 0,  # 0.9-1.0
            "good": 0,  # 0.7-0.89
            "fair": 0,  # 0.5-0.69
            "poor": 0,  # 0.3-0.49
            "very_poor": 0,  # 0.0-0.29
        }

        for score in quality_scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.7:
                distribution["good"] += 1
            elif score >= 0.5:
                distribution["fair"] += 1
            elif score >= 0.3:
                distribution["poor"] += 1
            else:
                distribution["very_poor"] += 1

        return distribution

    def _analyze_temporal_trends(
        self, creation_dates: List[datetime], monthly_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """Analyze temporal trends in resource creation."""
        trends = {
            "total_timespan_days": 0,
            "avg_resources_per_month": 0.0,
            "peak_month": None,
            "recent_activity": 0,
            "growth_trend": "stable",
        }

        if not creation_dates:
            return trends

        # Calculate timespan
        min_date = min(creation_dates)
        max_date = max(creation_dates)
        timespan = (max_date - min_date).days
        trends["total_timespan_days"] = timespan

        # Average per month
        if monthly_counts:
            trends["avg_resources_per_month"] = statistics.mean(monthly_counts.values())

            # Peak month
            peak_month = max(monthly_counts.items(), key=lambda x: x[1])
            trends["peak_month"] = {"month": peak_month[0], "count": peak_month[1]}

        # Recent activity (last 30 days)
        recent_threshold = datetime.now() - timedelta(days=30)
        recent_count = sum(1 for date in creation_dates if date >= recent_threshold)
        trends["recent_activity"] = recent_count

        # Growth trend analysis
        if len(monthly_counts) >= 3:
            recent_months = sorted(monthly_counts.items())[-3:]
            counts = [count for _, count in recent_months]

            if len(counts) >= 2:
                if counts[-1] > counts[0]:
                    trends["growth_trend"] = "growing"
                elif counts[-1] < counts[0]:
                    trends["growth_trend"] = "declining"

        return trends

    def _analyze_collaboration_patterns(
        self, collaboration_pairs: List[Tuple[str, str]], all_creators: Set[str]
    ) -> Dict[str, Any]:
        """Analyze collaboration patterns in the community."""
        patterns = {
            "total_collaborations": len(collaboration_pairs),
            "collaboration_rate": 0.0,
            "most_collaborative_users": [],
            "collaboration_network_density": 0.0,
            "average_collaborators_per_user": 0.0,
        }

        if not all_creators:
            return patterns

        # Collaboration rate
        patterns["collaboration_rate"] = len(collaboration_pairs) / len(all_creators)

        # Count collaborations per user
        user_collaborations = defaultdict(set)
        for user1, user2 in collaboration_pairs:
            user_collaborations[user1].add(user2)
            user_collaborations[user2].add(user1)

        # Most collaborative users
        if user_collaborations:
            most_collaborative = sorted(
                user_collaborations.items(), key=lambda x: len(x[1]), reverse=True
            )[:5]
            patterns["most_collaborative_users"] = [
                {"user": user, "collaborator_count": len(collaborators)}
                for user, collaborators in most_collaborative
            ]

            # Average collaborators per user
            patterns["average_collaborators_per_user"] = statistics.mean(
                [len(collaborators) for collaborators in user_collaborations.values()]
            )

        # Network density (simplified)
        max_possible_connections = len(all_creators) * (len(all_creators) - 1) / 2
        if max_possible_connections > 0:
            patterns["collaboration_network_density"] = (
                len(collaboration_pairs) / max_possible_connections
            )

        return patterns

    def _update_community_patterns(
        self, resources: List[Dict[str, Any]], metrics: CommunityMetrics
    ):
        """Update community pattern database with new insights."""

        # Store quality benchmarks
        self.quality_benchmarks = {
            "avg_completeness": metrics.avg_metadata_completeness,
            "quality_distribution": metrics.metadata_quality_distribution,
            "total_resources": metrics.total_resources,
            "last_updated": datetime.now().isoformat(),
        }

        # Extract domain standards
        for resource_type, count in metrics.common_resource_types:
            if count >= self.min_community_size:
                domain_resources = [
                    r
                    for r in resources
                    if self._extract_meta_value(r.get("metas", []), "type")
                    == resource_type
                ]
                self._extract_domain_standards(resource_type, domain_resources)

        # Store community patterns
        self.community_patterns = {
            "keywords": dict(metrics.top_keywords[:50]),  # Top 50 keywords
            "licenses": dict(metrics.popular_licenses),
            "resource_types": dict(metrics.common_resource_types),
            "temporal_trends": metrics.temporal_trends,
            "collaboration_metrics": metrics.collaboration_patterns,
            "last_analysis": datetime.now().isoformat(),
        }

    def _extract_domain_standards(
        self, domain: str, domain_resources: List[Dict[str, Any]]
    ):
        """Extract best practices and standards for a specific domain."""
        if domain not in self.domain_standards:
            self.domain_standards[domain] = {}

        # Analyze field usage patterns
        field_usage = defaultdict(int)
        field_values = defaultdict(list)

        for resource in domain_resources:
            metas = resource.get("metas", [])
            for meta in metas:
                property_uri = meta.get("propertyUri", "")
                value = meta.get("value", "")

                if property_uri and value:
                    field_name = property_uri.split("#")[-1].split("/")[-1].lower()
                    field_usage[field_name] += 1
                    field_values[field_name].append(value)

        # Store domain standards
        total_resources = len(domain_resources)
        standards = {}

        for field, count in field_usage.items():
            usage_rate = count / total_resources
            if usage_rate >= 0.5:  # Field used in at least 50% of resources
                values = field_values[field]
                value_counts = Counter(values)

                standards[field] = {
                    "usage_rate": usage_rate,
                    "common_values": value_counts.most_common(5),
                    "total_occurrences": count,
                }

        self.domain_standards[domain] = standards

    def _create_minimal_metrics(
        self, resources: List[Dict[str, Any]]
    ) -> CommunityMetrics:
        """Create minimal metrics when insufficient data is available."""
        return CommunityMetrics(
            total_resources=len(resources),
            total_users=0,
            avg_metadata_completeness=0.0,
            top_keywords=[],
            popular_licenses=[],
            common_resource_types=[],
            metadata_quality_distribution={"poor": len(resources)},
            temporal_trends={},
            collaboration_patterns={},
        )

    def get_community_recommendations(
        self, user_context: Dict[str, Any]
    ) -> List[CollaborativeInsight]:
        """Generate recommendations based on community analysis."""
        recommendations = []

        # Quality improvement recommendations
        if self.quality_benchmarks:
            avg_quality = self.quality_benchmarks.get("avg_completeness", 0)
            if avg_quality > 0:
                recommendations.append(
                    CollaborativeInsight(
                        insight_id="quality_benchmark",
                        insight_type="best_practice",
                        confidence=0.8,
                        impact_score=0.7,
                        evidence_count=self.quality_benchmarks.get(
                            "total_resources", 0
                        ),
                        created_at=datetime.now(),
                        context={"benchmark_score": avg_quality},
                        recommendation=(
                            f"Community average metadata completeness is {avg_quality:.1%}. "
                            "Consider enhancing your metadata to meet or exceed this standard."
                        ),
                    )
                )

        # Keyword recommendations
        if self.community_patterns.get("keywords"):
            popular_keywords = list(self.community_patterns["keywords"].keys())[:10]
            recommendations.append(
                CollaborativeInsight(
                    insight_id="popular_keywords",
                    insight_type="community_trend",
                    confidence=0.7,
                    impact_score=0.6,
                    evidence_count=len(popular_keywords),
                    created_at=datetime.now(),
                    context={"keywords": popular_keywords},
                    recommendation=(
                        f"Consider using popular community keywords: "
                        f"{', '.join(popular_keywords[:5])}"
                    ),
                )
            )

        # License recommendations
        if self.community_patterns.get("licenses"):
            popular_licenses = list(self.community_patterns["licenses"].keys())[:3]
            recommendations.append(
                CollaborativeInsight(
                    insight_id="license_trends",
                    insight_type="community_trend",
                    confidence=0.9,
                    impact_score=0.8,
                    evidence_count=len(popular_licenses),
                    created_at=datetime.now(),
                    context={"licenses": popular_licenses},
                    recommendation=(
                        f"Most used licenses in community: {', '.join(popular_licenses)}"
                    ),
                )
            )

        # Domain-specific recommendations
        user_type = user_context.get("type", "unknown")
        if user_type in self.domain_standards:
            domain_info = self.domain_standards[user_type]
            high_usage_fields = [
                field for field, info in domain_info.items() if info["usage_rate"] > 0.8
            ]

            if high_usage_fields:
                recommendations.append(
                    CollaborativeInsight(
                        insight_id=f"domain_standards_{user_type}",
                        insight_type="domain_standard",
                        confidence=0.85,
                        impact_score=0.9,
                        evidence_count=len(high_usage_fields),
                        created_at=datetime.now(),
                        context={"domain": user_type, "fields": high_usage_fields},
                        recommendation=(
                            f"For {user_type} resources, consider including these commonly "
                            f"used fields: {', '.join(high_usage_fields)}"
                        ),
                    )
                )

        return recommendations


class CollaborativeIntelligenceEngine:
    """Main engine combining ML patterns with collaborative intelligence."""

    def __init__(self, user_client: NakalaUserInfoClient, cache_dir: str = None):
        self.user_client = user_client
        self.community_analyzer = CommunityAnalyzer(user_client, cache_dir)
        self.ml_learner = MLPatternLearner(cache_dir)
        self.semantic_analyzer = SemanticAnalyzer(cache_dir)

        # Collaborative insights storage
        self.insights_cache: Dict[str, CollaborativeInsight] = {}

    async def analyze_and_learn(self) -> Dict[str, Any]:
        """Perform comprehensive collaborative analysis and learning."""
        results = {
            "community_metrics": None,
            "ml_patterns_learned": 0,
            "semantic_embeddings": 0,
            "collaborative_insights": [],
            "processing_time": 0.0,
        }

        start_time = datetime.now()

        try:
            # Analyze community patterns
            logger.info("Starting collaborative intelligence analysis...")
            community_metrics = (
                await self.community_analyzer.analyze_community_patterns()
            )
            results["community_metrics"] = asdict(community_metrics)

            # Learn ML patterns from community data
            user_profile = self.user_client.get_complete_user_profile()
            all_resources = user_profile.get("datasets", []) + user_profile.get(
                "collections", []
            )

            if all_resources:
                patterns_learned = self.ml_learner.learn_from_metadata(all_resources)
                results["ml_patterns_learned"] = patterns_learned

                # Create semantic embeddings for content analysis
                for resource in all_resources[:50]:  # Limit for performance
                    content = self._extract_content_for_analysis(resource)
                    if content:
                        self.semantic_analyzer.analyze_content(
                            content=content,
                            content_id=resource.get("identifier", "unknown"),
                            content_type=self._extract_meta_value(
                                resource.get("metas", []), "type"
                            )
                            or "unknown",
                            language=self._extract_meta_value(
                                resource.get("metas", []), "language"
                            )
                            or "en",
                        )
                        results["semantic_embeddings"] += 1

            # Generate collaborative insights
            insights = self.community_analyzer.get_community_recommendations({})
            results["collaborative_insights"] = [
                asdict(insight) for insight in insights
            ]

            # Store insights
            for insight in insights:
                self.insights_cache[insight.insight_id] = insight

            processing_time = (datetime.now() - start_time).total_seconds()
            results["processing_time"] = processing_time

            logger.info(f"Collaborative analysis completed in {processing_time:.2f}s")
            logger.info(
                f"Learned {patterns_learned} ML patterns, "
                f"created {results['semantic_embeddings']} embeddings"
            )

        except Exception as e:
            logger.error(f"Collaborative analysis failed: {e}")
            results["error"] = str(e)

        return results

    def _extract_content_for_analysis(self, resource: Dict[str, Any]) -> str:
        """Extract text content from resource for semantic analysis."""
        content_parts = []

        metas = resource.get("metas", [])

        # Extract text fields
        text_fields = ["title", "description", "subject", "alternative"]
        for field in text_fields:
            value = self._extract_meta_value(metas, field)
            if value:
                content_parts.append(value)

        return " ".join(content_parts)

    def _extract_meta_value(self, metas: List[Dict], property_name: str) -> str:
        """Extract metadata value by property name."""
        for meta in metas:
            property_uri = meta.get("propertyUri", "").lower()
            if property_name.lower() in property_uri:
                return meta.get("value", "")
        return ""

    async def get_intelligent_suggestions(
        self, context: Dict[str, Any]
    ) -> List[PredictionResult]:
        """Get intelligent suggestions combining ML and collaborative intelligence."""
        suggestions = []

        # Get ML-based predictions
        for field in ["title", "description", "keywords", "license", "type"]:
            ml_prediction = self.ml_learner.predict_field_value(context, field)
            if ml_prediction:
                suggestions.append(ml_prediction)

        # Enhance with collaborative insights
        collaborative_insights = self.community_analyzer.get_community_recommendations(
            context
        )

        # Combine insights into suggestions
        for insight in collaborative_insights:
            if (
                insight.insight_type == "community_trend"
                and "keywords" in insight.context
            ):
                keywords = insight.context["keywords"]
                suggestion = PredictionResult(
                    field_name="keywords",
                    predicted_value=";".join(keywords[:5]),
                    confidence=insight.confidence,
                    reasoning=f"Community trend analysis: {insight.recommendation}",
                    evidence=[f"Used by {insight.evidence_count} community members"],
                    alternatives=[
                        (";".join(keywords[i : i + 3]), insight.confidence * 0.8)
                        for i in range(1, min(3, len(keywords)))
                    ],
                )
                suggestions.append(suggestion)

        return suggestions

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of collaborative intelligence analysis."""
        return {
            "ml_patterns": self.ml_learner.get_pattern_summary(),
            "semantic_trends": self.semantic_analyzer.analyze_semantic_trends(),
            "community_insights": len(self.insights_cache),
            "cache_status": {
                "ml_cache": self.ml_learner.cache_dir.exists(),
                "semantic_cache": self.semantic_analyzer.cache_dir.exists(),
                "community_cache": self.community_analyzer.cache_dir.exists(),
            },
        }


# Factory function
def create_collaborative_intelligence(
    user_client: NakalaUserInfoClient, cache_dir: str = None
) -> CollaborativeIntelligenceEngine:
    """Create collaborative intelligence engine with dependencies."""
    return CollaborativeIntelligenceEngine(user_client, cache_dir)
