// Chart Manager - Handles price chart visualization using ApexCharts
let priceChart = null;

// Initialize chart
function initChart() {
    const chartContainer = document.querySelector("#priceChart");
    if (!chartContainer) return;

    // ApexCharts options
    const options = {
        series: [],
        chart: {
            type: 'candlestick',
            height: 350,
            background: 'transparent',
            toolbar: {
                show: false
            },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            },
            fontFamily: 'Inter, sans-serif'
        },
        title: {
            text: undefined, // cleaner look without internal title
        },
        annotations: {
            xaxis: [{
                x: new Date().getTime(),
                borderColor: '#6c5ce7',
                label: {
                    style: {
                        color: '#fff',
                        background: '#6c5ce7',
                        fontSize: '10px',
                        padding: { left: 4, right: 4, top: 2, bottom: 2 }
                    },
                    text: 'TODAY',
                    orientation: 'horizontal',
                    offsetY: 0
                },
                strokeDashArray: 0,
            }]
        },
        xaxis: {
            type: 'datetime',
            tooltip: { enabled: false },
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: {
                style: { colors: '#6b6b8a', fontSize: '10px' },
                datetimeFormatter: { year: 'yyyy', month: 'MMM', day: 'dd' }
            },
            crosshairs: {
                show: true,
                width: 1,
                position: 'back',
                opacity: 0.9,
                stroke: { color: '#6c5ce7', width: 1, dashArray: 3 }
            }
        },
        yaxis: {
            tooltip: { enabled: true },
            labels: {
                style: { colors: '#6b6b8a', fontSize: '10px', fontFamily: 'JetBrains Mono' },
                formatter: (value) => "$" + value.toLocaleString()
            }
        },
        grid: {
            borderColor: 'rgba(255, 255, 255, 0.05)',
            strokeDashArray: 4,
            xaxis: { lines: { show: true } },
            yaxis: { lines: { show: true } },
            padding: { top: 0, right: 0, bottom: 0, left: 10 }
        },
        theme: { mode: 'dark' },
        plotOptions: {
            candlestick: {
                colors: {
                    upward: '#00E396',
                    downward: '#FF4560'
                },
                wick: { useFillColor: true }
            }
        },
        tooltip: {
            theme: 'dark',
            style: { fontSize: '12px' },
            x: { format: 'dd MMM yyyy' },
            y: { formatter: (value) => "$" + value.toLocaleString() }
        }
    };

    priceChart = new ApexCharts(chartContainer, options);
    priceChart.render();
}

// Update chart with new data
function updateChart(historicalData, predictionData) {
    if (!priceChart) {
        initChart();
    }

    if (!historicalData || historicalData.length === 0) {
        console.error('No historical data to display');
        return;
    }

    // Format historical data for ApexCharts Candlestick
    // Needed format: { x: date, y: [Open, High, Low, Close] }
    const historicalSeries = historicalData.map(item => {
        return {
            x: new Date(item.date).getTime(), // Timestamp
            y: [item.open, item.high, item.low, item.close]
        };
    });

    const seriesData = [{
        name: 'Historical',
        type: 'candlestick',
        data: historicalSeries
    }];

    // Add Prediction
    // Since prediction is just a price (Close), representing it as a point or line
    // For visual comparison, we can show it as a Line series
    // Add Prediction
    // Since prediction is just a price (Close), representing it as a point or line
    // For visual comparison, we can show it as a Line series
    if (predictionData) {
        // Handle array or object format
        const preds = Array.isArray(predictionData) ? predictionData : (predictionData.predictions || []);

        if (preds.length > 0 && historicalSeries.length > 0) {
            // Link predicted points to the last historical point
            const lastHistPoint = historicalSeries[historicalSeries.length - 1];

            // Convert predictions to line data points
            const predictionPoints = [];

            // Start connection from last known close
            if (lastHistPoint && lastHistPoint.y) {
                predictionPoints.push({
                    x: lastHistPoint.x,
                    y: lastHistPoint.y[3] // Close price
                });
            }

            preds.forEach(pred => {
                let timestamp;
                if (typeof pred.date === 'string') {
                    timestamp = new Date(pred.date).getTime();
                } else if (pred.date) {
                    timestamp = pred.date; // already ts
                } else {
                    return; // Skip invalid
                }

                const price = parseFloat(pred.price);
                if (!isNaN(price)) {
                    predictionPoints.push({
                        x: timestamp,
                        y: price
                    });
                }
            });

            if (predictionPoints.length > 0) {
                seriesData.push({
                    name: 'Predicted Path',
                    type: 'line',
                    data: predictionPoints,
                    color: '#6c5ce7', // Prediction color (Primary Purple)
                    stroke: {
                        width: 3,
                        dashArray: 5
                    }
                });
            }
        }
    }

    // Update chart
    priceChart.updateSeries(seriesData);

    // Update options if needed (e.g. title) but usually series update is enough
}

// Destroy chart
function destroyChart() {
    if (priceChart) {
        priceChart.destroy();
        priceChart = null;
    }
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChart);
} else {
    initChart();
}
