"""
Quick API Test Script
Tests CoinGecko API connection and live prices
"""

from data.coingecko_api import CoinGeckoAPI
import sys

def test_api():
    print("="*60)
    print("Testing CoinGecko API Connection")
    print("="*60)
    
    api = CoinGeckoAPI()
    coins = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE']
    
    results = []
    for coin in coins:
        try:
            print(f"\nTesting {coin}...")
            result = api.get_current_price(coin)
            
            if result and result.get('price'):
                price = result['price']
                change = result.get('change_24h', 0)
                volume = result.get('volume', 0)
                
                print(f"  ✓ SUCCESS")
                print(f"  Price: ${price:,.2f}")
                print(f"  24h Change: {change:+.2f}%")
                print(f"  Volume: ${volume:,.0f}")
                
                results.append({
                    'coin': coin,
                    'status': 'SUCCESS',
                    'price': price
                })
            else:
                print(f"  ✗ FAILED - No data returned")
                results.append({
                    'coin': coin,
                    'status': 'FAILED',
                    'error': 'No data'
                })
                
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            results.append({
                'coin': coin,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    print(f"Successful: {success_count}/{len(coins)}")
    
    for r in results:
        status_symbol = "✓" if r['status'] == 'SUCCESS' else "✗"
        if r['status'] == 'SUCCESS':
            print(f"{status_symbol} {r['coin']}: ${r['price']:,.2f}")
        else:
            print(f"{status_symbol} {r['coin']}: {r.get('error', 'FAILED')}")
    
    if success_count == len(coins):
        print("\n✓ All APIs working correctly!")
        return 0
    else:
        print(f"\n✗ {len(coins) - success_count} API(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(test_api())
