"""
CryptoCompare API integration for cryptocurrency data
Free tier: 100,000 calls/month, no API key required
Full historical data available
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class CryptoCompareAPI:
    """Fetch cryptocurrency data from CryptoCompare API"""
    
    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data"
        
        # Coin symbol mapping (CryptoCompare uses standard symbols)
        self.coin_symbols = {
            'BTC': 'BTC',
            'ETH': 'ETH',
            'SOLANA': 'SOL',
            'BNB': 'BNB',
            'DOGE': 'DOGE',
            'XRP': 'XRP',
            'ADA': 'ADA',
            'AVAX': 'AVAX',
            'DOT': 'DOT',
            'LINK': 'LINK'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        })
    
    def get_current_price(self, coin):
        """
        Get current price and market data
        
        Args:
            coin: Cryptocurrency symbol
        
        Returns:
            Dictionary with price data
        """
        symbol = self.coin_symbols.get(coin.upper())
        if not symbol:
            raise ValueError(f"Unsupported coin: {coin}")
        
        try:
            url = f"{self.base_url}/pricemultifull"
            params = {
                'fsyms': symbol,
                'tsyms': 'USD'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'RAW' not in data or symbol not in data['RAW']:
                return None
            
            coin_data = data['RAW'][symbol]['USD']
            
            return {
                'coin': coin,
                'price': coin_data.get('PRICE', 0),
                'change_24h': coin_data.get('CHANGEPCT24HOUR', 0),
                'volume': coin_data.get('VOLUME24HOURTO', 0),
                'market_cap': coin_data.get('MKTCAP', 0),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"CryptoCompare API error for {coin}: {str(e)}")
            return None
    
    def get_historical_data(self, coin, days=365):
        """
        Get historical OHLC data
        
        Args:
            coin: Cryptocurrency symbol
            days: Number of days of historical data
        
        Returns:
            DataFrame with OHLCV data
        """
        symbol = self.coin_symbols.get(coin.upper())
        if not symbol:
            raise ValueError(f"Unsupported coin: {coin}")
        
        try:
            # CryptoCompare returns max 2000 data points per request
            # For 5 years (1825 days), we need 1 request with daily data
            url = f"{self.base_url}/v2/histoday"
            params = {
                'fsym': symbol,
                'tsym': 'USD',
                'limit': min(days, 2000)  # Max 2000 per request
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Response') != 'Success':
                print(f"CryptoCompare API error: {data.get('Message', 'Unknown error')}")
                return None
            
            hist_data = data.get('Data', {}).get('Data', [])
            
            if not hist_data:
                return None
            
            # Convert to DataFrame
            df_data = []
            for item in hist_data:
                timestamp = datetime.fromtimestamp(item['time'])
                df_data.append({
                    'Date': timestamp,
                    'Open': item['open'],
                    'High': item['high'],
                    'Low': item['low'],
                    'Close': item['close'],
                    'Volume': item['volumeto']  # Volume in USD
                })
            
            df = pd.DataFrame(df_data)
            
            # Filter out any rows with zero values (exchange downtime)
            df = df[(df['Open'] > 0) & (df['Close'] > 0)]
            
            return df
        
        except Exception as e:
            print(f"CryptoCompare API error for {coin} historical data: {str(e)}")
            return None

if __name__ == "__main__":
    # Test CryptoCompare API
    api = CryptoCompareAPI()
    
    for coin in ['BTC', 'ETH', 'SOLANA']:
        print(f"\n{'='*50}")
        print(f"Testing CryptoCompare API for {coin}")
        print(f"{'='*50}")
        
        # Current price
        current = api.get_current_price(coin)
        if current:
            print(f"Current Price: ${current['price']:,.2f}")
            print(f"24h Change: {current['change_24h']:.2f}%")
            print(f"Market Cap: ${current['market_cap']:,.0f}")
        
        # Historical data
        time.sleep(1)  # Rate limiting
        hist = api.get_historical_data(coin, days=1825)  # 5 years
        if hist is not None:
            print(f"Historical data points: {len(hist)}")
            print(f"Date range: {hist['Date'].iloc[0]} to {hist['Date'].iloc[-1]}")
            print(f"Latest close: ${hist['Close'].iloc[-1]:,.2f}")
