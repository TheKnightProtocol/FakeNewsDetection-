# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# News feeds (use reliable ones)
NEWS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.wsj.com/xml/rss/3_7085.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
]

# Risk keywords (simple word lists)
RISK_KEYWORDS = {
    'financial': ['bankruptcy', 'loss', 'debt', 'default', 'credit', 'downgrade', 'insolvent', 'fraud'],
    'supplier': ['strike', 'labor', 'dispute', 'quality', 'delay', 'shortage', 'recall', 'disruption'],
    'geopolitical': ['tariff', 'sanction', 'embargo', 'trade', 'war', 'export', 'regulation'],
    'weather': ['hurricane', 'flood', 'drought', 'storm', 'earthquake', 'cyclone'],
    'legitimate': ['report', 'announces', 'launches', 'expands', 'partners', 'growth']
}

# Risk weights (0–1)
RISK_WEIGHTS = {
    'financial': 0.9,
    'supplier': 0.8,
    'geopolitical': 0.7,
    'weather': 0.6,
    'legitimate': 0.1
}
