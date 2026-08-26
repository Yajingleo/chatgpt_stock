import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

from agent.config import settings
from agent.utils import get_session_cache

class SECFilingsAnalyzer:
    """Analyze SEC filings for major customer disclosures and insider trading"""
    
    def __init__(self):
        self.base_url = "https://www.sec.gov/Archives/edgar/data"
        self.search_url = "https://efts.sec.gov/LATEST/search-index"
        self.headers = {
            'User-Agent': 'Your Company Name your-email@company.com',  # SEC requires identification
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        self._cache = get_session_cache('sec_filings', settings.cache.sec_filings_ttl)
    
    def get_company_cik(self, ticker):
        """Get CIK (Central Index Key) for a company"""
        try:
            cache_key = {'kind': 'company_cik', 'ticker': ticker.upper()}
            cached_cik = self._cache.get(cache_key) if settings.cache.enabled else None
            if isinstance(cached_cik, str):
                return cached_cik

            url = f"https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            companies = response.json()
            
            for company_data in companies.values():
                if company_data['ticker'] == ticker.upper():
                    cik = str(company_data['cik_str']).zfill(10)
                    if settings.cache.enabled:
                        self._cache.set(cache_key, cik)
                    return cik
            return None
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None
    
    def get_latest_10k(self, cik):
        """Get the latest 10-K filing for a company"""
        try:
            cache_key = {'kind': 'latest_10k', 'cik': cik}
            cached_filing = self._cache.get(cache_key) if settings.cache.enabled else None
            if isinstance(cached_filing, dict):
                return cached_filing

            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            # Find latest 10-K filing
            filings = data['filings']['recent']
            for i, form in enumerate(filings['form']):
                if form in ['10-K', '10-K/A']:
                    filing = {
                        'accession_number': filings['accessionNumber'][i],
                        'filing_date': filings['filingDate'][i],
                        'form': form
                    }
                    if settings.cache.enabled:
                        self._cache.set(cache_key, filing)
                    return filing
            return None
        except Exception as e:
            print(f"Error getting 10-K for CIK {cik}: {e}")
            return None
    
    def analyze_major_customers(self, ticker) -> pd.DataFrame:
        """Extract major customer information from 10-K filings"""
        cache_key = {'kind': 'major_customers', 'ticker': ticker.upper()}
        cached_analysis = self._cache.get(cache_key) if settings.cache.enabled else None
        if isinstance(cached_analysis, pd.DataFrame):
            return cached_analysis

        cik = self.get_company_cik(ticker)
        if not cik:
            return pd.DataFrame()
        
        filing_info = self.get_latest_10k(cik)
        if not filing_info:
            return pd.DataFrame()

        # This is a simplified example - real implementation would need
        # more sophisticated text parsing
        analysis = pd.DataFrame({
            'ticker': [ticker],
            'cik': [cik],
            'latest_10k_date': [filing_info['filing_date']],
            'major_customers_analysis': ['Would require full text analysis of 10-K']
        })
        if settings.cache.enabled:
            self._cache.set(cache_key, analysis)
        return analysis

class InsiderTradingAnalyzer:
    """Analyze insider trading data from SEC Form 4 filings"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Your Company Name your-email@company.com'
        }
        self._cache = get_session_cache('sec_filings', settings.cache.sec_filings_ttl)
    
    def get_insider_trades(self, ticker, days_back=90) -> pd.DataFrame:
        """Get recent insider trading data"""
        # Using SEC EDGAR API for Form 4 filings
        try:
            cache_key = {
                'kind': 'insider_trades', 'ticker': ticker.upper(), 'days_back': days_back,
            }
            cached_trades = self._cache.get(cache_key) if settings.cache.enabled else None
            if isinstance(cached_trades, pd.DataFrame):
                return cached_trades

            cik = self.get_company_cik(ticker)
            if not cik:
                return pd.DataFrame()
            
            # Get recent Form 4 filings (insider trading)
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            insider_trades = []
            filings = data['filings']['recent']
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for i, form in enumerate(filings['form']):
                if form == '4':  # Form 4 is for insider trading
                    filing_date = datetime.strptime(filings['filingDate'][i], '%Y-%m-%d')
                    if filing_date >= cutoff_date:
                        insider_trades.append({
                            'ticker': ticker,
                            'form': form,
                            'filing_date': filings['filingDate'][i],
                            'accession_number': filings['accessionNumber'][i],
                            'size': filings['size'][i]
                        })

            trades = pd.DataFrame(insider_trades)
            if settings.cache.enabled:
                self._cache.set(cache_key, trades)
            return trades

        except Exception as e:
            print(f"Error getting insider trades for {ticker}: {e}")
            return pd.DataFrame()

    def get_company_cik(self, ticker) -> str:
        """Get CIK for company"""
        try:
            cache_key = {'kind': 'company_cik', 'ticker': ticker.upper()}
            cached_cik = self._cache.get(cache_key) if settings.cache.enabled else None
            if isinstance(cached_cik, str):
                return cached_cik

            url = f"https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            companies = response.json()
            
            for company_data in companies.values():
                if company_data['ticker'] == ticker.upper():
                    cik = str(company_data['cik_str']).zfill(10)
                    if settings.cache.enabled:
                        self._cache.set(cache_key, cik)
                    return cik
            return None
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None


# Additional data sources you can use:

class AlternativeDataSources:
    """Access alternative data sources for corporate relationships"""
    
    def get_customer_data_sources(self) -> dict:
        """List of data sources for customer/supplier information"""
        return {
            "free_sources": [
                "SEC EDGAR filings (10-K, 10-Q)",
                "Yahoo Finance business summary",
                "Company annual reports",
                "Industry research reports",
                "OpenCorporates API (corporate relationships)"
            ],
            "paid_sources": [
                "Bloomberg Terminal",
                "Refinitiv (formerly Reuters)",
                "S&P Capital IQ",
                "Factset",
                "PitchBook (for private companies)",
                "Crunchbase (tech companies)",
                "Owler (competitive intelligence)"
            ],
            "web_scraping": [
                "Company websites (investor relations)",
                "Industry publications",
                "Supply chain databases",
                "Trade publications"
            ]
        }

    def scrape_company_relationships(self, ticker) -> dict:
        """Example: Scrape basic company relationship data"""
        import yfinance as yf
        
        try:
            cache = get_session_cache('alternative_data', settings.cache.fundamentals_ttl)
            cache_key = {'kind': 'company_relationships', 'ticker': ticker.upper()}
            cached_relationships = cache.get(cache_key) if settings.cache.enabled else None
            if isinstance(cached_relationships, dict):
                return cached_relationships

            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract business summary for customer mentions
            business_summary = info.get('longBusinessSummary', '')
            
            # Simple keyword analysis (this would be much more sophisticated in practice)
            customer_keywords = ['customer', 'client', 'partner', 'serves', 'provides']
            potential_relationships = []
            
            sentences = business_summary.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in customer_keywords):
                    potential_relationships.append(sentence.strip())

            relationships = {
                'ticker': [ticker],
                'company_name': [info.get('longName', ticker)],
                'sector': [info.get('sector', 'Unknown')],
                'business_relationships': [potential_relationships]
            }
            if settings.cache.enabled:
                cache.set(cache_key, relationships)
            return relationships
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            return pd.DataFrame()
        
if __name__ == "__main__":
    # Example usage
    ticker = "AMD"
    
    sec_analyzer = SECFilingsAnalyzer()
    major_customers = sec_analyzer.analyze_major_customers(ticker)
    print("Major Customers Analysis: \n", major_customers, "\n")
    
    insider_analyzer = InsiderTradingAnalyzer()
    insider_trades = insider_analyzer.get_insider_trades(ticker)
    print("Recent Insider Trades: \n", insider_trades, "\n")

    alt_data = AlternativeDataSources()
    customer_data_sources = alt_data.get_customer_data_sources()
    print("Customer Data Sources: \n", customer_data_sources, "\n")

    company_relationships = alt_data.scrape_company_relationships(ticker)
    print("Company Relationships: \n", company_relationships, "\n")
