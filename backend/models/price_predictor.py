import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import os
import pickle
import json
from datetime import datetime, timedelta

class PricePredictor:
    def __init__(self, coin, model_dir='models/saved'):
        self.coin = coin
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, f'{coin}_model.h5')
        self.scaler_path = os.path.join(model_dir, f'{coin}_scaler.pkl')
        self.config_path = os.path.join(model_dir, f'{coin}_config.json')
        
        os.makedirs(model_dir, exist_ok=True)
        
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.lookback = 60  # Use 60 days of historical data
        self.prediction_days = 3  # Predict next 3 days
        
    def create_model(self, input_shape):
        """
        Create LSTM model architecture
        
        Args:
            input_shape: Shape of input data (lookback, features)
        
        Returns:
            Compiled Keras model
        """
        model = Sequential([
            # First Bidirectional LSTM layer - processes sequence forward and backward
            Bidirectional(LSTM(128, return_sequences=True), input_shape=input_shape),
            BatchNormalization(),  # Normalizes activations for better training
            Dropout(0.3),
            
            # Second Bidirectional LSTM layer
            Bidirectional(LSTM(64, return_sequences=True)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Third Bidirectional LSTM layer
            Bidirectional(LSTM(32, return_sequences=False)),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers for final prediction
            Dense(16, activation='relu'),
            BatchNormalization(),
            Dense(self.prediction_days)  # Predict next 3 days
        ])
        
        # Use Huber loss - more robust to outliers than MSE
        model.compile(
            optimizer='adam',
            loss='huber',  # Better for Bidirectional LSTM
            metrics=['mae', 'mse']
        )
        
        return model
    
    def prepare_sequences(self, data, target_col='Close'):
        """
        Prepare sequences for LSTM training
        
        Args:
            data: DataFrame with features
            target_col: Column to predict
        
        Returns:
            X, y arrays for training
        """
        # Select features for training
        feature_cols = ['Close', 'Volume', 'MA7', 'MA21', 'RSI', 'MACD']
        
        # Filter available columns
        available_cols = [col for col in feature_cols if col in data.columns]
        
        if not available_cols:
            raise ValueError("No valid feature columns found in data")
        
        # Extract features
        features = data[available_cols].values
        
        # Scale features
        scaled_data = self.scaler.fit_transform(features)
        
        X, y = [], []
        
        # Create sequences
        for i in range(self.lookback, len(scaled_data) - self.prediction_days):
            X.append(scaled_data[i - self.lookback:i])
            
            # Target is the closing price for next 3 days
            close_idx = available_cols.index('Close')
            y.append(scaled_data[i:i + self.prediction_days, close_idx])
        
        return np.array(X), np.array(y), available_cols
    
    def train(self, data, epochs=100, batch_size=32, validation_split=0.2):
        """
        Train the LSTM model
        
        Args:
            data: DataFrame with historical price data and indicators
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data for validation
        
        Returns:
            Training history
        """
        print(f"Training model for {self.coin}...")
        
        # Prepare sequences
        X, y, feature_cols = self.prepare_sequences(data)
        
        print(f"Training data shape: X={X.shape}, y={y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Create model
        self.model = self.create_model(input_shape=(X.shape[1], X.shape[2]))
        
        print(self.model.summary())
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=15,  # Increased patience for Bidirectional LSTM
            restore_best_weights=True
        )
        
        checkpoint = ModelCheckpoint(
            self.model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
        
        # Reduce learning rate when validation loss plateaus
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001,
            verbose=1
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stop, checkpoint, reduce_lr],
            verbose=1
        )
        
        # Save scaler
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save config
        config = {
            'coin': self.coin,
            'lookback': self.lookback,
            'prediction_days': self.prediction_days,
            'feature_cols': feature_cols,
            'trained_date': datetime.now().isoformat(),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1])
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Model trained and saved to {self.model_path}")
        
        return history
    
    def load_model(self):
        """Load trained model and scaler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = load_model(self.model_path)
            
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            print(f"Model loaded for {self.coin}")
            return True
        else:
            print(f"No saved model found for {self.coin}")
            return False
    
    def predict(self, data):
        """
        Make price predictions for next 3 days
        
        Args:
            data: Recent historical data (at least lookback days)
        
        Returns:
            Dictionary with predictions
        """
        if self.model is None:
            if not self.load_model():
                raise ValueError(f"No trained model available for {self.coin}")
        
        # Load config to get feature columns
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        feature_cols = config['feature_cols']
        
        # Prepare input data
        available_cols = [col for col in feature_cols if col in data.columns]
        features = data[available_cols].tail(self.lookback).values
        
        # Scale features
        scaled_data = self.scaler.transform(features)
        
        # Reshape for LSTM
        X = np.array([scaled_data])
        
        # Make prediction
        prediction_scaled = self.model.predict(X, verbose=0)
        
        # Inverse transform predictions
        # Create dummy array with same shape as original features
        dummy = np.zeros((self.prediction_days, len(available_cols)))
        close_idx = available_cols.index('Close')
        dummy[:, close_idx] = prediction_scaled[0]
        
        prediction = self.scaler.inverse_transform(dummy)[:, close_idx]
        
        # Get current price
        current_price = data['Close'].iloc[-1]
        
        # Calculate prediction dates
        last_date = data.index[-1] if isinstance(data.index[-1], pd.Timestamp) else pd.to_datetime(data['Date'].iloc[-1])
        
        predictions = []
        for i in range(self.prediction_days):
            pred_date = last_date + timedelta(days=i+1)
            pred_price = float(prediction[i])
            change_pct = ((pred_price - current_price) / current_price) * 100
            
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'price': pred_price,
                'change_percent': change_pct
            })
        
        return {
            'coin': self.coin,
            'current_price': float(current_price),
            'predictions': predictions,
            'model_info': {
                'trained_date': config['trained_date'],
                'lookback_days': self.lookback
            }
        }

if __name__ == "__main__":
    # Test the predictor
    from data.data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    
    for coin in ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE']:
        print(f"\n{'='*60}")
        print(f"Training model for {coin}")
        print(f"{'='*60}")
        
        # Get data
        data = fetcher.prepare_data_for_model(coin)
        
        if data is not None and len(data) > 100:
            # Train model
            predictor = PricePredictor(coin)
            history = predictor.train(data, epochs=30, batch_size=32)
            
            # Make prediction
            prediction = predictor.predict(data)
            print(f"\nPredictions for {coin}:")
            print(f"Current Price: ${prediction['current_price']:,.2f}")
            for pred in prediction['predictions']:
                print(f"  {pred['date']}: ${pred['price']:,.2f} ({pred['change_percent']:+.2f}%)")

