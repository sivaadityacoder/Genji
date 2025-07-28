# Technical Documentation for Project Genji

This document provides a detailed technical overview for developers and engineers.

## 1. System Requirements
* Python 3.9+
* n8n (local or cloud instance)
* PostgreSQL
* API Keys for:
    * Google AI (Gemini)
    * (Any other APIs you use, e.g., Twitter/X)

## 2. Environment Setup

1.  Clone the repository: `git clone ...`
2.  Install Python dependencies: `pip install -r requirements.txt`
3.  Create a `.env` file and add the following environment variables:
    ```
    GOOGLE_API_KEY="your_key_here"
    DATABASE_URL="your_postgres_url_here"
    ```

## 3. Architecture Component: Data Ingestion (n8n)

* **Workflow 1: `scrape_tech_news.json`**
    * **Purpose:** Scrapes the front page of TechCrunch every 6 hours.
    * **Triggers:** Cron job.
    * **Steps:**
        1.  HTTP Request Node: GET request to TechCrunch.
        2.  HTML Extract Node: Extracts article links and titles.
        3.  Execute Command Node: Calls the Python analysis script for each article.
    * **Output:** Stores analyzed data in the PostgreSQL database.

* **Workflow 2: `scrape_reddit.json`**
    * **Purpose:** ...

## 4. Architecture Component: Core Analysis Module (Python)

* **File:** `python-analysis-module/main.py`
* **Function: `run_analysis_pipeline(text, source)`**
    * **Description:** Takes raw text and a source name, and runs the full 5-step AI analysis.
    * **Step 1 - Translation:** Calls Gemini to translate text to Japanese.
    * **Step 2 - Summarization:** Calls Gemini with a summarization prompt.
    * **... (document all 5 steps)**
    * **Returns:** A JSON object with all the analyzed data fields.

## 5. Architecture Component: Executive Dashboard (Streamlit)

* **File:** `streamlit-dashboard/app.py`
* **To Run:** `streamlit run streamlit-dashboard/app.py`
* **Key Features:**
    * Connects to the PostgreSQL database to fetch the latest data.
    * Uses `plotly` to display the sentiment analysis chart.
    * Displays the latest Strategic Briefs in a formatted markdown component.
