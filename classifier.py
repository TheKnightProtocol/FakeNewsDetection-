# classifier.py
import pandas as pd
from config import RISK_KEYWORDS, RISK_WEIGHTS

class SupplyChainRiskClassifier:
    """Simple keyword-based risk scorer – no ML dependencies"""
    
    def __init__(self):
        self.keywords = RISK_KEYWORDS
        self.weights = RISK_WEIGHTS
        
    def load_or_train(self):
        """No training needed – always ready"""
        return True
    
    def predict(self, text):
        """Score text based on keyword presence"""
        if not text or not text.strip():
            return {'category': 'legitimate', 'confidence': 0.5, 'risk_score': 0.0}
        
        text_lower = text.lower()
        max_score = 0.0
        detected_category = 'legitimate'
        
        for category, keywords in self.keywords.items():
            if any(kw in text_lower for kw in keywords):
                score = self.weights.get(category, 0.0)
                if score > max_score:
                    max_score = score
                    detected_category = category
        
        # Return a dict matching the old ML interface
        return {
            'category': detected_category,
            'confidence': min(max_score * 1.5, 1.0),  # approximate confidence
            'risk_score': max_score
        }
    
    def analyze_articles(self, df):
        """Analyze a batch of articles"""
        if df.empty:
            return pd.DataFrame()
        
        results = []
        for idx, row in df.iterrows():
            text = f"{row.get('title', '')} {row.get('summary', '')}"
            result = self.predict(text)
            result['article_id'] = row.get('id', idx)
            result['title'] = row.get('title', '')
            result['source'] = row.get('source', '')
            result['link'] = row.get('link', '#')
            results.append(result)
            
        return pd.DataFrame(results)
