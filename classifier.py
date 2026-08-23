# classifier.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import pickle
import os

class SupplyChainRiskClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=3000, stop_words='english')
        self.classifier = LogisticRegression(multi_class='multinomial', max_iter=1000, random_state=42)
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
    def load_or_train(self):
        """Load saved model or train new one"""
        model_dir = 'models'
        os.makedirs(model_dir, exist_ok=True)
        
        vectorizer_path = f'{model_dir}/vectorizer.pkl'
        classifier_path = f'{model_dir}/classifier.pkl'
        encoder_path = f'{model_dir}/encoder.pkl'
        
        if all(os.path.exists(p) for p in [vectorizer_path, classifier_path, encoder_path]):
            try:
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                with open(classifier_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                self.is_trained = True
                return True
            except:
                pass
        
        return self._train_demo()
    
    def _train_demo(self):
        """Train with expanded demo data"""
        categories = {
            'legitimate': [
                "company reports record profits", "company announces new investment", 
                "company expands operations", "company launches new product",
                "company partners with supplier", "company achieves milestone",
                "company completes acquisition", "company opens new facility"
            ],
            'financial': [
                "company files for bankruptcy", "company faces massive lawsuit",
                "company stock crashes", "company reports huge losses",
                "company fraud investigation", "company default on loans",
                "company insolvency risk", "company credit rating downgrade"
            ],
            'supplier': [
                "supply chain disruption", "supplier quality issues",
                "factory production delay", "parts shortage warning",
                "supplier labor strike", "logistics breakdown",
                "shipping container shortage", "inventory depletion"
            ],
            'labor': [
                "workers strike", "labor union dispute",
                "employee walkout", "wage negotiation failure",
                "work stoppage", "collective bargaining breakdown"
            ],
            'compliance': [
                "regulatory investigation", "environmental violation",
                "safety compliance failure", "customs violation",
                "trade compliance issue", "corruption investigation"
            ],
            'geopolitical': [
                "new tariff implemented", "trade sanctions imposed",
                "embargo announced", "trade war escalation",
                "export restrictions", "import duties increase"
            ]
        }
        
        # Create training data
        texts = []
        labels = []
        
        for label, phrases in categories.items():
            for phrase in phrases:
                texts.append(phrase)
                labels.append(label)
                # Add variations
                texts.append(f"Breaking: {phrase}")
                texts.append(f"Warning: {phrase}")
                texts.append(f"Alert: {phrase}")
                labels.extend([label, label, label])
        
        # Vectorize
        X = self.vectorizer.fit_transform(texts)
        y = self.label_encoder.fit_transform(labels)
        
        # Train
        self.classifier.fit(X, y)
        self.is_trained = True
        
        # Save
        try:
            with open('models/vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            with open('models/classifier.pkl', 'wb') as f:
                pickle.dump(self.classifier, f)
            with open('models/encoder.pkl', 'wb') as f:
                pickle.dump(self.label_encoder, f)
        except:
            pass
            
        return True
    
    def predict(self, text):
        """Predict risk category"""
        if not text or not text.strip():
            return {'category': 'legitimate', 'confidence': 0.5, 'risk_score': 0.1}
        
        if not self.is_trained:
            self._train_demo()
        
        try:
            X = self.vectorizer.transform([text])
            proba = self.classifier.predict_proba(X)[0]
            pred_idx = self.classifier.predict(X)[0]
            prediction = self.label_encoder.inverse_transform([pred_idx])[0]
            confidence = max(proba)
            
            risk_scores = {
                'legitimate': 0.1,
                'financial': 0.9,
                'supplier': 0.8,
                'labor': 0.7,
                'compliance': 0.6,
                'geopolitical': 0.75
            }
            
            return {
                'category': prediction,
                'confidence': confidence,
                'risk_score': risk_scores.get(prediction, 0.3)
            }
        except:
            return {'category': 'legitimate', 'confidence': 0.5, 'risk_score': 0.1}
    
    def analyze_articles(self, df):
        """Analyze batch of articles"""
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
