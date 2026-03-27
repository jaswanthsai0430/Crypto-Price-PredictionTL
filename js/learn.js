// ===================================================
// learn.js - Crypto Education Page Logic
// ===================================================

// --- Chapter Navigation ---
function showChapter(id) {
    // Hide all chapters
    document.querySelectorAll('.chapter').forEach(c => {
        c.classList.remove('active-chapter');
    });

    // Deactivate all tabs
    document.querySelectorAll('.learn-tab').forEach(t => {
        t.classList.remove('active');
    });

    // Show target chapter
    const target = document.getElementById('chapter-' + id);
    if (target) target.classList.add('active-chapter');

    // Activate the clicked tab
    const tabs = document.querySelectorAll('.learn-tab');
    const chapterOrder = ['intro', 'blockchain', 'trading', 'profits', 'strategies', 'tools', 'history', 'glossary', 'videos'];
    const idx = chapterOrder.indexOf(id);
    if (tabs[idx]) tabs[idx].classList.add('active');

    // Scroll to top of content area
    document.querySelector('.learn-scroll').scrollTo({ top: 0, behavior: 'smooth' });
}

// --- Glossary Data ---
const glossaryTerms = [
    { word: "HODL", def: "Hold On for Dear Life — a strategy of keeping crypto long-term instead of selling during dips. Originally a typo for 'hold' that became a meme." },
    { word: "Altcoin", def: "Any cryptocurrency other than Bitcoin. ETH, SOL, DOGE, XRP are all altcoins." },
    { word: "Blockchain", def: "A distributed, decentralized digital ledger that records all crypto transactions across a network of computers." },
    { word: "Bull Market", def: "A period when prices are rising or expected to rise. Investors are optimistic ('bulls charge forward')." },
    { word: "Bear Market", def: "A period when prices are falling by 20%+. Investors are pessimistic ('bears swipe downward')." },
    { word: "FOMO", def: "Fear Of Missing Out — the anxiety of not buying a coin that is rapidly rising, often leading to poor decisions." },
    { word: "FUD", def: "Fear, Uncertainty, Doubt — negative news or rumors spread to manipulate the market and cause panic selling." },
    { word: "Whale", def: "An individual or entity that holds a very large amount of cryptocurrency, enough to influence market prices." },
    { word: "DeFi", def: "Decentralized Finance — financial services (lending, borrowing, trading) built on blockchain without banks or middlemen." },
    { word: "NFT", def: "Non-Fungible Token — a unique digital asset (art, music, collectibles) stored on a blockchain. Each NFT is one-of-a-kind." },
    { word: "Smart Contract", def: "Self-executing code on a blockchain that automatically enforces agreement terms without needing a third party." },
    { word: "Mining", def: "The process of verifying cryptocurrency transactions and adding them to the blockchain. Miners are rewarded with new crypto." },
    { word: "Staking", def: "Locking up crypto in a wallet or protocol to support network operations (like validating transactions) in exchange for rewards (APY)." },
    { word: "Gas Fees", def: "Transaction fees paid on the Ethereum network to compensate miners/validators for processing transactions. High during congestion." },
    { word: "Market Cap", def: "Total value of a cryptocurrency. Calculated as: Current Price × Total Circulating Supply. Used to rank coins by size." },
    { word: "Volatility", def: "How rapidly and dramatically a coin's price changes. Crypto is known for extreme volatility — both up and down." },
    { word: "Liquidity", def: "How easily a coin can be bought or sold without significantly impacting its price. High liquidity = easier to trade." },
    { word: "Private Key", def: "A secret password (long string of letters/numbers) that proves you own your crypto. NEVER share it with anyone." },
    { word: "Public Key", def: "Your crypto wallet address — like an email address. You share this with others so they can send you crypto." },
    { word: "RSI", def: "Relative Strength Index — a momentum indicator (0-100) showing if a coin is overbought (>70) or oversold (<30)." },
    { word: "MACD", def: "Moving Average Convergence Divergence — an indicator showing momentum direction. A crossover signals buy or sell opportunities." },
    { word: "Bollinger Bands", def: "Volatility bands placed above and below a moving average. When price hits the lower band, it often bounces back up." },
    { word: "ATR", def: "Average True Range — measures market volatility. High ATR = high volatility. Helps set smart stop-loss levels." },
    { word: "Fibonacci Retracement", def: "Key price levels (23.6%, 38.2%, 61.8%) derived from the Fibonacci sequence, used to predict support/resistance zones." },
    { word: "Stop-Loss", def: "An automatic sell order set below your buy price to limit losses if the market moves against you. Essential risk management." },
    { word: "Take-Profit", def: "An automatic sell order set above your buy price to lock in gains when the target price is reached." },
    { word: "DCA", def: "Dollar-Cost Averaging — investing a fixed amount at regular intervals regardless of price. Reduces risk of buying at the peak." },
    { word: "All-Time High (ATH)", def: "The highest price a cryptocurrency has ever reached in its entire history." },
    { word: "Rug Pull", def: "A scam where developers abandon a project and run away with all investors' money. A major risk in DeFi and new tokens." },
    { word: "Fear & Greed Index", def: "A 0–100 scale measuring market sentiment. Low = extreme fear (often a buy signal). High = extreme greed (sell signal)." },
    { word: "Long / Short", def: "Going 'long' means betting the price will rise (buy). Going 'short' means betting the price will fall (sell/borrow)." },
    { word: "Fork", def: "When a blockchain protocol is updated. A 'hard fork' creates a permanent split (like Bitcoin Cash from Bitcoin)." },
    { word: "Satoshi", def: "The smallest unit of Bitcoin. 1 Bitcoin = 100,000,000 Satoshis. Named after Bitcoin's creator, Satoshi Nakamoto." },
    { word: "P2P", def: "Peer-to-Peer — when two people transact directly without a middleman (bank or exchange)." },
    { word: "CEX / DEX", def: "Centralized Exchange (Binance, Coinbase) vs. Decentralized Exchange (Uniswap, 1inch). CEX is easier; DEX gives full control." },
    { word: "Pump and Dump", def: "A market manipulation scheme where a coin's price is artificially 'pumped' up before insiders 'dump' it on unsuspecting buyers." },
];

