"""
retrain_phase12.py
Launcher for Phase 12 — BiLSTM + Attention + Sentiment + External Market Data.

Run from project root:
    venv\Scripts\python retrain_phase12.py
"""
import sys
import os
import pandas as pd

# Add backend/ to path so 'data' and 'models' modules resolve
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# ---- now safe to import ----
from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor

coins = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']

fetcher = DataFetcher()
results = []

for coin in coins:
    print(f"\n{'='*70}")
    print(f"  Training {coin}  [Phase 12 - BiLSTM + Attention + Sentiment + External]")
    print(f"{'='*70}")

    # Phase 12: include_external=True is now default in DataFetcher.prepare_data_for_model
    data = fetcher.prepare_data_for_model(coin, include_sentiment=True, include_external=True)

    if data is not None and len(data) > 100:
        predictor = PricePredictor(coin, model_dir='backend/models/saved')
        
        # We'll use 150 epochs with early stopping to ensure convergence with more features
        history = predictor.train(data, epochs=150, batch_size=16)

        prediction = predictor.predict(data)
        print(f"\n📈 {coin} Prediction:")
        print(f"   Current : ${prediction['current_price']:,.2f}")
        for p in prediction['predictions']:
            print(f"   {p['date']} : ${p['price']:,.2f}  ({p['change_percent']:+.2f}%)")
        
        print(f"   Features: {prediction['model_info']['num_features']}")
        print(f"   Architecture: {prediction['model_info']['architecture']}")

        results.append({
            'coin': coin,
            'val_loss': float(history.history['val_loss'][-1]),
            'epochs': len(history.history['loss']),
            'features': data.shape[1]
        })
    else:
        print(f"❌ Insufficient data for {coin}")

print(f"\n{'='*70}")
print("✅  Phase 12 Training Complete — Results Summary:")
print(f"{'='*70}")
for r in results:
    print(f"  {r['coin']:8s}  val_loss={r['val_loss']:.6f}  epochs={r['epochs']:3d}  features={r['features']}")
