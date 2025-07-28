"""
Project Genji - n8n Integration Module
This module provides webhook endpoints and API integration for n8n workflows
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Import our existing analysis module
from main import GenjiAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8nIntegration:
    """Handles integration between n8n workflows and Project Genji"""
    
    def __init__(self):
        load_dotenv()
        self.analyzer = GenjiAnalyzer()
        
        # Database configuration
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def get_database_connection(self):
        """Create and return a database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def process_n8n_article(self, article_data: Dict) -> Dict:
        """
        Process a single article from n8n workflow
        
        Args:
            article_data: Dictionary containing article data from n8n
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Extract data from n8n payload
            title = article_data.get('title', '')
            content = article_data.get('content', article_data.get('description', ''))
            link = article_data.get('link', '')
            pub_date = article_data.get('pubDate', datetime.now().isoformat())
            
            logger.info(f"Processing article from n8n: {title[:50]}...")
            
            # Store article in database
            article_id = self.store_article(title, content, link, pub_date)
            
            if not article_id:
                return {
                    'success': False,
                    'error': 'Failed to store article in database'
                }
            
            # Analyze with AI
            analysis_result = self.analyzer.analyze_text_with_gemini(content, title)
            
            if analysis_result:
                # Update database with analysis
                conn = self.get_database_connection()
                success = self.analyzer.update_article_analysis(conn, article_id, analysis_result)
                conn.close()
                
                if success:
                    return {
                        'success': True,
                        'article_id': article_id,
                        'analysis': analysis_result,
                        'message': 'Article processed successfully'
                    }
                else:
                    return {
                        'success': False,
                        'article_id': article_id,
                        'error': 'Failed to update analysis results'
                    }
            else:
                return {
                    'success': False,
                    'article_id': article_id,
                    'error': 'AI analysis failed'
                }
                
        except Exception as e:
            logger.error(f"Error processing n8n article: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def store_article(self, title: str, content: str, link: str, pub_date: str) -> Optional[int]:
        """
        Store article in database and return the article ID
        
        Returns:
            Article ID if successful, None if failed
        """
        try:
            conn = self.get_database_connection()
            
            with conn.cursor() as cur:
                # Check if article already exists
                cur.execute("""
                    SELECT id FROM market_insights 
                    WHERE url = %s OR title = %s
                """, (link, title))
                
                existing = cur.fetchone()
                if existing:
                    logger.info(f"Article already exists with ID: {existing[0]}")
                    conn.close()
                    return existing[0]
                
                # Insert new article
                insert_query = """
                    INSERT INTO market_insights 
                    (title, raw_text, url, source, category, published_at, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    RETURNING id
                """
                
                cur.execute(insert_query, (
                    title,
                    content,
                    link,
                    'n8n_workflow',  # Source identifier
                    'Technology',    # Default category
                    pub_date
                ))
                
                article_id = cur.fetchone()[0]
                conn.commit()
                conn.close()
                
                logger.info(f"Stored new article with ID: {article_id}")
                return article_id
                
        except Exception as e:
            logger.error(f"Error storing article: {e}")
            if 'conn' in locals():
                conn.close()
            return None
    
    def process_bulk_articles(self, articles: List[Dict]) -> Dict:
        """
        Process multiple articles from n8n workflow
        
        Args:
            articles: List of article dictionaries from n8n
            
        Returns:
            Summary of processing results
        """
        results = {
            'total_articles': len(articles),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'processed_ids': []
        }
        
        for i, article in enumerate(articles):
            try:
                result = self.process_n8n_article(article)
                
                if result['success']:
                    results['successful'] += 1
                    results['processed_ids'].append(result['article_id'])
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'article_index': i,
                        'error': result['error']
                    })
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'article_index': i,
                    'error': str(e)
                })
        
        logger.info(f"Bulk processing completed: {results['successful']}/{results['total_articles']} successful")
        return results

# Flask app for webhook endpoints
app = Flask(__name__)
n8n_integration = N8nIntegration()

@app.route('/webhook/n8n/article', methods=['POST'])
def webhook_single_article():
    """
    Webhook endpoint for processing a single article from n8n
    
    Expected payload:
    {
        "title": "Article title",
        "content": "Article content/description",
        "link": "Article URL",
        "pubDate": "Publication date"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400
        
        result = n8n_integration.process_n8n_article(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webhook/n8n/articles', methods=['POST'])
def webhook_bulk_articles():
    """
    Webhook endpoint for processing multiple articles from n8n
    
    Expected payload:
    {
        "articles": [
            {
                "title": "Article 1 title",
                "content": "Article 1 content",
                "link": "Article 1 URL",
                "pubDate": "Publication date"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'articles' not in data:
            return jsonify({
                'success': False,
                'error': 'No articles array found in payload'
            }), 400
        
        articles = data['articles']
        if not isinstance(articles, list):
            return jsonify({
                'success': False,
                'error': 'Articles must be an array'
            }), 400
        
        result = n8n_integration.process_bulk_articles(articles)
        
        return jsonify({
            'success': True,
            'results': result
        }), 200
        
    except Exception as e:
        logger.error(f"Bulk webhook error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webhook/n8n/status', methods=['GET'])
def webhook_status():
    """Health check endpoint for n8n"""
    try:
        # Test basic service availability
        status_info = {
            'status': 'healthy',
            'service': 'Project Genji n8n Integration',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'single_article': '/webhook/n8n/article (POST)',
                'bulk_articles': '/webhook/n8n/articles (POST)',
                'health_check': '/webhook/n8n/status (GET)'
            }
        }
        
        # Try database connection (optional)
        try:
            conn = n8n_integration.get_database_connection()
            conn.close()
            status_info['database'] = 'connected'
        except Exception as db_e:
            status_info['database'] = f'unavailable: {str(db_e)}'
            status_info['note'] = 'Service running but database connection failed'
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Run Flask app for webhook endpoints
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
