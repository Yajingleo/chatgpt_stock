import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

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
    
    def get_company_cik(self, ticker):
        """Get CIK (Central Index Key) for a company"""
        try:
            url = f"https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            companies = response.json()
            
            for company_data in companies.values():
                if company_data['ticker'] == ticker.upper():
                    return str(company_data['cik_str']).zfill(10)
            return None
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None
    
    def get_latest_10k(self, cik):
        """Get the latest 10-K filing for a company"""
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            
            # Find latest 10-K filing
            filings = data['filings']['recent']
            for i, form in enumerate(filings['form']):
                if form in ['10-K', '10-K/A']:
                    return {
                        'accession_number': filings['accessionNumber'][i],
                        'filing_date': filings['filingDate'][i],
                        'form': form
                    }
            return None
        except Exception as e:
            print(f"Error getting 10-K for CIK {cik}: {e}")
            return None
    
    def analyze_major_customers(self, ticker):
        """Extract major customer information from 10-K filings"""
        cik = self.get_company_cik(ticker)
        if not cik:
            return None
        
        filing_info = self.get_latest_10k(cik)
        if not filing_info:
            return None
        
        # This is a simplified example - real implementation would need
        # more sophisticated text parsing
        return {
            'ticker': ticker,
            'cik': cik,
            'latest_10k_date': filing_info['filing_date'],
            'major_customers_analysis': 'Would require full text analysis of 10-K'
        }

class InsiderTradingAnalyzer:
    """Analyze insider trading data from SEC Form 4 filings"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Your Company Name your-email@company.com'
        }
    
    def get_insider_trades(self, ticker, days_back=90):
        """Get recent insider trading data"""
        # Using SEC EDGAR API for Form 4 filings
        try:
            cik = self.get_company_cik(ticker)
            if not cik:
                return []
            
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
            
            return insider_trades
            
        except Exception as e:
            print(f"Error getting insider trades for {ticker}: {e}")
            return []
    
    def get_company_cik(self, ticker):
        """Get CIK for company"""
        try:
            url = f"https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            companies = response.json()
            
            for company_data in companies.values():
                if company_data['ticker'] == ticker.upper():
                    return str(company_data['cik_str']).zfill(10)
            return None
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None


# Additional data sources you can use:

class AlternativeDataSources:
    """Access alternative data sources for corporate relationships"""
    
    def get_customer_data_sources(self):
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
    
    def scrape_company_relationships(self, ticker):
        """Example: Scrape basic company relationship data"""
        import yfinance as yf
        
        try:
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
            
            return {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'business_relationships': potential_relationships
            }
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            return None
        
if __name__ == "__main__":
    # Example usage
    ticker = "AAPL"
    
    sec_analyzer = SECFilingsAnalyzer()
    major_customers = sec_analyzer.analyze_major_customers(ticker)
    print("Major Customers Analysis:", major_customers)
    
    insider_analyzer = InsiderTradingAnalyzer()
    insider_trades = insider_analyzer.get_insider_trades(ticker)
    print("Recent Insider Trades:", insider_trades)
    
    alt_data = AlternativeDataSources()
    customer_data_sources = alt_data.get_customer_data_sources()
    print("Customer Data Sources:", customer_data_sources)
    
    company_relationships = alt_data.scrape_company_relationships(ticker)
    print("Company Relationships:", company_relationships)