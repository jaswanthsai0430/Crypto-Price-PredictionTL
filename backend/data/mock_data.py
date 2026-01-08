"""
Mock data generator for cryptocurrency prices when Yahoo Finance is unavailable
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MockDataGenerator:
    """Generate realistic mock cryptocurrency data"""
    
    def __init__(self):
        # Base prices for cryptocurrencies (approximate current values)
        self.base_prices = {
            'BTC': 96000,
            'ETH': 3600,
            'SOLANA': 235,
            'BNB': 600,
            'DOGE': 0.08
        }
        
        # Market caps (approximate)
        self.market_caps = {
            'BTC': 1900000000000,  # $1.9T
            'ETH': 430000000000,   # $430B
            'SOLANA': 110000000000,  # $110B
            'BNB': 90000000000,    # $90B
            'DOGE': 12000000000    # $12B
        }
    
    def generate_historical_data(self, coin, days=365):
        """
        Generate mock historical price data
        
        Args:
            coin: Cryptocurrency symbol (BTC, ETH, SOLANA)
            days: Number of days of historical data
        
        Returns:
            DataFrame with OHLCV data
        """
        base_price = self.base_prices.get(coin, 1000)
        
        # Generate dates
        end_date = datetime.now()
        dates = [end_date - timedelta(days=x) for x in range(days, 0, -1)]
        
        # Generate price data with realistic volatility
        np.random.seed(hash(coin) % 2**32)  # Consistent data for same coin
        
        prices = []
        current_price = base_price * 0.7  # Start at 70% of current price
        
        for i in range(days):
            # Random walk with slight upward trend
            change = np.random.normal(0.001, 0.03)  # 0.1% mean, 3% std dev
            current_price *= (1 + change)
            prices.append(current_price)
        
        # Ensure last price is close to base price
        adjustment = base_price / prices[-1]
        prices = [p * adjustment for p in prices]
        
        # Generate OHLCV data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC from close price
            volatility = close * 0.02  # 2% daily volatility
            high = close + abs(np.random.normal(0, volatility))
            low = close - abs(np.random.normal(0, volatility))
            open_price = np.random.uniform(low, high)
            
            # Volume varies with price movement
            base_volume = 1000000000 if coin == 'BTC' else 500000000
            volume = base_volume * (1 + abs(np.random.normal(0, 0.5)))
            
            data.append({
                'Date': date,
                'Open': open_price,
                'High': high,
                'Low': low,
                'Close': close,
                'Volume': volume
            })
        
        df = pd.DataFrame(data)
        return df
    
    def get_current_price(self, coin):
        """
        Generate mock current price data
        
        Args:
            coin: Cryptocurrency symbol
        
        Returns:
            Dictionary with price data
        """
        base_price = self.base_prices.get(coin, 1000)
        
        # Add small random variation
        np.random.seed(int(datetime.now().timestamp()) % 2**32)
        current_price = base_price * (1 + np.random.normal(0, 0.01))
        
        # Random 24h change between -5% and +5%
        change_24h = np.random.uniform(-5, 5)
        
        # Volume
        base_volume = 30000000000 if coin == 'BTC' else 15000000000
        volume = base_volume * (1 + np.random.normal(0, 0.2))
        
        return {
            'coin': coin,
            'price': current_price,
            'change_24h': change_24h,
            'volume': volume,
            'market_cap': self.market_caps.get(coin, 100000000000),
            'timestamp': datetime.now().isoformat()
        }
    
    def prepare_data_for_model(self, coin):
        """
        Generate mock data prepared for ML model
        
        Args:
            coin: Cryptocurrency symbol
        
        Returns:
            DataFrame with features
        """
        # Generate 2 years of data
        df = self.generate_historical_data(coin, days=730)
        
        # Calculate technical indicators
        df = self._calculate_indicators(df)
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        return df
    
    def _calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Moving Averages
        df['MA7'] = df['Close'].rolling(window=7).mean()
        df['MA21'] = df['Close'].rolling(window=21).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Average
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Volume Moving Average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        return df

if __name__ == "__main__":
    # Test mock data generator
    generator = MockDataGenerator()
    
    for coin in ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE']:
        print(f"\n{'='*50}")
        print(f"Mock data for {coin}")
        print(f"{'='*50}")
        
        # Current price
        current = generator.get_current_price(coin)
        print(f"Current Price: ${current['price']:,.2f}")
        print(f"24h Change: {current['change_24h']:.2f}%")
        
        # Historical data
        data = generator.prepare_data_for_model(coin)
        print(f"Historical data points: {len(data)}")
        print(f"Latest close: ${data['Close'].iloc[-1]:,.2f}")