// --- Generate Glossary Grid ---
function buildGlossary() {
    const grid = document.getElementById('glossary-grid');
    if (!grid) return;

    grid.innerHTML = glossaryTerms
        .sort((a, b) => a.word.localeCompare(b.word))
        .map(t => `
        <div class="glossary-term" data-term="${t.word.toLowerCase()}">
            <div class="term-word">${t.word}</div>
            <div class="term-def">${t.def}</div>
        </div>
    `).join('');
}

// --- Search Filter ---
function filterGlossary() {
    const query = document.getElementById('glossary-search').value.toLowerCase();
    document.querySelectorAll('.glossary-term').forEach(el => {
        const term = el.getAttribute('data-term') || '';
        const def = el.querySelector('.term-def').textContent.toLowerCase();
        if (term.includes(query) || def.includes(query)) {
            el.classList.remove('term-hidden');
        } else {
            el.classList.add('term-hidden');
        }
    });
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    buildGlossary();

    // Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Scroll animation for cards
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.learn-card, .profit-method-card, .indicator-card, .glossary-term, .timeline-event, .calc-card, .gauge-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        observer.observe(card);
    });

    // Initialize FNG Gauge if visible
    if (document.getElementById('chapter-tools')) {
        updateFNGGauge();
    }
});

// --- DCA Simulation Logic ---
function runDCASimulation() {
    const amount = parseFloat(document.getElementById('dca-amount').value);
    const frequency = document.getElementById('dca-frequency').value;
    const years = parseInt(document.getElementById('dca-years').value);

    if (isNaN(amount) || amount <= 0) return;

    // Simulation constants (based on historical Bitcoin bull/bear cycles approx 40% annual growth)
    const annualRate = 0.40;
    const periodsPerYear = frequency === 'weekly' ? 52 : 12;
    const periodicRate = Math.pow(1 + annualRate, 1 / periodsPerYear) - 1;
    const totalPeriods = years * periodsPerYear;

    // Future Value formula for ordinary annuity
    const finalValue = amount * ((Math.pow(1 + periodicRate, totalPeriods) - 1) / periodicRate);
    const totalInvested = amount * totalPeriods;
    const profit = finalValue - totalInvested;
    const profitPct = (profit / totalInvested) * 100;

    // Update UI
    document.getElementById('res-invested').innerText = `₹${totalInvested.toLocaleString()}`;
    document.getElementById('res-value').innerText = `₹${Math.round(finalValue).toLocaleString()}`;
    document.getElementById('res-profit').innerText = `+${Math.round(profitPct)}%`;
}

