"""
train_ensemble.py
Comprehensive trainer for Phase 12 Ensemble System.
Trains 3 architectures (Attention-LSTM, GRU, Transformer) for each coin.

Run from project root:
    venv\Scripts\python train_ensemble.py
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add backend/ to path so 'data' and 'models' modules resolve
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# ---- now safe to import ----
from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor, EnsemblePredictor

coins = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']
model_types = ['attention_lstm', 'gru', 'transformer']

fetcher = DataFetcher()
overall_results = []

print(f"\n{'='*80}")
print(f"🚀  PHASE 12: ENSEMBLE TRAINING SYSTEM STARTING")
print(f"    Architectures: {', '.join(model_types)}")
print(f"    Features     : Price + Sentiment (FNG) + External Market (SP500, DXY, GOLD)")
print(f"{'='*80}\n")

for coin in coins:
    print(f"\n{'#'*70}")
    print(f"##  Training Ensemble for {coin}")
    print(f"{'#'*70}")

    data = fetcher.prepare_data_for_model(coin, include_sentiment=True, include_external=True)

    if data is not None and len(data) > 100:
        epoch_settings = {
            'attention_lstm': 100,
            'gru': 100,
            'transformer': 150  # Transformers often need more epochs to stabilise
        }
        
        for mt in model_types:
            print(f"\n>>> Training variant: {mt.upper()}")
            
            # Setup specific paths for this coin + architecture
            predictor = PricePredictor(coin, model_dir='backend/models/saved')
            predictor.model_path = os.path.join('backend/models/saved', f'{coin}_{mt}_model.h5')
            predictor.config_path = os.path.join('backend/models/saved', f'{coin}_{mt}_config.json')
            
            history = predictor.train(data, epochs=epoch_settings[mt], batch_size=16, model_type=mt)
            
            val_loss = float(history.history['val_loss'][-1])
            overall_results.append({
                'coin': coin,
                'model': mt,
                'val_loss': val_loss,
                'epochs': len(history.history['loss'])
            })
            
        # Final test of the ensemble
        print(f"\n>>> Verifying {coin} Ensemble...")
        ensemble = EnsemblePredictor(coin, model_dir='backend/models/saved')
        try:
            res = ensemble.predict(data)
            print(f"✅ Ensemble valid for {coin}")
            print(f"   Pred: ${res['predictions'][0]['price']:,.2f} ({res['predictions'][0]['change_percent']:+.2f}%)")
        except Exception as e:
            print(f"❌ Ensemble test failed for {coin}: {e}")

    else:
        print(f"❌ Insufficient data for {coin}")

print(f"\n{'='*80}")
print("✅  Phase 12 Ensemble Training Complete")
print(f"{'='*80}")

# Detailed Summary
summary_df = pd.DataFrame(overall_results)
print("\nValidation Loss Summary:")
print(summary_df.pivot(index='coin', columns='model', values='val_loss'))
