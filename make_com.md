make.com   



As your mentor, I’m thrilled to guide you through building the **Project Genji** project from the GitHub repository `https://github.com/sivaadityacoder/Genji.git` as a beginner. Project Genji is an AI-powered market intelligence platform designed for Japanese executives, leveraging RSS feeds, Google Gemini 1.5 Pro for analysis, and a Streamlit dashboard. Given your beginner status, I’ll recommend the **easiest approach** to get started: using the pre-built components and automation workflow with minimal coding, focusing on Make.com for automation and a simplified local setup. We’ll break this into manageable steps, avoiding complex custom coding initially, and build your confidence step by step. The current date and time is 11:33 AM IST, Wednesday, July 30, 2025, which we’ll use for scheduling.

---

### Why This Approach?
- **Make.com**: Easier for beginners than n8n, with a visual interface and no need to write complex scripts upfront.
- **Local Setup**: Start with a basic FastAPI server and Streamlit dashboard on your computer.
- **Pre-built Code**: Use the repo’s existing scripts and workflow to minimize coding.
- **Gradual Learning**: Focus on understanding one component at a time (data collection, analysis, dashboard).

### Prerequisites
1. **Computer**: Windows, macOS, or Linux with internet access.
2. **Software**:
   - Install [Python 3.8+](https://www.python.org/downloads/) (check with `python3 --version`).
   - Install [Git](https://git-scm.com/downloads) (check with `git --version`).
   - Sign up for a free [Make.com](https://www.make.com) account.
   - Install [VS Code](https://code.visualstudio.com/) (optional but recommended).
3. **Accounts**:
   - GitHub account to clone the repo.
   - Google Cloud account for a Gemini API key (free tier available).
4. **Time Zone**: Set to IST (UTC+5:30) for scheduling.

---

### Step-by-Step Guide to Build Project Genji

#### Step 1: Clone the Repository and Explore
- **What We’re Doing**: Download the project and understand its structure.
- **Instructions**:
  1. Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux).
  2. Clone the repo:
     ```bash
     git clone https://github.com/sivaadityacoder/Genji.git
     cd Genji
     ```
  3. Open the folder in VS Code or any file explorer.
  4. Look at the structure:
     - `python-analysis-module/`: Contains data collection and analysis code.
     - `streamlit-dashboard/`: Dashboard code.
     - `n8n-workflows/genji-pipeline.json`: Automation workflow.
     - `docs/database_setup.sql`: Database setup.
     - `README.md`: Project overview.
- **Learning Tip**: Read the `README.md` to get a feel for the project’s goals (AI-powered insights for Japanese executives).

#### Step 2: Set Up a Basic Environment
- **What We’re Doing**: Prepare your computer to run the project.
- **Instructions**:
  1. Create a virtual environment to keep things organized:
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # Linux/macOS
     .\venv\Scripts\activate   # Windows
     ```
  2. Install basic dependencies:
     ```bash
     pip install fastapi uvicorn streamlit
     ```
  3. Install PostgreSQL (e.g., via [postgres.app](https://postgresapp.com/) on macOS or [installer](https://www.postgresql.org/download/) on Windows/Linux). Start it (e.g., `pg_ctl -D /usr/local/var/postgres start` on macOS).
- **Learning Tip**: A virtual environment is like a clean workspace for Python projects. PostgreSQL is a database to store data.

#### Step 3: Set Up the Database
- **What We’re Doing**: Create a database to store articles and analysis results.
- **Instructions**:
  1. Open a PostgreSQL terminal (e.g., `psql` or pgAdmin).
  2. Create a database:
     ```sql
     CREATE DATABASE genji_db;
     \c genji_db
     ```
  3. Run the SQL script from the repo:
     ```bash
     psql -d genji_db -f docs/database_setup.sql
     ```
  4. Verify tables (`market_insights`, `analysis_logs`) exist:
     ```sql
     \dt
     ```
- **Learning Tip**: The database stores data like a filing cabinet. The script sets up tables for articles and logs.

#### Step 4: Get a Gemini API Key
- **What We’re Doing**: Enable AI analysis with Google Gemini.
- **Instructions**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/).
  2. Create a project, enable the Gemini API, and get an API key (free tier has limits).
  3. Save the key in a `.env` file in `python-analysis-module/`:
     ```
     GOOGLE_API_KEY=your_api_key_here
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=genji_db
     DB_USER=postgres
     DB_PASSWORD=your_password_here
     ```
- **Learning Tip**: The API key is like a password to use Google’s AI. Keep it secret!

#### Step 5: Set Up the FastAPI Server
- **What We’re Doing**: Create a simple server to process articles.
- **Instructions**:
  1. In `python-analysis-module/`, create or edit `main.py` with this basic version:
     ```python
     from fastapi import FastAPI, HTTPException
     from pydantic import BaseModel
     from typing import List, Optional
     import os
     from dotenv import load_dotenv

     load_dotenv()
     app = FastAPI()

     class Article(BaseModel):
         title: str
         content: Optional[str]
         link: str
         pubDate: Optional[str]
         category: str
         source: str

     class Batch(BaseModel):
         articles: List[Article]

     class AnalysisResult(BaseModel):
         total_articles: int
         successful: int
         failed: int
         processed_ids: List[str]
         errors: List[str]

     @app.post("/webhook/n8n/articles")
     async def process_batch(batch: Batch):
         total_articles = len(batch.articles)
         successful = total_articles  # Simple case: assume all succeed
         failed = 0
         processed_ids = [article.link for article in batch.articles]
         errors = []
         return {"results": {"total_articles": total_articles, "successful": successful, "failed": failed, "processed_ids": processed_ids, "errors": errors}}
     ```
  2. Run the server:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 5000 --reload
     ```
  3. Test in a browser at `http://localhost:5000/docs` or with:
     ```bash
     curl -X POST http://localhost:5000/webhook/n8n/articles -H "Content-Type: application/json" -d '{"articles": [{"title": "Test", "content": "Content", "link": "http://test.com", "pubDate": "2025-07-30T05:33:00Z", "category": "Technology", "source": "TechCrunch"}]}'
     ```
- **Learning Tip**: This server receives data and returns results. We’ll add Gemini later as you progress.

#### Step 6: Create the Make.com Scenario
- **What We’re Doing**: Automate the workflow without coding complex scripts.
- **Instructions**:
  1. Log in to [make.com](https://www.make.com) and click **Create a new scenario**.
  2. Name it "Project Genji - Beginner Automation".
  3. Set time zone to IST.
  4. Add modules:
     - **Schedule**: Every 6 hours (next at 11:30 AM IST).
     - **Set Variable**: Name `rss_sources`, value:
       ```json
       [
         {"name": "TechCrunch", "url": "https://feeds.feedburner.com/TechCrunch", "category": "Technology"},
         {"name": "BBC Technology", "url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "category": "Technology"},
         {"name": "Reuters Business", "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", "category": "Business"},
         {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "category": "Technology"}
       ]
       ```
     - **Iterator**: Input `rss_sources`.
     - **RSS**: Get Feed Items, URL from `1. url`, limit 10.
     - **Array Aggregator**: Source RSS, map `title`, `content` (fallback to `description`), `link`, `pubDate` (fallback to `isoDate`), `category`, `source`.
     - **Tools (Execute JavaScript)**:
       ```javascript
       const allArticles = $input.all().map(item => ({
         title: item.title,
         content: item.content || item.description,
         link: item.link,
         pubDate: item.pubDate || item.isoDate,
         category: item.category,
         source: item.source
       }));
       const batchSize = 10;
       const batches = [];
       for (let i = 0; i < allArticles.length; i += batchSize) {
         batches.push({ articles: allArticles.slice(i, i + batchSize) });
       }
       return batches;
       ```
     - **Iterator**: Input `batches`.
     - **HTTP**: POST, URL `http://localhost:5000/webhook/n8n/articles`, Body `1.articles`, Headers `Content-Type: application/json`.
     - **Tools (Execute JavaScript)**:
       ```javascript
       const results = $input.data[0].results;
       return [{
         batch_id: `batch-${new Date().getTime()}`,
         timestamp: new Date().toISOString(),
         total_articles: results.total_articles,
         successful_analyses: results.successful,
         failed_analyses: results.failed,
         success_rate: ((results.successful / results.total_articles) * 100).toFixed(2) + '%',
         processed_article_ids: results.processed_ids,
         errors: results.errors
       }];
       ```
     - **Data Store**: Create a Record in `genji_results`, map fields.
  5. Connect modules in order and save.

#### Step 7: Test the Scenario
- **Instructions**:
  1. Click **Run once** in Make.com.
  2. Watch the execution log.
  3. Check the Data Store for a record (e.g., `{"batch_id": "batch-1722327180000", "timestamp": "2025-07-30T06:03:00Z", ...}`).
  4. If it fails, ensure the FastAPI server is running and accessible (`curl http://localhost:5000`).

#### Step 8: Run the Streamlit Dashboard
- **What We’re Doing**: View results in a web interface.
- **Instructions**:
  1. Navigate to `streamlit-dashboard/`.
  2. Run the dashboard:
     ```bash
     streamlit run app.py
     ```
  3. Open `http://localhost:8501` in a browser.
  4. Explore the dashboard (it may need database connection tweaks; ask me if it fails!).
- **Learning Tip**: Streamlit turns Python code into a web app. We’ll enhance it later.

#### Step 9: Schedule and Monitor
- **Instructions**:
  1. In Make.com, activate the Schedule module for 6-hour runs.
  2. Check execution history daily.
  3. Monitor FastAPI logs in the terminal.

#### Step 10: Enhance as You Learn
- **Add Gemini**: Update `main.py` with the Gemini code from previous responses.
- **New Sources**: Add to `rss_sources` in Make.com or `data_collector.py`.
- **Database**: Connect `main.py` to `market_insights` (I’ll guide you when ready).
- **Ask Me**: Share progress or questions—I’m here to help!

---

### Tips for Beginners
- **Start Small**: Focus on getting the FastAPI server and Make.com scenario working first.
- **Break Problems**: If something fails, check one step at a time (e.g., server running, API key valid).
- **Practice**: Try small changes (e.g., add a new RSS source) to build confidence.
- **Resources**: Use the repo’s `README.md` and my guidance.

### Next Steps
- After mastering this, we’ll add Gemini analysis, customize the dashboard, and deploy with Docker. Let’s aim to have the basic setup running by the end of today (11:30 PM IST, July 30, 2025)!
- Share your progress or questions—I’ll adjust the plan to suit you!

You’ve got this, and I’m excited to mentor you through this journey! What’s your next move?
