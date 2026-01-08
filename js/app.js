// Main Application Logic
const API_BASE_URL = 'http://localhost:5000/api';
let currentCoin = 'BTC';
let updateInterval = null;

// Coin name mapping
const coinNames = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'SOLANA': 'Solana',
    'BNB': 'Binance Coin',
    'DOGE': 'Dogecoin'
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    loadCoinData(currentCoin);
    startAutoUpdate();
});

// Initialize tab switching
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab-btn');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            tab.classList.add('active');

            // Get selected coin
            currentCoin = tab.dataset.coin;

            // Load data for selected coin
            loadCoinData(currentCoin);
        });
    });
}

// Load all data for a coin
async function loadCoinData(coin) {
    console.log(`Loading data for ${coin}...`);

    // Update coin name
    document.getElementById('current-coin-name').textContent = coinNames[coin];

    // Show loading state
    showLoading();

    try {
        // Fetch all data
        const response = await fetch(`${API_BASE_URL}/all/${coin}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // Update UI with data
            updatePriceDisplay(data.current);
            updateChart(data.historical, data.prediction);
            updatePredictions(data.prediction);
            updateSentiment(data.sentiment);
        } else {
            console.error('API returned error:', data.error);
            showError('Failed to load data');
        }
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to connect to API. Make sure the backend server is running.');
    } finally {
        hideLoading();
    }
}

// Update price display
function updatePriceDisplay(priceData) {
    if (!priceData) return;

    // Update price
    const priceElement = document.getElementById('current-price');
    priceElement.textContent = formatPrice(priceData.price);

    // Update 24h change
    const changeElement = document.getElementById('price-change');
    const changeValue = priceData.change_24h;

    changeElement.textContent = `${changeValue >= 0 ? '+' : ''}${changeValue.toFixed(2)}%`;
    changeElement.className = 'price-change ' + (changeValue >= 0 ? 'positive' : 'negative');

    // Update volume
    const volumeElement = document.getElementById('volume');
    volumeElement.textContent = formatLargeNumber(priceData.volume);

    // Update market cap
    const marketCapElement = document.getElementById('market-cap');
    marketCapElement.textContent = formatLargeNumber(priceData.market_cap);

    // Animate price update
    priceElement.style.animation = 'none';
    setTimeout(() => {
        priceElement.style.animation = 'priceUpdate 0.5s ease';
    }, 10);
}

// Update predictions display
function updatePredictions(predictionData) {
    if (!predictionData || !predictionData.predictions) return;

    const grid = document.getElementById('prediction-grid');
    grid.innerHTML = '';

    predictionData.predictions.forEach((pred, index) => {
        const card = document.createElement('div');
        card.className = 'prediction-card';
        card.style.animationDelay = `${index * 0.1}s`;

        const changeClass = pred.change_percent >= 0 ? 'positive' : 'negative';
        const changeSymbol = pred.change_percent >= 0 ? '+' : '';

        card.innerHTML = `
            <div class="prediction-date">Day ${index + 1} - ${formatDate(pred.date)}</div>
            <div class="prediction-price">$${formatPrice(pred.price)}</div>
            <div class="prediction-change ${changeClass}">
                ${changeSymbol}${pred.change_percent.toFixed(2)}%
            </div>
        `;

        grid.appendChild(card);
    });
}

// Start auto-update
function startAutoUpdate() {
    // Update every 60 seconds
    updateInterval = setInterval(() => {
        loadCoinData(currentCoin);
    }, 60000);
}

// Stop auto-update
function stopAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('chart-loading');
    if (overlay) {
        overlay.classList.add('active');
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('chart-loading');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Show error message
function showError(message) {
    console.error(message);
    // You could add a toast notification here
}

// Format price
function formatPrice(price) {
    if (price >= 1000) {
        return price.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    } else if (price >= 1) {
        return price.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 4
        });
    } else {
        return price.toLocaleString('en-US', {
            minimumFractionDigits: 4,
            maximumFractionDigits: 6
        });
    }
}

// Format large numbers
function formatLargeNumber(num) {
    if (num >= 1e12) {
        return `$${(num / 1e12).toFixed(2)}T`;
    } else if (num >= 1e9) {
        return `$${(num / 1e9).toFixed(2)}B`;
    } else if (num >= 1e6) {
        return `$${(num / 1e6).toFixed(2)}M`;
    } else if (num >= 1e3) {
        return `$${(num / 1e3).toFixed(2)}K`;
    } else {
        return `$${num.toFixed(2)}`;
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes priceUpdate {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .prediction-card {
        animation: slideIn 0.5s ease forwards;
        opacity: 0;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoUpdate();
});
