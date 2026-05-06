# ML Model Performance & Parameters Report

## 1. Model Architecture Summary

| Attribute | Value |
|-----------|-------|
| **Model Type** | Bidirectional LSTM (4 layers) |
| **Task** | Time-series cryptocurrency price prediction |
| **Target Variable** | Next-day closing price |
| **Output Type** | Regression (continuous price values) |

---

## 2. Main Parameters Considered

### Input/Sequence Parameters
| Parameter | Value |
|-----------|-------|
| Lookback window | 60 days |
| Prediction horizon | 1 day ahead |
| Total features used | 10+ (Close, Volume, MA7, MA21, MA50, RSI, MACD, etc.) |
| Training/Test split | 80% / 20% (time-based) |

### Model Architecture Parameters
| Layer | Units | Activation | Return Sequences |
|-------|-------|-----------|-----------------|
| LSTM Layer 1 (Bidirectional) | 256 | tanh | True |
| LSTM Layer 2 (Bidirectional) | 192 | tanh | True |
| LSTM Layer 3 (Bidirectional) | 128 | tanh | True |
| LSTM Layer 4 (Bidirectional) | 64 | tanh | False |
| Dense Layer 1 | 64 | ReLU | - |
| Dense Layer 2 | 32 | ReLU | - |
| Output Layer | 1 | Linear | - |

### Regularization Parameters
| Parameter | Value |
|-----------|-------|
| Dropout rate (Layer 1-2) | 0.30 |
| Dropout rate (Layer 3) | 0.25 |
| Dropout rate (Layer 4) | 0.20 |
| Dropout rate (Dense layers) | 0.20 |
| Batch Normalization | Applied after each layer |

### Training Parameters
| Parameter | Value |
|-----------|-------|
| Optimizer | Adam |
| Learning rate | 0.001 |
| Loss function | Huber |
| Batch size | 16 |
| Max epochs | 150 |
| Early stopping patience | 20 epochs |
| Learning rate reduction factor | 0.5 (when plateau) |
| Validation split | 20% |

---

## 3. Model Performance Metrics (Latest Training Results)

### Individual Coin Performance (as of March 23, 2026)

| Coin | Training Loss | Validation Loss | Epochs Trained | Training Duration | Samples |
|------|---------------|-----------------|-----------------|-------------------|---------|
| **BTC** | 0.00273 | 0.00124 | 100 | 3,122s | 1,777 |
| **ETH** | 0.00381 | 0.00380 | 35 | 625s | 1,777 |
| **SOLANA** | 0.00501 | 0.00196 | 51 | 1,578s | 1,777 |
| **BNB** | 0.00198 | 0.01641 | 35 | 805s | 1,777 |
| **DOGE** | 0.00281 | 0.00103 | 41 | 1,422s | 1,777 |
| **XRP** | 0.00271 | 0.00218 | 86 | 1,370s | 1,777 |
| **ADA** | 0.00408 | 0.00099 | 33 | 695s | 1,777 |
| **AVAX** | 0.00394 | 0.00039 | 39 | 1,375s | 1,777 |
| **DOT** | 0.00350 | 0.00032 | 45 | 1,445s | 1,777 |
| **LINK** | - | - | - | - | 1,777 |

### Accuracy Metrics (from 30-day backtest)

The model uses **Directional Accuracy** and **MAPE** (Mean Absolute Percentage Error) as primary metrics:

| Metric | Description |
|--------|-------------|
| **Directional Accuracy** | % of times the model correctly predicted whether price would go up or down |
| **MAPE** | Mean Absolute Percentage Error - average error as % of actual price |

---

## 4. Feature Engineering

### Features used for training:
- **Price indicators**: Close, Open, High, Low, Volume
- **Moving Averages**: MA7, MA21, MA50
- **Momentum indicators**: RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence)
- **Data preprocessing**: MinMax scaling (0-1 range), forward/backward fill for missing values

---

## 5. Model Strengths & Characteristics

| Aspect | Details |
|--------|---------|
| **Sequence Learning** | Bidirectional LSTM captures patterns in both past-to-future and future-to-past directions |
| **Regularization** | Multiple dropout layers + batch normalization prevent overfitting |
| **Adaptability** | Early stopping and learning rate reduction ensure convergence |
| **Multi-coin support** | Separate models trained for 10 cryptocurrencies |
| **Real-time prediction** | Can predict next-day price given last 60 days of data |

---

## 6. Key Metrics Interpretation

- **Training Loss**: Lower is better (model fit quality)
- **Validation Loss**: Critical indicator of generalization (not overfitting)
- **Directional Accuracy**: > 50% means better than random guessing
- **MAPE < 5%**: Excellent; 5-10%: Good; 10-20%: Acceptable; > 20%: Needs improvement

---

*Report generated for cryptocurrency price prediction system using deep learning*
