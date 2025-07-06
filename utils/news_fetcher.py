"""
News fetching utility for stock analysis dashboard.
Fetches relevant financial news for stocks from multiple sources.
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import trafilatura
import time
import os

class NewsAPI:
    """Fetch financial news from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_stock_news(self, symbol: str, company_name: Optional[str] = None, max_articles: int = 5) -> List[Dict]:
        """
        Get news articles for a specific stock from multiple sources
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'SHOP.TO')
            company_name: Company name for better search results
            max_articles: Maximum number of articles to return
            
        Returns:
            List of news articles with title, summary, link, date, and source
        """
        news_articles = []
        
        # Clean symbol for search (remove exchange suffixes)
        clean_symbol = symbol.replace('.TO', '').replace('.V', '').replace('.TSX', '')
        
        # Try multiple news sources
        sources = [
            self._get_yahoo_finance_news,
            self._get_google_finance_news,
            self._get_finviz_news,
            self._get_reuters_news
        ]
        
        for source_func in sources:
            try:
                articles = source_func(clean_symbol, company_name)
                news_articles.extend(articles)
                if len(news_articles) >= max_articles:
                    break
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching from source: {e}")
                continue
        
        # Remove duplicates and sort by date
        unique_articles = self._remove_duplicates(news_articles)
        unique_articles = sorted(unique_articles, key=lambda x: x.get('date', datetime.min), reverse=True)
        
        return unique_articles[:max_articles]
    
    def _get_yahoo_finance_news(self, symbol: str, company_name: Optional[str] = None) -> List[Dict]:
        """Get news from Yahoo Finance RSS feed"""
        try:
            # Yahoo Finance RSS feed for stock news
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            feed = feedparser.parse(url)
            
            articles = []
            for entry in feed.entries[:10]:  # Limit to 10 entries
                articles.append({
                    'title': entry.title,
                    'summary': entry.get('summary', entry.title),
                    'link': entry.link,
                    'date': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'source': 'Yahoo Finance'
                })
            
            return articles
        except Exception as e:
            print(f"Yahoo Finance news error: {e}")
            return []
    
    def _get_google_finance_news(self, symbol: str, company_name: Optional[str] = None) -> List[Dict]:
        """Get news from Google Finance RSS feed"""
        try:
            # Google Finance RSS feed
            search_term = company_name if company_name else symbol
            url = f"https://news.google.com/rss/search?q={search_term}+stock+finance&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)
            
            articles = []
            for entry in feed.entries[:5]:  # Limit to 5 entries
                articles.append({
                    'title': entry.title,
                    'summary': entry.get('summary', entry.title),
                    'link': entry.link,
                    'date': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                    'source': 'Google News'
                })
            
            return articles
        except Exception as e:
            print(f"Google Finance news error: {e}")
            return []
    
    def _get_finviz_news(self, symbol: str, company_name: Optional[str] = None) -> List[Dict]:
        """Get news from Finviz (simulated - would need scraping)"""
        try:
            # This would typically require web scraping
            # For now, return empty list to avoid scraping issues
            return []
        except Exception as e:
            print(f"Finviz news error: {e}")
            return []
    
    def _get_reuters_news(self, symbol: str, company_name: Optional[str] = None) -> List[Dict]:
        """Get news from Reuters RSS feed"""
        try:
            # Reuters business news RSS feed
            url = "https://feeds.reuters.com/reuters/businessNews"
            feed = feedparser.parse(url)
            
            articles = []
            search_terms = [symbol.upper(), company_name.upper() if company_name else '']
            
            for entry in feed.entries[:20]:  # Check more entries for relevance
                title_upper = entry.title.upper()
                summary_upper = entry.get('summary', '').upper()
                
                # Check if article mentions the stock or company
                if any(term and term in title_upper or term in summary_upper for term in search_terms):
                    articles.append({
                        'title': entry.title,
                        'summary': entry.get('summary', entry.title),
                        'link': entry.link,
                        'date': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                        'source': 'Reuters'
                    })
            
            return articles[:3]  # Return top 3 relevant articles
        except Exception as e:
            print(f"Reuters news error: {e}")
            return []
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_lower = article['title'].lower()
            # Simple duplicate detection
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_market_news(self, max_articles: int = 10) -> List[Dict]:
        """Get general market news"""
        try:
            # General market news from multiple sources
            sources = [
                "https://feeds.reuters.com/reuters/businessNews",
                "https://rss.cnn.com/rss/money_latest.rss",
                "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"
            ]
            
            all_articles = []
            
            for source_url in sources:
                try:
                    feed = feedparser.parse(source_url)
                    for entry in feed.entries[:5]:
                        all_articles.append({
                            'title': entry.title,
                            'summary': entry.get('summary', entry.title),
                            'link': entry.link,
                            'date': datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                            'source': self._get_source_name(source_url)
                        })
                except Exception as e:
                    print(f"Error fetching from {source_url}: {e}")
                    continue
            
            # Sort by date and return most recent
            all_articles = sorted(all_articles, key=lambda x: x.get('date', datetime.min), reverse=True)
            return all_articles[:max_articles]
            
        except Exception as e:
            print(f"Market news error: {e}")
            return []
    
    def _get_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        if 'reuters' in url:
            return 'Reuters'
        elif 'cnn' in url:
            return 'CNN Business'
        elif 'yahoo' in url:
            return 'Yahoo Finance'
        else:
            return 'Financial News'
    
    def get_news_summary(self, article_url: str) -> str:
        """Get full article content summary using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(article_url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text:
                    # Return first few sentences as summary
                    sentences = text.split('.')[:3]
                    return '.'.join(sentences) + '.' if sentences else text[:300]
            return "Summary not available"
        except Exception as e:
            print(f"Error extracting article summary: {e}")
            return "Summary not available"
    
    def format_news_for_display(self, articles: List[Dict]) -> List[Dict]:
        """Format news articles for display in Streamlit"""
        formatted_articles = []
        
        for article in articles:
            # Calculate how long ago the article was published
            if article.get('date'):
                time_diff = datetime.now() - article['date']
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hours ago"
                else:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes} minutes ago"
            else:
                time_ago = "Recently"
            
            formatted_articles.append({
                'title': article.get('title', 'No title'),
                'summary': article.get('summary', 'No summary available'),
                'link': article.get('link', '#'),
                'source': article.get('source', 'Unknown'),
                'time_ago': time_ago,
                'date': article.get('date', datetime.now())
            })
        
        return formatted_articles