// --- Fear & Greed Gauge ---
async function updateFNGGauge() {
    try {
        // Try to fetch from backend or fallback to official API
        let val = 50;
        let label = "Neutral";

        try {
            const response = await fetch('https://api.alternative.me/fng/');
            const data = await response.json();
            val = parseInt(data.data[0].value);
            label = data.data[0].value_classification;
        } catch (e) {
            console.warn("FNG API fetch failed, using fallback:", e);
        }

        const gaugeFill = document.getElementById('gauge-fill');
        const needle = document.getElementById('gauge-needle');
        const valDisplay = document.getElementById('fng-val');
        const labelDisplay = document.getElementById('fng-label');
        const adviceDisplay = document.getElementById('fng-advice');

        if (!gaugeFill) return;

        // Path is an arc from 20 to 180 (total angle 180)
        // val 0-100 -> angle 0-180
        const angle = (val / 100) * 180;
        const dashOffset = 500 - (val / 100 * 500); // Reversed for stroke-dasharray? Actually easier to use rotation

        // Accurate rotation for needle: 0 is at 20deg from horizontal left
        // Starting pos: x2="40" y2="60" for arc 20,100 -> 180,100
        // Simplest: just rotate the needle element from center 100,100
        needle.style.transform = `rotate(${val * 1.8}deg)`;

        // Update text
        valDisplay.innerText = val;
        labelDisplay.innerText = label;

        // Visual feedback for fill
        gaugeFill.style.strokeDasharray = `${val * 2.5} 500`; // Approximate
        if (val < 30) gaugeFill.style.stroke = "#00d764"; // Extreme Fear = Green (Buy)
        else if (val > 70) gaugeFill.style.stroke = "#ff4d4d"; // Extreme Greed = Red (Sell)
        else gaugeFill.style.stroke = "#6c5ce7";

        // Advice
        const advices = {
            'Extreme Fear': 'Market is terrified. Historically, this is a premium entry zone for long-term investors.',
            'Fear': 'Pessimism is high. Watch for reversal signals on RSI before entry.',
            'Neutral': 'Market is in equilibrium. Wait for a breakout or trend confirmation.',
            'Greed': 'Euphoria is rising. Be cautious and start securing some profits.',
            'Extreme Greed': 'Market is overheated. Major correction risks are extremely high. Avoid FOMO.'
        };
        adviceDisplay.innerText = advices[label] || "Monitor the trend carefully.";

    } catch (err) {
        console.error("Gauge update error:", err);
    }
}

// --- P/L Calculator ---
function calculatePL() {
    const buy = parseFloat(document.getElementById('pl-buy').value);
    const sell = parseFloat(document.getElementById('pl-sell').value);
    const resText = document.getElementById('pl-res-text');

    if (buy && sell) {
        const roi = ((sell - buy) / buy) * 100;
        resText.innerText = `ROI: ${roi.toFixed(2)}% (${roi >= 0 ? 'Profit' : 'Loss'})`;
        resText.style.color = roi >= 0 ? '#00d764' : '#ff4d4d';
    }
}
