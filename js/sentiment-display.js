// Sentiment Display Manager
function updateSentiment(sentimentData) {
    if (!sentimentData) {
        console.error('No sentiment data provided');
        return;
    }

    // Update sentiment score
    updateSentimentMeter(sentimentData.score);

    // Update sentiment label
    const labelElement = document.getElementById('sentiment-label');
    if (labelElement) {
        labelElement.textContent = sentimentData.category || 'Unknown';
        labelElement.style.color = sentimentData.color || '#ffb800';
    }

    // Update breakdown counts
    updateBreakdownCounts(sentimentData);

    // Update summary
    updateSentimentSummary(sentimentData.summary);

    // Update news list
    updateNewsList(sentimentData.articles);
}

// Update sentiment meter animation
function updateSentimentMeter(score) {
    const scoreElement = document.getElementById('sentiment-score');
    const meterFill = document.getElementById('meter-fill');

    if (!scoreElement || !meterFill) return;

    // Animate score counter
    animateValue(scoreElement, 0, score, 1000);

    // Calculate arc length (251.2 is the total arc length)
    const totalLength = 251.2;
    const offset = totalLength - (totalLength * score / 100);

    // Animate meter fill
    meterFill.style.transition = 'stroke-dashoffset 1.5s ease-out';
    meterFill.style.strokeDashoffset = offset;

    // Update gradient based on score
    updateMeterGradient(score);
}

// Update meter gradient color based on score
function updateMeterGradient(score) {
    const gradient = document.getElementById('gradient');
    if (!gradient) return;

    // Define color stops based on score ranges
    let color1, color2;

    if (score < 20) {
        color1 = '#ff0000';
        color2 = '#ff0000';
    } else if (score < 40) {
        color1 = '#ff0000';
        color2 = '#ff6b00';
    } else if (score < 60) {
        color1 = '#ff6b00';
        color2 = '#ffb800';
    } else if (score < 80) {
        color1 = '#ffb800';
        color2 = '#90ee90';
    } else {
        color1 = '#90ee90';
        color2 = '#00ff00';
    }

    // This is a simplified version - the gradient is already defined in HTML
    // For dynamic updates, you would need to modify the gradient stops
}

// Animate number counter
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// Update breakdown counts
function updateBreakdownCounts(data) {
    const positiveElement = document.getElementById('positive-count');
    const neutralElement = document.getElementById('neutral-count');
    const negativeElement = document.getElementById('negative-count');

    if (positiveElement) {
        animateValue(positiveElement, 0, data.positive || 0, 800);
    }

    if (neutralElement) {
        animateValue(neutralElement, 0, data.neutral || 0, 800);
    }

    if (negativeElement) {
        animateValue(negativeElement, 0, data.negative || 0, 800);
    }
}

// Update sentiment summary
function updateSentimentSummary(summary) {
    const summaryElement = document.getElementById('sentiment-summary');

    if (summaryElement && summary) {
        // Fade out
        summaryElement.style.opacity = '0';

        setTimeout(() => {
            summaryElement.textContent = summary;
            // Fade in
            summaryElement.style.transition = 'opacity 0.5s ease';
            summaryElement.style.opacity = '1';
        }, 300);
    }
}

// Update news list
function updateNewsList(articles) {
    const newsList = document.getElementById('news-list');

    if (!newsList) return;

    // Clear existing news
    newsList.innerHTML = '';

    if (!articles || articles.length === 0) {
        newsList.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No recent news available</p>';
        return;
    }

    // Display up to 5 articles
    const displayArticles = articles.slice(0, 5);

    displayArticles.forEach((article, index) => {
        const newsItem = createNewsItem(article, index);
        newsList.appendChild(newsItem);
    });
}

// Create news item element
function createNewsItem(article, index) {
    const item = document.createElement('div');
    item.className = `news-item ${article.sentiment_label.toLowerCase()}`;
    item.style.animationDelay = `${index * 0.1}s`;

    const sentimentLabel = article.sentiment_label || 'Neutral';
    const sentimentClass = sentimentLabel.toLowerCase();

    item.innerHTML = `
        <div class="news-header">
            <div class="news-title">${escapeHtml(article.title)}</div>
            <span class="news-sentiment ${sentimentClass}">${sentimentLabel}</span>
        </div>
        <div class="news-meta">
            <span>${article.source || 'Unknown Source'}</span>
            <span>${formatNewsDate(article.published_at)}</span>
        </div>
    `;

    // Add click handler if URL is available
    if (article.url && article.url !== '#') {
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
            window.open(article.url, '_blank');
        });
    }

    return item;
}

// Format news date
function formatNewsDate(dateString) {
    if (!dateString) return 'Recently';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
        return `${diffMins}m ago`;
    } else if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else if (diffDays < 7) {
        return `${diffDays}d ago`;
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS animations for news items
const newsStyle = document.createElement('style');
newsStyle.textContent = `
    .news-item {
        animation: newsSlideIn 0.5s ease forwards;
        opacity: 0;
    }
    
    @keyframes newsSlideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(newsStyle);
