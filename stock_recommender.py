"""
Stock Recommendation Engine Module

This module handles the generation of investment recommendations based on 
sentiment analysis and other market factors. It provides tools for creating
buy/sell/hold recommendations with confidence levels and reasoning.
"""

import sys
import os
from typing import List, Dict, Any

# Import existing functionality
sys.path.append(os.path.join(os.path.dirname(__file__), 'stock_selection'))
from stock_selection.sp_500_energy import SP500StockAnalyzer


def get_sp500_recommendations_tool(lookback_days: int = 30) -> List[str]:
    """ADK Tool: Get S&P 500 stock recommendations"""
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
    """ADK Tool: Generate stock recommendations based on sentiment"""
    try:
        recommendations = []
        
        for ticker, analysis in sentiment_analysis.items():
            score = analysis['sentiment_score']
            news_count = analysis['news_count']
            content_depth = analysis.get('content_depth', 'summary_only')
            confidence_level = analysis.get('confidence', 'low')
            
            # Generate recommendation based on sentiment score and news volume
            if score >= 3 and news_count >= 2:
                action = "BUY"
                confidence = "HIGH" if score >= 5 else "MEDIUM"
                reason = f"Strong positive sentiment (score: {score}, {news_count} news items)"
            elif score <= -3 and news_count >= 2:
                action = "SELL"  
                confidence = "HIGH" if score <= -5 else "MEDIUM"
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
                recommendation['key_phrases'] = analysis['key_phrases'][:3]  # Top 3 phrases
            
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
    """Calculate quality metrics for the analysis"""
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


def generate_advanced_recommendations(sentiment_analysis: Dict[str, Any], 
                                    market_context: Dict[str, Any] = None,
                                    risk_tolerance: str = "moderate") -> Dict[str, Any]:
    """Generate more sophisticated recommendations with additional context"""
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
                "key_phrases": key_phrases[:3],
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
    """Generate base recommendation without risk adjustments"""
    if score >= 3 and news_count >= 2:
        return {
            "action": "BUY",
            "confidence": "HIGH" if score >= 5 else "MEDIUM",
            "reason": f"Strong positive sentiment (score: {score}, {news_count} news items)"
        }
    elif score <= -3 and news_count >= 2:
        return {
            "action": "SELL",
            "confidence": "HIGH" if score <= -5 else "MEDIUM",
            "reason": f"Strong negative sentiment (score: {score}, {news_count} news items)"
        }
    else:
        return {
            "action": "HOLD",
            "confidence": "LOW",
            "reason": f"Neutral/mixed sentiment (score: {score}, {news_count} news items)"
        }


def _adjust_for_risk_tolerance(base_rec: Dict[str, Any], score: int, risk_tolerance: str) -> Dict[str, Any]:
    """Adjust recommendations based on risk tolerance"""
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
    """Generate insights based on key sentiment phrases"""
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
    
    return insights[:3]  # Return top 3 insights


class StockRecommender:
    """Main class for generating stock recommendations"""
    
    def __init__(self, risk_tolerance: str = "moderate"):
        self.risk_tolerance = risk_tolerance
    
    def generate_recommendations(self, sentiment_analysis: Dict[str, Any], 
                               use_advanced: bool = False) -> Dict[str, Any]:
        """Generate recommendations from sentiment analysis"""
        if use_advanced:
            return generate_advanced_recommendations(
                sentiment_analysis, 
                risk_tolerance=self.risk_tolerance
            )
        else:
            return generate_recommendations_tool(sentiment_analysis)
    
    def get_sp500_recommendations(self, lookback_days: int = 30) -> Dict[str, Any]:
        """Get S&P 500 stock recommendations"""
        return get_sp500_recommendations_tool(lookback_days)


def create_recommendation_tools():
    """Create ADK tools for recommendation functionality"""
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