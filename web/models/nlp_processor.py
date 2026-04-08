"""Natural language processing for stock queries"""

import re
from typing import Dict, Any

# Import config if available
try:
    from stock_agent.config import settings, EXCLUDED_WORDS
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    settings = None
    EXCLUDED_WORDS = []


class NaturalLanguageProcessor:
    """Process natural language queries for stock analysis"""

    def __init__(self):
        self.patterns = {
            'analyze_stock': r'(?:analyze|analysis|look at|check|research)\s+(?:stock\s+)?([A-Z]{2,5})(?:\s+stock)?',
            'get_news': r'(?:news|recent news|latest news)\s+(?:about|for|on)\s+([A-Z]{2,5}|google|tesla|apple|microsoft|amazon)',
            'sentiment': r'(?:sentiment|feeling|mood)\s+(?:about|for|on)\s+([A-Z]{2,5})',
            'recommendations': r'(?:recommend|recommendation|suggestions?|advice|what should i buy|best stocks)',
            'portfolio': r'(?:portfolio|holdings|my stocks)',
            'market_overview': r'(?:market|overall|general|broad|how is.*market)\s*(?:overview|analysis|condition|doing|performing)',
            'help': r'(?:help|how|what can you do|commands|features|capabilities)',
            'conversational': r'(?:hello|hi|hey|thank|bye|goodbye|how are you)'
        }

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query and extract intent and entities"""
        query_lower = query.lower().strip()

        result = {
            'intent': 'general_analysis',
            'entities': {},
            'original_query': query,
            'confidence': 0.5
        }

        # Check for specific patterns with higher confidence
        for intent, pattern in self.patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                result['intent'] = intent
                result['confidence'] = 0.8

                if intent in ['analyze_stock', 'get_news', 'sentiment']:
                    result['entities']['ticker'] = match.group(1).upper()
                break

        # Extract multiple tickers if present (only likely stock tickers)
        ticker_matches = re.findall(r'\b([A-Z]{2,5})\b', query.upper())

        # Filter out common false positives and English words
        # Use constants if available, otherwise use fallback set
        if CONFIG_AVAILABLE:
            excluded_upper = {w.upper() for w in EXCLUDED_WORDS}
        else:
            excluded_upper = {
                'GET', 'THE', 'AND', 'FOR', 'ARE', 'CAN', 'YOU', 'HOW', 'WHY', 'WHAT', 'WHO', 'WHEN', 'WHERE',
                'THIS', 'THAT', 'BUT', 'NOT', 'ALL', 'ANY', 'HAS', 'HIS', 'HER', 'HAD', 'HIM', 'HAS', 'HER',
                'WAS', 'WERE', 'BEEN', 'HAVE', 'HELP', 'HELLO', 'THANK', 'THANKS', 'PLEASE', 'WILL', 'WOULD',
                'COULD', 'SHOULD', 'MIGHT', 'MUST', 'MAY', 'GOING', 'COME', 'CAME', 'WANT', 'NEED', 'LIKE',
                'NEWS', 'MARKET', 'PRICE', 'BUY', 'SELL', 'TRADE', 'INVEST', 'IS', 'AS', 'BE', 'TO', 'OF', 'IN'
            }

        # Only include potential tickers that are not common English words
        ticker_matches = [t for t in ticker_matches if t not in excluded_upper and len(t) >= 3]

        if ticker_matches:
            result['entities']['tickers'] = list(set(ticker_matches))

        # Extract time references
        time_matches = re.search(r'(?:last|past)\s+(\d+)\s+(days?|weeks?|months?)', query_lower)
        if time_matches:
            result['entities']['timeframe'] = {
                'value': int(time_matches.group(1)),
                'unit': time_matches.group(2)
            }

        # Adjust intent for conversational queries (lower confidence for general chat)
        conversational_words = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye', 'how are you']
        if any(word in query_lower for word in conversational_words):
            result['intent'] = 'conversational'
            result['confidence'] = 0.9

        return result
