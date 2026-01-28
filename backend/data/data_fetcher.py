import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time
from data.coingecko_api import CoinGeckoAPI
from data.mock_data import MockDataGenerator

class DataFetcher:
    def __init__(self, cache_dir='cache', use_mock_data=False):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cryptocurrency ticker mapping
        self.tickers = {
            'BTC': 'BTC',
            'ETH': 'ETH',
            'SOLANA': 'SOLANA',
            'BNB': 'BNB',
            'DOGE': 'DOGE',
            'XRP': 'XRP',
            'ADA': 'ADA',
            'AVAX': 'AVAX',
            'DOT': 'DOT',
            'LINK': 'LINK'
        }
        
        # CoinGecko API (free, reliable)
        self.coingecko = CoinGeckoAPI()
        
        # Mock data generator for fallback
        self.mock_generator = MockDataGenerator()
        self.use_mock_data = use_mock_data
        self.api_failed = False  # Track if API is failing
    
    def get_historical_data(self, coin, period='1y', interval='1d', max_retries=2):
        """
        Fetch historical price data using CoinGecko API
        
        Args:
            coin: Cryptocurrency symbol (BTC, ETH, SOLANA)
            period: Data period (converted to days)
            interval: Data interval (not used with CoinGecko)
            max_retries: Maximum number of retry attempts
        
        Returns:
            DataFrame with OHLCV data
        """
        # Use mock data if enabled or API has failed
        if self.use_mock_data or self.api_failed:
            print(f"Using mock data for {coin} (API unavailable)")
            days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 365, '5y': 365}
            days = days_map.get(period, 365)
            return self.mock_generator.generate_historical_data(coin, days=days)
        
        # Convert period to days
        days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 365, '5y': 365}
        days = days_map.get(period, 365)
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt
                    print(f"Retry {attempt + 1}/{max_retries} for {coin} after {wait_time}s delay...")
                    time.sleep(wait_time)
                
                # Fetch from CoinGecko
                data = self.coingecko.get_historical_data(coin, days=days)
                
                if data is None or data.empty:
                    if attempt < max_retries - 1:
                        continue
                    raise ValueError(f"No data found for {coin}")
                
                print(f"Successfully fetched {len(data)} data points for {coin} from CoinGecko")
                self.api_failed = False
                return data
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error fetching data for {coin} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(1)  # Brief delay before retry
                    continue
                else:
                    print(f"CoinGecko API failed for {coin}. Switching to mock data mode.")
                    self.api_failed = True
                    return self.mock_generator.generate_historical_data(coin, days=days)
        
        return None
    
    def get_current_price(self, coin, max_retries=2):
        """
        Get current price using CoinGecko API
        
        Args:
            coin: Cryptocurrency symbol (BTC, ETH, SOLANA)
            max_retries: Maximum number of retry attempts
        
        Returns:
            Dictionary with current price, 24h change, and other metrics
        """
        # Use mock data if enabled or API has failed
        if self.use_mock_data or self.api_failed:
            print(f"Using mock price data for {coin}")
            return self.mock_generator.get_current_price(coin)
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2
                    print(f"Retry {attempt + 1}/{max_retries} for {coin} price after {wait_time}s delay...")
                    time.sleep(wait_time)
                
                # Fetch from CoinGecko
                data = self.coingecko.get_current_price(coin)
                
                if data is None:
                    if attempt < max_retries - 1:
                        continue
                    raise ValueError(f"No price data available for {coin}")
                
                self.api_failed = False
                return data
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error fetching price for {coin} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(1)
                    continue
                else:
                    print(f"CoinGecko API failed for {coin} price. Using mock data.")
                    self.api_failed = True
                    return self.mock_generator.get_current_price(coin)
        
        return None
    
    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators for the dataset
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added technical indicators
        """
        # Make a copy to avoid modifying original
        data = df.copy()
        
        # Moving Averages
        data['MA7'] = data['Close'].rolling(window=7).mean()
        data['MA21'] = data['Close'].rolling(window=21).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        
        # Exponential Moving Average
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        data['MACD'] = data['EMA12'] - data['EMA26']
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        # Volume Moving Average
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        
        return data
    
    def prepare_data_for_model(self, coin, lookback=60):
        """
        Prepare data for ML model training/prediction
        
        Args:
            coin: Cryptocurrency symbol
            lookback: Number of days to look back for features
        
        Returns:
            Prepared DataFrame with features
        """
        # Use mock data if API has failed
        if self.use_mock_data or self.api_failed:
            print(f"Using mock data for {coin} model training")
            return self.mock_generator.prepare_data_for_model(coin)
        
        # Get historical data
        df = self.get_historical_data(coin, period='2y', interval='1d')
        
        if df is None or df.empty:
            print(f"No data available, using mock data for {coin}")
            return self.mock_generator.prepare_data_for_model(coin)
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        return df

if __name__ == "__main__":
    # Test the data fetcher
    fetcher = DataFetcher()
    
    for coin in ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']:
        print(f"\n{'='*50}")
        print(f"Testing {coin}")
        print(f"{'='*50}")
        
        # Get current price
        current = fetcher.get_current_price(coin)
        if current:
            print(f"Current Price: ${current['price']:,.2f}")
            print(f"24h Change: {current['change_24h']:.2f}%")
        
        # Get historical data
        data = fetcher.prepare_data_for_model(coin)
        if data is not None:
            print(f"Historical data points: {len(data)}")
            print(f"Latest close: ${data['Close'].iloc[-1]:,.2f}")

