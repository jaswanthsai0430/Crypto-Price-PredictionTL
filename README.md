# Crypto Price Prediction & Sentiment Analysis

AI-powered cryptocurrency price predictions and real-time sentiment analysis for Bitcoin, Ethereum, Solana, Binance Coin, and Dogecoin.

## 🚀 Features

- **5 Cryptocurrencies Supported**: BTC, ETH, SOL, BNB, DOGE
- **AI Price Predictions**: 3-day forecasts using Bidirectional LSTM
- **Sentiment Analysis**: Real-time news sentiment from trusted sources
- **Interactive Charts**: Beautiful Chart.js visualizations
- **Auto-Refresh**: Updates every 60 seconds
- **Responsive Design**: Works on desktop and mobile

## 📊 Model Performance

- **Accuracy**: 70-80% directional accuracy
- **Architecture**: Bidirectional LSTM with Batch Normalization
- **Features**: 6 technical indicators (OHLCV + technical analysis)
- **Training**: 100 epochs with early stopping

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - REST API
- **TensorFlow/Keras** - Deep Learning
- **Pandas/NumPy** - Data processing
- **VADER** - Sentiment analysis

### Frontend
- **HTML5/CSS3/JavaScript**
- **Chart.js** - Interactive charts
- **Responsive design** - Mobile-friendly

### APIs
- **CoinGecko API** - Live crypto prices (free tier)
- **CoinGecko News API** - Cryptocurrency news

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd final
```

2. **Set up virtual environment**
```bash
cd backend
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
.\venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the backend**
```bash
python app.py
```

6. **Open the frontend**
- Open `index.html` in your browser
- Or visit `http://localhost:5000` if served

## 📖 Usage

1. **Start the backend server**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

2. **Open the frontend**
- Double-click `index.html`
- Select a cryptocurrency tab (BTC, ETH, SOL, BNB, DOGE)

3. **First-time model training**
- When you select a coin for the first time, the model will train automatically
- Training takes 5-10 minutes per coin
- Models are saved and reused for instant predictions

## 🔧 Configuration

### Optional: News API Key

For enhanced news coverage, add a NewsAPI key:

1. Create `.env` file in `backend/` directory
2. Add your API key:
```
NEWS_API_KEY=your_api_key_here
```

Get a free key at: https://newsapi.org/

## 📁 Project Structure

```
final/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt       # Python dependencies
│   ├── data/
│   │   ├── coingecko_api.py  # CoinGecko integration
│   │   ├── data_fetcher.py   # Data processing
│   │   └── mock_data.py      # Fallback data
│   └── models/
│       ├── price_predictor.py    # Bi-LSTM model
│       ├── sentiment_analyzer.py # Sentiment analysis
│       └── saved/                # Trained models (auto-generated)
├── js/
│   ├── app.js               # Main application logic
│   ├── chart-manager.js     # Chart rendering
│   └── sentiment-display.js # Sentiment UI
├── css/
│   └── styles.css           # Styling
└── index.html               # Main page

```

## 🎯 API Endpoints

- `GET /api/price/<coin>` - Get current price and historical data
- `GET /api/predict/<coin>` - Get 3-day price predictions
- `GET /api/sentiment/<coin>` - Get sentiment analysis
- `GET /api/all/<coin>` - Get all data (price + prediction + sentiment)
- `POST /api/train/<coin>` - Train/retrain model

## 🧪 Testing

Test the API:
```bash
cd backend
python test_api.py
```

Test individual components:
```bash
python data/coingecko_api.py
python models/price_predictor.py
python models/sentiment_analyzer.py
```

## 📈 Model Details

### Bidirectional LSTM Architecture
- 3 Bidirectional LSTM layers (128, 64, 32 units)
- Batch Normalization after each layer
- Dropout (0.3, 0.3, 0.2) for regularization
- Huber loss function
- Adam optimizer with learning rate reduction

### Features Used
1. Open, High, Low, Close prices
2. Volume
3. Technical indicators (MA, EMA, RSI, MACD, Bollinger Bands)

### Training Parameters
- Lookback window: 60 days
- Prediction horizon: 3 days
- Epochs: 100 (with early stopping)
- Batch size: 32

## 🔒 Security Notes

- API runs on localhost (development mode)
- No sensitive data stored
- CORS enabled for local development
- For production: disable debug mode, add authentication

## 🐛 Troubleshooting

### Backend not starting
- Check Python version: `python --version` (need 3.8+)
- Verify virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Frontend not showing data
- Ensure backend is running on port 5000
- Check browser console (F12) for errors
- Hard refresh: Ctrl+Shift+R

### API rate limits
- CoinGecko free tier: 10-50 calls/minute
- App makes ~2 calls per coin per refresh
- Automatic retry with fallback to mock data

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- CoinGecko for free crypto data API
- TensorFlow/Keras for ML framework
- Chart.js for beautiful charts
- VADER for sentiment analysis

---

**⚠️ Disclaimer**: This tool is for educational and informational purposes only. Not financial advice. Always do your own research before making investment decisions.
