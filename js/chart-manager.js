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
                show: true,
                tools: {
                    download: false
                }
            },
            animations: {
                enabled: true
            }
        },
        title: {
            text: 'Live vs Predicted',
            align: 'left',
            style: {
                color: '#fff'
            }
        },
        xaxis: {
            type: 'datetime',
            labels: {
                style: {
                    colors: '#8e8da4'
                }
            },
            axisBorder: {
                show: false
            },
            axisTicks: {
                show: false
            }
        },
        yaxis: {
            tooltip: {
                enabled: true
            },
            labels: {
                style: {
                    colors: '#8e8da4'
                },
                formatter: function (value) {
                    return "$" + value.toLocaleString();
                }
            }
        },
        grid: {
            borderColor: '#2a2a3e',
            strokeDashArray: 4
        },
        theme: {
            mode: 'dark'
        },
        plotOptions: {
            candlestick: {
                colors: {
                    upward: '#00ff00',
                    downward: '#ff0000'
                }
            }
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
                    color: '#f5576c' // Prediction color
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
