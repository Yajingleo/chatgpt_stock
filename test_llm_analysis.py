#!/usr/bin/env python3
"""
Test script to demonstrate LLM-powered sentiment analysis
"""

# Simple simulation of LLM analysis without external dependencies
def simulate_llm_analysis(article_text: str, ticker: str) -> dict:
    """Simulate intelligent LLM analysis of financial news"""
    
    # More sophisticated analysis than simple keyword counting
    text_lower = article_text.lower()
    
    # Context-aware positive signals
    strong_positive_signals = [
        'record earnings', 'beats expectations', 'revenue surge', 'strong growth',
        'market leader', 'competitive advantage', 'expansion success', 'record profit',
        'upgraded by analysts', 'strategic partnership', 'breakthrough innovation'
    ]
    
    # Context-aware negative signals
    strong_negative_signals = [
        'significant loss', 'revenue decline', 'missing earnings', 'market share loss',
        'regulatory investigation', 'competitive pressure', 'cost overruns', 'downgraded',
        'lawsuit filed', 'management turnover', 'debt concerns'
    ]
    
    # Financial performance indicators
    financial_positive = ['profit', 'earnings', 'revenue up', 'growth', 'dividend', 'buyback']
    financial_negative = ['loss', 'debt', 'bankruptcy', 'layoffs', 'restructuring', 'writedown']
    
    # Market sentiment indicators  
    sentiment_positive = ['bullish', 'optimistic', 'confident', 'surge', 'rally', 'momentum']
    sentiment_negative = ['bearish', 'pessimistic', 'concern', 'volatile', 'uncertainty', 'risk']
    
    # Calculate weighted scores
    strong_pos_score = sum(5 for signal in strong_positive_signals if signal in text_lower)
    strong_neg_score = sum(5 for signal in strong_negative_signals if signal in text_lower)
    
    financial_pos_score = sum(3 for word in financial_positive if word in text_lower)
    financial_neg_score = sum(3 for word in financial_negative if word in text_lower)
    
    sentiment_pos_score = sum(2 for word in sentiment_positive if word in text_lower)
    sentiment_neg_score = sum(2 for word in sentiment_negative if word in text_lower)
    
    # Total weighted sentiment score
    total_positive = strong_pos_score + financial_pos_score + sentiment_pos_score
    total_negative = strong_neg_score + financial_neg_score + sentiment_neg_score
    
    sentiment_score = min(100, max(-100, total_positive - total_negative))
    
    # Determine investment impact and confidence
    if sentiment_score >= 15:
        investment_impact = "very_positive" if sentiment_score >= 25 else "positive"
        confidence = "high" if strong_pos_score > 0 else "medium"
    elif sentiment_score <= -15:
        investment_impact = "very_negative" if sentiment_score <= -25 else "negative"  
        confidence = "high" if strong_neg_score > 0 else "medium"
    else:
        investment_impact = "neutral"
        confidence = "low" if abs(sentiment_score) < 5 else "medium"
    
    # Generate key factors based on detected signals
    key_factors = []
    if any(signal in text_lower for signal in ['earnings', 'revenue', 'profit']):
        key_factors.append("Financial Performance")
    if any(signal in text_lower for signal in ['market', 'competition', 'industry']):
        key_factors.append("Market Position")
    if any(signal in text_lower for signal in ['growth', 'expansion', 'development']):
        key_factors.append("Business Growth")
    
    # Generate market catalysts
    catalysts = []
    if 'earnings' in text_lower:
        catalysts.append("Earnings Report")
    if any(word in text_lower for word in ['partnership', 'acquisition', 'deal']):
        catalysts.append("Strategic Moves")
    if any(word in text_lower for word in ['analyst', 'upgrade', 'rating']):
        catalysts.append("Analyst Coverage")
    
    return {
        "sentiment_score": sentiment_score,
        "confidence": confidence,
        "key_factors": key_factors or ["Financial Metrics"],
        "investment_impact": investment_impact,
        "reasoning": f"Intelligent analysis detected {total_positive} positive and {total_negative} negative signals in {ticker} news",
        "market_catalysts": catalysts or ["Market Trends"]
    }

# Test with sample financial news
if __name__ == "__main__":
    sample_articles = [
        {
            "ticker": "AAPL",
            "title": "Apple Reports Record Quarterly Revenue, Beats Analyst Expectations",
            "content": """Apple Inc. reported record quarterly revenue of $95.2 billion, beating Wall Street expectations by a significant margin. The company's strong growth was driven by iPhone sales surge and expanding services revenue. CEO Tim Cook expressed optimistic outlook for the next quarter, citing strong demand and competitive advantage in the premium smartphone market. Analysts upgraded the stock following the earnings beat."""
        },
        {
            "ticker": "NVDA", 
            "title": "Nvidia Faces Supply Chain Challenges, Regulatory Investigation",
            "content": """Nvidia Corp. is experiencing significant challenges with regulatory investigation into its AI chip exports and supply chain disruptions affecting production. The company warned of potential revenue decline in the next quarter due to these headwinds. Market share loss to competitors in certain segments has raised concerns among investors. Several analysts downgraded the stock citing regulatory risks and competitive pressure."""
        }
    ]
    
    print("🤖 LLM-Powered Financial News Analysis Demo")
    print("=" * 50)
    
    for article in sample_articles:
        print(f"\n📰 Analyzing: {article['ticker']}")
        print(f"Title: {article['title']}")
        
        result = simulate_llm_analysis(article['content'], article['ticker'])
        
        print(f"\n🧠 LLM Analysis Results:")
        print(f"   Sentiment Score: {result['sentiment_score']}")
        print(f"   Investment Impact: {result['investment_impact']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Key Factors: {', '.join(result['key_factors'])}")
        print(f"   Market Catalysts: {', '.join(result['market_catalysts'])}")
        print(f"   Reasoning: {result['reasoning']}")
        
        # Investment recommendation
        if result['investment_impact'] in ['very_positive', 'positive']:
            action = "BUY"
            emoji = "🟢📈"
        elif result['investment_impact'] in ['very_negative', 'negative']:
            action = "SELL"
            emoji = "🔴📉"
        else:
            action = "HOLD"
            emoji = "🟡➡️"
        
        print(f"   \n💡 Recommendation: {emoji} {action}")
        print("-" * 50)