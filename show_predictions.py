import requests
import json

coins = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']

print("\n" + "="*110)
print("CRYPTOCURRENCY PRICE PREDICTIONS - CURRENT FORECAST")
print("="*110 + "\n")

print(f"{'Coin':<8} | {'Current Price':<15} | {'Predicted Price':<15} | {'Change %':<12} | {'Prediction Date':<15}")
print("-" * 110)

try:
    for coin in coins:
        r = requests.get(f'http://localhost:5000/api/predict/{coin}')
        if r.status_code == 200:
            data = r.json()['prediction']
            current = data['current_price']
            pred = data['predictions'][0]
            pred_price = pred['price']
            change = pred['change_percent']
            date = pred['date']
            
            # Color indicator for change
            arrow = "UP" if change > 0 else "DOWN" if change < 0 else "STABLE"
            
            print(f"{coin:<8} | ${current:>13,.2f} | ${pred_price:>13,.2f} | {change:>10.2f}% ({arrow:<5}) | {date:<15}")
        else:
            print(f"{coin:<8} | Error connecting to API")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*110)

# Sentiment Analysis
print("\nMARKET SENTIMENT ANALYSIS")
print("="*110 + "\n")

print(f"{'Coin':<8} | {'Sentiment Score':<18} | {'Category':<15} | {'Positive':<10} | {'Neutral':<10} | {'Negative':<10}")
print("-" * 110)

try:
    for coin in coins:
        r = requests.get(f'http://localhost:5000/api/sentiment/{coin}')
        if r.status_code == 200:
            sent_data = r.json()['sentiment']
            score = sent_data['score']
            category = sent_data['category']
            positive = sent_data['positive']
            neutral = sent_data['neutral']
            negative = sent_data['negative']
            
            print(f"{coin:<8} | {score:>16.2f}/100 | {category:<15} | {positive:<10} | {neutral:<10} | {negative:<10}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*110 + "\n")

# Summary Statistics
print("SUMMARY")
print("="*110 + "\n")

try:
    bullish = 0
    bearish = 0
    neutral = 0
    
    for coin in coins:
        r = requests.get(f'http://localhost:5000/api/predict/{coin}')
        if r.status_code == 200:
            data = r.json()['prediction']
            change = data['predictions'][0]['change_percent']
            
            if change > 1:
                bullish += 1
            elif change < -1:
                bearish += 1
            else:
                neutral += 1
    
    print(f"Total Coins: {len(coins)}")
    print(f"Bullish Predictions (>+1%): {bullish}")
    print(f"Bearish Predictions (<-1%): {bearish}") 
    print(f"Neutral Predictions (±1%): {neutral}")
    print(f"\nOverall Trend: {'BULLISH' if bullish > bearish else 'BEARISH' if bearish > bullish else 'NEUTRAL'}")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*110 + "\n")
