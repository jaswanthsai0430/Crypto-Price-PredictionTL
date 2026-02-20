import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization, Attention
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam
import os
import pickle
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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
        self.prediction_days = 1  # Predict next 1 day
        
    def create_model(self, input_shape):
        """
        Create improved LSTM model architecture with better hyperparameters
        
        Args:
            input_shape: Shape of input data (lookback, features)
        
        Returns:
            Compiled Keras model
        """
        model = Sequential([
            # First Bidirectional LSTM layer - processes sequence forward and backward
            Bidirectional(LSTM(256, return_sequences=True), input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.3),
            
            # Second Bidirectional LSTM layer
            Bidirectional(LSTM(192, return_sequences=True)),
            BatchNormalization(),
            Dropout(0.3),
            
            # Third Bidirectional LSTM layer
            Bidirectional(LSTM(128, return_sequences=True)),
            BatchNormalization(),
            Dropout(0.25),
            
            # Fourth Bidirectional LSTM layer
            Bidirectional(LSTM(64, return_sequences=False)),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers for final prediction
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            
            Dense(self.prediction_days)  # Predict next 1 day
        ])
        
        # Use optimized Adam optimizer with custom learning rate
        optimizer = Adam(learning_rate=0.001)
        
        model.compile(
            optimizer=optimizer,
            loss='huber',
            metrics=['mae', 'mse']
        )
        
        return model
    
    def prepare_sequences(self, data, target_col='Close'):
        """
        Prepare sequences for LSTM training using all available features
        
        Args:
            data: DataFrame with features
            target_col: Column to predict
        
        Returns:
            X, y arrays for training
        """
        # Use all available numeric columns except Date as features
        exclude_cols = ['Date', 'Unnamed: 0']
        feature_cols = [col for col in data.columns if col not in exclude_cols and data[col].dtype in ['float64', 'int64']]
        
        # Ensure Close is in features
        if 'Close' not in feature_cols:
            print("Warning: 'Close' column not found in features")
            feature_cols = ['Close', 'Volume', 'MA7', 'MA21', 'MA50', 'RSI', 'MACD']
        
        available_cols = [col for col in feature_cols if col in data.columns]
        
        if not available_cols:
            raise ValueError("No valid feature columns found in data")
        
        print(f"Using {len(available_cols)} features for training: {available_cols[:10]}..." if len(available_cols) > 10 else f"Using {len(available_cols)} features: {available_cols}")
        
        # Extract features
        features = data[available_cols].values
        
        # Handle NaN values - forward fill then backward fill
        df_features = pd.DataFrame(features, columns=available_cols)
        df_features = df_features.fillna(method='ffill').fillna(method='bfill')
        features = df_features.values
        
        # Scale features
        scaled_data = self.scaler.fit_transform(features)
        
        X, y = [], []
        
        # Create sequences
        for i in range(self.lookback, len(scaled_data) - self.prediction_days):
            X.append(scaled_data[i - self.lookback:i])
            
            # Target is the closing price for next days
            close_idx = available_cols.index('Close')
            y.append(scaled_data[i:i + self.prediction_days, close_idx])
        
        return np.array(X), np.array(y), available_cols
    
    def train(self, data, epochs=150, batch_size=16, validation_split=0.2):
        """
        Train the LSTM model with improved hyperparameters
        
        Args:
            data: DataFrame with historical price data and indicators
            epochs: Number of training epochs (default 150 for better convergence)
            batch_size: Batch size for training (smaller for more frequent updates)
            validation_split: Fraction of data for validation
        
        Returns:
            Training history
        """
        print(f"\n{'='*70}")
        print(f"🚀 Training Improved Model for {self.coin}")
        print(f"{'='*70}")
        
        # Prepare sequences
        X, y, feature_cols = self.prepare_sequences(data)
        
        print(f"📊 Training data shape: X={X.shape}, y={y.shape}")
        print(f"📈 Total samples: {len(X)}")
        
        # Split data using time-based split (more realistic for time series)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"📚 Train samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        # Create model
        self.model = self.create_model(input_shape=(X.shape[1], X.shape[2]))
        
        print(f"\n🔧 Model Architecture:")
        print(self.model.summary())
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=20,  # Increased patience
            restore_best_weights=True,
            verbose=1
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
            patience=8,
            min_lr=0.00001,
            verbose=1
        )
        
        # Train model
        print(f"\n⏳ Starting training... (this may take a few minutes)")
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
            'final_val_loss': float(history.history['val_loss'][-1]),
            'epochs_trained': len(history.history['loss']),
            'num_features': len(feature_cols)
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Model trained and saved to {self.model_path}")
        print(f"📊 Final Training Loss: {history.history['loss'][-1]:.6f}")
        print(f"📊 Final Validation Loss: {history.history['val_loss'][-1]:.6f}")
        print(f"🔢 Features used: {len(feature_cols)}")
        
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
        Make price predictions for next days
        
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
        
        # Reshape prediction if it's 1D but we need to assign it to a 2D slice
        if self.prediction_days == 1:
             dummy[0, close_idx] = prediction_scaled[0][0]
             prediction = self.scaler.inverse_transform(dummy)[0, close_idx]
             # Make it a list/array for consistent processing below
             prediction = [prediction]
        else:
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
    
    for coin in ['BTC', 'ETH', 'SOLANA', 'BNB', 'DOGE', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK']:
        print(f"\n{'='*70}")
        print(f"Training model for {coin}")
        print(f"{'='*70}")
        
        # Get data
        data = fetcher.prepare_data_for_model(coin)
        
        if data is not None and len(data) > 100:
            # Train model with improved hyperparameters
            predictor = PricePredictor(coin)
            history = predictor.train(data, epochs=150, batch_size=16)
            
            # Make prediction
            prediction = predictor.predict(data)
            print(f"\nPredictions for {coin}:")
            print(f"Current Price: ${prediction['current_price']:,.2f}")
            for pred in prediction['predictions']:
                print(f"  {pred['date']}: ${pred['price']:,.2f} ({pred['change_percent']:+.2f}%)")
        else:
            print(f"❌ Insufficient data for {coin}")

