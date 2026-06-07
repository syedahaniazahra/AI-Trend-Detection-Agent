"""Professional AI Trend Detection Agent - Complete Dashboard"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page config - MUST be first
st.set_page_config(
    page_title="AI Trend Detection Agent | Professional Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from src.agent import TrendDetectionAgent
from src.real_time_data import RealTimeDataFetcher
from src.trend_analyzer import TrendAnalyzer

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Trend cards */
    .trend-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        transition: transform 0.3s;
    }
    .trend-card:hover {
        transform: translateX(5px);
    }
    
    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Badge */
    .badge {
        background: #ff4757;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = TrendDetectionAgent()
    st.session_state.current_data = None
    st.session_state.last_refresh = None
    st.session_state.analysis_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 AI Trend Detection Agent</h1>
    <p>Real-time social media trend analysis with AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📡 Data Control")
    
    # Data refresh button with spinner
    if st.button("🔄 Fetch Live Data", use_container_width=True, type="primary"):
        with st.spinner("Fetching real-time data from social media..."):
            fetcher = RealTimeDataFetcher()
            df = fetcher.fetch_multiple_sources()
            if df is not None and not df.empty:
                st.session_state.current_data = df
                st.session_state.last_refresh = datetime.now()
                st.success(f"✅ Loaded {len(df)} posts!")
            else:
                st.error("Failed to fetch data")
    
    if st.session_state.last_refresh:
        st.caption(f"🕐 Last updated: {st.session_state.last_refresh.strftime('%I:%M:%S %p')}")
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Filters")
    
    time_filter = st.selectbox(
            "📅 Time Range",
            ["Last 24 Hours", "Last 3 Days", "Last 7 Days", "Last 14 Days", "All Data"],
            index=2
    )
    
    # Get available platforms from data (after data is loaded)
    if st.session_state.current_data is not None:
        available_platforms = st.session_state.current_data['platform'].unique().tolist()
    else:
        available_platforms = ["Twitter", "Reddit", "HackerNews"]

    platform_filter = st.multiselect(
        "📱 Platform",
        available_platforms,
        default=available_platforms  # Select all platforms by default
    )
    
    min_score = st.slider("⭐ Minimum Engagement Score", 0, 100, 0)
    
    st.markdown("---")
    
    # Analysis options
    st.markdown("### ⚙️ Analysis Options")
    
    top_k_topics = st.slider("Number of Topics to Show", 5, 20, 10)
    show_emerging = st.checkbox("Show Emerging Topics", True)
    show_sentiment = st.checkbox("Show Detailed Sentiment", True)
    
    st.markdown("---")
    
    # Stats
    if st.session_state.current_data is not None:
        st.markdown("### 📊 Data Stats")
        df = st.session_state.current_data
        st.metric("Total Posts", len(df))
        st.metric("Date Range", f"{df['date'].min().strftime('%m/%d')} - {df['date'].max().strftime('%m/%d')}")
        
        # Platform distribution
        platform_counts = df['platform'].value_counts()
        for plat, count in platform_counts.items():
            st.progress(count/len(df), text=f"{plat}: {count} posts")

# Main content
if st.session_state.current_data is not None:
    df = st.session_state.current_data.copy()
    
    # Only proceed if dataframe has data
    if df is not None and len(df) > 0:
        # Apply filters
        days_map = {
            "Last 24 Hours": 1, "Last 3 Days": 3, "Last 7 Days": 7, "Last 14 Days": 14, "All Data": 999
        }
        cutoff = datetime.now() - timedelta(days=days_map.get(time_filter, 7))
        df_filtered = df[df['date'] >= cutoff]
        
        # Only filter by platform if platform_filter has values
        if platform_filter and len(platform_filter) > 0:
            df_filtered = df_filtered[df_filtered['platform'].isin(platform_filter)]
        
        # Apply score filter
        if min_score > 0:
            df_filtered = df_filtered[df_filtered['score'] >= min_score]
        
        if not df_filtered.empty:
            # Initialize analyzer
            analyzer = TrendAnalyzer()
            
            # Get analysis results
            key_phrases = analyzer.extract_key_phrases(df_filtered, top_k_topics)
            trending_hashtags = analyzer.get_trending_hashtags(df_filtered, 15)
            emerging_topics = analyzer.detect_emerging_topics(df_filtered) if show_emerging else []
            sentiment = analyzer.get_sentiment_distribution(df_filtered)
            time_series = analyzer.get_time_series_data(df_filtered, 'platform')
            momentum = analyzer.calculate_trend_momentum(df_filtered, 'platform')
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Trending Now", "🔬 Deep Analysis", "📊 Time Series", 
                "🏷️ Hashtags & Topics", "📄 Export Report"
            ])
            
            # TAB 1: Trending Now
            with tab1:
                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📊 Total Posts</h3>
                        <h2>{len(df_filtered)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🎯 Topics Found</h3>
                        <h2>{len(key_phrases)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🏷️ Hashtags</h3>
                        <h2>{len(trending_hashtags)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    sentiment_color = "🟢" if sentiment['positive_pct'] > sentiment['negative_pct'] else "🔴"
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>💭 Sentiment</h3>
                        <h2>{sentiment_color} {sentiment['positive_pct']}%</h2>
                        <small>Positive vs Negative</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Top trending topics
                st.subheader("🔥 Top Trending Topics")
                cols = st.columns(3)
                for idx, phrase in enumerate(key_phrases[:9]):
                    with cols[idx % 3]:
                        if idx < 3:
                            badge = "🔥 HOT"
                        elif idx < 6:
                            badge = "📈 TRENDING"
                        else:
                            badge = "📊 RISING"
                        
                        st.markdown(f"""
                        <div class="trend-card">
                            <span class="badge">{badge}</span>
                            <h2 style="margin: 0.5rem 0;">#{idx+1}</h2>
                            <h3 style="margin: 0;">{phrase['term']}</h3>
                            <p style="margin: 0.5rem 0 0 0;">📊 {phrase['count']} mentions</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Emerging topics section
                if emerging_topics:
                    st.subheader("🚀 Emerging Trends (High Growth)")
                    cols = st.columns(4)
                    for idx, topic in enumerate(emerging_topics[:8]):
                        with cols[idx % 4]:
                            st.markdown(f"""
                            <div style="background: #fff3cd; padding: 0.8rem; border-radius: 8px; margin: 0.3rem 0; border-left: 4px solid #ffc107;">
                                <strong>{topic['topic']}</strong><br>
                                <small>↑ {topic['growth_percentage']}% growth</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Sentiment gauge
                if show_sentiment:
                    st.subheader("💭 Sentiment Overview")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=sentiment['positive_pct'],
                            title={'text': "Positive Sentiment Score"},
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': "#2ecc71"},
                                'steps': [
                                    {'range': [0, 33], 'color': "#e74c3c"},
                                    {'range': [33, 66], 'color': "#f39c12"},
                                    {'range': [66, 100], 'color': "#2ecc71"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 50
                                }
                            }
                        ))
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <p>😊 <strong>Positive:</strong> {sentiment['positive']} posts ({sentiment['positive_pct']}%)</p>
                            <p>😞 <strong>Negative:</strong> {sentiment['negative']} posts ({sentiment['negative_pct']}%)</p>
                            <p>😐 <strong>Neutral:</strong> {sentiment['neutral']} posts ({sentiment['neutral_pct']}%)</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # TAB 2: Deep Analysis
            with tab2:
                st.subheader("🔬 Deep Topic Analysis")
                
                if key_phrases:
                    selected_topic = st.selectbox(
                        "Select a topic to analyze in depth",
                        [p['term'] for p in key_phrases[:15]]
                    )
                    
                    if selected_topic:
                        topic_df = df_filtered[df_filtered['text'].str.contains(selected_topic, case=False)]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"### 📊 Statistics for '{selected_topic}'")
                            st.metric("Total Mentions", len(topic_df))
                            st.metric("Growth Rate", f"{momentum.get(selected_topic, {}).get('change_percentage', 0)}%")
                            st.metric("Trend Status", momentum.get(selected_topic, {}).get('status', 'Unknown'))
                        
                        with col2:
                            topic_sentiment = analyzer.get_sentiment_distribution(topic_df)
                            fig = px.pie(
                                values=[topic_sentiment['positive'], topic_sentiment['negative'], topic_sentiment['neutral']],
                                names=['Positive', 'Negative', 'Neutral'],
                                color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'},
                                title=f"Sentiment for '{selected_topic}'"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander(f"📝 View Sample Posts about '{selected_topic}'"):
                            for idx, post in topic_df.head(10).iterrows():
                                st.markdown(f"**Post {idx+1}:** {post['text']}")
                                st.caption(f"Platform: {post['platform']} | Score: {post.get('score', 'N/A')}")
                                st.markdown("---")
                else:
                    st.info("No topics detected. Try fetching fresh data!")
            
            # TAB 3: Time Series
            with tab3:
                st.subheader("📈 Trend Evolution Over Time")
                
                if 'platform' in df_filtered.columns and len(df_filtered) > 0:
                    df_filtered['date_only'] = df_filtered['date'].dt.date
                    time_data = df_filtered.groupby(['date_only', 'platform']).size().reset_index(name='count')
                    
                    fig = px.line(
                        time_data,
                        x='date_only',
                        y='count',
                        color='platform',
                        title="Posts Over Time by Platform",
                        markers=True
                    )
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Number of Posts",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("🕐 Activity by Hour")
                df_filtered['hour'] = df_filtered['date'].dt.hour
                hourly_data = df_filtered.groupby(['hour', 'platform']).size().reset_index(name='count')
                
                fig = px.bar(
                    hourly_data,
                    x='hour',
                    y='count',
                    color='platform',
                    title="Posting Activity by Hour",
                    labels={'hour': 'Hour of Day', 'count': 'Number of Posts'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # TAB 4: Hashtags & Topics
            with tab4:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🏷️ Top Hashtags")
                    if trending_hashtags:
                        max_count = trending_hashtags[0]['count'] if trending_hashtags else 1
                        for ht in trending_hashtags[:20]:
                            st.markdown(f"- **#{ht['hashtag']}** - {ht['count']} posts")
                            st.progress(min(ht['count']/max_count, 1.0))
                    else:
                        st.info("No hashtags detected")
                
                with col2:
                    st.subheader("📊 Topic Distribution")
                    topic_data = [{'Topic': p['term'], 'Mentions': p['count']} for p in key_phrases[:15]]
                    topic_df_plot = pd.DataFrame(topic_data)
                    
                    fig = px.bar(
                        topic_df_plot,
                        x='Mentions',
                        y='Topic',
                        orientation='h',
                        title="Topic Mentions",
                        color='Mentions',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # TAB 5: Export Report
            with tab5:
                st.subheader("📄 Generate Report")
                
                report_format = st.radio("Report Format", ["CSV", "JSON", "Summary Text"])
                
                if st.button("Generate Report", type="primary"):
                    if report_format == "CSV":
                        csv = df_filtered.to_csv(index=False)
                        st.download_button("Download CSV", csv, "trend_report.csv", "text/csv")
                    elif report_format == "JSON":
                        json_str = df_filtered.to_json(orient='records')
                        st.download_button("Download JSON", json_str, "trend_report.json", "application/json")
                    else:
                        summary = f"""
                        ========================================
                        AI TREND DETECTION REPORT
                        ========================================
                        
                        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        SUMMARY STATISTICS:
                        - Total Posts Analyzed: {len(df_filtered)}
                        - Unique Topics Found: {len(key_phrases)}
                        - Trending Hashtags: {len(trending_hashtags)}
                        
                        TOP TRENDING TOPICS:
                        """
                        for p in key_phrases[:10]:
                            summary += f"\n  - {p['term']}: {p['count']} mentions"
                        
                        summary += f"""
                        
                        SENTIMENT ANALYSIS:
                        - Positive: {sentiment['positive_pct']}%
                        - Negative: {sentiment['negative_pct']}%
                        - Neutral: {sentiment['neutral_pct']}%
                        
                        EMERGING TOPICS:
                        """
                        for e in emerging_topics[:5]:
                            summary += f"\n  - {e['topic']}: ↑{e['growth_percentage']}%"
                        
                        st.text_area("Report Preview", summary, height=400)
                        st.download_button("Download Report", summary, "trend_report.txt")
            
            # CHAT SECTION - Add after tabs
            st.markdown("---")
            st.markdown("### 💬 Ask the AI Agent")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <small>🤖 Ask me anything about the trends! I can answer questions about hashtags, 
                sentiment, topics, emerging trends, and more.</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize chat history
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = []
            
            # Display chat history
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 0.8rem; border-radius: 15px; 
                                margin: 0.5rem 0; text-align: right;">
                        👤 {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 0.8rem; border-radius: 15px; 
                                margin: 0.5rem 0;">
                        🤖 {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Chat input
            chat_query = st.chat_input("Ask me about trends, hashtags, sentiment, or topics...")
            
            if chat_query:
                st.session_state.chat_messages.append({"role": "user", "content": chat_query})
                
                with st.spinner("🤖 AI is thinking..."):
                    agent = st.session_state.agent
                    agent.reset_thinking()
                    
                    chat_analysis_results = {
                        'key_phrases': key_phrases,
                        'trending_hashtags': trending_hashtags,
                        'emerging_topics': emerging_topics if show_emerging else [],
                        'sentiment': sentiment,
                        'total_posts': len(df_filtered),
                        'momentum': momentum
                    }
                    
                    response = agent.chat_with_data(chat_query, df_filtered, chat_analysis_results)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                    with st.expander("🤔 View Agent's Reasoning"):
                        st.markdown(agent.get_thinking_display())
                    
                    st.rerun()
            
            # Clear chat button
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
            
            # Export button
            csv = df_filtered.to_csv(index=False)
            st.download_button("📥 Export Data as CSV", csv, "trend_analysis.csv", "text/csv")
            
        else:
            st.warning("⚠️ No data matches your filters. Try:")
            st.markdown("""
            - Selecting a wider time range
            - Including more platforms
            - Lowering the minimum engagement score
            - Clicking 'Fetch Live Data' again for fresh data
            """)
    else:
        st.warning("⚠️ The fetched data is empty. Click 'Fetch Live Data' again.")
else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>🎯 Welcome to AI Trend Detection Agent</h2>
        <p style="font-size: 1.2rem;">Click <strong>Fetch Live Data</strong> in the sidebar to start analyzing real-time social media trends!</p>
        <br>
        <h3>✨ Features</h3>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div>📈 Real-time trend detection</div>
            <div>🔬 Deep topic analysis</div>
            <div>💭 Sentiment analysis</div>
            <div>📊 Time series visualization</div>
            <div>🤖 AI-powered chat</div>
            <div>📄 Export reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 AI Trend Detection Agent | Built with Streamlit + Gemini AI | UET Taxila</p>
</div>
""", unsafe_allow_html=True)