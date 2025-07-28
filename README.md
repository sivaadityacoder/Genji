# Project Genji (源氏) - AI-Powered Global Market Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red.svg)](https://streamlit.io/)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285f4.svg)](https://ai.google.dev/)

## 🌟 Overview

Project Genji is a sophisticated AI-powered market intelligence platform specifically designed for Japanese business executives. Named after the classical Japanese literary work "Genji Monogatari" (The Tale of Genji), this platform bridges traditional Japanese business wisdom with cutting-edge artificial intelligence technology.

### ✨ Key Features

- **🤖 AI-Powered Analysis**: Leverages Google Gemini 1.5 Pro for advanced text analysis and cross-lingual processing
- **🇯🇵 Japanese Localization**: Provides professional summaries in perfect Japanese tailored for business executives
- **📊 Executive Dashboard**: Clean, professional interface with real-time insights and visualizations
- **🔄 Automated Pipeline**: Continuous data collection and analysis from multiple global news sources
- **💡 Strategic Intelligence**: Transforms raw data into actionable business insights

## 🏗️ Architecture

Project Genji is built on four core pillars:

### 1. **Data Collection Engine**
- Automated RSS feed processing
- Multi-source news aggregation
- Duplicate detection and filtering
- Scalable data ingestion pipeline

### 2. **AI Analysis Core**
- Google Gemini 1.5 Pro integration
- Cross-lingual sentiment analysis
- Topic extraction and entity recognition
- Business impact assessment

### 3. **Strategic Synthesis**
- Professional Japanese summaries
- Executive-ready insights
- Trend identification
- Opportunity mapping

### 4. **Executive Interface**
- Streamlit-powered dashboard
- Real-time analytics
- Interactive visualizations
- Mobile-responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Google Gemini API key
- Git (for deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd project-genji
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables**
   ```bash
   cp python-analysis-module/.env.example python-analysis-module/.env
   # Edit .env with your actual API keys and database credentials
   ```

4. **Set up the database**
   ```bash
   # Run the SQL script in your PostgreSQL database
   psql -d your_database -f docs/database_setup.sql
   ```

5. **Start the system**
   ```bash
   # Collect initial data
   ./run_data_collection.sh
   
   # Run AI analysis
   ./run_analysis.sh
   
   # Start the dashboard
   ./run_dashboard.sh
   ```

## 📱 Usage

### Data Collection
```bash
# Manual data collection
./run_data_collection.sh

# Or run directly
python python-analysis-module/data_collector.py
```

### AI Analysis
```bash
# Process unanalyzed articles
./run_analysis.sh

# Or run directly  
python python-analysis-module/main.py
```

### Dashboard
```bash
# Start the web dashboard
./run_dashboard.sh

# Access at http://localhost:8501
```

### n8n Automation
1. Import the workflow from `n8n-workflows/genji-pipeline.json`
2. Configure your PostgreSQL credentials
3. Activate the workflow for automated processing

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `python-analysis-module` directory:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password_here

# Optional: Additional APIs
NEWS_API_KEY=your_news_api_key_here
```

### Database Configuration

The system uses PostgreSQL with the following main tables:
- `market_insights`: Stores articles and analysis results
- `analysis_logs`: Tracks processing operations

## 📊 Dashboard Features

### Executive Overview
- Real-time metrics and KPIs
- Sentiment analysis trends
- Business impact assessment
- Source distribution analytics

### Strategic Insights
- AI-generated Japanese summaries
- Cross-lingual sentiment analysis
- Topic and entity extraction
- Timeline visualization

### Interactive Filters
- Date range selection
- News source filtering
- Sentiment-based views
- Business impact categories

## 🛠️ Development

### Project Structure
```
project-genji/
├── python-analysis-module/    # Core AI processing
│   ├── main.py               # Main analysis script
│   ├── data_collector.py     # Data collection module
│   └── .env                  # Environment variables
├── streamlit-dashboard/       # Web interface
│   └── app.py               # Dashboard application
├── n8n-workflows/            # Automation workflows
│   └── genji-pipeline.json  # Complete workflow
├── docs/                     # Documentation
│   └── database_setup.sql   # Database schema
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

### Adding New Data Sources

1. **Update data_collector.py**:
   ```python
   self.rss_sources.append({
       'name': 'Your Source',
       'url': 'https://example.com/feed.xml',
       'category': 'Technology'
   })
   ```

2. **Test the new source**:
   ```bash
   python python-analysis-module/data_collector.py
   ```

### Customizing AI Analysis

Modify the analysis prompt in `main.py`:
```python
def analyze_text_with_gemini(self, text: str, title: str = "") -> Optional[Dict]:
    prompt = f"""
    Your custom analysis prompt here...
    """
```

## 🚢 Deployment

### Streamlit Community Cloud
1. Push your code to a public GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set environment variables in "Advanced settings"
5. Deploy!

### Docker Deployment
```bash
# Build Docker image
docker build -t project-genji .

# Run container
docker run -p 8501:8501 project-genji
```

## 📈 Performance

### Scalability Features
- Database connection pooling
- Efficient SQL queries with proper indexing
- Streamlit caching for improved performance
- Batch processing for large datasets

### Monitoring
- Analysis logs in `analysis_logs` table
- Processing time tracking
- Error handling and reporting
- System health metrics

## 🔐 Security

- Environment variable protection
- SQL injection prevention
- API key management
- Database access controls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language processing
- **Streamlit** for the beautiful web interface
- **n8n** for workflow automation
- **PostgreSQL** for robust data storage
- **The Tale of Genji** for inspiring the project name

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the code comments for implementation details

---

**Project Genji (源氏)** - *Transforming global intelligence for Japanese business excellence*

🇯🇵 Made with ❤️ for Japanese business executives
