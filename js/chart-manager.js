// Chart Manager - Professional Price/Volume Viz with Neon AI Path
let priceChart = null;
let volumeChart = null;

// Initialize charts with pro aesthetics
function initChart() {
    const priceContainer = document.querySelector("#priceChart");
    const volumeContainer = document.querySelector("#volumeChart");
    if (!priceContainer || !volumeContainer) return;

    // Common styling tokens
    const commonOptions = {
        chart: {
            background: 'transparent',
            toolbar: { show: false },
            animations: { enabled: true, easing: 'linear', speed: 200 },
            fontFamily: 'Inter, sans-serif',
            sparkline: { enabled: false }
        },
        theme: { mode: 'dark' },
        grid: {
            borderColor: 'rgba(255, 255, 255, 0.05)',
            strokeDashArray: 4,
            padding: { left: 10, right: 10 }
        },
        xaxis: {
            type: 'datetime',
            labels: { show: false },
            axisBorder: { show: false },
            axisTicks: { show: false },
            crosshairs: {
                show: true,
                stroke: { color: '#6c5ce7', width: 1, dashArray: 3 }
            }
        },
        yaxis: {
            labels: {
                style: { colors: '#6b6b8a', fontSize: '10px', fontFamily: 'JetBrains Mono' },
                formatter: (val) => val > 1000 ? "$" + Math.round(val).toLocaleString() : "$" + val.toFixed(2)
            }
        },
        noData: {
            text: 'Analyzing Market Data...',
            style: { color: '#8888aa', fontSize: '14px' }
        }
    };

    // Price Chart Options (Candlestick + Technical Indicators + Pro Forecast)
    const priceOptions = {
        ...commonOptions,
        series: [],
        chart: {
            ...commonOptions.chart,
            id: 'price-chart',
            type: 'candlestick',
            height: 380,
            group: 'trading-view',
            // Add drop shadow for the "Neon" effect
            dropShadow: {
                enabled: true,
                top: 0,
                left: 0,
                blur: 3,
                opacity: 0.35,
                color: '#6c5ce7'
            }
        },
        plotOptions: {
            candlestick: {
                colors: { upward: '#00D764', downward: '#FF4D6D' },
                wick: { useFillColor: true }
            }
        },
        stroke: {
            width: [1, 2, 2, 2, 4], // Thicker AI path (Index 4)
            curve: 'smooth',
            dashArray: [0, 0, 0, 0, 0] // Solid AI Path for maximum clarity
        },
        // Neon Purple for AI path, distinct colors for MAs
        colors: ['#fff', '#feb019', '#00e396', '#ff4560', '#A29BFE'],
        tooltip: {
            theme: 'dark',
            x: { format: 'dd MMM HH:mm' },
            y: { formatter: (v) => "$" + v.toLocaleString() }
        },
        markers: {
            size: 0,
            hover: { size: 5, strokeWidth: 0 }
        }
    };

    // Volume Chart Options
    const volumeOptions = {
        ...commonOptions,
        series: [],
        chart: {
            ...commonOptions.chart,
            id: 'volume-chart',
            type: 'bar',
            height: 120,
            group: 'trading-view'
        },
        xaxis: {
            ...commonOptions.xaxis,
            labels: { show: true, style: { colors: '#6b6b8a', fontSize: '10px' } }
        },
        yaxis: {
            ...commonOptions.yaxis,
            labels: {
                ...commonOptions.yaxis.labels,
                formatter: (val) => val >= 1e6 ? (val / 1e6).toFixed(1) + 'M' : (val / 1e3).toFixed(1) + 'K'
            },
            max: (max) => max * 1.5
        },
        plotOptions: {
            bar: { columnWidth: '85%' }
        },
        dataLabels: { enabled: false }
    };

    priceChart = new ApexCharts(priceContainer, priceOptions);
    volumeChart = new ApexCharts(volumeContainer, volumeOptions);

    priceChart.render();
    volumeChart.render();
}

// Calculate Moving Average based on OHLC data
function calculateMA(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push({ x: data[i].x, y: null });
            continue;
        }
        let sum = 0;
        for (let j = 0; j < period; j++) {
            sum += data[i - j].y[3]; // Close price index
        }
        result.push({ x: data[i].x, y: parseFloat((sum / period).toFixed(2)) });
    }
    return result;
}

// Synchronously update both charts with fresh data
function updateChart(historicalData, predictionData) {
    if (!priceChart) initChart();
    if (!historicalData || historicalData.length === 0) return;

    // Filter valid data points
    const validData = historicalData.filter(d => d.close > 0);

    const ohlc = validData.map(item => ({
        x: new Date(item.date).getTime(),
        y: [item.open, item.high, item.low, item.close]
    }));

    const volume = validData.map(item => ({
        x: new Date(item.date).getTime(),
        y: item.volume
    }));

    // Technical Analysis Layer
    const ma7 = calculateMA(ohlc, 7);
    const ma25 = calculateMA(ohlc, 25);
    const ma99 = calculateMA(ohlc, 99);

    const priceSeries = [
        { name: 'Price', type: 'candlestick', data: ohlc },
        { name: 'MA7', type: 'line', data: ma7 },
        { name: 'MA25', type: 'line', data: ma25 },
        { name: 'MA99', type: 'line', data: ma99 }
    ];

    // High Impact AI Forecast Path
    if (predictionData && predictionData.predictions && predictionData.predictions.length > 0) {
        const lastPoint = ohlc[ohlc.length - 1];
        const predPoints = [{ x: lastPoint.x, y: lastPoint.y[3] }];

        predictionData.predictions.forEach(p => {
            predPoints.push({ x: new Date(p.date).getTime(), y: p.price });
        });

        priceSeries.push({
            name: 'AI Path Highlighted',
            type: 'line',
            data: predPoints
        });
    }

    priceChart.updateSeries(priceSeries);

    // Color-coded Volume Series
    const volumeData = volume.map((v, i) => {
        const item = validData[i];
        return {
            x: v.x,
            y: v.y,
            fillColor: item.close >= item.open ? '#00D764' : '#FF4D6D'
        };
    });

    volumeChart.updateSeries([{
        name: 'Volume',
        data: volumeData
    }]);
}

function destroyChart() {
    if (priceChart) priceChart.destroy();
    if (volumeChart) volumeChart.destroy();
    priceChart = null;
    volumeChart = null;
}

// Automatic init on entry
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChart);
} else {
    initChart();
}
