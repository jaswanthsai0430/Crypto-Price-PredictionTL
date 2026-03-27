"""
retrain_phase11.py
Root-level launcher — sets sys.path correctly, then calls the
price_predictor training script.

Run from project root:
    venv\Scripts\python retrain_phase11.py
"""
import sys
import os

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
    print(f"  Training {coin}  [Phase 11 - BiLSTM + Attention + Sentiment]")
    print(f"{'='*70}")

    data = fetcher.prepare_data_for_model(coin, include_sentiment=True)

    if data is not None and len(data) > 100:
        predictor = PricePredictor(coin, model_dir='backend/models/saved')
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
print("✅  Phase 11 Training Complete — Results Summary:")
print(f"{'='*70}")
for r in results:
    print(f"  {r['coin']:8s}  val_loss={r['val_loss']:.6f}  epochs={r['epochs']:3d}  features={r['features']}")
