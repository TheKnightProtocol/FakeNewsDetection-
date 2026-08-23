# data_ingestion.py
import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import hashlib
import time
from config import NEWS_FEEDS, RISK_KEYWORDS

class NewsIngestionEngine:
    def __init__(self):
        self.articles = []
        
    def fetch_news(self, sources=None, max_articles=15):
        """Fetch news from RSS feeds with robust error handling"""
        sources = sources or NEWS_FEEDS
        all_articles = []
        
        for feed_url in sources:
            try:
                print(f"Fetching: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                # Check for feed errors
                if feed.bozo:
                    print(f"Warning: {feed_url} - {feed.bozo_exception}")
                    continue
                    
                for entry in feed.entries[:8]:
                    try:
                        article = {
                            'id': hashlib.md5(f"{entry.get('title', '')}{entry.get('link', '')}".encode()).hexdigest()[:8],
                            'title': entry.get('title', 'No title'),
                            'summary': BeautifulSoup(entry.get('summary', ''), 'html.parser').get_text()[:500],
                            'link': entry.get('link', '#'),
                            'published': entry.get('published', datetime.now().isoformat()),
                            'source': feed_url.split('/')[2] if '/' in feed_url else 'Unknown',
                            'fetched_at': datetime.now().isoformat()
                        }
                        
                        # Detect risk categories
                        text = f"{article['title']} {article['summary']}".lower()
                        detected_categories = []
                        for category, keywords in RISK_KEYWORDS.items():
                            if any(kw in text for kw in keywords):
                                detected_categories.append(category)
                        
                        if not detected_categories:
                            detected_categories = ['legitimate']
                            
                        article['risk_categories'] = detected_categories
                        all_articles.append(article)
                        
                    except Exception as e:
                        print(f"Error parsing entry: {e}")
                        continue
                        
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        
        # If no articles, use demo data
        if not all_articles:
            print("No articles fetched, using demo data")
            all_articles = self._create_demo_articles()
            
        df = pd.DataFrame(all_articles[:max_articles])
        
        # Ensure all required columns exist
        for col in ['id', 'title', 'summary', 'link', 'published', 'source', 'fetched_at', 'risk_categories']:
            if col not in df.columns:
                df[col] = 'Unknown'
                
        return df
    
    def _create_demo_articles(self):
        """Create demo articles with realistic supply chain scenarios"""
        return [
            {
                'id': hashlib.md5(b"article1").hexdigest()[:8],
                'title': 'Magna International Reports Record Profits',
                'summary': 'Canadian auto parts manufacturer posts strong Q3 results exceeding expectations',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'Reuters',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['legitimate']
            },
            {
                'id': hashlib.md5(b"article2").hexdigest()[:8],
                'title': 'BREAKING: Major Semiconductor Plant Explosion in Taiwan',
                'summary': 'TSMC factory suffers explosion, production halted indefinitely',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'Bloomberg',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['financial', 'supplier']
            },
            {
                'id': hashlib.md5(b"article3").hexdigest()[:8],
                'title': 'Toyota Plant Strike Halts Global Production',
                'summary': '5000 workers walk out demanding higher wages amid supply chain crisis',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'WSJ',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['supplier']
            },
            {
                'id': hashlib.md5(b"article4").hexdigest()[:8],
                'title': 'DHL Announces Major Logistics Expansion in Europe',
                'summary': '€2 billion investment in sustainable supply chain infrastructure',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'FT',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['legitimate']
            },
            {
                'id': hashlib.md5(b"article5").hexdigest()[:8],
                'title': 'Warning: Samsung Battery Recall Imminent',
                'summary': 'Defective batteries in smartphones may cause fires, recall expected',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'TechCrunch',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['financial']
            },
            {
                'id': hashlib.md5(b"article6").hexdigest()[:8],
                'title': 'New Tariffs on Chinese Imports Announced',
                'summary': 'US imposes 25% tariff on $300 billion of Chinese goods',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'CNBC',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['geopolitical']
            },
            {
                'id': hashlib.md5(b"article7").hexdigest()[:8],
                'title': 'Hurricane Disrupts Gulf Coast Shipping Lanes',
                'summary': 'Major storm forces closure of key ports, causing delays',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'Weather Channel',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['weather']
            },
            {
                'id': hashlib.md5(b"article8").hexdigest()[:8],
                'title': 'Intel Announces New US Factory, Creating 10,000 Jobs',
                'summary': 'Major investment in domestic semiconductor manufacturing',
                'link': '#',
                'published': datetime.now().isoformat(),
                'source': 'Reuters',
                'fetched_at': datetime.now().isoformat(),
                'risk_categories': ['legitimate']
            }
        ]
    
    def get_articles_by_keyword(self, df, keyword):
        """Filter articles by keyword"""
        if not keyword or df.empty:
            return df
            
        keyword_lower = keyword.lower()
        mask = (
            df['title'].str.lower().str.contains(keyword_lower, na=False) |
            df['summary'].str.lower().str.contains(keyword_lower, na=False)
        )
        return df[mask]
