
import google.generativeai as genai
import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TrendDetectionAgent:
    """The main AI agent that understands queries and provides intelligent responses"""
    
    def __init__(self, api_key: str = None):
        # Configure Gemini
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.llm_available = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.llm_available = True
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.llm_available = False
        else:
            print("⚠️ No API key found. LLM features disabled.")
        
        self.thinking_steps = []
        self.analysis_results = None
        self.current_data = None
        self.conversation_history = []
    
    def add_thought(self, thought: str):
        self.thinking_steps.append({"type": "thought", "content": thought})
    
    def add_action(self, action: str):
        self.thinking_steps.append({"type": "action", "content": action})
    
    def add_observation(self, observation: str):
        self.thinking_steps.append({"type": "observation", "content": observation})
    
    def understand_query(self, user_query: str) -> Dict[str, Any]:
        """Use LLM to understand what the user wants"""
        self.add_thought(f"Analyzing user query: '{user_query}'")
        
        if not self.llm_available:
            return self._simple_intent_analysis(user_query)
        
        prompt = f"""Analyze this user query about social media trend detection.
        
User Query: "{user_query}"

Return a JSON object with:
{{
    "task_type": "trend_detection" or "sentiment_analysis" or "summarization" or "emerging_topics" or "general",
    "topic": "what specific topic to analyze",
    "time_range": "last 24 hours" or "last 7 days" or "last month" or "all",
    "specific_aspect": "any specific aspect mentioned or null"
}}

Only return the JSON, no other text."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                intent = json.loads(json_str)
            else:
                intent = self._simple_intent_analysis(user_query)
        except Exception as e:
            print(f"LLM error: {e}")
            intent = self._simple_intent_analysis(user_query)
        
        self.add_observation(f"Understood: {intent.get('task_type', 'trend_detection')} about '{intent.get('topic', 'trends')}'")
        return intent
    
    def _simple_intent_analysis(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        
        if "sentiment" in query_lower:
            task_type = "sentiment_analysis"
        elif "emerging" in query_lower or "rising" in query_lower:
            task_type = "emerging_topics"
        elif "summar" in query_lower or "overview" in query_lower:
            task_type = "summarization"
        elif "trend" in query_lower or "topic" in query_lower or "popular" in query_lower:
            task_type = "trend_detection"
        else:
            task_type = "general"
        
        # Extract topics
        topics = ["iphone", "samsung", "google", "pixel", "oneplus", "xiaomi", 
                  "camera", "battery", "display", "performance", "charging", "5g", "ai"]
        topic = None
        for t in topics:
            if t in query_lower:
                topic = t
                break
        
        return {
            "task_type": task_type,
            "topic": topic,
            "time_range": "last 7 days",
            "specific_aspect": None
        }
    
    def chat_with_data(self, user_query: str, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """
        Answer user questions about the trend data using LLM
        This is the main chat function
        """
        self.add_action(f"Processing chat query: '{user_query}'")
        
        if not self.llm_available:
            return self._fallback_chat_response(user_query, analysis_results)
        
        # Prepare data context for LLM
        context = self._prepare_context_for_llm(df, analysis_results)
        
        # Build prompt
        prompt = f"""You are an AI Trend Analysis Agent. You have analyzed social media data and can answer questions about trends.

{context}

User Question: "{user_query}"

