import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.price_predictor import PricePredictor
from data.data_fetcher import DataFetcher
import json

# List of supported coins
SUPPORTED_COINS = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']

def train_phase1():
    print("="*70)
    print("PHASE 1: Training Models with 5 New Indicators + Attention")
    print("="*70)
    
    fetcher = DataFetcher()
    
    for coin in SUPPORTED_COINS:
        print(f"\n{'='*70}")
        print(f"Training {coin} Model")
        print(f"{'='*70}")
        
        try:
            # Prepare data (now includes the 5 new indicators)
            print(f"Fetching and preparing data for {coin}...")
            data = fetcher.prepare_data_for_model(coin)
            
            if data is None or len(data) < 100:
                print(f"✗ ERROR: Insufficient data for {coin}")
                continue
            
            print(f"✓ Data prepared: {len(data)} days")
            
            # Initialize predictor
            predictor = PricePredictor(coin)
            
            # The PricePredictor.train will now use the new create_model with Attention
            # and the LearningRateScheduler
            print(f"Training {coin} model (100 epochs)...")
            history = predictor.train(data, epochs=100, batch_size=32)
            
            print(f"✓ {coin} model trained successfully!")
            print(f"  Final loss: {history.history['loss'][-1]:.6f}")
            print(f"  Final val_loss: {history.history['val_loss'][-1]:.6f}")
            
        except Exception as e:
            print(f"✗ ERROR training {coin}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("Phase 1 Training Complete!")
    print("="*70)

if __name__ == "__main__":
    train_phase1()
