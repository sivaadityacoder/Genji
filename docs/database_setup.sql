-- Project Genji Database Schema
-- Run this SQL script to create the required database tables

-- Drop existing tables if they exist (for fresh setup)
DROP TABLE IF EXISTS market_insights CASCADE;
DROP TABLE IF EXISTS analysis_logs CASCADE;

-- Create the main market insights table
CREATE TABLE market_insights (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    url TEXT UNIQUE, -- UNIQUE prevents duplicate articles
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- AI Analysis Results
    summary_jp TEXT,
    summary_en TEXT,
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT,
    topics TEXT[],
    key_entities TEXT[],
    business_impact VARCHAR(50),
    
    -- Metadata
    analyzed_at TIMESTAMPTZ,
    analysis_version VARCHAR(10) DEFAULT '1.0'
);

-- Create analysis logs table for debugging and monitoring
CREATE TABLE analysis_logs (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES market_insights(id),
    operation VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_market_insights_created_at ON market_insights(created_at DESC);
CREATE INDEX idx_market_insights_source ON market_insights(source);
CREATE INDEX idx_market_insights_sentiment ON market_insights(sentiment_label);
CREATE INDEX idx_market_insights_analyzed ON market_insights(analyzed_at DESC);

-- Insert sample data for testing
INSERT INTO market_insights (source, title, raw_text, url) VALUES 
(
    'Sample Source',
    'AI市場の急速な成長について',
    'Artificial Intelligence market is experiencing unprecedented growth across all sectors, with particular strength in enterprise applications and consumer technologies.',
    'https://example.com/sample-article-1'
),
(
    'Tech News',
    'Japanese Companies Embrace Digital Transformation',
    'Major Japanese corporations are accelerating their digital transformation initiatives, investing heavily in AI and cloud technologies to remain competitive in the global market.',
    'https://example.com/sample-article-2'
);

-- Success message
SELECT 'Project Genji database schema created successfully!' AS result;
