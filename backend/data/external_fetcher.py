import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

class ExternalMarketFetcher:
    """Fetch external market data (Stock indices, Gold, etc.)"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_path = os.path.join(cache_dir, 'external_market_data.csv')
        
        # Mapping for yfinance tickers
        self.tickers = {
            'SP500': 'SPY',      # S&P 500 ETF
            'DXY': 'UUP',        # Dollar Index ETF
            'GOLD': 'GLD',       # Gold ETF
            'NASDAQ': 'QQQ'      # Nasdaq 100 ETF
        }
    
    def fetch_historical_data(self, years=6):
        """Fetch historical data for all tickers"""
        print(f"Fetching external market data for the last {years} years...")
        all_data = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        for name, ticker in self.tickers.items():
            print(f"  Fetching {name} ({ticker})...")
            try:
                df = yf.download(ticker, start=start_date, end=end_date)
                if df.empty:
                    print(f"  Warning: No data found for {name}")
                    continue
                
                # Keep only Close price and rename
                df = df[['Close']].rename(columns={'Close': f'{name}_Close'})
                all_data.append(df)
            except Exception as e:
                print(f"  Error fetching {name}: {str(e)}")
        
        if not all_data:
            return None
        
        # Merge all data on index (Date)
        combined_df = pd.concat(all_data, axis=1)
        
        # Reset index to make Date a column
        combined_df = combined_df.reset_index()
        combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.date
        
        # Fill missing values (weekends/holidays) - forward fill
        combined_df = combined_df.ffill().bfill()
        
        # Save to cache
        combined_df.to_csv(self.cache_path, index=False)
        print(f"✓ Saved {len(combined_df)} external data points to {self.cache_path}")
        
        return combined_df

    def get_market_data(self):
        """Get market data from cache or fetch if missing"""
        if os.path.exists(self.cache_path):
            df = pd.read_csv(self.cache_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
            # Check if cache is old (older than today) - use yesterday for stability
            last_date = df['Date'].max()
            if last_date < (datetime.now() - timedelta(days=2)).date():
                print("External market cache is outdated. Updating...")
                return self.fetch_historical_data()
            
            return df
        else:
            return self.fetch_historical_data()

if __name__ == "__main__":
    fetcher = ExternalMarketFetcher()
    data = fetcher.get_market_data()
    if data is not None:
        print(data.tail())
