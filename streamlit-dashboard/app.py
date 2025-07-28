"""
Project Genji - Executive Dashboard
A sophisticated web interface for displaying AI-powered market intelligence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Page Configuration
st.set_page_config(
    page_title="Project Genji (源氏) - Executive Intelligence",
    page_icon="🇯🇵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #c41e3a;
        padding-bottom: 1rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #c41e3a;
        margin: 1rem 0;
    }
    .insight-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f4e79;
    }
    .japanese-text {
        font-family: 'Noto Sans JP', sans-serif;
        line-height: 1.6;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load analyzed data from the database"""
    load_dotenv(dotenv_path='../python-analysis-module/.env')
    
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        
        query = """
            SELECT 
                created_at, 
                source, 
                title, 
                summary_jp, 
                summary_en,
                sentiment_label, 
                sentiment_score,
                topics, 
                key_entities,
                business_impact,
                url,
                analyzed_at
            FROM market_insights 
            WHERE summary_jp IS NOT NULL 
            ORDER BY created_at DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert timestamps to datetime
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['analyzed_at'] = pd.to_datetime(df['analyzed_at'])
        
        return df
        
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return pd.DataFrame()

def create_sentiment_chart(df):
    """Create sentiment analysis visualization"""
    if df.empty:
        return go.Figure()
    
    sentiment_counts = df['sentiment_label'].value_counts()
    
    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="市場センチメント分析",
        color_discrete_map={
            'Positive': '#28a745',
            'Negative': '#dc3545',
            'Neutral': '#6c757d'
        }
    )
    
    fig.update_layout(
        font=dict(size=12),
        showlegend=True,
        height=400
    )
    
    return fig

def create_business_impact_chart(df):
    """Create business impact visualization"""
    if df.empty:
        return go.Figure()
    
    impact_counts = df['business_impact'].value_counts()
    
    fig = px.bar(
        x=impact_counts.index,
        y=impact_counts.values,
        title="ビジネスインパクト評価",
        color=impact_counts.values,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis_title="インパクトレベル",
        yaxis_title="記事数",
        showlegend=False,
        height=400
    )
    
    return fig

def create_timeline_chart(df):
    """Create timeline visualization of articles and sentiment"""
    if df.empty:
        return go.Figure()
    
    # Group by date and sentiment
    df['date'] = df['created_at'].dt.date
    timeline_data = df.groupby(['date', 'sentiment_label']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    colors = {'Positive': '#28a745', 'Negative': '#dc3545', 'Neutral': '#6c757d'}
    
    for sentiment in timeline_data.columns:
        fig.add_trace(go.Scatter(
            x=timeline_data.index,
            y=timeline_data[sentiment],
            mode='lines+markers',
            name=sentiment,
            line=dict(color=colors.get(sentiment, '#007bff'), width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="市場センチメント推移",
        xaxis_title="日付",
        yaxis_title="記事数",
        hovermode='x unified',
        height=400
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">Project Genji (源氏)<br>AI-Powered Global Market Intelligence</h1>', unsafe_allow_html=True)
    st.markdown("*グローバル市場インテリジェンス - 日本のエグゼクティブのためのAI戦略分析*")
    
    # Load data
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 フィルターオプション")
        
        if not df.empty:
            # Date range filter
            date_range = st.date_input(
                "期間選択",
                value=(df['created_at'].min().date(), df['created_at'].max().date()),
                min_value=df['created_at'].min().date(),
                max_value=df['created_at'].max().date()
            )
            
            # Source filter
            sources = st.multiselect(
                "ニュースソース",
                options=df['source'].unique(),
                default=df['source'].unique()
            )
            
            # Sentiment filter
            sentiments = st.multiselect(
                "センチメント",
                options=df['sentiment_label'].unique(),
                default=df['sentiment_label'].unique()
            )
            
            # Apply filters
            if len(date_range) == 2:
                df = df[
                    (df['created_at'].dt.date >= date_range[0]) &
                    (df['created_at'].dt.date <= date_range[1]) &
                    (df['source'].isin(sources)) &
                    (df['sentiment_label'].isin(sentiments))
                ]
        
        st.markdown("---")
        st.markdown("**システム情報**")
        st.info(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if df.empty:
        st.warning("⚠️ 分析済みデータが見つかりません。データパイプラインを実行してください。")
        st.markdown("""
        ### セットアップ手順:
        1. PostgreSQLデータベースを設定
        2. `.env`ファイルにAPI認証情報を設定
        3. データ収集スクリプトを実行: `python python-analysis-module/data_collector.py`
        4. AI分析スクリプトを実行: `python python-analysis-module/main.py`
        """)
        return
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_articles = len(df)
        st.metric("📈 総記事数", f"{total_articles:,}")
    
    with col2:
        avg_sentiment = df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
        st.metric("😊 平均センチメント", f"{avg_sentiment:.2f}")
    
    with col3:
        high_impact = len(df[df['business_impact'] == 'High']) if 'business_impact' in df.columns else 0
        st.metric("🔥 高インパクト記事", f"{high_impact}")
    
    with col4:
        latest_update = df['analyzed_at'].max().strftime('%m/%d %H:%M') if 'analyzed_at' in df.columns else "N/A"
        st.metric("🕐 最新分析", latest_update)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        sentiment_fig = create_sentiment_chart(df)
        st.plotly_chart(sentiment_fig, use_container_width=True)
    
    with col2:
        impact_fig = create_business_impact_chart(df)
        st.plotly_chart(impact_fig, use_container_width=True)
    
    # Timeline Chart
    timeline_fig = create_timeline_chart(df)
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Strategic Insights
    st.header("📰 最新の戦略的インサイト")
    
    # Top insights based on business impact and recency
    top_insights = df.head(10)
    
    for idx, row in top_insights.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### [{row['title']}]({row['url']})")
                
                # Source and metadata
                st.markdown(f"**ソース:** {row['source']} | **センチメント:** {row['sentiment_label']} | **インパクト:** {row.get('business_impact', 'N/A')}")
                
                # Japanese summary
                if row['summary_jp']:
                    st.markdown("**AI要約 (日本語):**")
                    st.markdown(f'<div class="japanese-text">{row["summary_jp"]}</div>', unsafe_allow_html=True)
                
                # English summary
                if row.get('summary_en'):
                    st.markdown("**AI Summary (English):**")
                    st.info(row['summary_en'])
                
                # Topics and entities
                if row.get('topics'):
                    topics_str = ' • '.join([f"`{topic}`" for topic in row['topics'][:5]])
                    st.markdown(f"**キートピック:** {topics_str}")
                
                if row.get('key_entities'):
                    entities_str = ' • '.join([f"`{entity}`" for entity in row['key_entities'][:5]])
                    st.markdown(f"**主要エンティティ:** {entities_str}")
            
            with col2:
                # Sentiment indicator
                sentiment_color = {
                    'Positive': '🟢',
                    'Negative': '🔴', 
                    'Neutral': '🟡'
                }.get(row['sentiment_label'], '⚪')
                
                st.markdown(f"**センチメント**<br>{sentiment_color} {row['sentiment_label']}", unsafe_allow_html=True)
                
                # Business impact indicator
                impact_emoji = {
                    'High': '🔥',
                    'Medium': '⚡',
                    'Low': '📈',
                    'Unknown': '❓'
                }.get(row.get('business_impact', 'Unknown'), '❓')
                
                st.markdown(f"**ビジネスインパクト**<br>{impact_emoji} {row.get('business_impact', 'Unknown')}", unsafe_allow_html=True)
                
                # Publication date
                pub_date = row['created_at'].strftime('%m/%d %H:%M')
                st.markdown(f"**発行日時**<br>📅 {pub_date}", unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>Project Genji (源氏) - Powered by Google Gemini AI | Built with Streamlit</p>
        <p>🇯🇵 日本のビジネスエグゼクティブのためのグローバル市場インテリジェンス</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
