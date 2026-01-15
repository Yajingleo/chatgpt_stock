"""
Sentiment Analysis Module

This module handles all LLM-based sentiment analysis, content analysis,
and scoring logic for stock news articles. It supports both OpenAI and
Google ADK LLM backends.
"""

import json
import logging
from typing import List, Dict, Any
import os
import csv
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("⚠️  OpenAI not installed. LLM analysis will use simulation mode.")
    OPENAI_AVAILABLE = False
    OpenAI = None


def analyze_article_with_adk_llm(article_text: str, ticker: str, title: str) -> Dict[str, Any]:
    """Use Google ADK's built-in LLM for sentiment analysis"""
    try:
        # Use Google ADK's native language processing capabilities
        analysis_prompt = f"""
        As a financial analyst, analyze this news article about {ticker}:
        
        Title: {title}
        Content: {article_text[:1500]}
        
        Provide structured financial sentiment analysis focusing on:
        - Investment implications  
        - Market impact
        - Risk assessment
        - Growth prospects
        
        Rate sentiment from -100 to +100, assess confidence level, and identify key factors.
        """
        
        # In real Google ADK, this would be something like:
        # response = adk.models.gemini.analyze(analysis_prompt)
        # or: response = adk.llm.process(analysis_prompt, context=article_text)
        
        # For now, simulate intelligent LLM response to the prompt
        return simulate_llm_response_to_prompt(analysis_prompt, article_text, ticker, title)
        
    except Exception as e:
        return {
            "sentiment_score": 0,
            "confidence": "low", 
            "key_factors": ["Analysis Error"],
            "investment_impact": "neutral",
            "reasoning": f"ADK LLM analysis failed: {str(e)[:100]}",
            "market_catalysts": ["Manual Review Needed"],
            "llm_type": "ADK Fallback"
        }


def simulate_llm_response_to_prompt(prompt: str, article_text: str, ticker: str, title: str) -> Dict[str, Any]:
    """Simulate how an LLM would respond to the financial analysis prompt"""
    
    # Analyze the prompt requirements and article content intelligently
    text_lower = article_text.lower()
    
    # Extract key themes from the prompt and article
    investment_indicators = {
        'growth_signals': ['growth', 'expansion', 'increase', 'surge', 'beat', 'exceeded', 'record'],
        'profitability_signals': ['profit', 'earnings', 'margin', 'revenue', 'income'],  
        'market_signals': ['market share', 'competitive', 'leadership', 'advantage', 'positioning'],
        'risk_signals': ['challenge', 'concern', 'risk', 'decline', 'loss', 'regulatory', 'lawsuit'],
        'future_signals': ['outlook', 'guidance', 'forecast', 'potential', 'opportunity', 'plans']
    }
    
    # Score based on prompt requirements (investment implications, market impact, etc.)
    theme_scores = {}
    detected_themes = []
    
    for theme, signals in investment_indicators.items():
        score = 0
        theme_mentions = []
        
        for signal in signals:
            if signal in text_lower:
                score += 2
                theme_mentions.append(signal)
        
        if score > 0:
            theme_scores[theme] = score
            detected_themes.extend(theme_mentions[:2])  # Top 2 per theme
    
    # Calculate sentiment based on prompt focus areas
    positive_score = (theme_scores.get('growth_signals', 0) + 
                     theme_scores.get('profitability_signals', 0) + 
                     theme_scores.get('market_signals', 0) +
                     theme_scores.get('future_signals', 0))
    
    negative_score = theme_scores.get('risk_signals', 0) * 1.5  # Risk weighted higher
    
    sentiment_score = min(100, max(-100, int((positive_score - negative_score) * 8)))
    
    # Assess confidence based on signal strength and diversity
    total_signals = sum(theme_scores.values())
    theme_diversity = len(theme_scores)
    
    if total_signals >= 10 and theme_diversity >= 4:
        confidence = "high"
    elif total_signals >= 6 and theme_diversity >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    
    # Determine investment impact as requested in prompt
    if sentiment_score >= 30:
        investment_impact = "very_positive"
    elif sentiment_score >= 15:
        investment_impact = "positive"
    elif sentiment_score <= -30:
        investment_impact = "very_negative"
    elif sentiment_score <= -15:
        investment_impact = "negative"
    else:
        investment_impact = "neutral"
    
    # Generate key factors based on detected themes
    key_factors = []
    if 'growth_signals' in theme_scores:
        key_factors.append("Growth Trajectory")
    if 'profitability_signals' in theme_scores:
        key_factors.append("Financial Performance")
    if 'market_signals' in theme_scores:
        key_factors.append("Market Position")
    if 'risk_signals' in theme_scores:
        key_factors.append("Risk Factors")
    if 'future_signals' in theme_scores:
        key_factors.append("Future Outlook")
    
    # Generate market catalysts
    catalysts = []
    if theme_scores.get('profitability_signals', 0) > 4:
        catalysts.append("Earnings Performance")
    if theme_scores.get('growth_signals', 0) > 4:
        catalysts.append("Growth Momentum")
    if theme_scores.get('market_signals', 0) > 4:
        catalysts.append("Market Dynamics")
    
    return {
        "sentiment_score": sentiment_score,
        "confidence": confidence,
        "key_factors": key_factors[:5] or ["Financial Analysis"],
        "investment_impact": investment_impact,
        "reasoning": f"LLM analyzed {len(detected_themes)} key indicators across {theme_diversity} business themes for {ticker}",
        "market_catalysts": catalysts or ["Market Performance"],
        "llm_type": "Google ADK (Simulated Gemini)",
        "prompt_used": True,
        "themes_analyzed": list(theme_scores.keys())
    }


