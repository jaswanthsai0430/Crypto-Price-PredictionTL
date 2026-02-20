from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

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
            'train': '/api/train/<coin>'
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
        # Get current price
        current = data_fetcher.get_current_price(coin)
        
        # Get historical data
        historical = data_fetcher.get_historical_data(coin, period='1mo', interval='1d')

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

if __name__ == '__main__':
    print("Starting Crypto Analysis API...")
    print(f"Supported coins: {', '.join(SUPPORTED_COINS)}")
    print("API running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
