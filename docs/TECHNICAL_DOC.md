# Project Genji - Technical Documentation

## System Architecture

### Overview
Project Genji implements a sophisticated four-pillar architecture designed to deliver enterprise-grade market intelligence to Japanese business executives.

### Core Components

#### 1. Data Collection Engine (`data_collector.py`)
- **Purpose**: Automated collection from multiple RSS news sources
- **Technology**: Python with feedparser library
- **Features**:
  - Multi-source RSS processing
  - Duplicate detection via URL uniqueness
  - Error handling and retry logic
  - Configurable source management

#### 2. AI Analysis Core (`main.py`)
- **Purpose**: Advanced text analysis using Google Gemini 1.5 Pro
- **Technology**: Google Generative AI SDK
- **Features**:
  - Cross-lingual analysis (English → Japanese)
  - Sentiment analysis with scoring
  - Topic extraction and entity recognition
  - Business impact assessment
  - Processing time tracking

#### 3. Database Layer (PostgreSQL)
- **Schema Design**:
  ```sql
  market_insights:
    - id (SERIAL PRIMARY KEY)
    - source, title, raw_text, url
    - summary_jp, summary_en
    - sentiment_label, sentiment_score  
    - topics[], key_entities[]
    - business_impact
    - created_at, analyzed_at
  
  analysis_logs:
    - id, article_id, operation, status
    - error_message, processing_time_ms
    - created_at
  ```

#### 4. Executive Interface (`app.py`)
- **Technology**: Streamlit with Plotly visualizations
- **Features**:
  - Real-time dashboard updates
  - Interactive filtering and search
  - Japanese/English bilingual support
  - Executive-ready formatting
  - Mobile-responsive design

### Data Flow Architecture

```
RSS Sources → Data Collector → PostgreSQL → AI Analyzer → Database → Dashboard
     ↓              ↓             ↓            ↓           ↓         ↓
   Multiple       Dedupe       Store        Gemini      Update    Visualize
   Feeds          Filter       Raw          API         Results   Insights
```

## AI Analysis Pipeline

### Gemini 1.5 Pro Integration

#### Prompt Engineering
The system uses carefully crafted prompts optimized for:
- Japanese business context
- Professional tone and terminology
- Structured JSON output
- Cultural sensitivity

#### Analysis Components

1. **Summary Generation**:
   - Japanese: Professional keigo (敬語) style
   - English: Executive briefing format
   - 2-3 sentence maximum length

2. **Sentiment Analysis**:
   - Label: Positive/Negative/Neutral
   - Score: 0.0-1.0 numerical rating
   - Cultural context consideration

3. **Topic Extraction**:
   - Maximum 5 key topics per article
   - Business-relevant keyword selection
   - Japanese and English term support

4. **Entity Recognition**:
   - Company names and brands
   - Executive names and titles
   - Product and service mentions
   - Geographic locations

5. **Business Impact Assessment**:
   - High/Medium/Low/Unknown classification
   - Based on market relevance to Japanese enterprises
   - Strategic importance evaluation

### Error Handling and Logging

#### Comprehensive Logging
- Operation tracking in `analysis_logs` table
- Processing time measurement
- Error message capture
- Status monitoring (started/completed/failed)

#### Retry Logic
- API rate limit handling
- Network timeout recovery
- Database connection retry
- Graceful degradation

## Database Design

### Indexing Strategy
```sql
-- Performance optimization indexes
CREATE INDEX idx_market_insights_created_at ON market_insights(created_at DESC);
CREATE INDEX idx_market_insights_source ON market_insights(source);
CREATE INDEX idx_market_insights_sentiment ON market_insights(sentiment_label);
CREATE INDEX idx_market_insights_analyzed ON market_insights(analyzed_at DESC);
```

### Data Integrity
- URL uniqueness constraints prevent duplicates
- Foreign key relationships ensure referential integrity
- NOT NULL constraints on critical fields
- Timestamp defaults for audit trails