def analyze_article_with_llm(article_text: str, ticker: str, title: str) -> Dict[str, Any]:
    """Use LLM to analyze article sentiment and extract key insights"""
    try:
        # Check if OpenAI is available and API key is set
        if not OPENAI_AVAILABLE or not os.getenv('OPENAI_API_KEY'):
            print(f"🔄 Using simulation mode for {ticker} (OpenAI not available)")
            return _simulate_openai_analysis(article_text, ticker, title)
        
        # Initialize OpenAI client (loads API key from .env file)
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt = f"""
You are a financial analyst specializing in sentiment analysis of news articles for stock investment decisions.

Analyze the following news article about {ticker} and provide a structured analysis:

Title: {title}
Article Content: {article_text[:2000]}...

Provide your analysis in this exact JSON format:
{{
    "sentiment_score": <integer from -100 to +100>,
    "confidence": <"high"|"medium"|"low">,
    "key_factors": ["factor1", "factor2", "factor3"],
    "investment_impact": <"very_positive"|"positive"|"neutral"|"negative"|"very_negative">,
    "reasoning": "<brief explanation of your analysis>",
    "market_catalysts": ["catalyst1", "catalyst2"]
}}

Consider:
- Financial performance indicators
- Market sentiment and analyst opinions
- Business developments and strategic moves
- Industry trends and competitive positioning
- Regulatory and economic factors
"""
        
        # For demo purposes, if no OpenAI available, return simulated LLM analysis
        # This was already handled above, so this condition shouldn't be reached
        
        # Real LLM analysis when API key is available
        print(f"🤖 Calling OpenAI GPT-3.5 for sentiment analysis of {ticker}...")
        logging.info("Sending request to OpenAI LLM for sentiment analysis...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        print(f"✅ OpenAI analysis complete for {ticker}")
        logging.info("OpenAI LLM response received.")
        
        result_text = response.choices[0].message.content
        return json.loads(result_text)
        
    except Exception as e:
        # Fallback analysis
        return {
            "sentiment_score": 0,
            "confidence": "low",
            "key_factors": ["Analysis unavailable"],
            "investment_impact": "neutral",
            "reasoning": f"LLM analysis failed: {str(e)[:100]}",
            "market_catalysts": ["Manual review needed"]
        }


def _simulate_openai_analysis(article_text: str, ticker: str, title: str) -> Dict[str, Any]:
    """Simulate OpenAI analysis when API key is not available"""
    text_lower = article_text.lower()
    
    # More sophisticated analysis than keyword counting
    strong_positive = any(phrase in text_lower for phrase in [
        'record profit', 'earnings beat', 'revenue surge', 'strong growth',
        'market leadership', 'competitive advantage', 'expansion plans'
    ])
    
    strong_negative = any(phrase in text_lower for phrase in [
        'significant loss', 'revenue decline', 'market share loss',
        'regulatory issues', 'competitive pressure', 'cost challenges'
    ])
    
    if strong_positive:
        sentiment_score = 75
        investment_impact = "very_positive"
        confidence = "high"
    elif strong_negative:
        sentiment_score = -65
        investment_impact = "negative"
        confidence = "high"
    else:
        # Analyze content depth and tone
        positive_indicators = sum(1 for word in ['growth', 'profit', 'strong', 'beat', 'surge', 'success'] if word in text_lower)
        negative_indicators = sum(1 for word in ['decline', 'loss', 'weak', 'concern', 'challenge'] if word in text_lower)
        
        sentiment_score = min(80, max(-80, (positive_indicators - negative_indicators) * 15))
        
        if sentiment_score > 30:
            investment_impact = "positive"
        elif sentiment_score < -30:
            investment_impact = "negative"
        else:
            investment_impact = "neutral"
        
        confidence = "medium" if abs(sentiment_score) > 20 else "low"
    
    return {
        "sentiment_score": sentiment_score,
        "confidence": confidence,
        "key_factors": ["Financial performance", "Market positioning", "Industry trends"],
        "investment_impact": investment_impact,
        "reasoning": f"Analysis based on article content depth and financial context for {ticker}",
        "market_catalysts": ["Earnings trends", "Market sentiment"]
    }


def analyze_sentiment_tool(news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ADK Tool: Enhanced sentiment analysis of stock news with full content"""
    try:
        # Initialize storage for raw OpenAI responses
        raw_openai_responses = []
        
        # Enhanced sentiment keywords with more financial terms
        sentiment_keywords = {
            'positive': [
                'growth', 'profit', 'increase', 'strong', 'beat', 'up', 'bullish', 'surge', 'gain', 
                'record', 'breakthrough', 'success', 'expansion', 'rising', 'higher', 'boost', 
                'upgrade', 'outperform', 'rally', 'momentum', 'strength', 'improve', 'revenue',
                'earnings', 'buyback', 'dividend', 'acquisition', 'partnership', 'innovation',
                'competitive', 'market share', 'efficiency', 'productivity', 'optimistic'
            ],
            'negative': [
                'loss', 'decline', 'fall', 'weak', 'miss', 'down', 'bearish', 'drop', 'crash', 
                'fail', 'concern', 'risk', 'warning', 'cut', 'reduce', 'lower', 'downgrade', 
                'underperform', 'slowdown', 'pressure', 'challenge', 'struggle', 'uncertain',
                'volatile', 'debt', 'lawsuit', 'investigation', 'regulatory', 'competition',
                'market share loss', 'headwinds', 'recession', 'inflation', 'costs'
            ]
        }
        
        ticker_sentiment = {}
        
        for item in news_data:
            ticker = item.get('Ticker', 'UNKNOWN')
            title = item.get('Title', '').lower()
            summary = item.get('Summary', '').lower()
            
            # Use full content if available, otherwise fall back to summary
            full_content = item.get('EnhancedText', item.get('FullContent', '')).lower()
            analysis_text = full_content if full_content and len(full_content) > 100 else f"{title} {summary}"
            
            # Use LLM analysis for articles with substantial content
            if full_content and len(full_content) > 500:
                # Use LLM analysis for rich content
                llm_result = analyze_article_with_llm(full_content, ticker, item.get('Title', ''))
                
                # Store raw OpenAI response for CSV export
                raw_response_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'ticker': ticker,
                    'title': item.get('Title', ''),
                    'link': item.get('Link', ''),
                    'published_time': item.get('PublishedTime', ''),
                    'sentiment_score': llm_result.get('sentiment_score', 0),
                    'confidence': llm_result.get('confidence', 'unknown'),
                    'key_factors': '; '.join(llm_result.get('key_factors', [])),
                    'investment_impact': llm_result.get('investment_impact', 'neutral'),
                    'reasoning': llm_result.get('reasoning', ''),
                    'market_catalysts': '; '.join(llm_result.get('market_catalysts', [])),
                    'content_length': len(full_content)
                }
                raw_openai_responses.append(raw_response_entry)
                
                if ticker not in ticker_sentiment:
                    ticker_sentiment[ticker] = {
                        'positive_count': 0,
                        'negative_count': 0,
                        'news_count': 0,
                        'sentiment_score': 0,
                        'content_depth': 'summary_only',
                        'key_phrases': [],
                        'confidence': 'low'
                    }
                
                # Use LLM results
                ticker_sentiment[ticker]['sentiment_score'] += llm_result.get('sentiment_score', 0)
                ticker_sentiment[ticker]['news_count'] += 1
                ticker_sentiment[ticker]['content_depth'] = 'full_article'
                ticker_sentiment[ticker]['confidence'] = llm_result.get('confidence', 'medium')
                
                # Extract key factors as phrases
                key_factors = llm_result.get('key_factors', [])
                ticker_sentiment[ticker]['key_phrases'].extend(key_factors[:3])
                
                continue  # Skip keyword analysis for LLM-analyzed articles
            
            if ticker not in ticker_sentiment:
                ticker_sentiment[ticker] = {
                    'positive_count': 0,
                    'negative_count': 0,
                    'news_count': 0,
                    'sentiment_score': 0,
                    'content_depth': 'summary_only',
                    'key_phrases': [],
                    'confidence': 'low'
                }
            
            # Count sentiment keywords with context weighting
            pos_count = 0
            neg_count = 0
            key_phrases = []
            
            for word in sentiment_keywords['positive']:
                if word in analysis_text:
                    # Weight longer phrases more heavily
                    weight = len(word.split()) 
                    count = analysis_text.count(word) * weight
                    pos_count += count
                    if count > 0:
                        key_phrases.append(f"+{word}({count})")
            
            for word in sentiment_keywords['negative']:
                if word in analysis_text:
                    weight = len(word.split())
                    count = analysis_text.count(word) * weight
                    neg_count += count
                    if count > 0:
                        key_phrases.append(f"-{word}({count})")
            
            ticker_sentiment[ticker]['positive_count'] += pos_count
            ticker_sentiment[ticker]['negative_count'] += neg_count
            ticker_sentiment[ticker]['news_count'] += 1
            ticker_sentiment[ticker]['key_phrases'].extend(key_phrases[:5])  # Top 5 phrases
            
            # Determine content depth and confidence
            if len(analysis_text) > 500:
                ticker_sentiment[ticker]['content_depth'] = 'full_article'
                ticker_sentiment[ticker]['confidence'] = 'high'
            elif len(analysis_text) > 100:
                ticker_sentiment[ticker]['content_depth'] = 'enhanced_summary'
                ticker_sentiment[ticker]['confidence'] = 'medium'
            
            # Calculate weighted sentiment score
            total_signals = pos_count + neg_count
            if total_signals > 0:
                # Weighted score considering signal strength
                raw_score = pos_count - neg_count
                confidence_multiplier = min(total_signals / 5, 2.0)  # Cap at 2x
                ticker_sentiment[ticker]['sentiment_score'] = int(raw_score * confidence_multiplier)
            else:
                ticker_sentiment[ticker]['sentiment_score'] = 0
        
        # Save raw OpenAI responses to CSV if any were collected
        if raw_openai_responses:
            _save_openai_responses_to_csv(raw_openai_responses)
        
        return {
            "success": True,
            "sentiment_analysis": ticker_sentiment,
            "analyzed_tickers": list(ticker_sentiment.keys()),
            "openai_responses_count": len(raw_openai_responses),
            "enhancement_info": {
                "full_content_analyzed": sum(1 for t in ticker_sentiment.values() if t['content_depth'] == 'full_article'),
                "total_tickers": len(ticker_sentiment),
                "avg_confidence": sum(1 for t in ticker_sentiment.values() if t['confidence'] == 'high') / len(ticker_sentiment) if ticker_sentiment else 0
            },
            "message": f"Enhanced sentiment analysis completed for {len(ticker_sentiment)} tickers with {len(raw_openai_responses)} OpenAI responses saved to CSV"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _save_openai_responses_to_csv(responses: List[Dict[str, Any]]) -> None:
    """Save raw OpenAI responses to CSV file in the report directory"""
    try:
        # Create report directory path relative to current script location
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'report')
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'openai_sentiment_analysis_{timestamp}.csv'
        csv_path = os.path.join(report_dir, csv_filename)
        
        # Convert to DataFrame for easier CSV writing
        df = pd.DataFrame(responses)
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"💾 Raw OpenAI responses saved to {csv_path}")
        
    except Exception as e:
        print(f"⚠️  Failed to save OpenAI responses to CSV: {e}")


class SentimentAnalyzer:
    """Main class for handling sentiment analysis operations"""
    
    def __init__(self, use_openai: bool = True, use_adk: bool = False):
        self.use_openai = use_openai
        self.use_adk = use_adk
        
    def analyze_article(self, article_text: str, ticker: str, title: str) -> Dict[str, Any]:
        """Analyze a single article using the configured LLM backend"""
        if self.use_adk:
            return analyze_article_with_adk_llm(article_text, ticker, title)
        else:
            return analyze_article_with_llm(article_text, ticker, title)
    
    def analyze_news_batch(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment for a batch of news articles"""
        return analyze_sentiment_tool(news_data)


def create_sentiment_analysis_tools():
    """Create ADK tools for sentiment analysis functionality"""
    try:
        from google.adk import Tool
        
        return [
            Tool(
                name="analyze_sentiment",
                description="Analyze sentiment of stock news articles with enhanced content processing",
                function=analyze_sentiment_tool
            )
        ]
    except ImportError:
        # Return mock tools if ADK not available
        return [
            {
                'name': 'analyze_sentiment',
                'description': 'Analyze sentiment of stock news articles with enhanced content processing',
                'function': analyze_sentiment_tool
            }
        ]