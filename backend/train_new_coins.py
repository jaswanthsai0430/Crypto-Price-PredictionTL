"""
Train models for BNB and DOGE specifically
Quick training script with reduced epochs for faster initial setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.price_predictor import PricePredictor
from data.data_fetcher import DataFetcher

def train_new_coins():
    print("="*70)
    print("Training Models for BNB and DOGE")
    print("="*70)
    
    fetcher = DataFetcher()
    new_coins = ['BNB', 'DOGE']
    
    for coin in new_coins:
        print(f"\n{'='*70}")
        print(f"Training {coin} Model")
        print(f"{'='*70}")
        
        try:
            # Get data
            print(f"Fetching data for {coin}...")
            data = fetcher.prepare_data_for_model(coin)
            
            if data is None or len(data) < 100:
                print(f"✗ ERROR: Insufficient data for {coin}")
                print(f"  Data points: {len(data) if data is not None else 0}")
                print(f"  Required: 100+")
                continue
            
            print(f"✓ Data fetched: {len(data)} days")
            
            # Train model
            print(f"\nTraining {coin} model...")
            print("This will take 5-10 minutes...")
            
            predictor = PricePredictor(coin)
            history = predictor.train(data, epochs=50, batch_size=32)
            
            print(f"\n✓ {coin} model trained successfully!")
            
            # Test prediction
            print(f"\nTesting {coin} predictions...")
            prediction = predictor.predict(data)
            
            print(f"\n{coin} Predictions:")
            print(f"  Current Price: ${prediction['current_price']:,.2f}")
            for pred in prediction['predictions']:
                print(f"  {pred['date']}: ${pred['price']:,.2f} ({pred['change_percent']:+.2f}%)")
            
            print(f"\n✓ {coin} is ready to use!")
            
        except Exception as e:
            print(f"\n✗ ERROR training {coin}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print("\nYou can now use BNB and DOGE in the frontend.")
    print("Refresh your browser and click the BNB or DOGE tabs.")

if __name__ == "__main__":
    train_new_coins()
