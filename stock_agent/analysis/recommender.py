"""
Stock Recommendation Engine Module

This module handles the generation of investment recommendations based on
sentiment analysis and other market factors. It provides tools for creating
buy/sell/hold recommendations with confidence levels and reasoning.

Uses configurable thresholds for buy/sell signals.
"""

from typing import List, Dict, Any, Optional

from stock_agent.config import settings, MAX_KEY_PHRASES, MAX_INSIGHTS
from stock_agent.data.sp500_analyzer import SP500StockAnalyzer


def get_sp500_recommendations_tool(lookback_days: Optional[int] = None) -> Dict[str, Any]:
    """
    ADK Tool: Get S&P 500 stock recommendations.

    Args:
        lookback_days: Days to look back for analysis. Defaults to config value.

    Returns:
        Dictionary with recommended tickers
    """
    lookback_days = lookback_days or settings.analysis.lookback_days

    try:
        analyzer = SP500StockAnalyzer()
        analyzer.analyze_stocks(lookback_days=lookback_days)
        tickers = analyzer.get_recommanded_tickers()
        return {
            "success": True,
            "tickers": tickers,
            "count": len(tickers),
            "message": f"Retrieved {len(tickers)} recommended tickers"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_recommendations_tool(sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    ADK Tool: Generate stock recommendations based on sentiment.

    Args:
        sentiment_analysis: Dictionary of ticker -> analysis data

    Returns:
        Dictionary with recommendations and quality metrics
    """
    # Get thresholds from config
    buy_threshold = settings.analysis.buy_threshold
    sell_threshold = settings.analysis.sell_threshold
    high_buy = settings.analysis.high_confidence_buy
    high_sell = settings.analysis.high_confidence_sell
    min_news = settings.analysis.min_news_count

    try:
        recommendations = []

        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            news_count = analysis['news_count']
            content_depth = analysis.get('content_depth', 'summary_only')
            confidence_level = analysis.get('confidence', 'low')

            # Generate recommendation based on sentiment score and news volume
            if score >= buy_threshold and news_count >= min_news:
                action = "BUY"
                confidence = "HIGH" if score >= high_buy else "MEDIUM"
                reason = f"Strong positive sentiment (score: {score}, {news_count} news items)"
            elif score <= sell_threshold and news_count >= min_news:
                action = "SELL"
                confidence = "HIGH" if score <= high_sell else "MEDIUM"
                reason = f"Strong negative sentiment (score: {score}, {news_count} news items)"
            else:
                action = "HOLD"
                confidence = "LOW"
                reason = f"Neutral/mixed sentiment (score: {score}, {news_count} news items)"

            # Adjust confidence based on content depth
            if content_depth == 'full_article' and confidence_level == 'high':
                confidence = confidence  # Keep original confidence
            elif content_depth == 'summary_only':
                confidence = "LOW"  # Reduce confidence for summary-only analysis

            recommendation = {
                "ticker": ticker,
                "action": action,
                "confidence": confidence,
                "sentiment_score": score,
                "news_count": news_count,
                "reason": reason,
                "content_depth": content_depth,
                "confidence_level": confidence_level
            }

            # Add key phrases and insights if available
            if 'key_phrases' in analysis:
                recommendation['key_phrases'] = analysis['key_phrases'][:MAX_KEY_PHRASES]

            if 'insights' in analysis:
                recommendation['insights'] = analysis['insights']

            recommendations.append(recommendation)

        # Sort by absolute sentiment score (strongest signals first)
        recommendations.sort(key=lambda x: abs(x['sentiment_score']), reverse=True)

        # Calculate quality metrics
        analysis_quality = _calculate_analysis_quality(recommendations)

        return {
            "success": True,
            "recommendations": recommendations,
            "total_analyzed": len(recommendations),
            "analysis_quality": analysis_quality,
            "message": f"Generated {len(recommendations)} recommendations"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _calculate_analysis_quality(recommendations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate quality metrics for the analysis."""
    quality_metrics = {
        'full_articles': 0,
        'enhanced_summaries': 0,
        'summary_only': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0
    }

    for rec in recommendations:
        # Count content depth
        content_depth = rec.get('content_depth', 'summary_only')
        if content_depth == 'full_article':
            quality_metrics['full_articles'] += 1
        elif content_depth == 'enhanced_summary':
            quality_metrics['enhanced_summaries'] += 1
        else:
            quality_metrics['summary_only'] += 1

        # Count confidence levels
        confidence = rec.get('confidence', 'LOW').lower()
        if confidence == 'high':
            quality_metrics['high_confidence'] += 1
        elif confidence == 'medium':
            quality_metrics['medium_confidence'] += 1
        else:
            quality_metrics['low_confidence'] += 1

    return quality_metrics


def generate_advanced_recommendations(
    sentiment_analysis: Dict[str, Any],
    market_context: Dict[str, Any] = None,
    risk_tolerance: str = "moderate"
) -> Dict[str, Any]:
    """
    Generate more sophisticated recommendations with additional context.

    Args:
        sentiment_analysis: Dictionary of ticker -> analysis data
        market_context: Optional market context data
        risk_tolerance: Risk tolerance level (conservative/moderate/aggressive)

    Returns:
        Dictionary with advanced recommendations
    """
    try:
        recommendations = []

        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            news_count = analysis['news_count']
            content_depth = analysis.get('content_depth', 'summary_only')
            confidence_level = analysis.get('confidence', 'low')
            key_phrases = analysis.get('key_phrases', [])

            # Base recommendation logic
            base_recommendation = _generate_base_recommendation(score, news_count, confidence_level)

            # Adjust for risk tolerance
            adjusted_recommendation = _adjust_for_risk_tolerance(
                base_recommendation, score, risk_tolerance
            )

            # Generate insights based on key phrases
            insights = _generate_insights_from_phrases(key_phrases)

            recommendation = {
                "ticker": ticker,
                "action": adjusted_recommendation['action'],
                "confidence": adjusted_recommendation['confidence'],
                "sentiment_score": score,
                "news_count": news_count,
                "reason": adjusted_recommendation['reason'],
                "content_depth": content_depth,
                "confidence_level": confidence_level,
                "key_phrases": key_phrases[:MAX_KEY_PHRASES],
                "insights": insights,
                "risk_adjusted": adjusted_recommendation.get('risk_adjusted', False)
            }

            recommendations.append(recommendation)

        # Sort by score and confidence
        recommendations.sort(key=lambda x: (abs(x['sentiment_score']), x['news_count']), reverse=True)

        analysis_quality = _calculate_analysis_quality(recommendations)

        return {
            "success": True,
            "recommendations": recommendations,
            "total_analyzed": len(recommendations),
            "analysis_quality": analysis_quality,
            "risk_tolerance": risk_tolerance,
            "message": f"Generated {len(recommendations)} advanced recommendations"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _generate_base_recommendation(score: int, news_count: int, confidence_level: str) -> Dict[str, Any]:
    """Generate base recommendation without risk adjustments."""
    buy_threshold = settings.analysis.buy_threshold
    sell_threshold = settings.analysis.sell_threshold
    high_buy = settings.analysis.high_confidence_buy
    high_sell = settings.analysis.high_confidence_sell
    min_news = settings.analysis.min_news_count

    if score >= buy_threshold and news_count >= min_news:
        return {
            "action": "BUY",
            "confidence": "HIGH" if score >= high_buy else "MEDIUM",
            "reason": f"Strong positive sentiment (score: {score}, {news_count} news items)"
        }
    elif score <= sell_threshold and news_count >= min_news:
        return {
            "action": "SELL",
            "confidence": "HIGH" if score <= high_sell else "MEDIUM",
            "reason": f"Strong negative sentiment (score: {score}, {news_count} news items)"
        }
    else:
        return {
            "action": "HOLD",
            "confidence": "LOW",
            "reason": f"Neutral/mixed sentiment (score: {score}, {news_count} news items)"
        }


def _adjust_for_risk_tolerance(base_rec: Dict[str, Any], score: int, risk_tolerance: str) -> Dict[str, Any]:
    """Adjust recommendations based on risk tolerance."""
    adjusted = base_rec.copy()

    if risk_tolerance == "conservative":
        # More conservative approach
        if base_rec["action"] == "BUY" and abs(score) < 10:
            adjusted["action"] = "HOLD"
            adjusted["confidence"] = "LOW"
            adjusted["reason"] += " (adjusted for conservative risk tolerance)"
            adjusted["risk_adjusted"] = True
        elif base_rec["action"] == "SELL" and abs(score) < 8:
            adjusted["action"] = "HOLD"
            adjusted["confidence"] = "LOW"
            adjusted["reason"] += " (adjusted for conservative risk tolerance)"
            adjusted["risk_adjusted"] = True

    elif risk_tolerance == "aggressive":
        # More aggressive approach
        if base_rec["action"] == "HOLD" and abs(score) >= 2:
            if score > 0:
                adjusted["action"] = "BUY"
                adjusted["confidence"] = "MEDIUM"
            else:
                adjusted["action"] = "SELL"
                adjusted["confidence"] = "MEDIUM"
            adjusted["reason"] += " (adjusted for aggressive risk tolerance)"
            adjusted["risk_adjusted"] = True

    return adjusted


def _generate_insights_from_phrases(key_phrases: List[str]) -> List[str]:
    """Generate insights based on key sentiment phrases."""
    insights = []

    positive_phrases = [p for p in key_phrases if p.startswith('+')]
    negative_phrases = [p for p in key_phrases if p.startswith('-')]

    if len(positive_phrases) > len(negative_phrases):
        insights.append("Predominantly positive market sentiment")
    elif len(negative_phrases) > len(positive_phrases):
        insights.append("Concerning negative indicators present")

    # Look for specific financial themes
    financial_terms = ['profit', 'earnings', 'revenue', 'growth']
    if any(term in ' '.join(key_phrases).lower() for term in financial_terms):
        insights.append("Financial performance indicators detected")

    risk_terms = ['risk', 'concern', 'challenge', 'decline']
    if any(term in ' '.join(key_phrases).lower() for term in risk_terms):
        insights.append("Risk factors identified in analysis")

    return insights[:MAX_INSIGHTS]


class StockRecommender:
    """Main class for generating stock recommendations."""

    def __init__(self, risk_tolerance: str = "moderate"):
        """
        Initialize the recommender.

        Args:
            risk_tolerance: Risk tolerance level (conservative/moderate/aggressive)
        """
        self.risk_tolerance = risk_tolerance

    def generate_recommendations(
        self,
        sentiment_analysis: Dict[str, Any],
        use_advanced: bool = False
    ) -> Dict[str, Any]:
        """
        Generate recommendations from sentiment analysis.

        Args:
            sentiment_analysis: Dictionary of ticker -> analysis data
            use_advanced: Whether to use advanced recommendation logic

        Returns:
            Dictionary with recommendations
        """
        if use_advanced:
            return generate_advanced_recommendations(
                sentiment_analysis,
                risk_tolerance=self.risk_tolerance
            )
        else:
            return generate_recommendations_tool(sentiment_analysis)

    def get_sp500_recommendations(self, lookback_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Get S&P 500 stock recommendations.

        Args:
            lookback_days: Days to look back for analysis. Defaults to config value.

        Returns:
            Dictionary with recommended tickers
        """
        return get_sp500_recommendations_tool(lookback_days)


def create_recommendation_tools():
    """Create ADK tools for recommendation functionality."""
    try:
        from google.adk import Tool

        return [
            Tool(
                name="get_sp500_recommendations",
                description="Get recommended S&P 500 stock tickers based on technical analysis",
                function=get_sp500_recommendations_tool
            ),
            Tool(
                name="generate_recommendations",
                description="Generate buy/sell/hold recommendations based on sentiment analysis",
                function=generate_recommendations_tool
            )
        ]
    except ImportError:
        # Return mock tools if ADK not available
        return [
            {
                'name': 'get_sp500_recommendations',
                'description': 'Get recommended S&P 500 stock tickers based on technical analysis',
                'function': get_sp500_recommendations_tool
            },
            {
                'name': 'generate_recommendations',
                'description': 'Generate buy/sell/hold recommendations based on sentiment analysis',
                'function': generate_recommendations_tool
            }
        ]
