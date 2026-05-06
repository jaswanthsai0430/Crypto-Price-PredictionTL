#!/usr/bin/env python3
"""
Test script for the new plot comparison feature
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor
import matplotlib.pyplot as plt
import pandas as pd

def test_plot_functionality():
    """Test the plot generation functionality"""
    print("Testing plot functionality...")

    # Test with BTC
    coin = 'BTC'
    fetcher = DataFetcher()
    predictor = PricePredictor(coin)

    # Get data
    data = fetcher.prepare_data_for_model(coin)
    if data is None or len(data) < 100:
        print("Insufficient data for testing")
        return

    print(f"Data shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")

    # Load model
    if not predictor.load_model():
        print("No trained model found")
        return

    # Test prediction
    prediction = predictor.predict(data)
    print(f"Prediction result: {prediction}")

    # Test basic plotting
    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'].tail(30), data['Close'].tail(30))
    plt.title(f'{coin} Price Test Plot')
    plt.savefig('test_plot.png')
    plt.close()

    print("Plot test completed successfully!")
    print("New plot endpoint should work at: /api/plot/<coin>?days=30")

if __name__ == "__main__":
    test_plot_functionality()