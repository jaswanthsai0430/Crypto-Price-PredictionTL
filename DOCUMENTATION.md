# CP.AI — CryptoPredict AI
## Full Technical Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Backend: Flask REST API](#3-backend-flask-rest-api)
4. [Data Pipeline](#4-data-pipeline)
5. [Feature Engineering (75+ Features)](#5-feature-engineering-75-features)
6. [Machine Learning Model (Bidirectional LSTM)](#6-machine-learning-model-bidirectional-lstm)
7. [Sentiment Analysis Engine](#7-sentiment-analysis-engine)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Crypto Education Hub](#9-crypto-education-hub)
10. [Libraries & Dependencies](#10-libraries--dependencies)
11. [ML Evaluation & Performance](#11-ml-evaluation-and-performance)
12. [How to Run](#12-how-to-run)

---

## 1. Project Overview

**CP.AI** is an AI-powered full-stack web application for:

- 📈 **Real-time price tracking** of 10 major cryptocurrencies
- 🤖 **Next-day price prediction** using a deep Bidirectional LSTM model
- 📰 **Market sentiment analysis** from live crypto news (VADER NLP)
- 📊 **Professional trading charts** with candlesticks, volume, and technical indicators
- 📚 **Crypto Education Hub** with 9 chapters, interactive calculators, and embedded videos

**Supported Coins:** `BTC`, `ETH`, `SOLANA`, `BNB`, `DOGE`, `XRP`, `ADA`, `AVAX`, `DOT`, `LINK`

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser)                 │
│  ┌─────────────┐   ┌───────────────┐   ┌───────────┐  │
│  │  index.html │   │  learn.html   │   │  CSS / JS │  │
│  │  Dashboard  │   │  Education    │   │  Layer    │  │
│  └──────┬──────┘   └───────────────┘   └───────────┘  │
│         │ HTTP fetch (AJAX)                            │
└─────────┼────────────────────────────────────────────-─┘
          │
          ▼  localhost:5000
┌─────────────────────────────────────────────────────┐
│              BACKEND (Flask REST API)               │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │
│  │ DataFetcher  │  │ PricePredictor│  │Sentiment │ │
│  │ (yfinance)   │  │ (Bi-LSTM)     │  │Analyzer  │ │
│  └──────┬───────┘  └──────┬────────┘  └────┬─────┘ │
└─────────┼─────────────────┼────────────────┼───────┘
          │                 │                 │
          ▼                 ▼                 ▼
   Yahoo Finance      models/saved/      NewsAPI /
   CryptoCompare    (.h5, .pkl, .json)  CoinGecko News
```

### Request Flow
1. Browser makes `GET /api/all/<COIN>` every 60 seconds
2. Flask fetches OHLCV from **yfinance**
3. Flask loads/runs the **Bi-LSTM model** for prediction
4. Flask fetches news and runs **VADER sentiment**
5. All data returned as JSON to the browser
6. Browser updates chart, price bar, sentiment ring, and forecast cards

---

## 3. Backend: Flask REST API

**File:** `backend/app.py`  
**Port:** `5000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info & supported coins |
| `GET` | `/api/price/<coin>` | Current price + 30-day OHLCV history |
| `GET` | `/api/predict/<coin>` | Next-day price prediction |
| `GET` | `/api/sentiment/<coin>` | News sentiment score & articles |
| `POST` | `/api/train/<coin>` | Train/retrain model for a coin |
| `GET` | `/api/all/<coin>` | Combined: price + prediction + sentiment |

### Query Parameters for `/api/all/<coin>`

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `period` | `1d`, `5d`, `1mo`, `1y` | `1mo` | Date range |
| `interval` | `1h`, `4h`, `1d`, `1w` | `1d` | Candle interval |

### Example Response — `/api/all/BTC?period=1mo&interval=1d`

```json
{
  "success": true,
  "coin": "BTC",
  "current": {
    "price": 65432.10,
    "change_24h": 2.34,
    "volume": 32000000000,
    "market_cap": 1280000000000
  },
  "historical": [
    {
      "date": "2024-02-01",
      "open": 42000.0,
      "high": 43500.0,
      "low": 41200.0,
      "close": 43100.0,
      "volume": 28000000000
    }
  ],
  "prediction": {
    "coin": "BTC",
    "current_price": 65432.10,
    "predictions": [
      {
        "date": "2024-03-24",
        "price": 66800.00,
        "change_percent": 2.08
      }
    ]
  },
  "sentiment": {
    "score": 72.4,
    "category": "Medium",
    "positive": 8,
    "neutral": 3,
    "negative": 2,
    "summary": "Market sentiment for BTC is currently medium..."
  }
}
```

---

## 4. Data Pipeline

**File:** `backend/data/data_fetcher.py`

### Data Source
- **Yahoo Finance** via `yfinance` library
- Ticker mappings: `BTC-USD`, `ETH-USD`, `SOL-USD`, `BNB-USD`, etc.

### OHLCV Fields
Each daily candle contains:

| Field | Description |
|-------|-------------|
| `Open` | Opening price |
| `High` | Day's highest price |
| `Low` | Day's lowest price |
| `Close` | Closing price |
| `Volume` | Total trading volume (USD) |

### Data Preparation Flow

```
yfinance raw data
       ↓
 Clean NaN values (ffill → bfill)
       ↓
 AdvancedFeatureEngineer.generate_all_features()
       ↓
 75+ engineered features
       ↓
 MinMaxScaler (0–1 normalization)
       ↓
 Sequence slicing: [t-60 : t] → predict [t+1]
       ↓
 LSTM input tensor: shape (samples, 60, n_features)
```

---

## 5. Feature Engineering (75+ Features)

**File:** `backend/data/advanced_features.py`

75+ features across **11 groups** feed into the LSTM model.

---

### Group 1 — Raw Price Features (5)

| Feature | Formula |
|---------|---------|
| `Open` | Raw open price |
| `High` | Raw high price |
| `Low` | Raw low price |
| `Close` | Raw close price |
| `Typical_Price` | `(High + Low + Close) / 3` |

---

### Group 2 — Candlestick Features (5)

| Feature | Formula |
|---------|---------|
| `Body_Size` | `\|Close - Open\|` |
| `Upper_Wick` | `High - max(Open, Close)` |
| `Lower_Wick` | `min(Open, Close) - Low` |
| `Range` | `High - Low` |
| `Candle_Direction` | `1` if `Close > Open` else `0` |

---

### Group 3 — Returns & Momentum (6)

| Feature | Formula |
|---------|---------|
| `Log_Return` | `ln(Close_t / Close_{t-1})` |
| `Return_1` | `(Close_t - Close_{t-1}) / Close_{t-1}` |
| `Return_3` | `(Close_t - Close_{t-3}) / Close_{t-3}` |
| `Return_5` | `(Close_t - Close_{t-5}) / Close_{t-5}` |
| `Rolling_Mean_Return_5` | `mean(Return_1)` over last 5 days |
| `Rolling_Std_5` | `std(Close)` over last 5 days |

---

### Group 4 — Moving Averages & Trend (12)

#### Exponential Moving Average (EMA)

> **EMA Formula:**
> ```
> EMA_t = α × Price_t + (1 - α) × EMA_{t-1}
> where α = 2 / (span + 1)
> ```

| Feature | Span |
|---------|------|
| `EMA_9` | 9 days |
| `EMA_20` | 20 days |
| `EMA_50` | 50 days |
| `EMA_100` | 100 days |
| `EMA_200` | 200 days |

**Derived Cross Signals:**

| Feature | Formula |
|---------|---------|
| `Close_minus_EMA20` | `Close - EMA_20` |
| `Close_minus_EMA50` | `Close - EMA_50` |
| `Close_minus_EMA200` | `Close - EMA_200` |
| `EMA20_minus_EMA50` | `EMA_20 - EMA_50` *(Golden/Death Cross signal)* |
| `EMA50_minus_EMA200` | `EMA_50 - EMA_200` |
| `EMA20_Slope` | `EMA_20_t - EMA_20_{t-1}` |
| `EMA50_Slope` | `EMA_50_t - EMA_50_{t-1}` |

---

### Group 5 — Momentum Indicators (8)

#### RSI — Relative Strength Index

> **RSI Formula:**
> ```
> Step 1: Avg_Gain = mean(gains over 14 days)
>         Avg_Loss = mean(losses over 14 days)
> Step 2: RS = Avg_Gain / Avg_Loss
> Step 3: RSI = 100 - (100 / (1 + RS))
>
> Interpretation:
>   RSI > 70 → Overbought (potential sell signal)
>   RSI < 30 → Oversold (potential buy signal)
> ```

| Feature | Description |
|---------|-------------|
| `RSI` | 14-period RSI |
| `RSI_Slope` | `RSI_t - RSI_{t-1}` |
| `RSI_minus_50` | Deviation from neutral (50) |

#### MACD — Moving Average Convergence Divergence

> **MACD Formula:**
> ```
> MACD Line   = EMA_12 - EMA_26
> Signal Line = EMA_9 of MACD Line
> Histogram   = MACD Line - Signal Line
>
> Interpretation:
>   MACD crosses above Signal → Bullish
>   MACD crosses below Signal → Bearish
> ```

| Feature | Description |
|---------|-------------|
| `MACD` | MACD line |
| `MACD_Signal` | Signal line |
| `MACD_Hist` | Histogram (divergence) |

#### Stochastic RSI

> **StochRSI Formula:**
> ```
> StochRSI = (RSI - min(RSI, 14)) / (max(RSI, 14) - min(RSI, 14))
> %K = 3-period SMA of StochRSI
> %D = 3-period SMA of %K
> ```

| Feature | Description |
|---------|-------------|
| `Stoch_RSI_K` | %K line |
| `Stoch_RSI_D` | %D line (signal) |

---

### Group 6 — Volatility Features (6)

#### ATR — Average True Range

> **ATR Formula:**
> ```
> True Range (TR) = max(
>     High - Low,
>     |High - Close_{t-1}|,
>     |Low  - Close_{t-1}|
> )
> ATR = 14-period Wilder's moving average of TR
> ATR_Normalized = ATR / Close  (percentage volatility)
> ```

#### Bollinger Bands

> **Bollinger Band Formula:**
> ```
> Middle Band  = SMA_20
> Upper Band   = SMA_20 + (2 × StdDev_20)
> Lower Band   = SMA_20 - (2 × StdDev_20)
> BB_Width     = Upper Band - Lower Band
> BB_Percent   = (Close - Lower Band) / BB_Width
>
> Interpretation:
>   BB_Percent > 1 → Price above upper band (overbought)
>   BB_Percent < 0 → Price below lower band (oversold)
>   Narrow BB_Width → Low volatility squeeze (breakout expected)
> ```

| Feature | Description |
|---------|-------------|
| `ATR` | 14-period Average True Range |
| `ATR_Normalized` | `ATR / Close` |
| `BB_Upper` | Upper Bollinger Band |
| `BB_Lower` | Lower Bollinger Band |
| `BB_Width` | Band width |
| `BB_Percent` | Price position within bands (0–1) |

---

### Group 7 — Volume & Liquidity (7)

#### VWAP — Volume Weighted Average Price

> **VWAP Formula:**
> ```
> VWAP = Σ(Typical_Price × Volume) / Σ(Volume)
>
> where Typical_Price = (High + Low + Close) / 3
>
> Interpretation:
>   Close > VWAP → Bullish (price above fair value)
>   Close < VWAP → Bearish (price below fair value)
> ```

#### OBV — On-Balance Volume

> **OBV Formula:**
> ```
> If Close_t > Close_{t-1}:  OBV_t = OBV_{t-1} + Volume_t
> If Close_t < Close_{t-1}:  OBV_t = OBV_{t-1} - Volume_t
> If Close_t = Close_{t-1}:  OBV_t = OBV_{t-1}
>
> Rising OBV with rising price → Confirms uptrend
> Falling OBV with rising price → Divergence (bearish warning)
> ```

| Feature | Formula |
|---------|---------|
| `Volume` | Raw trading volume |
| `Volume_Change` | `(Volume_t - Volume_{t-1}) / Volume_{t-1}` |
| `Volume_MA20` | 20-day SMA of Volume |
| `Volume_Ratio` | `Volume / Volume_MA20` |
| `OBV` | Cumulative On-Balance Volume |
| `VWAP` | Volume Weighted Average Price |
| `Close_minus_VWAP` | Deviation from VWAP |

---

### Group 8 — Support & Resistance (6)

| Feature | Formula |
|---------|---------|
| `Rolling_High_20` | `max(High)` over last 20 days |
| `Rolling_Low_20` | `min(Low)` over last 20 days |
| `Distance_to_Resistance` | `(Rolling_High_20 - Close) / Close` |
| `Distance_to_Support` | `(Close - Rolling_Low_20) / Close` |
| `Breakout_Flag` | `1` if `Close > Rolling_High_20_{t-1}` |
| `Breakdown_Flag` | `1` if `Close < Rolling_Low_20_{t-1}` |

---

### Group 9 — Time-Based Features (4)

Cyclical encoding using sine/cosine to preserve time continuity (avoids the 23→0 hour jump problem):

> **Cyclical Encoding Formula:**
> ```
> Hour_Sin      = sin(2π × hour / 24)
> Hour_Cos      = cos(2π × hour / 24)
> DayOfWeek_Sin = sin(2π × day_of_week / 7)
> DayOfWeek_Cos = cos(2π × day_of_week / 7)
> ```

---

### Group 10 — Lag Features (10)

| Feature | Description |
|---------|-------------|
| `Close_Lag1` | Close price from 1 day ago |
| `Close_Lag2` | Close price from 2 days ago |
| `Close_Lag3` | Close price from 3 days ago |
| `Close_Lag5` | Close price from 5 days ago |
| `RSI_Lag1` | RSI from 1 day ago |
| `RSI_Lag2` | RSI from 2 days ago |
| `EMA20_Lag1` | EMA20 from 1 day ago |
| `EMA50_Lag1` | EMA50 from 1 day ago |
| `Return1_Lag1` | 1-day return from yesterday |
| `Return1_Lag3` | 1-day return from 3 days ago |

---

### Group 11 — Sentiment Features (7)

| Feature | Description |
|---------|-------------|
| `Sentiment_Score` | 0–100 sentiment score from news |
| `Sentiment_Category` | Encoded: 0=Worst, 1=Bad, 2=Average, 3=Medium, 4=Good |
| `Positive_Count` | Number of positive news articles |
| `Negative_Count` | Number of negative news articles |
| `Neutral_Count` | Number of neutral news articles |
| `Sentiment_Momentum` | `Sentiment_Score_t - Sentiment_Score_{t-1}` |
| `News_Volume` | `Positive + Negative + Neutral` article count |

---

## 6. Machine Learning Model (Bidirectional LSTM)

**File:** `backend/models/price_predictor.py`

### Why Bidirectional LSTM?

Standard LSTM processes sequences only **forward** (past → future).  
Bidirectional LSTM processes sequences **both directions** simultaneously:

```
Forward LSTM:  [t-60 → t-59 → ... → t-1 → t]
Backward LSTM: [t    → t-1  → ... → t-59 → t-60]
Output = concat(forward_hidden, backward_hidden)
```

This allows the model to capture patterns that depend on **future context within the lookback window**, improving prediction quality.

---

### Model Architecture

```
Input: (batch, 60 days, 75 features)
         ↓
┌─────────────────────────────────┐
│  Bidirectional LSTM (256 units) │  → output: (batch, 60, 512)
│  BatchNormalization             │
│  Dropout (0.30)                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Bidirectional LSTM (192 units) │  → output: (batch, 60, 384)
│  BatchNormalization             │
│  Dropout (0.30)                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Bidirectional LSTM (128 units) │  → output: (batch, 60, 256)
│  BatchNormalization             │
│  Dropout (0.25)                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Bidirectional LSTM  (64 units) │  → output: (batch, 128)
│  BatchNormalization             │
│  Dropout (0.20)                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Dense (64, ReLU)               │
│  BatchNormalization             │
│  Dropout (0.20)                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Dense (32, ReLU)               │
│  BatchNormalization             │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Dense (1)  → predicted price   │
└─────────────────────────────────┘
```

---

### Loss Function — Huber Loss

> **Huber Loss Formula:**
> ```
>             ½ × (y - ŷ)²           if |y - ŷ| ≤ δ
> L(y, ŷ) = {
>             δ × (|y - ŷ| - ½ × δ)  otherwise
>
> where δ = 1.0 (default threshold)
> ```

**Why Huber?** It behaves like **MSE** for small errors (smooth gradient) and like **MAE** for large errors (robust to outliers). Crypto prices often have sudden spikes — Huber loss prevents these from destabilizing training.

---

### Optimizer — Adam

> **Adam Update Rule:**
> ```
> m_t = β₁ × m_{t-1} + (1 - β₁) × g_t        (1st moment / mean)
> v_t = β₂ × v_{t-1} + (1 - β₂) × g_t²        (2nd moment / variance)
>
> m̂_t = m_t / (1 - β₁ᵗ)   (bias correction)
> v̂_t = v_t / (1 - β₂ᵗ)   (bias correction)
>
> θ_t = θ_{t-1} - α × m̂_t / (√v̂_t + ε)
>
> where α = 0.001, β₁ = 0.9, β₂ = 0.999, ε = 1e-8
> ```

---

### Training Hyperparameters

| Parameter | Value |
|-----------|-------|
| Learning Rate | `0.001` |
| Epochs (max) | `150` |
| Batch Size | `16` |
| Lookback Window | `60` days |
| Train/Test Split | `80% / 20%` (time-based, no shuffle) |
| Early Stopping Patience | `20` epochs |
| LR Reduction Factor | `0.5` (when val_loss plateaus for 8 epochs) |
| Minimum LR | `1e-5` |

---

### Training Callbacks

| Callback | Trigger | Action |
|----------|---------|--------|
| `EarlyStopping` | `val_loss` no improvement for 20 epochs | Stop training, restore best weights |
| `ModelCheckpoint` | Each epoch | Save model if `val_loss` improved |
| `ReduceLROnPlateau` | `val_loss` no improvement for 8 epochs | Multiply LR by 0.5 |

---

### Normalization — MinMaxScaler

> **MinMax Scaling Formula:**
> ```
> X_scaled = (X - X_min) / (X_max - X_min)
>
> Inverse Transform (for prediction output):
> X_original = X_scaled × (X_max - X_min) + X_min
> ```

All 75 features are scaled to `[0, 1]` before feeding into the LSTM. Predictions are inverse-transformed back to real USD prices.

---

### Sequence Construction

```
For each time step t (where t ≥ 60):
  Input  X[t] = scaled_features[t-60 : t]   → shape (60, 75)
  Target y[t] = scaled_Close[t]              → shape (1,)

Total sequences = (total_days - 60 - 1)
```

---

### Model Persistence

Each trained coin model saves 3 files:

| File | Content |
|------|---------|
| `<COIN>_model.h5` | Full Keras model weights + architecture |
| `<COIN>_scaler.pkl` | Fitted MinMaxScaler (pickle) |
| `<COIN>_config.json` | Feature list, lookback, training metadata |

---

## 7. Sentiment Analysis Engine

**File:** `backend/models/sentiment_analyzer.py`

### Pipeline

```
1. Fetch news: NewsAPI (premium) → CoinGecko (free) → Mock (fallback)
2. Filter: Remove spam/unreliable sources
3. Analyze: VADER sentiment per article
4. Aggregate: Compute overall compound score
5. Scale: Convert to 0–100 for UI display
```

---

### VADER — Valence Aware Dictionary and sEntiment Reasoner

VADER is a **rule-based NLP** model built specifically for social media and news text.

#### VADER Output Scores

| Score | Range | Description |
|-------|-------|-------------|
| `pos` | 0–1 | Proportion of positive sentiment |
| `neg` | 0–1 | Proportion of negative sentiment |
| `neu` | 0–1 | Proportion of neutral content |
| `compound` | -1 to +1 | Overall normalized sentiment score |

#### Article Classification Thresholds

```
compound ≥  0.05  → "Positive"
compound ≤ -0.05  → "Negative"
-0.05 < compound < 0.05  → "Neutral"
```

---

### Compound Score → 0-100 Scale

> ```
> sentiment_score = ((avg_compound + 1) / 2) × 100
>
> Example:
>   avg_compound =  0.6  → score = ((0.6 + 1) / 2) × 100 = 80  (Good)
>   avg_compound =  0.0  → score = ((0.0 + 1) / 2) × 100 = 50  (Average)
>   avg_compound = -0.5  → score = ((-0.5 + 1) / 2) × 100 = 25 (Bad)
> ```

---

### Sentiment Score Categories

| Score Range | Category | Color |
|-------------|----------|-------|
| 0 – 20 | Worst | `#ff0000` (Red) |
| 20 – 40 | Bad | `#ff6b00` (Orange) |
| 40 – 60 | Average | `#ffb800` (Yellow) |
| 60 – 80 | Medium | `#90ee90` (Light Green) |
| 80 – 100 | Good | `#00ff00` (Green) |

---

### Source Trust Filter (5-layer validation)

1. **Whitelist check** — Source name matches trusted list (CoinDesk, Bloomberg, Binance, etc.)
2. **Domain check** — URL contains `.com`, `.org`, `.io`, `.news`
3. **Spam filter** — Title does NOT contain: "pump", "moon", "airdrop", "100x", "giveaway"...
4. **Content check** — Title length ≥ 10 characters
5. **URL validation** — URL starts with `http://` or `https://`

---

## 8. Frontend Architecture

### `index.html` — Main Dashboard

| Section | ID | Description |
|---------|----|-------------|
| Price Card | `current-price`, `price-change` | Live price + 24h % change |
| Pro Price Bar | `pro-price`, `pro-high`, `pro-low`, `pro-volume` | Trading terminal header |
| Candlestick Chart | `priceChart` | ApexCharts OHLCV candlestick |
| Volume Chart | `volumeChart` | Color-coded volume bars |
| Sentiment Ring | `sentiment-circle`, `sentiment-score-val` | SVG circular progress meter |
| AI Forecast | `prediction-grid` | Next-day prediction cards |
| News Feed | `news-list` | Sentiment-labeled article list |

---

### `chart-manager.js` — ApexCharts Integration

The chart renders 5 overlapping series simultaneously:

| Series | Type | Color | Description |
|--------|------|-------|-------------|
| Price | `candlestick` | Green/Red | OHLCV candles |
| MA7 | `line` | `#feb019` | 7-day Moving Average |
| MA25 | `line` | `#00e396` | 25-day Moving Average |
| MA99 | `line` | `#ff4560` | 99-day Moving Average |
| AI Path | `line` | `#A29BFE` | AI-predicted forecast path |

#### Moving Average Calculation (Frontend)

```javascript
// Close prices from OHLC data  [open, high, low, close]
MA(period) = mean(close[i-period+1 ... i])
```

#### Volume Color Coding

```javascript
fillColor = (close >= open) ? '#00D764'  // Green = bullish candle
                            : '#FF4D6D'  // Red   = bearish candle
```

#### Chart Synchronization

Both price and volume charts share `group: 'trading-view'`, so panning/zooming one automatically syncs the other.

---

### `app.js` — Data Orchestration

```
DOMContentLoaded
    ├── initializeTabs()   → coin switcher event listeners
    ├── initializeTimeframes() → 1H / 4H / 1D / 1W buttons
    ├── loadCoinData()     → fetch + render everything
    └── startAutoUpdate()  → setInterval(60000ms)

loadCoinData(coin, period, interval)
    ├── GET /api/all/<coin>?period=...&interval=...
    └── on success:
         ├── updatePriceDisplay(current)
         ├── updateProPriceBar(current, historical, interval)
         ├── updateChart(historical, prediction)  → chart-manager.js
         ├── updatePredictions(prediction)
         └── updateSentiment(sentiment)           → sentiment-display.js
```

---

### `sentiment-display.js` — Sentiment UI

**Circular SVG Progress Meter:**
```
stroke-dasharray = "score, 100"
(e.g. score=72 → "72, 100" → fills 72% of circle)
```

**Animated Counter:**
```javascript
// 60fps counter animation from 0 → score over 1000ms
increment = (end - start) / (1000 / 16)
```

---

### `learn.js` — Education Hub Logic

#### DCA Calculator Formula

> ```
> Total Invested = monthly_amount × months
> Total Coins    = Σ(monthly_amount / price_each_month)
>
> For simplified estimate:
> Avg Price   = (start_price + end_price) / 2
> Total Coins = Total Invested / Avg Price
> Current Value = Total Coins × current_price
> Profit/Loss   = Current Value - Total Invested
> ROI %         = (Profit/Loss / Total Invested) × 100
> ```

#### Profit/Loss Calculator Formula

> ```
> Investment Amount = entry_price × quantity
> Current Value     = current_price × quantity
> Profit/Loss       = Current Value - Investment Amount
> ROI %             = (Profit/Loss / Investment Amount) × 100
> ```

---

### CSS Design System

| File | Theme |
|------|-------|
| `styles.css` | Dark fintech: `#0b0b1a` background, `#6c5ce7` purple accent |
| `learn.css` | Glassmorphism: `rgba(255,255,255,0.05)` frosted panels, animated indigo gradient background |
| `dropdown.css` | Dropdown menus |

**Fonts:**
- `Inter` — UI text (weights 300–800)
- `JetBrains Mono` — Price/number displays

**Icons:** Lucide Icons (SVG) via CDN — `unpkg.com/lucide@latest`

---

## 9. Crypto Education Hub

**Files:** `learn.html`, `css/learn.css`, `js/learn.js`

### 9 Chapters

| # | Chapter ID | Title | Key Topics |
|---|-----------|-------|-----------|
| 1 | `chapter-crypto` | What is Crypto? | Definition, history, use cases |
| 2 | `chapter-how` | How it Works | Blockchain, mining, nodes |
| 3 | `chapter-trading` | Crypto Trading | Exchanges, order types |
| 4 | `chapter-profits` | Making Profits | HODLing, DCA, staking, yield |
| 5 | `chapter-strategies` | Trading Strategies | RSI, MACD, Bollinger Bands |
| 6 | `chapter-tools` | Tools & Calculators | DCA calc, P/L calc, Fear & Greed |
| 7 | `chapter-history` | Market History | 2009 genesis → 2024 ETF |
| 8 | `chapter-glossary` | Glossary | 30+ searchable crypto terms |
| 9 | `chapter-videos` | Video Hub | 5 curated YouTube videos |

### Video Hub

| Video | Channel | Level |
|-------|---------|-------|
| How Blockchain Works | Various | Beginner |
| But how does Bitcoin actually work? | 3Blue1Brown | Beginner |
| Crypto Technical Analysis for Beginners | Various | Intermediate |
| Mastering the RSI Indicator | Various | Intermediate |
| DON'T GET REKT!! Crypto Risk Management 101 | Coin Bureau | Advanced |

### Live Fear & Greed Index

Fetched from `https://api.alternative.me/fng/` — returns a 0–100 score:

| Score | Classification |
|-------|---------------|
| 0–24 | Extreme Fear |
| 25–49 | Fear |
| 50 | Neutral |
| 51–74 | Greed |
| 75–100 | Extreme Greed |

---

## 10. Libraries & Dependencies

### Python (Backend)

| Library | Version | Purpose |
|---------|---------|---------|
| `flask` | 3.0.0 | REST API web server |
| `flask-cors` | 4.0.0 | Cross-origin (frontend ↔ backend) |
| `yfinance` | 0.2.32 | Yahoo Finance OHLCV data |
| `pandas` | 2.1.3 | Data manipulation, time series |
| `numpy` | 1.26.2 | Numerical computing |
| `scikit-learn` | 1.3.2 | MinMaxScaler, train/test split |
| `tensorflow` | 2.15.0 | LSTM model training & inference |
| `keras` | 2.15.0 | High-level neural network API |
| `torch` | 2.1.1 | PyTorch (transformer-based NLP) |
| `transformers` | 4.35.2 | HuggingFace NLP models |
| `vaderSentiment` | 3.3.2 | Rule-based news sentiment |
| `newsapi-python` | 0.2.7 | NewsAPI client |
| `requests` | 2.31.0 | HTTP client |
| `python-dotenv` | 1.0.0 | `.env` configuration |

### JavaScript (Frontend — CDN)

| Library | Source | Purpose |
|---------|--------|---------|
| ApexCharts | jsdelivr.net | Candlestick + volume charts |
| Lucide Icons | unpkg.com | Professional SVG icons |
| Inter Font | fonts.googleapis.com | UI typography |
| JetBrains Mono | fonts.googleapis.com | Monospace price display |

### External APIs

| API | Use | Auth |
|-----|-----|------|
| Yahoo Finance (yfinance) | OHLCV price data | None (free) |
| CoinGecko News API | Crypto news articles | None (free tier) |
| NewsAPI | News articles | `NEWS_API_KEY` in `.env` |
| Alternative.me FNG | Fear & Greed Index | None (free) |

---

## 11. ML Evaluation & Performance

The reliability of CP.AI's predictions is measured using two primary metrics: **Mean Absolute Percentage Error (MAPE)** and **Directional Accuracy**.

### Backtesting Process (`backend/check_accuracy.py`)

The evaluation engine performs a "Walk-Forward" backtest on the last 30 days of data:

1.  **Iterative Prediction:** For each day `t` in the test set, the model receives the previous 60 days of data `[t-60:t]`.
2.  **Comparison:** The predicted price for `t+1` is compared with the actual price once it becomes available.
3.  **Metric Accumulation:** Errors and directional moves are stored to calculate final performance scores.

### Key Evaluation Metrics

#### 1. Mean Absolute Percentage Error (MAPE)

MAPE measures the average magnitude of prediction errors in percentage terms. It is the primary indicator of how "close" the predicted price is to the real price.

> **MAPE Formula:**
> ```
> MAPE = (100% / n) × Σ |(Actual_t - Predicted_t) / Actual_t|
> ```

*   **Interpretation:** A lower MAPE indicates higher precision. In CP.AI, a MAPE under 3% for Bitcoin/Ethereum is considered excellent for a 24-hour horizon.

#### 2. Directional Accuracy (Hit Rate)

This metric evaluates how often the model correctly predicts whether the price will go **UP** or **DOWN** relative to the previous day's close.

> **Directional Accuracy Formula:**
> ```
> Let Signal_t = 1  if (Predicted_t - Actual_{t-1}) > 0 else 0
> Let ActualMove_t = 1 if (Actual_t - Actual_{t-1}) > 0 else 0
>
> Accuracy = (Count of Signal_t == ActualMove_t / Total Predictions) × 100%
> ```

*   **Interpretation:** An accuracy > 50% is profitable, as it means the model is better than a coin flip at guessing market direction.

---

### Real-World Performance (Phase 12 Results)

Based on the automated retraining logs (`retraining_results.json`), here is the typical performance across major assets:

| Asset | Samples (Days) | Loss (Huber) | Est. MAPE | Directional Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **BTC** | 1,777 | 0.0028 | 1.8% | 62.5% |
| **ETH** | 1,777 | 0.0027 | 2.1% | 58.3% |
| **SOLANA** | 1,777 | 0.0065 | 3.4% | 54.2% |
| **DOGE** | 1,777 | 0.0017 | 4.2% | 50.0% |

> [!NOTE]
> Performance varies by market volatility. Blue-chip assets like BTC and ETH typically show higher accuracy than smaller, more volatile "altcoins."

---

## 12. How to Run

### Prerequisites
- Python 3.10+
- Node.js (optional, for live-server)

### Step 1 — Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Configure API Keys (Optional)

```bash
cp .env.example .env
# Edit .env and add:
NEWS_API_KEY=your_newsapi_key_here
```

### Step 3 — Train Models

```bash
# From project root
python train_ensemble.py
# Trains all 10 coin models (BTC, ETH, SOL, BNB, DOGE, XRP, ADA, AVAX, DOT, LINK)
# Models saved to backend/models/saved/
```

### Step 4 — Start Backend API

```bash
cd backend
python app.py
# API running at http://localhost:5000
```

### Step 5 — Open Frontend

Open `index.html` using VS Code Live Server (port 5500), or any local server:

```bash
# Python quick server
python -m http.server 5500
```

Then visit:
- **Dashboard:** http://localhost:5500/index.html
- **Education Hub:** http://localhost:5500/learn.html

### Step 6 — Retrain Models (when needed)

```bash
python retrain_phase11.py   # Phase 11 retraining
python retrain_phase12.py   # Phase 12 retraining
```

---

## Quick Reference — Key Formulas

| Formula | Expression |
|---------|-----------|
| Typical Price | `(H + L + C) / 3` |
| EMA | `α × P_t + (1-α) × EMA_{t-1}`, `α = 2/(n+1)` |
| RSI | `100 - 100/(1 + Avg_Gain/Avg_Loss)` |
| MACD | `EMA_12 - EMA_26` |
| Bollinger Upper | `SMA_20 + 2σ` |
| ATR | `EWM(max(H-L, |H-C_{t-1}|, |L-C_{t-1}|), 14)` |
| VWAP | `Σ(TP × Vol) / Σ(Vol)` |
| Log Return | `ln(C_t / C_{t-1})` |
| Huber Loss | `½(y-ŷ)²` if `|y-ŷ|≤δ`, else `δ|y-ŷ| - ½δ²` |
| Sentiment Scale | `((compound + 1) / 2) × 100` |
| MinMax Scale | `(X - X_min) / (X_max - X_min)` |
| ROI % | `(Current Value - Invested) / Invested × 100` |

---

*Documentation generated for CP.AI — CryptoPredict AI*  
*© 2026 CP.AI*
