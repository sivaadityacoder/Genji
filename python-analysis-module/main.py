"""
Project Genji - Core AI Analysis Module
This module handles the AI-powered analysis of market intelligence data using Google Gemini.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GenjiAnalyzer:
    """Main class for Project Genji AI analysis"""
    
    def __init__(self):
        """Initialize the analyzer with API keys and database connection"""
        load_dotenv()
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Database configuration
        self.db_config = {
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        if not self.db_config['password']:
            raise ValueError("DB_PASSWORD not found in environment variables")
    
    def get_database_connection(self) -> psycopg2.extensions.connection:
        """Create and return a database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def analyze_text_with_gemini(self, text: str, title: str = "") -> Optional[Dict]:
        """
        Analyze text using Gemini API and return structured results
        
        Args:
            text: The article text to analyze
            title: Optional article title for context
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        
        prompt = f"""
あなたは日本のビジネスエグゼクティブ向けの戦略的市場分析の専門家です。
以下の記事を分析し、JSON形式で結果を返してください。

記事タイトル: {title}
記事内容: {text}

以下の形式で分析結果をJSONで返してください：

{{
    "summary_jp": "日本語での2-3文の要約（丁寧語を使用）",
    "summary_en": "English summary in 2-3 sentences",
    "sentiment_label": "Positive, Negative, または Neutral",
    "sentiment_score": 0.0から1.0の間の数値,
    "topics": ["キーワード1", "キーワード2", "キーワード3"],
    "key_entities": ["企業名", "人名", "製品名など"],
    "business_impact": "High, Medium, Low, または Unknown"
}}

重要な注意事項：
- レスポンスはJSONのみで、他のテキストは含めない
- 日本語要約は敬語を使用し、ビジネス文書として適切な表現にする
- sentiment_scoreは記事の感情的な傾向を0（非常にネガティブ）から1（非常にポジティブ）で表現
- business_impactは日本企業への潜在的な影響度を評価
"""

        try:
            start_time = time.time()
            response = self.model.generate_content(prompt)
            processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            # Clean and parse the response
            cleaned_response = response.text.strip()
            # Remove markdown formatting if present
            cleaned_response = cleaned_response.replace("```json", "").replace("```", "").strip()
            
            analysis_result = json.loads(cleaned_response)
            analysis_result['processing_time_ms'] = processing_time
            
            logger.info(f"Successfully analyzed text (took {processing_time}ms)")
            return analysis_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}. Response was: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None
    
    def log_analysis_operation(self, conn: psycopg2.extensions.connection, 
                              article_id: int, operation: str, status: str, 
                              error_message: str = None, processing_time_ms: int = None):
        """Log analysis operations for monitoring and debugging"""
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO analysis_logs (article_id, operation, status, error_message, processing_time_ms)
                    VALUES (%s, %s, %s, %s, %s)
                """, (article_id, operation, status, error_message, processing_time_ms))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
    
    def update_article_analysis(self, conn: psycopg2.extensions.connection, 
                               article_id: int, analysis_data: Dict) -> bool:
        """Update database with analysis results"""
        try:
            with conn.cursor() as cur:
                update_query = """
                    UPDATE market_insights 
                    SET summary_jp = %s, 
                        summary_en = %s,
                        sentiment_label = %s, 
                        sentiment_score = %s,
                        topics = %s,
                        key_entities = %s,
                        business_impact = %s,
                        analyzed_at = NOW(),
                        analysis_version = '1.0'
                    WHERE id = %s
                """
                
                cur.execute(update_query, (
                    analysis_data.get('summary_jp'),
                    analysis_data.get('summary_en'),
                    analysis_data.get('sentiment_label'),
                    analysis_data.get('sentiment_score'),
                    analysis_data.get('topics', []),
                    analysis_data.get('key_entities', []),
                    analysis_data.get('business_impact'),
                    article_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Database update error for article {article_id}: {e}")
            conn.rollback()
            return False
    
    def process_unanalyzed_articles(self, limit: int = 5) -> int:
        """
        Process articles that haven't been analyzed yet
        
        Args:
            limit: Maximum number of articles to process
            
        Returns:
            Number of articles successfully processed
        """
        conn = None
        processed_count = 0
        
        try:
            conn = self.get_database_connection()
            
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Fetch unanalyzed articles
                cur.execute("""
                    SELECT id, title, raw_text 
                    FROM market_insights 
                    WHERE summary_jp IS NULL 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                
                articles = cur.fetchall()
                
                if not articles:
                    logger.info("No new articles to analyze")
                    return 0
                
                logger.info(f"Found {len(articles)} articles to analyze")
                
                for article in articles:
                    article_id = article['id']
                    title = article['title'] or ""
                    raw_text = article['raw_text']
                    
                    logger.info(f"Analyzing article ID: {article_id}")
                    
                    # Log start of analysis
                    self.log_analysis_operation(conn, article_id, "analysis", "started")
                    
                    # Perform AI analysis
                    analysis_result = self.analyze_text_with_gemini(raw_text, title)
                    
                    if analysis_result:
                        # Update database with results
                        success = self.update_article_analysis(conn, article_id, analysis_result)
                        
                        if success:
                            self.log_analysis_operation(
                                conn, article_id, "analysis", "completed", 
                                processing_time_ms=analysis_result.get('processing_time_ms')
                            )
                            processed_count += 1
                            logger.info(f"Successfully processed article ID: {article_id}")
                        else:
                            self.log_analysis_operation(conn, article_id, "analysis", "failed", "Database update failed")
                    else:
                        self.log_analysis_operation(conn, article_id, "analysis", "failed", "AI analysis failed")
                    
                    # Small delay to respect API limits
                    time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in process_unanalyzed_articles: {e}")
        finally:
            if conn:
                conn.close()
        
        logger.info(f"Processing completed. {processed_count}/{len(articles) if 'articles' in locals() else 0} articles processed successfully")
        return processed_count

def main():
    """Main execution function"""
    try:
        analyzer = GenjiAnalyzer()
        processed = analyzer.process_unanalyzed_articles(limit=10)
        
        if processed > 0:
            print(f"✅ Successfully processed {processed} articles")
        else:
            print("ℹ️ No articles were processed")
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
