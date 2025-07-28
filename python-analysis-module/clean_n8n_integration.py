"""
Project Genji - Clean n8n Integration Module
Production-ready webhook server with proper error handling
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CleanN8nIntegration:
    """Clean, optimized n8n integration handler"""
    
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'genji_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'aditya'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Initialize AI analyzer only if API key is valid
        self.ai_enabled = self._validate_api_key()
        
    def _validate_api_key(self) -> bool:
        """Validate if AI analysis is available"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or api_key == 'your_valid_gemini_api_key_here':
            logger.warning("AI analysis disabled: No valid API key configured")
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Test with a simple request
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content("Test", timeout=5)
            logger.info("AI analysis enabled: API key validated")
            return True
        except Exception as e:
            logger.error(f"AI analysis disabled: API validation failed - {e}")
            return False
    
    def get_database_connection(self):
        """Create database connection with proper error handling"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def store_article(self, title: str, content: str, link: str, pub_date: str) -> Optional[int]:
        """Store article with improved error handling"""
        try:
            with self.get_database_connection() as conn:
                with conn.cursor() as cur:
                    # Check for duplicates
                    cur.execute("SELECT id FROM market_insights WHERE url = %s", (link,))
                    existing = cur.fetchone()
                    
                    if existing:
                        logger.info(f"Article already exists: {existing[0]}")
                        return existing[0]
                    
                    # Insert new article
                    cur.execute("""
                        INSERT INTO market_insights 
                        (title, raw_text, url, source, category, published_at, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                        RETURNING id
                    """, (title, content, link, 'n8n_rss', 'Technology', pub_date))
                    
                    article_id = cur.fetchone()[0]
                    logger.info(f"Article stored successfully: ID {article_id}")
                    return article_id
                    
        except Exception as e:
            logger.error(f"Failed to store article: {e}")
            return None
    
    def analyze_with_ai(self, content: str, title: str) -> Optional[Dict]:
        """AI analysis with fallback handling"""
        if not self.ai_enabled:
            return {
                'summary_jp': 'AI分析は現在利用できません',
                'summary_en': 'AI analysis currently unavailable',
                'sentiment_label': 'Neutral',
                'sentiment_score': 0.5,
                'topics': ['technology'],
                'key_entities': [],
                'business_impact': 'Unknown'
            }
        
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            prompt = f"""
Analyze this article and return JSON only:
Title: {title}
Content: {content}

Return exactly this format:
{{
    "summary_jp": "Japanese summary in 2-3 sentences",
    "summary_en": "English summary in 2-3 sentences", 
    "sentiment_label": "Positive/Negative/Neutral",
    "sentiment_score": 0.5,
    "topics": ["topic1", "topic2"],
    "key_entities": ["entity1", "entity2"],
    "business_impact": "High/Medium/Low"
}}
"""
            
            response = model.generate_content(prompt, timeout=30)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            logger.info("AI analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def process_article(self, article_data: Dict) -> Dict:
        """Process article with comprehensive error handling"""
        try:
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            link = article_data.get('link', '')
            pub_date = article_data.get('pubDate', datetime.now().isoformat())
            
            # Store article
            article_id = self.store_article(title, content, link, pub_date)
            if not article_id:
                return {'success': False, 'error': 'Failed to store article'}
            
            # Attempt AI analysis
            analysis = self.analyze_with_ai(content, title)
            
            if analysis:
                # Update with analysis results
                try:
                    with self.get_database_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE market_insights 
                                SET summary_jp = %s, summary_en = %s, sentiment_label = %s,
                                    sentiment_score = %s, topics = %s, key_entities = %s,
                                    business_impact = %s, analyzed_at = NOW()
                                WHERE id = %s
                            """, (
                                analysis['summary_jp'], analysis['summary_en'],
                                analysis['sentiment_label'], analysis['sentiment_score'],
                                analysis['topics'], analysis['key_entities'],
                                analysis['business_impact'], article_id
                            ))
                    
                    return {
                        'success': True,
                        'article_id': article_id,
                        'analysis': analysis,
                        'ai_enabled': self.ai_enabled
                    }
                except Exception as e:
                    logger.error(f"Failed to update analysis: {e}")
                    return {
                        'success': True,
                        'article_id': article_id,
                        'message': 'Article stored but analysis update failed',
                        'ai_enabled': self.ai_enabled
                    }
            else:
                return {
                    'success': True,
                    'article_id': article_id,
                    'message': 'Article stored, AI analysis failed',
                    'ai_enabled': self.ai_enabled
                }
                
        except Exception as e:
            logger.error(f"Article processing failed: {e}")
            return {'success': False, 'error': str(e)}

# Flask application
app = Flask(__name__)
integration = CleanN8nIntegration()

@app.route('/webhook/n8n/article', methods=['POST'])
def webhook_single_article():
    """Clean webhook endpoint for single articles"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data'}), 400
        
        result = integration.process_article(data)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/webhook/n8n/articles', methods=['POST'])
def webhook_bulk_articles():
    """Clean webhook endpoint for bulk articles"""
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        
        results = {'total': len(articles), 'successful': 0, 'failed': 0, 'details': []}
        
        for article in articles:
            result = integration.process_article(article)
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
            results['details'].append(result)
        
        return jsonify({'success': True, 'results': results}), 200
        
    except Exception as e:
        logger.error(f"Bulk webhook error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/webhook/n8n/status', methods=['GET'])
def webhook_status():
    """Clean status endpoint"""
    try:
        status = {
            'status': 'healthy',
            'service': 'Project Genji n8n Integration (Clean)',
            'timestamp': datetime.now().isoformat(),
            'ai_enabled': integration.ai_enabled,
            'endpoints': {
                'single_article': '/webhook/n8n/article (POST)',
                'bulk_articles': '/webhook/n8n/articles (POST)', 
                'status': '/webhook/n8n/status (GET)'
            }
        }
        
        # Test database connection
        try:
            with integration.get_database_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM market_insights')
                    count = cur.fetchone()[0]
                    status['database'] = 'connected'
                    status['articles_count'] = count
        except Exception as e:
            status['database'] = f'error: {str(e)}'
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Start server
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