Please provide a helpful, accurate, and concise answer based ONLY on the data above. If the user asks something not in the data, say so politely.
Be conversational but informative. Use emojis and bullet points where appropriate.

Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Chat error: {e}")
            return self._fallback_chat_response(user_query, analysis_results)
    
    def _prepare_context_for_llm(self, df: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """Prepare data context for LLM to understand"""
        key_phrases = analysis_results.get('key_phrases', [])[:10]
        trending_hashtags = analysis_results.get('trending_hashtags', [])[:10]
        emerging_topics = analysis_results.get('emerging_topics', [])[:5]
        sentiment = analysis_results.get('sentiment', {})
        
        context = f"""
========================================
SOCIAL MEDIA TREND ANALYSIS DATA
========================================

📊 OVERALL STATISTICS:
- Total posts analyzed: {len(df)}
- Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
- Platforms: {', '.join(df['platform'].unique())}

🔥 TOP TRENDING TOPICS (by mentions):
"""
        for i, p in enumerate(key_phrases[:10], 1):
            context += f"{i}. {p['term']} - {p['count']} mentions\n"
        
        context += f"""
🏷️ TRENDING HASHTAGS:
"""
        for h in trending_hashtags[:10]:
            context += f"  - #{h['hashtag']}: {h['count']} posts\n"
        
        if emerging_topics:
            context += f"""
🚀 EMERGING TOPICS (fastest growing):
"""
            for e in emerging_topics[:5]:
                context += f"  - {e['topic']}: ↑{e['growth_percentage']}% growth\n"
        
        context += f"""
💭 SENTIMENT ANALYSIS:
- Positive: {sentiment.get('positive_pct', 0)}% ({sentiment.get('positive', 0)} posts)
- Negative: {sentiment.get('negative_pct', 0)}% ({sentiment.get('negative', 0)} posts)
- Neutral: {sentiment.get('neutral_pct', 0)}% ({sentiment.get('neutral', 0)} posts)
- Overall sentiment: {sentiment.get('sentiment_category', 'Mixed')}

========================================
"""
        return context
    
    def _fallback_chat_response(self, user_query: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback response when LLM is not available"""
        key_phrases = analysis_results.get('key_phrases', [])[:5]
        sentiment = analysis_results.get('sentiment', {})
        query_lower = user_query.lower()
        
        if "hashtag" in query_lower:
            hashtags = analysis_results.get('trending_hashtags', [])[:5]
            if hashtags:
                response = "🏷️ **Top trending hashtags:**\n"
                for h in hashtags:
                    response += f"- #{h['hashtag']} ({h['count']} posts)\n"
                return response
            else:
                return "No hashtags detected in the current data. Try fetching fresh data!"
        
        elif "sentiment" in query_lower:
            return f"""💭 **Sentiment Analysis Results:**
- 😊 Positive: {sentiment.get('positive_pct', 0)}% ({sentiment.get('positive', 0)} posts)
- 😞 Negative: {sentiment.get('negative_pct', 0)}% ({sentiment.get('negative', 0)} posts)
- 😐 Neutral: {sentiment.get('neutral_pct', 0)}% ({sentiment.get('neutral', 0)} posts)

Overall sentiment is **{sentiment.get('sentiment_category', 'Mixed')}**."""
        
        elif "trend" in query_lower or "topic" in query_lower:
            if key_phrases:
                response = "🔥 **Top trending topics right now:**\n"
                for i, p in enumerate(key_phrases[:5], 1):
                    response += f"{i}. **{p['term']}** - {p['count']} mentions\n"
                return response
            else:
                return "No trends detected. Click 'Fetch Live Data' to get real-time trends!"
        
        else:
            return f"""I'm analyzing {analysis_results.get('total_posts', 0)} social media posts.

📊 **Quick Summary:**
- Top topic: {key_phrases[0]['term'] if key_phrases else 'N/A'}
- Sentiment: {sentiment.get('positive_pct', 0)}% positive, {sentiment.get('negative_pct', 0)}% negative

What would you like to know? Try asking about:
- "Show me trending hashtags"
- "What's the sentiment analysis?"
- "What are the hot topics?"
- "Tell me about emerging trends"
"""
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> str:
        """Generate actionable insights from data"""
        insights = []
        
        top_phrases = analysis_results.get('key_phrases', [])[:5]
        if top_phrases:
            phrase_list = [p['term'] for p in top_phrases]
            insights.append("🔍 **Top discussed topics:** " + ", ".join(phrase_list))
        
        hashtags = analysis_results.get('trending_hashtags', [])[:5]
        if hashtags:
            hashtag_list = ["#" + h['hashtag'] for h in hashtags]
            insights.append("🏷️ **Trending hashtags:** " + ", ".join(hashtag_list))
        
        emerging = analysis_results.get('emerging_topics', [])[:3]
        if emerging:
            insights.append("🚀 **Emerging trends:**")
            for e in emerging:
                insights.append(f"   - {e['topic']} (↑{e['growth_percentage']}% growth)")
        
        sentiment = analysis_results.get('sentiment', {})
        if sentiment:
            pos_pct = sentiment.get('positive_pct', 0)
            neg_pct = sentiment.get('negative_pct', 0)
            if pos_pct > 50:
                insights.append(f"😊 **Sentiment is positive** ({pos_pct}% positive)")
            elif neg_pct > 40:
                insights.append(f"😞 **Sentiment warning:** {neg_pct}% negative - user concerns detected")
            else:
                insights.append(f"🟡 **Mixed sentiment:** {pos_pct}% positive, {neg_pct}% negative")
        
        return "\n\n".join(insights)
    
    def get_thinking_display(self) -> str:
        display = []
        for step in self.thinking_steps:
            if step["type"] == "thought":
                display.append("🤔 **Thinking:** " + step["content"])
            elif step["type"] == "action":
                display.append("⚡ **Action:** " + step["content"])
            elif step["type"] == "observation":
                display.append("👁️ **Observation:** " + step["content"])
        return "\n\n".join(display)
    
    def reset_thinking(self):
        self.thinking_steps = []