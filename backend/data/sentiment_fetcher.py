import requests
import pandas as pd
from datetime import datetime
import os
import json

class MarketSentimentFetcher:
    """Fetch historical market sentiment data (Fear & Greed Index)"""
    
    def __init__(self, cache_dir='cache'):
        self.base_url = "https://api.alternative.me/fng/"
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_path = os.path.join(cache_dir, 'market_sentiment.csv')
    
    def fetch_historical_fng(self, limit=0):
        """
        Fetch all historical Fear & Greed Index data
        limit=0 returns all available data
        """
        print("Fetching historical Fear & Greed Index data...")
        try:
            params = {
                'limit': limit,
                'format': 'json'
            }
            response = requests.get(self.base_url, params=params, verify=False)
            response.raise_for_status()
            
            data = response.json()
            if data.get('metadata', {}).get('error'):
                print(f"API Error: {data['metadata']['error']}")
                return None
            
            fng_list = data.get('data', [])
            df_data = []
            
            for item in fng_list:
                timestamp = datetime.fromtimestamp(int(item['timestamp']))
                df_data.append({
                    'Date': timestamp.strftime('%Y-%m-%d'),
                    'FNG_Score': int(item['value']),
                    'FNG_Classification': item['value_classification']
                })
            
            df = pd.DataFrame(df_data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            
            # Save to cache
            df.to_csv(self.cache_path, index=False)
            print(f"✓ Saved {len(df)} sentiment data points to {self.cache_path}")
            
            return df
            
        except Exception as e:
            print(f"Error fetching sentiment data: {str(e)}")
            return None
    
    def get_sentiment_data(self):
        """Get sentiment data from cache or fetch if missing"""
        if os.path.exists(self.cache_path):
            df = pd.read_csv(self.cache_path)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Check if cache is old (older than today)
            last_date = df['Date'].max()
            if last_date.date() < datetime.now().date():
                print("Sentiment cache is outdated. Updating...")
                return self.fetch_historical_fng()
            
            return df
        else:
            return self.fetch_historical_fng()

if __name__ == "__main__":
    fetcher = MarketSentimentFetcher()
    data = fetcher.get_sentiment_data()
    if data is not None:
        print(data.tail())
