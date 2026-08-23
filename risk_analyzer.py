# risk_analyzer.py
import pandas as pd
import numpy as np
import os

class RiskAnalyzer:
    def __init__(self, supplier_csv='data/suppliers.csv'):
        self.suppliers = self._load_suppliers(supplier_csv)
        self.alternatives = self._load_alternatives('data/alternatives.csv')
        
    def _load_suppliers(self, path):
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                # Ensure required columns exist
                required = ['id', 'name', 'lat', 'lng', 'country', 'industry', 'annual_spend_usd', 'tier']
                for col in required:
                    if col not in df.columns:
                        df[col] = 'Unknown'
                return df
            except:
                pass
        return self._create_default_suppliers()
    
    def _create_default_suppliers(self):
        return pd.DataFrame([
            [1, 'TSMC', 23.6978, 120.9605, 'Taiwan', 'Semiconductor', 5000000, 1],
            [2, 'Toyota', 35.1815, 136.9066, 'Japan', 'Automotive', 8000000, 1],
            [3, 'Samsung', 37.5665, 126.9780, 'South Korea', 'Electronics', 4500000, 2],
            [4, 'Maersk', 55.6761, 12.5683, 'Denmark', 'Shipping', 9800000, 1],
            [5, 'Intel', 45.3409, -122.9908, 'USA', 'Semiconductor', 3200000, 1],
            [6, 'Bosch', 48.7833, 9.1833, 'Germany', 'Automotive', 4600000, 2],
            [7, 'DHL', 50.7374, 7.0982, 'Germany', 'Logistics', 3200000, 1],
        ], columns=['id', 'name', 'lat', 'lng', 'country', 'industry', 'annual_spend_usd', 'tier'])
    
    def _load_alternatives(self, path):
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except:
                pass
        return pd.DataFrame()
    
    def calculate_supplier_risk(self, article_df, classifier_results):
        """Calculate overall risk score for each supplier"""
        supplier_risks = []
        
        for _, supplier in self.suppliers.iterrows():
            # Check if any articles mention this supplier
            relevant_articles = []
            for _, article in classifier_results.iterrows():
                if str(supplier['name']).lower() in str(article.get('title', '')).lower():
                    relevant_articles.append(article)
            
            # Calculate risk
            if relevant_articles:
                avg_risk = np.mean([a['risk_score'] for a in relevant_articles])
                base_risk = avg_risk
            else:
                base_risk = 0.2
            
            # Industry risk multiplier
            industry_risk = {
                'Semiconductor': 0.3,
                'Automotive': 0.25,
                'Electronics': 0.25,
                'Shipping': 0.4,
                'Logistics': 0.35,
                'Pharmaceutical': 0.2,
                'Chemicals': 0.3,
                'Apparel': 0.15,
                'Aerospace': 0.2
            }.get(supplier.get('industry', ''), 0.2)
            
            # Tier multiplier
            tier_multiplier = {'1': 1.0, '2': 0.8, '3': 0.6}.get(str(supplier.get('tier', '2')), 0.8)
            
            # Final risk score
            final_risk = min(base_risk * tier_multiplier + industry_risk * 0.3 + 0.05, 1.0)
            
            # Financial exposure
            annual_spend = float(str(supplier.get('annual_spend_usd', '0')).replace(',', ''))
            exposure_at_risk = annual_spend * final_risk
            
            supplier_risks.append({
                'id': supplier['id'],
                'name': supplier['name'],
                'country': supplier.get('country', 'Unknown'),
                'industry': supplier.get('industry', 'Unknown'),
                'tier': supplier.get('tier', '2'),
                'latitude': float(supplier.get('lat', 0)),
                'longitude': float(supplier.get('lng', 0)),
                'risk_score': round(final_risk, 3),
                'annual_spend_usd': annual_spend,
                'exposure_at_risk_usd': round(exposure_at_risk, 0),
                'status': 'Active'
            })
        
        return pd.DataFrame(supplier_risks)
    
    def get_risk_summary(self, risk_df):
        """Generate summary statistics"""
        if risk_df.empty:
            return {
                'avg_risk': 0,
                'max_risk': 0,
                'high_risk_count': 0,
                'total_exposure': 0,
                'risk_distribution': {}
            }
        
        return {
            'avg_risk': risk_df['risk_score'].mean(),
            'max_risk': risk_df['risk_score'].max(),
            'high_risk_count': len(risk_df[risk_df['risk_score'] >= 0.6]),
            'total_exposure': risk_df['exposure_at_risk_usd'].sum(),
            'risk_distribution': risk_df['risk_score'].describe().to_dict()
        }
    
    def find_alternatives(self, supplier_name):
        """Find alternative suppliers"""
        if self.alternatives.empty:
            return pd.DataFrame()
        
        matches = self.alternatives[self.alternatives['primary_supplier'] == supplier_name]
        return matches
