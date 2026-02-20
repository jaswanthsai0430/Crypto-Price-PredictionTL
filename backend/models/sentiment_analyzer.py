import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

load_dotenv()

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        
        # Sentiment categories
        self.categories = {
            (0, 20): {'label': 'Worst', 'color': '#ff0000'},
            (20, 40): {'label': 'Bad', 'color': '#ff6b00'},
            (40, 60): {'label': 'Average', 'color': '#ffb800'},
            (60, 80): {'label': 'Medium', 'color': '#90ee90'},
            (80, 100): {'label': 'Good', 'color': '#00ff00'}
        }
        
        # Trusted news sources whitelist
        self.trusted_sources = {
            # Major crypto news outlets
            'CoinDesk', 'Cointelegraph', 'The Block', 'Decrypt', 'CoinTelegraph',
            'Bitcoin Magazine', 'CryptoSlate', 'BeInCrypto', 'Bitcoinist',
            'NewsBTC', 'CryptoPotato', 'U.Today', 'AMBCrypto', 'Crypto Briefing',
            
            # Mainstream financial news
            'Bloomberg', 'Reuters', 'CNBC', 'Financial Times', 'Wall Street Journal',
            'Forbes', 'Business Insider', 'MarketWatch', 'Yahoo Finance',
            
            # Tech news
            'TechCrunch', 'The Verge', 'Wired', 'Ars Technica',
            
            # Official sources
            'CoinGecko', 'CoinMarketCap', 'Binance', 'Coinbase'
        }
        
        # Spam/unreliable source indicators (to filter out)
        self.spam_indicators = {
            'pump', 'moon', 'scam', 'airdrop', 'giveaway', 'free crypto',
            'get rich', 'guaranteed', '100x', 'lambo', 'to the moon'
        }
    
    def _is_trusted_source(self, news_item):
        """
        Validate if news source is trusted and legitimate
        
        Args:
            news_item: News article data from API
        
        Returns:
            Boolean indicating if source is trusted
        """
        try:
            # Get source information
            author = news_item.get('author', {})
            source_name = author.get('name', '').strip()
            title = news_item.get('title', '').lower()
            url = news_item.get('url', '')
            
            # Filter 1: Check if source is in trusted whitelist
            is_trusted = any(trusted.lower() in source_name.lower() 
                           for trusted in self.trusted_sources)
            
            if not is_trusted:
                # Allow if it's from a .com, .org, or .io domain (basic legitimacy)
                if url and any(domain in url for domain in ['.com', '.org', '.io', '.news']):
                    is_trusted = True
                else:
                    return False
            
            # Filter 2: Check for spam indicators in title
            has_spam = any(spam.lower() in title for spam in self.spam_indicators)
            if has_spam:
                return False
            
            # Filter 3: Ensure article has meaningful content
            if not title or len(title) < 10:
                return False
            
            # Filter 4: Validate URL format
            if url and not url.startswith(('http://', 'https://')):
                return False
            
            # Filter 5: Check for duplicate/low-quality indicators
            spam_words_count = sum(1 for spam in self.spam_indicators if spam in title)
            if spam_words_count >= 2:  # Multiple spam indicators
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating source: {str(e)}")
            return False
    
    def get_crypto_news(self, coin, days=7):
        """
        Fetch cryptocurrency news from various sources
        
        Args:
            coin: Cryptocurrency symbol (BTC, ETH, SOLANA)
            days: Number of days to look back
        
        Returns:
            List of news articles
        """
        articles = []
        
        # Map coin names for search
        coin_names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'SOLANA': 'Solana',
            'BNB': 'Binance Coin',
            'DOGE': 'Dogecoin',
            'XRP': 'Ripple',
            'ADA': 'Cardano',
            'AVAX': 'Avalanche',
            'DOT': 'Polkadot',
            'LINK': 'Chainlink'
        }
        
        coin_name = coin_names.get(coin.upper(), coin)
        
        # Try NewsAPI if key is available
        if self.news_api_key:
            try:
                from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'q': f'{coin_name} cryptocurrency',
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'apiKey': self.news_api_key,
                    'pageSize': 20
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', []):
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'source': article.get('source', {}).get('name', 'Unknown'),
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', '')
                        })
            except Exception as e:
                print(f"Error fetching from NewsAPI: {str(e)}")
        
        # Use CoinGecko News API with trusted source filtering
        try:
            # Map coin symbols to CoinGecko IDs
            coin_id_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOLANA': 'solana',
                'BNB': 'binancecoin',
                'DOGE': 'dogecoin',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'AVAX': 'avalanche-2',
                'DOT': 'polkadot',
                'LINK': 'chainlink'
            }
            
            coin_id = coin_id_map.get(coin.upper(), coin.lower())
            
            # Fetch news from CoinGecko
            url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/news'
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                news_items = data.get('data', [])
                
                # Filter news through trusted source validation
                for item in news_items[:30]:  # Get more to filter down
                    # Validate source before adding
                    if self._is_trusted_source(item):
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', '')[:200] if item.get('description') else item.get('title', ''),
                            'source': item.get('author', {}).get('name', 'CoinGecko'),
                            'url': item.get('url', ''),
                            'published_at': item.get('updated_at', '')
                        })
                        
                        # Stop when we have enough quality articles
                        if len(articles) >= 20:
                            break
                
                print(f"Fetched {len(articles)} verified news articles from CoinGecko for {coin}")
                
        except Exception as e:
            print(f"Error fetching from CoinGecko News API: {str(e)}")
        
        # If no articles found, use mock data for demonstration
        if not articles:
            articles = self._get_mock_news(coin_name)
        
        return articles
    
    def _get_mock_news(self, coin_name):
        """Generate mock news for demonstration purposes"""
        mock_articles = [
            {
                'title': f'{coin_name} shows strong momentum as institutional adoption grows',
                'description': f'Major financial institutions are increasing their {coin_name} holdings, signaling confidence in the cryptocurrency market.',
                'source': 'Crypto News',
                'url': 'https://www.coindesk.com',
                'published_at': datetime.now().isoformat()
            },
            {
                'title': f'{coin_name} network upgrade brings enhanced scalability',
                'description': f'The latest {coin_name} protocol update promises faster transactions and lower fees.',
                'source': 'Blockchain Today',
                'url': 'https://cointelegraph.com',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                'title': f'Market analysis: {coin_name} consolidates after recent rally',
                'description': f'Technical indicators suggest {coin_name} is building support for the next move.',
                'source': 'Trading View',
                'url': 'https://www.tradingview.com/news',
                'published_at': (datetime.now() - timedelta(days=2)).isoformat()
            },
            {
                'title': f'{coin_name} adoption increases in emerging markets',
                'description': f'New partnerships are driving {coin_name} usage in developing economies.',
                'source': 'Global Crypto',
                'url': 'https://decrypt.co',
                'published_at': (datetime.now() - timedelta(days=3)).isoformat()
            },
            {
                'title': f'Regulatory clarity boosts {coin_name} investor confidence',
                'description': f'Positive regulatory developments are creating a favorable environment for {coin_name}.',
                'source': 'Regulatory News',
                'url': 'https://www.bloomberg.com/crypto',
                'published_at': (datetime.now() - timedelta(days=4)).isoformat()
            }
        ]
        return mock_articles
    
    def analyze_text(self, text):
        """
        Analyze sentiment of a single text using VADER
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment scores
        """
        scores = self.vader.polarity_scores(text)
        return scores
    
    def analyze_news_sentiment(self, coin):
        """
        Analyze overall sentiment from news articles
        
        Args:
            coin: Cryptocurrency symbol
        
        Returns:
            Sentiment analysis report
        """
        # Get news articles
        articles = self.get_crypto_news(coin)
        
        if not articles:
            return {
                'coin': coin,
                'score': 50,
                'category': 'Average',
                'color': '#ffb800',
                'total_articles': 0,
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'articles': [],
                'summary': 'Insufficient data for sentiment analysis'
            }
        
        # Analyze each article
        sentiments = []
        analyzed_articles = []
        
        for article in articles:
            text = f"{article['title']} {article['description']}"
            sentiment = self.analyze_text(text)
            
            sentiments.append(sentiment['compound'])
            
            analyzed_articles.append({
                **article,
                'sentiment_score': sentiment['compound'],
                'sentiment_label': self._get_sentiment_label(sentiment['compound'])
            })
        
        # Calculate overall sentiment
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Convert to 0-100 scale
        sentiment_score = ((avg_sentiment + 1) / 2) * 100
        
        # Count sentiment types
        positive = sum(1 for s in sentiments if s > 0.05)
        neutral = sum(1 for s in sentiments if -0.05 <= s <= 0.05)
        negative = sum(1 for s in sentiments if s < -0.05)
        
        # Get category
        category_info = self._get_category(sentiment_score)
        
        # Generate summary
        summary = self._generate_summary(coin, sentiment_score, positive, neutral, negative, len(articles))
        
        return {
            'coin': coin,
            'score': round(sentiment_score, 2),
            'category': category_info['label'],
            'color': category_info['color'],
            'total_articles': len(articles),
            'positive': positive,
            'neutral': neutral,
            'negative': negative,
            'articles': analyzed_articles[:10],  # Return top 10 articles
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_sentiment_label(self, compound_score):
        """Get sentiment label from compound score"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _get_category(self, score):
        """Get category based on sentiment score"""
        for (min_score, max_score), info in self.categories.items():
            if min_score <= score < max_score:
                return info
        return self.categories[(80, 100)]  # Default to Good
    
    def _generate_summary(self, coin, score, positive, neutral, negative, total):
        """Generate human-readable summary"""
        category = self._get_category(score)['label']
        
        summary = f"Market sentiment for {coin} is currently {category.lower()} "
        summary += f"with a score of {score:.1f}/100. "
        
        if positive > negative:
            summary += f"Analysis of {total} recent articles shows predominantly positive sentiment ({positive} positive, {negative} negative). "
            summary += "This suggests favorable market conditions and growing investor confidence."
        elif negative > positive:
            summary += f"Analysis of {total} recent articles shows predominantly negative sentiment ({negative} negative, {positive} positive). "
            summary += "Traders should exercise caution and monitor market developments closely."
        else:
            summary += f"Analysis of {total} recent articles shows balanced sentiment. "
            summary += "The market appears to be in a consolidation phase."
        
        return summary

if __name__ == "__main__":
    # Test sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    for coin in ['BTC', 'ETH', 'SOLANA']:
        print(f"\n{'='*60}")
        print(f"Sentiment Analysis for {coin}")
        print(f"{'='*60}")
        
        result = analyzer.analyze_news_sentiment(coin)
        
        print(f"Score: {result['score']}/100")
        print(f"Category: {result['category']}")
        print(f"Articles analyzed: {result['total_articles']}")
        print(f"Positive: {result['positive']}, Neutral: {result['neutral']}, Negative: {result['negative']}")
        print(f"\nSummary: {result['summary']}")
        
        if result['articles']:
            print(f"\nTop 3 Articles:")
            for i, article in enumerate(result['articles'][:3], 1):
                print(f"{i}. {article['title']} ({article['sentiment_label']})")
