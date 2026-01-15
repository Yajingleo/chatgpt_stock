#!/usr/bin/env python3
"""
Test OpenAI LLM integration for financial news analysis
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_analysis():
    """Test real OpenAI analysis with financial news"""
    
    # Sample financial news articles
    test_articles = [
        {
            "ticker": "AAPL",
            "title": "Apple Reports Record Revenue, Beats Expectations",
            "content": """Apple Inc. reported record quarterly revenue of $95.2 billion, surpassing Wall Street expectations by a significant margin. iPhone sales surged 12% year-over-year, while services revenue grew 16%. CEO Tim Cook expressed confidence in the company's AI strategy and upcoming product launches. Multiple analysts upgraded their price targets following the strong earnings report."""
        },
        {
            "ticker": "META",
            "title": "Meta Faces Regulatory Challenges, Revenue Concerns",
            "content": """Meta Platforms is facing increased regulatory scrutiny over its data practices and market dominance. The company warned of potential revenue headwinds due to privacy changes and increased competition from TikTok. Several key executives have departed recently, raising concerns about leadership stability. Advertising revenue declined 8% quarter-over-quarter."""
        }
    ]
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        return
        
    print(f"✅ OpenAI API key loaded: {api_key[:10]}...{api_key[-5:]}")
    print("\n🤖 Testing Real OpenAI LLM Analysis")
    print("=" * 50)
    
    try:
        client = OpenAI(api_key=api_key)
        
        for article in test_articles:
            print(f"\n📰 Analyzing: {article['ticker']} - {article['title']}")
            print("-" * 40)
            
            prompt = f"""
You are a professional financial analyst. Analyze this news article and provide a structured investment sentiment analysis.

Company: {article['ticker']}
Title: {article['title']}
Content: {article['content']}

Provide your analysis in JSON format:
{{
    "sentiment_score": <-100 to +100>,
    "confidence": <"high"|"medium"|"low">,
    "investment_impact": <"very_positive"|"positive"|"neutral"|"negative"|"very_negative">,
    "key_factors": ["factor1", "factor2", "factor3"],
    "reasoning": "<brief explanation>",
    "recommendation": <"BUY"|"HOLD"|"SELL">
}}

Focus on financial performance, market position, and future prospects.
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in stock sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            
            print(f"🧠 LLM Analysis Results:")
            print(f"   Sentiment Score: {analysis['sentiment_score']}")
            print(f"   Investment Impact: {analysis['investment_impact']}")
            print(f"   Confidence: {analysis['confidence']}")
            print(f"   Key Factors: {', '.join(analysis['key_factors'])}")
            print(f"   Recommendation: {analysis['recommendation']}")
            print(f"   Reasoning: {analysis['reasoning']}")
            
            # Visual recommendation
            if analysis['recommendation'] == 'BUY':
                print(f"   💡 Action: 🟢📈 {analysis['recommendation']}")
            elif analysis['recommendation'] == 'SELL':
                print(f"   💡 Action: 🔴📉 {analysis['recommendation']}")
            else:
                print(f"   💡 Action: 🟡➡️ {analysis['recommendation']}")
                
    except Exception as e:
        print(f"❌ Error with OpenAI API: {str(e)}")
        print("This could be due to:")
        print("- Invalid API key")
        print("- Network connection issues")
        print("- API rate limits")
        print("- Insufficient API credits")

if __name__ == "__main__":
    test_openai_analysis()