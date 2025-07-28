"""
Project Genji - Data Collection Module
This module handles automated data collection from various news sources.
"""

import os
import logging
import requests
import feedparser
import psycopg2
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Handles data collection from various news sources"""
    
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # RSS Feed sources for market intelligence
        self.rss_sources = [
            {
                'name': 'BBC Technology',
                'url': 'http://feeds.bbci.co.uk/news/technology/rss.xml',
                'category': 'Technology'
            },
            {
                'name': 'Reuters Business',
                'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
                'category': 'Business'
            },
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com/feed/',
                'category': 'Technology'
            }
        ]
    
    def get_database_connection(self):
        """Create database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def collect_rss_articles(self, source: Dict) -> List[Dict]:
        """Collect articles from RSS feed"""
        articles = []
        
        try:
            logger.info(f"Fetching from {source['name']}: {source['url']}")
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:10]:  # Limit to 10 articles per source
                article = {
                    'source': source['name'],
                    'title': entry.get('title', ''),
                    'description': entry.get('description', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'category': source['category']
                }
                articles.append(article)
                
            logger.info(f"Collected {len(articles)} articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error fetching RSS from {source['name']}: {e}")
        
        return articles
    
    def store_article(self, conn, article: Dict) -> bool:
        """Store article in database"""
        try:
            with conn.cursor() as cur:
                # Combine title and description for raw_text
                raw_text = f"{article['title']}. {article['description']}"
                
                insert_query = """
                    INSERT INTO market_insights (source, title, raw_text, url, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (url) DO NOTHING
                """
                
                cur.execute(insert_query, (
                    article['source'],
                    article['title'],
                    raw_text,
                    article['link']
                ))
                
                return cur.rowcount > 0  # Returns True if row was inserted
                
        except Exception as e:
            logger.error(f"Error storing article: {e}")
            return False
    
    def run_collection(self) -> int:
        """Run the complete data collection process"""
        total_new_articles = 0
        conn = None
        
        try:
            conn = self.get_database_connection()
            
            for source in self.rss_sources:
                articles = self.collect_rss_articles(source)
                
                new_articles_count = 0
                for article in articles:
                    if self.store_article(conn, article):
                        new_articles_count += 1
                
                logger.info(f"Stored {new_articles_count} new articles from {source['name']}")
                total_new_articles += new_articles_count
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Collection process error: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
        
        logger.info(f"Collection completed. Total new articles: {total_new_articles}")
        return total_new_articles

def main():
    """Main execution function for data collection"""
    try:
        collector = DataCollector()
        new_articles = collector.run_collection()
        
        if new_articles > 0:
            print(f"✅ Successfully collected {new_articles} new articles")
        else:
            print("ℹ️ No new articles were collected")
            
    except Exception as e:
        logger.error(f"Data collection error: {e}")
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
