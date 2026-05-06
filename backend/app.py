from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_fetcher import DataFetcher
from models.price_predictor import PricePredictor
from models.sentiment_analyzer import SentimentAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize components
data_fetcher = DataFetcher()
sentiment_analyzer = SentimentAnalyzer()

# Supported coins
SUPPORTED_COINS = ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Crypto Price Prediction & Sentiment Analysis API',
        'version': '1.0',
        'endpoints': {
            'current_price': '/api/price/<coin>',
            'predict': '/api/predict/<coin>',
            'sentiment': '/api/sentiment/<coin>',
            'train': '/api/train/<coin>',
            'plot_comparison': '/api/plot/<coin>?days=30',
            'all_data': '/api/all/<coin>?period=1mo&interval=1d'
        },
        'supported_coins': SUPPORTED_COINS
    })

@app.route('/api/price/<coin>', methods=['GET'])
def get_price(coin):
    """Get current price and historical data for a coin"""
    coin = coin.upper()
    
    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400
    
    try:
        # Get current price
        current = data_fetcher.get_current_price(coin)
        
        # Get recent historical data (last 30 days for chart)
        historical = data_fetcher.get_historical_data(coin, period='1mo', interval='1d')
        
        if historical is not None:
            # Convert to list of dictionaries for JSON
            chart_data = []
            for idx, row in historical.iterrows():
                chart_data.append({
                    'date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })
        else:
            chart_data = []
        
        return jsonify({
            'success': True,
            'current': current,
            'historical': chart_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/<coin>', methods=['GET'])
def predict_price(coin):
    """Get price predictions for a coin"""
    coin = coin.upper()
    
    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400
    
    try:
        # Get prepared data
        data = data_fetcher.prepare_data_for_model(coin)
        
        if data is None or len(data) < 60:
            return jsonify({'error': 'Insufficient data for prediction'}), 500
        
        # Initialize predictor
        predictor = PricePredictor(coin)
        
        # Try to load existing model, if not found, train a new one
        if not predictor.load_model():
            print(f"No model found for {coin}, training new model...")
            predictor.train(data, epochs=30, batch_size=32)
        
        # Make prediction
        prediction = predictor.predict(data)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<coin>', methods=['GET'])
def get_sentiment(coin):
    """Get sentiment analysis for a coin"""
    coin = coin.upper()
    
    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400
    
    try:
        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze_news_sentiment(coin)
        
        return jsonify({
            'success': True,
            'sentiment': sentiment
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train/<coin>', methods=['POST'])
def train_model(coin):
    """Train or retrain model for a coin"""
    coin = coin.upper()
    
    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400
    
    try:
        # Get data
        data = data_fetcher.prepare_data_for_model(coin)
        
        if data is None or len(data) < 100:
            return jsonify({'error': 'Insufficient data for training'}), 500
        
        # Get training parameters from request
        epochs = request.json.get('epochs', 30) if request.json else 30
        batch_size = request.json.get('batch_size', 32) if request.json else 32
        
        # Train model
        predictor = PricePredictor(coin)
        history = predictor.train(data, epochs=epochs, batch_size=batch_size)
        
        return jsonify({
            'success': True,
            'message': f'Model trained successfully for {coin}',
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/all/<coin>', methods=['GET'])
def get_all_data(coin):
    """Get all data for a coin (price, prediction, sentiment)"""
    coin = coin.upper()
    
    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400
    
    try:
        # Get timeframe params from query string
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        print(f"Fetch request for {coin}: period={period}, interval={interval}")

        # Get current price
        current = data_fetcher.get_current_price(coin)
        
        # Get historical data with timeframe support
        historical = data_fetcher.get_historical_data(coin, period=period, interval=interval)

        if historical is not None:
            chart_data = []
            for idx, row in historical.iterrows():
                chart_data.append({
                    'date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                })
        else:
            chart_data = []
        
        # Get prediction
        data = data_fetcher.prepare_data_for_model(coin)
        predictor = PricePredictor(coin)
        
        if not predictor.load_model():
            predictor.train(data, epochs=30, batch_size=32)
        
        prediction = predictor.predict(data)
        
        # Get sentiment
        sentiment = sentiment_analyzer.analyze_news_sentiment(coin)
        
        return jsonify({
            'success': True,
            'coin': coin,
            'current': current,
            'historical': chart_data,
            'prediction': prediction,
            'sentiment': sentiment
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plot/<coin>', methods=['GET'])
def get_price_comparison_plot(coin):
    """Generate comparison plot of actual vs predicted prices"""
    coin = coin.upper()

    if coin not in SUPPORTED_COINS:
        return jsonify({'error': f'Unsupported coin: {coin}'}), 400

    try:
        # Get parameters
        days = int(request.args.get('days', 30))  # Number of days to plot

        # Get historical data
        data = data_fetcher.prepare_data_for_model(coin)

        if data is None or len(data) < 60:
            return jsonify({'error': 'Insufficient data for plotting'}), 500

        # Initialize predictor
        predictor = PricePredictor(coin)

        # Try to load existing model
        if not predictor.load_model():
            return jsonify({'error': 'No trained model found for this coin'}), 500

        # Generate predictions for the last 'days' period
        actual_prices = []
        predicted_prices = []
        dates = []

        # Use the last 'days' of data for plotting
        plot_data = data.tail(days + predictor.lookback).copy()

        for i in range(len(plot_data) - predictor.lookback):
            # Get actual price for this day
            actual_price = plot_data['Close'].iloc[i + predictor.lookback]
            actual_prices.append(actual_price)

            # Get prediction for this day (using data up to this point)
            pred_data = plot_data.iloc[i:i + predictor.lookback]
            prediction = predictor.predict(pred_data)

            if prediction and 'predictions' in prediction and len(prediction['predictions']) > 0:
                predicted_prices.append(prediction['predictions'][0]['price'])
            else:
                predicted_prices.append(None)

            # Get date
            date = plot_data.index[i + predictor.lookback] if hasattr(plot_data.index[i + predictor.lookback], 'strftime') else pd.to_datetime(plot_data['Date'].iloc[i + predictor.lookback])
            dates.append(date)

        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.style.use('default')  # Use default style for clean look

        # Plot actual prices
        plt.plot(dates, actual_prices, label='Actual Price', color='#1f77b4', linewidth=2, marker='o', markersize=3)

        # Plot predicted prices (only where we have predictions)
        valid_predictions = [(d, p) for d, p in zip(dates, predicted_prices) if p is not None]
        if valid_predictions:
            pred_dates, pred_prices = zip(*valid_predictions)
            plt.plot(pred_dates, pred_prices, label='Predicted Price', color='#ff7f0e', linewidth=2, linestyle='--', marker='s', markersize=3)

        # Formatting
        plt.title(f'{coin} Price: Actual vs Predicted (Last {days} Days)', fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price (USD)', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)

        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
        plt.xticks(rotation=45, ha='right')

        # Tight layout
        plt.tight_layout()

        # Convert plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({
            'success': True,
            'coin': coin,
            'plot_data': image_base64,
            'plot_type': 'png',
            'days': days,
            'description': f'Comparison plot showing actual vs predicted {coin} prices over the last {days} days'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Crypto Analysis API...")
    print(f"Supported coins: {', '.join(SUPPORTED_COINS)}")
    print("API running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
