"""
NAKALA Predictive Analytics Engine

Advanced analytics system for predicting metadata quality, completeness trends,
and providing proactive recommendations. Part of Phase 3 - Advanced Intelligence.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

# Optional ML dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics
import math

from .ml_engine import MLPatternLearner
from .collaborative_intelligence import (
    CollaborativeIntelligenceEngine,
)
from .user_info import NakalaUserInfoClient

logger = logging.getLogger(__name__)


@dataclass
class QualityPrediction:
    """Prediction about metadata quality metrics."""

    metric_name: str
    current_value: float
    predicted_value: float
    prediction_timeframe: str  # '1_week', '1_month', '3_months', '1_year'
    confidence: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    contributing_factors: List[str]
    recommendations: List[str]

    def __post_init__(self):
        if (
            not hasattr(self, "contributing_factors")
            or self.contributing_factors is None
        ):
            self.contributing_factors = []
        if not hasattr(self, "recommendations") or self.recommendations is None:
            self.recommendations = []


@dataclass
class CompletenesPrediction:
    """Prediction about metadata completeness trends."""

    field_name: str
    current_completion_rate: float
    predicted_completion_rate: float
    prediction_timeframe: str
    confidence: float
    factors_influencing: List[str]
    suggested_actions: List[str]
    priority_level: str  # 'high', 'medium', 'low'

    def __post_init__(self):
        if not hasattr(self, "factors_influencing") or self.factors_influencing is None:
            self.factors_influencing = []
        if not hasattr(self, "suggested_actions") or self.suggested_actions is None:
            self.suggested_actions = []


@dataclass
class UsagePrediction:
    """Prediction about repository usage patterns."""

    usage_metric: str
    current_value: int
    predicted_value: int
    prediction_timeframe: str
    confidence: float
    seasonal_factors: List[str]
    growth_indicators: List[str]
    capacity_recommendations: List[str]

    def __post_init__(self):
        if not hasattr(self, "seasonal_factors") or self.seasonal_factors is None:
            self.seasonal_factors = []
        if not hasattr(self, "growth_indicators") or self.growth_indicators is None:
            self.growth_indicators = []
        if (
            not hasattr(self, "capacity_recommendations")
            or self.capacity_recommendations is None
        ):
            self.capacity_recommendations = []


@dataclass
class PredictiveAnalysisResult:
    """Complete result of predictive analysis."""

    analysis_date: datetime
    prediction_timeframes: List[str]
    quality_predictions: List[QualityPrediction]
    completeness_predictions: List[CompletenesPrediction]
    usage_predictions: List[UsagePrediction]
    overall_health_score: float
    key_insights: List[str]
    strategic_recommendations: List[str]
    processing_time: float
    data_quality_score: float

    def __post_init__(self):
        if not hasattr(self, "key_insights") or self.key_insights is None:
            self.key_insights = []
        if (
            not hasattr(self, "strategic_recommendations")
            or self.strategic_recommendations is None
        ):
            self.strategic_recommendations = []


class TrendAnalyzer:
    """Analyzes trends in metadata and usage patterns."""

    def __init__(self):
        self.min_data_points = 5
        self.trend_sensitivity = 0.1

    def analyze_temporal_trend(
        self, data_points: List[Tuple[datetime, float]]
    ) -> Dict[str, Any]:
        """Analyze temporal trend in data points."""
        if len(data_points) < self.min_data_points:
            return {
                "trend": "insufficient_data",
                "slope": 0.0,
                "confidence": 0.0,
                "r_squared": 0.0,
                "predicted_next": None,
            }

        # Sort by date
        sorted_data = sorted(data_points, key=lambda x: x[0])

        # Convert to numerical values for regression
        x_values = [(point[0] - sorted_data[0][0]).days for point in sorted_data]
        y_values = [point[1] for point in sorted_data]

        # Simple linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xx = sum(x * x for x in x_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))

        # Calculate slope and intercept
        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            slope = 0
            intercept = sum_y / n
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in y_values)
        ss_res = sum(
            (y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values)
        )

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Determine trend direction
        if abs(slope) < self.trend_sensitivity:
            trend = "stable"
        elif slope > 0:
            trend = "improving"
        else:
            trend = "declining"

        # Predict next value
        next_x = x_values[-1] + 30  # 30 days ahead
        predicted_next = slope * next_x + intercept

        return {
            "trend": trend,
            "slope": slope,
            "confidence": min(r_squared, 1.0),
            "r_squared": r_squared,
            "predicted_next": predicted_next,
        }

    def detect_seasonality(
        self, data_points: List[Tuple[datetime, float]]
    ) -> Dict[str, Any]:
        """Detect seasonal patterns in data."""
        if len(data_points) < 12:  # Need at least a year of monthly data
            return {"has_seasonality": False, "seasonal_factors": []}

        # Group by month
        monthly_averages = defaultdict(list)
        for date, value in data_points:
            month = date.month
            monthly_averages[month].append(value)

        # Calculate average for each month
        month_stats = {}
        overall_mean = statistics.mean([value for _, value in data_points])

        for month, values in monthly_averages.items():
            if len(values) >= 2:  # Need at least 2 data points per month
                month_mean = statistics.mean(values)
                month_stats[month] = {
                    "average": month_mean,
                    "deviation": (
                        (month_mean - overall_mean) / overall_mean
                        if overall_mean != 0
                        else 0
                    ),
                    "count": len(values),
                }

        # Detect significant seasonal variations
        seasonal_factors = []
        for month, stats in month_stats.items():
            if abs(stats["deviation"]) > 0.2:  # 20% deviation threshold
                month_name = datetime(2023, month, 1).strftime("%B")
                direction = "higher" if stats["deviation"] > 0 else "lower"
                seasonal_factors.append(
                    f"{month_name}: {direction} activity ({stats['deviation']:.1%})"
                )

        has_seasonality = len(seasonal_factors) > 0

        return {
            "has_seasonality": has_seasonality,
            "seasonal_factors": seasonal_factors,
            "month_stats": month_stats,
        }

    def predict_future_values(
        self, data_points: List[Tuple[datetime, float]], timeframes: List[str]
    ) -> Dict[str, float]:
        """Predict future values for given timeframes."""
        trend_analysis = self.analyze_temporal_trend(data_points)

        if trend_analysis["trend"] == "insufficient_data":
            return {
                timeframe: data_points[-1][1] if data_points else 0.0
                for timeframe in timeframes
            }

        predictions = {}
        slope = trend_analysis["slope"]
        # Extract the most recent date from data points
        max(data_points, key=lambda x: x[0])[0]
        last_value = trend_analysis.get("predicted_next", data_points[-1][1])

        # Map timeframes to days
        timeframe_days = {
            "1_week": 7,
            "1_month": 30,
            "3_months": 90,
            "6_months": 180,
            "1_year": 365,
        }

        for timeframe in timeframes:
            days = timeframe_days.get(timeframe, 30)
            predicted_value = last_value + (slope * days)
            # Ensure predictions stay within reasonable bounds
            predictions[timeframe] = max(0.0, min(1.0, predicted_value))

        return predictions


class QualityPredictor:
    """Predicts metadata quality trends and issues."""

    def __init__(self, trend_analyzer: TrendAnalyzer):
        self.trend_analyzer = trend_analyzer

    def predict_quality_trends(
        self,
        historical_data: Dict[str, List[Tuple[datetime, float]]],
        timeframes: List[str],
    ) -> List[QualityPrediction]:
        """Predict quality trends for various metrics."""
        predictions = []

        quality_metrics = {
            "completeness": "Metadata completeness rate",
            "accuracy": "Data accuracy score",
            "consistency": "Field consistency score",
            "richness": "Metadata richness index",
        }

        for metric, description in quality_metrics.items():
            if metric in historical_data:
                data_points = historical_data[metric]

                if not data_points:
                    continue

                # Analyze trend
                trend_analysis = self.trend_analyzer.analyze_temporal_trend(data_points)
                current_value = data_points[-1][1] if data_points else 0.0

                # Predict future values
                future_predictions = self.trend_analyzer.predict_future_values(
                    data_points, timeframes
                )

                for timeframe in timeframes:
                    predicted_value = future_predictions.get(timeframe, current_value)

                    # Generate contributing factors
                    factors = self._identify_quality_factors(
                        metric, trend_analysis, data_points
                    )

                    # Generate recommendations
                    recommendations = self._generate_quality_recommendations(
                        metric, trend_analysis, current_value
                    )

                    prediction = QualityPrediction(
                        metric_name=description,
                        current_value=current_value,
                        predicted_value=predicted_value,
                        prediction_timeframe=timeframe,
                        confidence=trend_analysis["confidence"],
                        trend_direction=trend_analysis["trend"],
                        contributing_factors=factors,
                        recommendations=recommendations,
                    )
                    predictions.append(prediction)

        return predictions

    def _identify_quality_factors(
        self,
        metric: str,
        trend_analysis: Dict[str, Any],
        data_points: List[Tuple[datetime, float]],
    ) -> List[str]:
        """Identify factors contributing to quality trends."""
        factors = []

        trend = trend_analysis["trend"]
        confidence = trend_analysis["confidence"]

        if trend == "improving":
            factors.append("Positive quality trend observed")
            if confidence > 0.7:
                factors.append("High confidence in improvement pattern")
        elif trend == "declining":
            factors.append("Declining quality trend detected")
            if confidence > 0.7:
                factors.append("Strong evidence of quality degradation")
        else:
            factors.append("Quality metrics remain stable")

        # Metric-specific factors
        if metric == "completeness":
            factors.append("Field completion rates influencing overall completeness")
        elif metric == "accuracy":
            factors.append("Data validation results affecting accuracy scores")
        elif metric == "consistency":
            factors.append("Standardization efforts impacting consistency")
        elif metric == "richness":
            factors.append("Metadata depth and detail levels")

        # Data quality factors
        if len(data_points) < 10:
            factors.append("Limited historical data for prediction")

        return factors

    def _generate_quality_recommendations(
        self, metric: str, trend_analysis: Dict[str, Any], current_value: float
    ) -> List[str]:
        """Generate recommendations for quality improvement."""
        recommendations = []

        trend = trend_analysis["trend"]
        confidence = trend_analysis["confidence"]

        # General recommendations based on trend
        if trend == "declining":
            recommendations.append("Immediate quality review recommended")
            recommendations.append(
                "Implement corrective measures to reverse declining trend"
            )
        elif trend == "stable" and current_value < 0.7:
            recommendations.append("Consider quality improvement initiatives")

        # Metric-specific recommendations
        if metric == "completeness":
            if current_value < 0.8:
                recommendations.append("Focus on completing essential metadata fields")
                recommendations.append("Implement guided metadata entry workflows")
        elif metric == "accuracy":
            if current_value < 0.8:
                recommendations.append("Enhance data validation rules")
                recommendations.append("Implement automated accuracy checking")
        elif metric == "consistency":
            if current_value < 0.8:
                recommendations.append("Standardize metadata entry procedures")
                recommendations.append("Use controlled vocabularies and templates")
        elif metric == "richness":
            if current_value < 0.7:
                recommendations.append("Encourage detailed metadata descriptions")
                recommendations.append("Provide training on metadata best practices")

        # Confidence-based recommendations
        if confidence < 0.5:
            recommendations.append(
                "Collect more historical data for better predictions"
            )

        return recommendations


class CompletenessPredictor:
    """Predicts metadata completeness trends for specific fields."""

    def __init__(self, trend_analyzer: TrendAnalyzer):
        self.trend_analyzer = trend_analyzer

    def predict_field_completeness(
        self, field_data: Dict[str, List[Tuple[datetime, float]]], timeframes: List[str]
    ) -> List[CompletenesPrediction]:
        """Predict completeness trends for metadata fields."""
        predictions = []

        priority_fields = {
            "title": "high",
            "description": "high",
            "creator": "high",
            "type": "high",
            "license": "high",
            "keywords": "medium",
            "language": "medium",
            "date": "medium",
            "spatial": "low",
            "temporal": "low",
        }

        for field_name, data_points in field_data.items():
            if not data_points:
                continue

            current_rate = data_points[-1][1] if data_points else 0.0
            trend_analysis = self.trend_analyzer.analyze_temporal_trend(data_points)
            future_predictions = self.trend_analyzer.predict_future_values(
                data_points, timeframes
            )

            for timeframe in timeframes:
                predicted_rate = future_predictions.get(timeframe, current_rate)

                # Identify influencing factors
                factors = self._identify_completeness_factors(
                    field_name, trend_analysis, current_rate
                )

                # Generate action suggestions
                actions = self._suggest_completeness_actions(
                    field_name, trend_analysis, current_rate
                )

                # Determine priority
                priority = priority_fields.get(field_name, "low")

                prediction = CompletenesPrediction(
                    field_name=field_name,
                    current_completion_rate=current_rate,
                    predicted_completion_rate=predicted_rate,
                    prediction_timeframe=timeframe,
                    confidence=trend_analysis["confidence"],
                    factors_influencing=factors,
                    suggested_actions=actions,
                    priority_level=priority,
                )
                predictions.append(prediction)

        return predictions

    def _identify_completeness_factors(
        self, field_name: str, trend_analysis: Dict[str, Any], current_rate: float
    ) -> List[str]:
        """Identify factors affecting field completeness."""
        factors = []

        trend = trend_analysis["trend"]

        if trend == "improving":
            factors.append(f"Users increasingly completing {field_name} field")
        elif trend == "declining":
            factors.append(f"Declining completion rate for {field_name}")

        # Field-specific factors
        if field_name in ["title", "description"]:
            factors.append("Essential field - completion expected")
        elif field_name in ["keywords", "spatial", "temporal"]:
            factors.append("Optional field - depends on content relevance")
        elif field_name == "creator":
            factors.append("Attribution field - varies by institutional policy")
        elif field_name == "license":
            factors.append("Legal requirement - should be consistently completed")

        # Rate-specific factors
        if current_rate < 0.5:
            factors.append("Low completion rate indicates potential barriers")
        elif current_rate > 0.9:
            factors.append("High completion rate suggests good adoption")

        return factors

    def _suggest_completeness_actions(
        self, field_name: str, trend_analysis: Dict[str, Any], current_rate: float
    ) -> List[str]:
        """Suggest actions to improve field completeness."""
        actions = []

        trend = trend_analysis["trend"]

        if current_rate < 0.7:
            actions.append(f"Improve {field_name} field completion guidance")
            actions.append(f"Add validation reminders for {field_name}")

        if trend == "declining":
            actions.append(f"Investigate barriers to {field_name} completion")
            actions.append(f"Review {field_name} field requirements")

        # Field-specific actions
        if field_name == "keywords":
            actions.append("Provide keyword suggestions from controlled vocabularies")
        elif field_name == "description":
            actions.append("Offer description templates and examples")
        elif field_name == "creator":
            actions.append("Implement author lookup and auto-completion")
        elif field_name == "license":
            actions.append("Default to institutional standard license")
        elif field_name in ["spatial", "temporal"]:
            actions.append("Show field only when relevant to content type")

        return actions


class UsagePredictor:
    """Predicts repository usage patterns and capacity needs."""

    def __init__(self, trend_analyzer: TrendAnalyzer):
        self.trend_analyzer = trend_analyzer

    def predict_usage_patterns(
        self, usage_data: Dict[str, List[Tuple[datetime, int]]], timeframes: List[str]
    ) -> List[UsagePrediction]:
        """Predict usage patterns for various metrics."""
        predictions = []

        usage_metrics = {
            "new_resources": "New resources created",
            "total_resources": "Total repository resources",
            "active_users": "Active users count",
            "api_requests": "API requests volume",
        }

        for metric, description in usage_metrics.items():
            if metric in usage_data:
                data_points = usage_data[metric]

                if not data_points:
                    continue

                current_value = data_points[-1][1] if data_points else 0

                # Analyze trends and seasonality
                trend_analysis = self.trend_analyzer.analyze_temporal_trend(
                    [(date, float(value)) for date, value in data_points]
                )
                seasonality = self.trend_analyzer.detect_seasonality(
                    [(date, float(value)) for date, value in data_points]
                )

                # Predict future values
                future_predictions = self.trend_analyzer.predict_future_values(
                    [(date, float(value)) for date, value in data_points], timeframes
                )

                for timeframe in timeframes:
                    predicted_value = int(
                        future_predictions.get(timeframe, current_value)
                    )

                    # Identify seasonal factors
                    seasonal_factors = seasonality.get("seasonal_factors", [])

                    # Identify growth indicators
                    growth_indicators = self._identify_growth_indicators(
                        metric, trend_analysis, data_points
                    )

                    # Generate capacity recommendations
                    capacity_recommendations = self._generate_capacity_recommendations(
                        metric, current_value, predicted_value, trend_analysis
                    )

                    prediction = UsagePrediction(
                        usage_metric=description,
                        current_value=current_value,
                        predicted_value=predicted_value,
                        prediction_timeframe=timeframe,
                        confidence=trend_analysis["confidence"],
                        seasonal_factors=seasonal_factors,
                        growth_indicators=growth_indicators,
                        capacity_recommendations=capacity_recommendations,
                    )
                    predictions.append(prediction)

        return predictions

    def _identify_growth_indicators(
        self,
        metric: str,
        trend_analysis: Dict[str, Any],
        data_points: List[Tuple[datetime, int]],
    ) -> List[str]:
        """Identify indicators of growth patterns."""
        indicators = []

        trend = trend_analysis["trend"]
        slope = trend_analysis.get("slope", 0)

        if trend == "improving":
            if slope > 0.1:
                indicators.append("Strong growth trend")
            else:
                indicators.append("Moderate growth trend")
        elif trend == "declining":
            indicators.append("Declining usage pattern")
        else:
            indicators.append("Stable usage pattern")

        # Calculate growth rate
        if len(data_points) >= 2:
            recent_value = data_points[-1][1]
            older_value = data_points[-min(len(data_points), 30)][
                1
            ]  # Compare with 30 periods ago

            if older_value > 0:
                growth_rate = (recent_value - older_value) / older_value
                if growth_rate > 0.2:
                    indicators.append(f"High growth rate: {growth_rate:.1%}")
                elif growth_rate > 0.05:
                    indicators.append(f"Moderate growth rate: {growth_rate:.1%}")
                elif growth_rate < -0.05:
                    indicators.append(f"Negative growth rate: {growth_rate:.1%}")

        return indicators

    def _generate_capacity_recommendations(
        self,
        metric: str,
        current_value: int,
        predicted_value: int,
        trend_analysis: Dict[str, Any],
    ) -> List[str]:
        """Generate capacity and scaling recommendations."""
        recommendations = []

        growth_factor = predicted_value / current_value if current_value > 0 else 1.0
        trend = trend_analysis["trend"]

        if growth_factor > 2.0:
            recommendations.append("Plan for significant capacity increases")
            recommendations.append("Consider infrastructure scaling")
        elif growth_factor > 1.5:
            recommendations.append("Moderate capacity expansion recommended")

        # Metric-specific recommendations
        if metric == "new_resources":
            if trend == "improving":
                recommendations.append("Prepare storage for increased data volume")
                recommendations.append("Scale metadata processing capabilities")
        elif metric == "active_users":
            if trend == "improving":
                recommendations.append("Plan for increased support needs")
                recommendations.append("Scale user management systems")
        elif metric == "api_requests":
            if trend == "improving":
                recommendations.append("Monitor API performance and limits")
                recommendations.append("Consider API rate limiting adjustments")

        return recommendations


class PredictiveAnalyticsEngine:
    """Main engine for predictive analytics and forecasting."""

    def __init__(self, user_client: NakalaUserInfoClient, cache_dir: str = None):
        self.user_client = user_client
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir
            else Path.home() / ".nakala" / "predictive_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.trend_analyzer = TrendAnalyzer()
        self.quality_predictor = QualityPredictor(self.trend_analyzer)
        self.completeness_predictor = CompletenessPredictor(self.trend_analyzer)
        self.usage_predictor = UsagePredictor(self.trend_analyzer)

        # Initialize ML and collaborative intelligence
        self.ml_learner = MLPatternLearner(str(self.cache_dir))
        self.collaborative_engine = CollaborativeIntelligenceEngine(
            user_client, str(self.cache_dir)
        )

        # Analysis settings
        self.default_timeframes = ["1_week", "1_month", "3_months", "1_year"]
        self.min_data_points = 5

    async def generate_predictive_analysis(
        self,
        custom_timeframes: List[str] = None,
        include_quality: bool = True,
        include_completeness: bool = True,
        include_usage: bool = True,
    ) -> PredictiveAnalysisResult:
        """Generate comprehensive predictive analysis."""
        start_time = datetime.now()

        logger.info("Starting comprehensive predictive analysis...")

        timeframes = custom_timeframes or self.default_timeframes

        try:
            # Gather historical data
            historical_data = await self._gather_historical_data()

            # Initialize result
            quality_predictions = []
            completeness_predictions = []
            usage_predictions = []

            # Generate quality predictions
            if include_quality and historical_data["quality"]:
                quality_predictions = self.quality_predictor.predict_quality_trends(
                    historical_data["quality"], timeframes
                )

            # Generate completeness predictions
            if include_completeness and historical_data["completeness"]:
                completeness_predictions = (
                    self.completeness_predictor.predict_field_completeness(
                        historical_data["completeness"], timeframes
                    )
                )

            # Generate usage predictions
            if include_usage and historical_data["usage"]:
                usage_predictions = self.usage_predictor.predict_usage_patterns(
                    historical_data["usage"], timeframes
                )

            # Calculate overall health score
            health_score = self._calculate_health_score(
                quality_predictions, completeness_predictions, usage_predictions
            )

            # Generate insights and recommendations
            insights = self._generate_key_insights(
                quality_predictions, completeness_predictions, usage_predictions
            )
            strategic_recommendations = self._generate_strategic_recommendations(
                quality_predictions,
                completeness_predictions,
                usage_predictions,
                health_score,
            )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Assess data quality for predictions
            data_quality = self._assess_data_quality(historical_data)

            result = PredictiveAnalysisResult(
                analysis_date=datetime.now(),
                prediction_timeframes=timeframes,
                quality_predictions=quality_predictions,
                completeness_predictions=completeness_predictions,
                usage_predictions=usage_predictions,
                overall_health_score=health_score,
                key_insights=insights,
                strategic_recommendations=strategic_recommendations,
                processing_time=processing_time,
                data_quality_score=data_quality,
            )

            logger.info(
                f"Predictive analysis completed in {processing_time:.2f}s: "
                f"health score {health_score:.1%}, data quality {data_quality:.1%}"
            )

            return result

        except Exception as e:
            logger.error(f"Predictive analysis failed: {e}")
            raise

    async def _gather_historical_data(
        self,
    ) -> Dict[str, Dict[str, List[Tuple[datetime, float]]]]:
        """Gather historical data for analysis."""
        # This would integrate with actual data sources
        # For now, we'll create mock data structure

        data = {"quality": {}, "completeness": {}, "usage": {}}

        try:
            # Get user profile for some real data
            # Get user profile for some real data
            self.user_client.get_complete_user_profile()

            # Mock historical data generation
            # In a real implementation, this would query actual historical metrics
            base_date = datetime.now() - timedelta(days=365)

            # Generate mock quality data
            for metric in ["completeness", "accuracy", "consistency", "richness"]:
                data["quality"][metric] = self._generate_mock_trend_data(
                    base_date, metric
                )

            # Generate mock completeness data for fields
            fields = [
                "title",
                "description",
                "creator",
                "keywords",
                "license",
                "type",
                "language",
            ]
            for field in fields:
                data["completeness"][field] = self._generate_mock_trend_data(
                    base_date, field, is_percentage=True
                )

            # Generate mock usage data
            for metric in ["new_resources", "total_resources", "active_users"]:
                data["usage"][metric] = self._generate_mock_usage_data(
                    base_date, metric
                )

        except Exception as e:
            logger.warning(f"Failed to gather some historical data: {e}")

        return data

    def _generate_mock_trend_data(
        self, start_date: datetime, metric: str, is_percentage: bool = False
    ) -> List[Tuple[datetime, float]]:
        """Generate mock trend data for testing."""
        import random

        data_points = []
        current_date = start_date

        # Base values for different metrics
        base_values = {
            "completeness": 0.7,
            "accuracy": 0.8,
            "consistency": 0.6,
            "richness": 0.5,
            "title": 0.95,
            "description": 0.8,
            "creator": 0.7,
            "keywords": 0.6,
            "license": 0.9,
            "type": 0.95,
            "language": 0.5,
        }

        base_value = base_values.get(metric, 0.7)

        # Generate weekly data points
        for week in range(52):
            # Add some trend and noise
            trend_factor = week * 0.002  # Slight upward trend
            noise = random.uniform(-0.05, 0.05)
            seasonal_factor = 0.1 * math.sin(
                2 * math.pi * week / 52
            )  # Annual seasonality

            value = base_value + trend_factor + noise + seasonal_factor

            if is_percentage:
                value = max(0.0, min(1.0, value))  # Clamp to 0-1 for percentages
            else:
                value = max(0.0, value)

            data_points.append((current_date, value))
            current_date += timedelta(days=7)

        return data_points

    def _generate_mock_usage_data(
        self, start_date: datetime, metric: str
    ) -> List[Tuple[datetime, int]]:
        """Generate mock usage data for testing."""
        import random

        data_points = []
        current_date = start_date

        base_values = {"new_resources": 10, "total_resources": 100, "active_users": 15}

        base_value = base_values.get(metric, 10)
        cumulative = metric == "total_resources"

        for week in range(52):
            # Growth trend
            growth_factor = 1 + (week * 0.01)  # 1% weekly growth
            noise = random.uniform(0.8, 1.2)

            if cumulative:
                value = int(base_value * growth_factor + (week * 5))
            else:
                value = int(base_value * growth_factor * noise)

            data_points.append((current_date, value))
            current_date += timedelta(days=7)

        return data_points

    def _calculate_health_score(
        self,
        quality_predictions: List[QualityPrediction],
        completeness_predictions: List[CompletenesPrediction],
        usage_predictions: List[UsagePrediction],
    ) -> float:
        """Calculate overall repository health score."""
        scores = []

        # Quality score (30% weight)
        if quality_predictions:
            quality_scores = [
                p.predicted_value
                for p in quality_predictions
                if p.prediction_timeframe == "1_month"
            ]
            if quality_scores:
                scores.append(statistics.mean(quality_scores) * 0.3)

        # Completeness score (40% weight)
        if completeness_predictions:
            high_priority_completeness = [
                p.predicted_completion_rate
                for p in completeness_predictions
                if p.priority_level == "high" and p.prediction_timeframe == "1_month"
            ]
            if high_priority_completeness:
                scores.append(statistics.mean(high_priority_completeness) * 0.4)

        # Usage trend score (30% weight)
        if usage_predictions:
            growth_scores = []
            for p in usage_predictions:
                if p.prediction_timeframe == "1_month":
                    growth_rate = (
                        (p.predicted_value - p.current_value) / p.current_value
                        if p.current_value > 0
                        else 0
                    )
                    # Normalize growth rate to 0-1 scale
                    normalized_growth = min(1.0, max(0.0, (growth_rate + 0.1) / 0.2))
                    growth_scores.append(normalized_growth)
            if growth_scores:
                scores.append(statistics.mean(growth_scores) * 0.3)

        return sum(scores) if scores else 0.5

    def _generate_key_insights(
        self,
        quality_predictions: List[QualityPrediction],
        completeness_predictions: List[CompletenesPrediction],
        usage_predictions: List[UsagePrediction],
    ) -> List[str]:
        """Generate key insights from predictions."""
        insights = []

        # Quality insights
        declining_quality = [
            p for p in quality_predictions if p.trend_direction == "declining"
        ]
        if declining_quality:
            insights.append(
                f"Quality decline detected in {len(declining_quality)} metrics"
            )

        # Completeness insights
        low_completeness = [
            p
            for p in completeness_predictions
            if p.predicted_completion_rate < 0.7 and p.priority_level == "high"
        ]
        if low_completeness:
            insights.append(
                f"{len(low_completeness)} high-priority fields show low completion rates"
            )

        # Usage insights
        high_growth = [
            p
            for p in usage_predictions
            if (p.predicted_value - p.current_value) / max(p.current_value, 1) > 0.5
        ]
        if high_growth:
            insights.append(
                f"High growth predicted for {len(high_growth)} usage metrics"
            )

        # Cross-cutting insights
        if len(insights) == 0:
            insights.append(
                "Repository metrics show stable patterns with no critical issues predicted"
            )

        return insights

    def _generate_strategic_recommendations(
        self,
        quality_predictions: List[QualityPrediction],
        completeness_predictions: List[CompletenesPrediction],
        usage_predictions: List[UsagePrediction],
        health_score: float,
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        # Health-based recommendations
        if health_score < 0.6:
            recommendations.append(
                "Implement comprehensive metadata quality improvement program"
            )
        elif health_score < 0.8:
            recommendations.append(
                "Focus on targeted improvements in underperforming areas"
            )

        # Specific recommendations based on predictions
        critical_quality = [
            p
            for p in quality_predictions
            if p.trend_direction == "declining" and p.confidence > 0.7
        ]
        if critical_quality:
            recommendations.append(
                "Address declining quality trends before they impact repository value"
            )

        capacity_issues = [
            p
            for p in usage_predictions
            if (p.predicted_value / max(p.current_value, 1)) > 2.0
        ]
        if capacity_issues:
            recommendations.append("Plan infrastructure scaling for predicted growth")

        # Long-term strategic recommendations
        recommendations.append(
            "Establish regular predictive analysis cycles for proactive management"
        )
        recommendations.append(
            "Implement automated monitoring for early trend detection"
        )

        return recommendations

    def _assess_data_quality(
        self, historical_data: Dict[str, Dict[str, List]]
    ) -> float:
        """Assess quality of historical data used for predictions."""
        total_metrics = 0
        adequate_metrics = 0

        for category, metrics in historical_data.items():
            for metric_name, data_points in metrics.items():
                total_metrics += 1
                if len(data_points) >= self.min_data_points:
                    adequate_metrics += 1

        return adequate_metrics / total_metrics if total_metrics > 0 else 0.0


# Factory function
def create_predictive_analytics(
    user_client: NakalaUserInfoClient, cache_dir: str = None
) -> PredictiveAnalyticsEngine:
    """Create predictive analytics engine with dependencies."""
    return PredictiveAnalyticsEngine(user_client, cache_dir)
