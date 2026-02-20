import pandas as pd
import numpy as np
from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def evaluate_model_accuracy(coin='BTC', days_to_test=30):
    """
    Backtest model predictions against actual prices
    """
    print(f"\n{'='*70}")
    print(f"Evaluating {coin} Model Accuracy")
    print(f"{'='*70}\n")
    
    fetcher = DataFetcher()
    df = fetcher.prepare_data_for_model(coin)
    
    if df is None or len(df) < 100:
        print("Insufficient data.")
        return None

    predictor = PricePredictor(coin)
    if not predictor.load_model():
        print("No trained model found.")
        return None

    # Get config
    import json
    with open(predictor.config_path, 'r') as f:
        config = json.load(f)
    
    feature_cols = config['feature_cols']
    available_cols = [col for col in feature_cols if col in df.columns]
    
    lookback = predictor.lookback
    scaled_data = predictor.scaler.transform(df[available_cols].values)
    close_idx = available_cols.index('Close')
    
    correct_direction = 0
    total_predictions = 0
    errors = []
    
    start_idx = len(df) - days_to_test
    
    for i in range(start_idx, len(df)):
        if i < lookback:
            continue
            
        input_seq = scaled_data[i-lookback : i]
        input_seq = np.array([input_seq])
        
        predicted_scaled = predictor.model.predict(input_seq, verbose=0)
        
        dummy = np.zeros((1, len(available_cols)))
        dummy[0, close_idx] = predicted_scaled[0][0]
        predicted_price = predictor.scaler.inverse_transform(dummy)[0, close_idx]
        
        actual_price = df['Close'].iloc[i]
        prev_price = df['Close'].iloc[i-1]
        
        error_pct = abs(predicted_price - actual_price) / actual_price * 100
        errors.append(error_pct)
        
        pred_move = predicted_price - prev_price
        actual_move = actual_price - prev_price
        
        same_direction = (pred_move > 0 and actual_move > 0) or (pred_move < 0 and actual_move < 0)
        if same_direction:
            correct_direction += 1
            
        total_predictions += 1
    
    directional_accuracy = (correct_direction / total_predictions * 100) if total_predictions > 0 else 0
    mape = sum(errors) / len(errors) if errors else 0
    
    return {
        'coin': coin,
        'directional_accuracy': directional_accuracy,
        'correct': correct_direction,
        'total': total_predictions,
        'mape': mape
    }

if __name__ == "__main__":
    coins = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']
    
    print("\n" + "="*70)
    print("MODEL ACCURACY REPORT (Last 30 Days)")
    print("="*70)
    
    results = []
    for coin in coins:
        result = evaluate_model_accuracy(coin, days_to_test=30)
        if result:
            results.append(result)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'Coin':<10} {'Directional Accuracy':<25} {'Avg Error (MAPE)':<20}")
    print("-"*70)
    
    for r in results:
        print(f"{r['coin']:<10} {r['correct']}/{r['total']} ({r['directional_accuracy']:.1f}%){' '*8} {r['mape']:.2f}%")
    
    if results:
        avg_accuracy = sum(r['directional_accuracy'] for r in results) / len(results)
        avg_mape = sum(r['mape'] for r in results) / len(results)
        
        print("-"*70)
        print(f"{'AVERAGE':<10} {avg_accuracy:.1f}%{' '*23} {avg_mape:.2f}%")
        print("="*70)
