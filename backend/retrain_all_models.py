#!/usr/bin/env python3
"""
Batch retraining script for all cryptocurrency models
Uses improved architecture and hyperparameters
"""

import sys
import os
from datetime import datetime
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor

def retrain_all_coins():
    """Retrain all supported coins with improved models"""
    
    # List of coins to retrain
    COINS = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']
    
    fetcher = DataFetcher()
    results = {}
    
    print("\n" + "="*70)
    print("🚀 BATCH RETRAINING ALL CRYPTO PRICE PREDICTION MODELS")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Retraining {len(COINS)} coins with improved architecture")
    print(f"   - Model: 4-layer Bidirectional LSTM (256→192→128→64 units)")
    print(f"   - Epochs: 150 with early stopping")
    print(f"   - Batch Size: 16 (smaller for better learning)")
    print(f"   - Features: All available technical indicators (20-75+ features)")
    print("="*70)
    
    for idx, coin in enumerate(COINS, 1):
        print(f"\n{'─'*70}")
        print(f"[{idx}/{len(COINS)}] 🪙 {coin}")
        print(f"{'─'*70}")
        
        start_time = time.time()
        
        try:
            # Get latest data for the coin
            print(f"📥 Fetching latest data for {coin}...")
            data = fetcher.prepare_data_for_model(coin)
            
            if data is None or len(data) < 100:
                print(f"❌ Insufficient data for {coin} (need >100 samples)")
                results[coin] = {
                    'status': 'FAILED',
                    'error': 'Insufficient data',
                    'duration': 0
                }
                continue
            
            print(f"✅ Data loaded: {len(data)} samples")
            
            # Train the model
            print(f"🔧 Initializing model for {coin}...")
            predictor = PricePredictor(coin)
            
            print(f"⏳ Training model (this may take 5-15 minutes)...")
            history = predictor.train(data, epochs=150, batch_size=16)
            
            # Calculate training time
            elapsed = time.time() - start_time
            
            # Get final metrics
            final_loss = history.history['loss'][-1]
            final_val_loss = history.history['val_loss'][-1]
            
            # Make a test prediction
            print(f"🔮 Making test prediction for {coin}...")
            prediction = predictor.predict(data)
            
            results[coin] = {
                'status': 'SUCCESS',
                'samples': len(data),
                'final_loss': float(final_loss),
                'final_val_loss': float(final_val_loss),
                'epochs_trained': len(history.history['loss']),
                'duration': elapsed,
                'current_price': prediction['current_price'],
                'predicted_price': prediction['predictions'][0]['price'] if prediction['predictions'] else 0
            }
            
            print(f"✅ {coin} training completed successfully!")
            print(f"   📊 Final Loss: {final_loss:.6f}")
            print(f"   📊 Validation Loss: {final_val_loss:.6f}")
            print(f"   ⏱️  Duration: {elapsed:.1f} seconds")
            print(f"   💰 Current: ${prediction['current_price']:,.2f}")
            print(f"   🔮 1-Day Forecast: ${prediction['predictions'][0]['price']:,.2f}")
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error training {coin}: {str(e)}")
            results[coin] = {
                'status': 'FAILED',
                'error': str(e),
                'duration': elapsed
            }
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📊 TRAINING SUMMARY")
    print(f"{'='*70}")
    
    successful = [coin for coin, result in results.items() if result['status'] == 'SUCCESS']
    failed = [coin for coin, result in results.items() if result['status'] == 'FAILED']
    
    print(f"\n✅ Successfully trained: {len(successful)}/{len(COINS)} coins")
    print(f"   {', '.join(successful)}")
    
    if failed:
        print(f"\n❌ Failed to train: {len(failed)}/{len(COINS)} coins")
        for coin in failed:
            error = results[coin].get('error', 'Unknown error')
            print(f"   {coin}: {error}")
    
    # Detailed results
    print(f"\n{'─'*70}")
    print("Detailed Results:")
    print(f"{'─'*70}")
    
    total_duration = 0
    for coin in COINS:
        result = results[coin]
        status_symbol = "✅" if result['status'] == 'SUCCESS' else "❌"
        
        print(f"{status_symbol} {coin:<10}", end="")
        
        if result['status'] == 'SUCCESS':
            print(f"Loss: {result['final_loss']:.6f} | Val Loss: {result['final_val_loss']:.6f} | Time: {result['duration']:.0f}s")
            total_duration += result['duration']
        else:
            print(f"Error: {result.get('error', 'Unknown')}")
    
    print(f"\n{'─'*70}")
    print(f"⏱️  Total training time: {total_duration/60:.1f} minutes ({total_duration:.0f} seconds)")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # Save results to file
    import json
    results_file = 'retraining_results.json'
    with open(results_file, 'w') as f:
        # Convert non-serializable types
        results_to_save = {}
        for coin, result in results.items():
            results_to_save[coin] = {k: float(v) if isinstance(v, (int, float)) else v for k, v in result.items()}
        
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_coins': len(COINS),
            'successful': len(successful),
            'failed': len(failed),
            'total_duration_seconds': total_duration,
            'results': results_to_save
        }, f, indent=2)
    
    print(f"💾 Detailed results saved to: {results_file}")
    print(f"\n🎉 Retraining complete!")

if __name__ == "__main__":
    retrain_all_coins()