## Performance Optimization

### Caching Strategy
- Streamlit `@st.cache_data` with 5-minute TTL
- Database query result caching
- Static asset caching
- API response caching

### Query Optimization
- Efficient pagination with LIMIT/OFFSET
- Index utilization for sorting and filtering
- Connection pooling for concurrent access
- Prepared statements for security

### Scalability Considerations
- Horizontal scaling via read replicas
- Background job processing for analysis
- Queue-based architecture for high volume
- CDN integration for static assets

## Security Implementation

### API Key Management
- Environment variable isolation
- No hardcoded credentials
- Secure key rotation support
- Access logging and monitoring

### Database Security
- Parameterized queries prevent SQL injection
- Connection encryption (SSL/TLS)
- Role-based access control
- Regular security updates

### Data Privacy
- No PII storage in raw text
- Anonymized logging
- GDPR compliance ready
- Secure data transmission

## Monitoring and Observability

### Health Checks
- Database connectivity monitoring
- API endpoint health verification
- Processing pipeline status
- Dashboard availability checks

### Metrics Collection
- Processing time distribution
- Error rate tracking
- API usage analytics
- User engagement metrics

### Alerting
- Failed analysis notifications
- API quota warnings
- Database connectivity alerts
- System performance degradation

## API Integration Details

### Google Gemini 1.5 Pro
- **Model**: `gemini-1.5-pro-latest`
- **Context Window**: 1 million tokens
- **Rate Limits**: Managed with exponential backoff
- **Response Format**: Structured JSON
- **Error Handling**: Comprehensive retry logic

### RSS Feed Processing
- **Parser**: feedparser library
- **Timeout**: 30 seconds per feed
- **Retry Logic**: 3 attempts with backoff
- **Encoding**: UTF-8 with fallback detection

## Development Workflow

### Code Organization
```
python-analysis-module/
├── main.py              # Core analysis logic
├── data_collector.py    # RSS collection
├── .env                 # Environment config
└── requirements.txt     # Dependencies

streamlit-dashboard/
└── app.py              # Web interface

n8n-workflows/
└── genji-pipeline.json # Automation config
```

### Testing Strategy
- Unit tests for core functions
- Integration tests for API calls
- End-to-end dashboard testing
- Performance benchmarks

### Deployment Pipeline
1. Code commit to repository
2. Automated testing execution
3. Docker image building
4. Staging environment deployment
5. Production deployment with rollback

## Configuration Management

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=<gemini-api-key>
DB_PASSWORD=<postgres-password>

# Optional
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
NEWS_API_KEY=<additional-api-key>
```

### Feature Flags
- Analysis module enable/disable
- Data source selection
- Dashboard component visibility
- Debug mode activation

## Troubleshooting Guide

### Common Issues
1. **Database Connection Failure**:
   - Verify PostgreSQL is running
   - Check connection parameters
   - Validate user permissions

2. **API Key Errors**:
   - Confirm Gemini API key validity
   - Check quota limits
   - Verify billing status

3. **Dashboard Loading Issues**:
   - Clear Streamlit cache
   - Check database connectivity
   - Validate data availability

### Debug Commands
```bash
# Test database connection
python -c "from main import GenjiAnalyzer; GenjiAnalyzer().get_database_connection()"

# Verify API access
python -c "import google.generativeai as genai; genai.configure(api_key='your-key'); print('API OK')"

# Check data availability
python -c "from app import load_data; print(len(load_data()))"
```

## Future Enhancements

### Planned Features
- Multi-language support (Chinese, Korean)
- Advanced visualization options
- Email alert system
- Mobile application
- API endpoint for third-party integration

### Scalability Roadmap
- Microservices architecture
- Kubernetes deployment
- Event-driven processing
- Machine learning model training
- Real-time streaming analytics

---

This technical documentation provides comprehensive implementation details for Project Genji's architecture, performance optimization, and operational procedures.
