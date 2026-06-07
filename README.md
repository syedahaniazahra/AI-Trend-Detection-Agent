# 🤖 AI Trend Detection Agent

## 📋 Project Overview

An intelligent AI agent that automatically identifies, ranks, and summarizes trending topics from social media in real-time. The system uses Natural Language Processing (NLP), LDA topic modeling, sentiment analysis, and Google Gemini AI to provide actionable insights.


## 🎯 Features

| Feature | Technology | Description |
|---------|------------|-------------|
| **Real-time Data Fetching** | Reddit API, HackerNews API | Fetches live social media posts |
| **Topic Modeling** | LDA (Latent Dirichlet Allocation) | Extracts hidden topics from text |
| **Trend Ranking** | Multi-factor scoring | Frequency (50%) + Growth (30%) + Recency (20%) |
| **Hashtag Extraction** | Regex + NLP | Identifies trending hashtags |
| **Sentiment Analysis** | VADER | Classifies positive/negative/neutral |
| **Emerging Trends** | Growth rate analysis | Detects rapidly rising topics |
| **AI Chat Assistant** | Google Gemini AI | Answers natural language queries |
| **Interactive Dashboard** | Streamlit | Professional web interface |

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────────────┐
│ USER INTERFACE │
│ (Streamlit Dashboard) │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ AI AGENT BRAIN │
│ (Gemini AI + Reasoning Engine) │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ DATA PROCESSING PIPELINE │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Data Fetcher │ Preprocessor │ Topic Modeler (LDA) │
│ (Reddit API) │ (Text Cleaning) │ │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ Trend Ranker │ Sentiment │ Insight Generator │
│ (Multi-factor) │ (VADER) │ (Gemini AI) │
└─────────────────┴─────────────────┴─────────────────────────────┘


### Trend Scoring Algorithm
Trend Score = (Frequency × 0.5) + (Growth Rate × 0.3) + (Recency × 0.2)

- **Frequency**: Number of mentions (normalized)
- **Growth Rate**: Change in mentions over time
- **Recency**: How recent the posts are

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

### Step 1: Clone the Repository

git clone https://github.com/YOUR_USERNAME/AI-Trend-Detection-Agent.git
cd AI-Trend-Detection-Agent

### Step 2: Install Dependencies

pip install -r requirements.txt
Step 3: Set Up Gemini API Key (For Chat Feature)
Go to Google AI Studio

Click "Get API Key"
Create a new API key
Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

Note: The app works without the API key, but the chat feature will use fallback responses.

### Step 4: Run the Application

Usage Guide

1. Fetch Real-time Data
Click "Fetch Live Data" in the sidebar. The agent will:

Connect to Reddit API (r/technology, r/gadgets, r/all)

Fetch top stories from HackerNews

Extract trending topics from Twitter RSS

Combine and deduplicate all posts

2. Analyze Trends

After data loads, the dashboard shows:

📈 Trending Now: Top trending topics with scores

🔬 Deep Analysis: Drill down into specific topics

📊 Time Series: Trend evolution over time

🏷️ Hashtags & Topics: List of trending hashtags

📄 Export Report: Download CSV/JSON reports

3. Chat with the AI Agent
Use the chat box to ask natural language questions:

text
💬 Examples:
- "What are the top trending topics right now?"
- "Show me trending hashtags"
- "How is the sentiment overall?"
- "What emerging topics should I watch?"
- "Tell me about AI trends"
- "Summarize everything in one paragraph"

4. Filter Data

Use sidebar filters to refine your analysis:

Time Range: Last 24h, 3 days, 7 days, or all

Platform: Select Twitter, Reddit, HackerNews

Minimum Engagement: Filter by score

📊 Sample Output
Top Trending Topics

🔥 HOT - #1: Artificial Intelligence (47 mentions)
📈 TRENDING - #2: iPhone 16 (32 mentions)  
📊 RISING - #3: Tesla Cybertruck (28 mentions)

Sentiment Analysis

😊 Positive: 65% (98 posts)
😞 Negative: 20% (30 posts)
😐 Neutral: 15% (22 posts)
Overall: Positive

Emerging Topics

🚀 SpaceX Starship: ↑340% growth
📈 Solid State Batteries: ↑180% growth
📊 Google Gemini: ↑95% growth


📁 Project Structure

AI-Trend-Detection-Agent/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not uploaded)
├── .gitignore                  # Git ignore file
│
├── src/
│   ├── __init__.py            # Package initializer
│   ├── agent.py               # AI agent brain (Gemini integration)
│   ├── real_time_data.py      # Real-time data fetcher
│   ├── trend_analyzer.py      # Trend detection logic
│   └── sentiment_analyzer.py  # Sentiment analysis
│
└── data/                      # Sample data (optional)
    └── sample_posts.csv


🔧 Dependencies
text
streamlit          # Web interface
pandas             # Data manipulation
numpy              # Numerical operations
scikit-learn       # LDA topic modeling
nltk               # Text preprocessing
matplotlib         # Charts
plotly             # Interactive visualizations
vaderSentiment     # Sentiment analysis
google-generativeai # Gemini AI integration
python-dotenv      # Environment variables
requests           # API calls

To verify the installation:

python -c "import streamlit, pandas, sklearn; print('✅ All dependencies OK')"

Then run the app:
bash
streamlit run app.py

Future Enhancements
Real-time Twitter API integration 
Multilingual trend detection
Predictive trend forecasting
Export to PDF reports
Email notifications for emerging trends
Database integration for historical analysis
