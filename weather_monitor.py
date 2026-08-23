# weather_monitor.py
import requests
import pandas as pd
from datetime import datetime

class WeatherMonitor:
    def __init__(self):
        self.weather_data = {}
        
    def get_weather(self, lat, lng):
        """Get current weather for a location"""
        try:
            params = {
                'latitude': lat,
                'longitude': lng,
                'current': ['temperature_2m', 'wind_speed_10m', 'precipitation'],
                'timezone': 'auto'
            }
            
            response = requests.get('https://api.open-meteo.com/v1/forecast', params=params, timeout=10)
            data = response.json()
            
            if 'current' in data:
                return {
                    'temperature': data['current']['temperature_2m'],
                    'wind_speed': data['current']['wind_speed_10m'],
                    'precipitation': data['current']['precipitation'],
                    'time': data['current']['time']
                }
            return None
            
        except:
            return None
    
    def get_suppliers_weather(self, suppliers_df):
        """Get weather for all suppliers"""
        results = []
        
        for _, supplier in suppliers_df.iterrows():
            try:
                lat = float(supplier.get('lat', 0))
                lng = float(supplier.get('lng', 0))
                
                if lat == 0 or lng == 0:
                    continue
                    
                weather = self.get_weather(lat, lng)
                
                if weather:
                    # Calculate weather risk
                    risk_score = 0
                    if weather['wind_speed'] > 40:
                        risk_score += 0.3
                    elif weather['wind_speed'] > 25:
                        risk_score += 0.15
                        
                    if weather['precipitation'] > 20:
                        risk_score += 0.3
                    elif weather['precipitation'] > 10:
                        risk_score += 0.15
                        
                    if weather['temperature'] > 35 or weather['temperature'] < -10:
                        risk_score += 0.2
                        
                    results.append({
                        'supplier_id': supplier.get('id', 0),
                        'supplier_name': supplier.get('name', 'Unknown'),
                        'temperature': weather['temperature'],
                        'wind_speed': weather['wind_speed'],
                        'precipitation': weather['precipitation'],
                        'weather_risk_score': min(risk_score, 1.0),
                        'last_updated': weather['time']
                    })
            except:
                continue
                
        return pd.DataFrame(results) if results else pd.DataFrame()
