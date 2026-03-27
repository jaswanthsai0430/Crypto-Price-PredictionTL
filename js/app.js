// Main Application Logic - Handles UI state and data orchestration
const API_BASE_URL = 'http://localhost:5000/api';
let currentCoin = 'BTC';
let currentPeriod = '1mo';
let currentInterval = '1d';
let updateInterval = null;

const coinNames = {
    'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'SOLANA': 'Solana',
    'BNB': 'Binance Coin', 'DOGE': 'Dogecoin', 'XRP': 'Ripple',
    'ADA': 'Cardano', 'AVAX': 'Avalanche', 'DOT': 'Polkadot',
    'LINK': 'Chainlink'
};

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeTimeframes();
    loadCoinData(currentCoin);
    startAutoUpdate();
});

function initializeTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.onclick = (e) => {
            const coin = item.dataset.coin;
            if (coin === currentCoin) return;

            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            currentCoin = coin;
            loadCoinData(currentCoin);
        };
    });
}

function initializeTimeframes() {
    const tfBtns = document.querySelectorAll('.tf-btn');
    tfBtns.forEach(btn => {
        btn.onclick = (e) => {
            e.preventDefault();
            const period = btn.dataset.period;
            const interval = btn.dataset.interval;

            if (period === currentPeriod && interval === currentInterval) return;

            tfBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentPeriod = period;
            currentInterval = interval;
            loadCoinData(currentCoin, currentPeriod, currentInterval);
        };
    });
}

async function loadCoinData(coin, period = currentPeriod, interval = currentInterval) {
    // Update headers immediately for responsiveness
    const headerName = document.getElementById('header-coin-name');
    const chartSymbol = document.getElementById('chart-symbol');
    if (headerName) headerName.textContent = coinNames[coin] || coin;
    if (chartSymbol) chartSymbol.textContent = `${coin}/USD`;

    showLoading();
    try {
        const url = `${API_BASE_URL}/all/${coin}?period=${period}&interval=${interval}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`API error: ${response.status}`);

        const data = await response.json();
        if (data.success) {
            updatePriceDisplay(data.current);
            updateProPriceBar(data.current, data.historical, interval);
            updateChart(data.historical, data.prediction);
            updatePredictions(data.prediction);
            if (data.sentiment) updateSentiment(data.sentiment);
        }
    } catch (error) {
        console.error('Data Load Error:', error);
    } finally {
        hideLoading();
    }
}

function updatePriceDisplay(priceData) {
    if (!priceData) return;
    const priceElement = document.getElementById('current-price');
    const changeElement = document.getElementById('price-change');

    if (priceElement) priceElement.textContent = formatPrice(priceData.price);

    const changeValue = priceData.change_24h || 0;
    if (changeElement) {
        changeElement.textContent = `${changeValue >= 0 ? '+' : ''}${changeValue.toFixed(2)}%`;
        changeElement.className = 'price-change ' + (changeValue >= 0 ? 'positive' : 'negative');
    }

    const volEl = document.getElementById('volume');
    const mcEl = document.getElementById('market-cap');
    if (volEl) volEl.textContent = formatLargeNumber(priceData.volume);
    if (mcEl) mcEl.textContent = formatLargeNumber(priceData.market_cap);
}

function updateProPriceBar(current, historical, interval) {
    if (!current || !historical || historical.length === 0) return;

    const pPrice = document.getElementById('pro-price');
    const pChange = document.getElementById('pro-change');
    const pHigh = document.getElementById('pro-high');
    const pLow = document.getElementById('pro-low');
    const pVol = document.getElementById('pro-volume');

    if (pPrice) pPrice.textContent = formatPrice(current.price);

    const change = current.change_24h || 0;
    if (pChange) {
        pChange.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
        pChange.className = 'pro-value ' + (change >= 0 ? 'positive' : 'negative');
    }

    // Calculate 24h High/Low from the relevant window
    let windowSize = 24;
    if (interval === '4h') windowSize = 6;
    if (interval === '1d' || interval === '1w') windowSize = 1;

    const recentData = historical.slice(-windowSize);
    const high = Math.max(...recentData.map(d => d.high || current.price));
    const low = Math.min(...recentData.map(d => d.low || current.price));

    if (pHigh) pHigh.textContent = formatPrice(high);
    if (pLow) pLow.textContent = formatPrice(low);
    if (pVol) pVol.textContent = formatLargeNumber(current.volume);
}

function updatePredictions(predictionData) {
    const grid = document.getElementById('prediction-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const preds = predictionData?.predictions || [];
    if (preds.length === 0) {
        grid.innerHTML = '<div class="no-prediction">Analysis model warming up...</div>';
        return;
    }

    preds.forEach((pred, index) => {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        card.style.animationDelay = `${index * 0.1}s`;
        const changeClass = pred.change_percent >= 0 ? 'positive' : 'negative';

        card.innerHTML = `
            <div class="prediction-date">Day ${index + 1} - ${formatDate(pred.date)}</div>
            <div class="prediction-price">$${formatPrice(pred.price)}</div>
            <div class="prediction-change ${changeClass}">
                ${pred.change_percent >= 0 ? '+' : ''}${pred.change_percent.toFixed(2)}%
            </div>
        `;
        grid.appendChild(card);
    });
}

function startAutoUpdate() {
    stopAutoUpdate();
    updateInterval = setInterval(() => {
        loadCoinData(currentCoin, currentPeriod, currentInterval);
    }, 60000);
}

function stopAutoUpdate() {
    if (updateInterval) clearInterval(updateInterval);
}

function showLoading() { document.getElementById('chart-loading')?.classList.add('active'); }
function hideLoading() { document.getElementById('chart-loading')?.classList.remove('active'); }

function formatPrice(price) {
    if (typeof price !== 'number') return '--';
    return price.toLocaleString('en-US', {
        minimumFractionDigits: price < 1 ? 4 : 2,
        maximumFractionDigits: price < 1 ? 6 : 2
    });
}

function formatLargeNumber(num) {
    if (typeof num !== 'number') return '--';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${(num / 1e3).toFixed(2)}K`;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

window.addEventListener('beforeunload', stopAutoUpdate);
