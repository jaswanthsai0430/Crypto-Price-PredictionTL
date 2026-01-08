// Chart Manager - Handles price chart visualization
let priceChart = null;

// Initialize chart
function initChart() {
    const ctx = document.getElementById('priceChart');

    if (!ctx) {
        console.error('Chart canvas not found');
        return;
    }

    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Historical Price',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#667eea',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                },
                {
                    label: 'Predicted Price',
                    data: [],
                    borderColor: '#f5576c',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    borderWidth: 3,
                    borderDash: [10, 5],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#f5576c',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(26, 26, 46, 0.95)',
                    titleColor: '#fff',
                    bodyColor: '#a0a0b8',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toLocaleString('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                });
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b6b8a',
                        maxRotation: 45,
                        minRotation: 0
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b6b8a',
                        callback: function (value) {
                            return '$' + value.toLocaleString('en-US', {
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            });
                        }
                    }
                }
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        }
    });
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

    // Prepare historical data
    const labels = [];
    const prices = [];

    historicalData.forEach(item => {
        labels.push(formatChartDate(item.date));
        prices.push(item.close);
    });

    // Prepare prediction data
    let predictionLabels = [];
    let predictionPrices = [];

    if (predictionData && predictionData.predictions) {
        // Add last historical point to connect the lines
        predictionLabels.push(labels[labels.length - 1]);
        predictionPrices.push(prices[prices.length - 1]);

        // Add prediction points
        predictionData.predictions.forEach(pred => {
            predictionLabels.push(formatChartDate(pred.date));
            predictionPrices.push(pred.price);
        });

        // Extend labels to include prediction dates
        predictionData.predictions.forEach(pred => {
            labels.push(formatChartDate(pred.date));
        });
    }

    // Update chart data
    priceChart.data.labels = labels;

    // Historical dataset
    priceChart.data.datasets[0].data = prices;

    // Prediction dataset - fill with null for historical period
    const predictionDataset = new Array(prices.length - 1).fill(null);
    predictionDataset.push(...predictionPrices);
    priceChart.data.datasets[1].data = predictionDataset;

    // Update chart
    priceChart.update('active');
}

// Format date for chart
function formatChartDate(dateString) {
    const date = new Date(dateString);
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
}

// Destroy chart (cleanup)
function destroyChart() {
    if (priceChart) {
        priceChart.destroy();
        priceChart = null;
    }
}

// Initialize chart when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChart);
} else {
    initChart();
}
