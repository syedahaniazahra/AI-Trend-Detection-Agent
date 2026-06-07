"""Trend analysis module - Extracts trends, topics, hashtags, and insights from social media data"""

import pandas as pd
import re
from collections import Counter
from datetime import datetime, timedelta
import numpy as np

class TrendAnalyzer:
    """Analyzes social media data to detect trends, topics, and sentiments"""
    
    @staticmethod
    def extract_key_phrases(df, n=20):
        """
        Extract most common key phrases and tech terms from text data
        
        Parameters:
        - df: DataFrame with 'text' column
        - n: Number of top phrases to return
        
        Returns:
        - List of dictionaries with 'term' and 'count'
        """
        # Comprehensive list of tech and smartphone related terms
        tech_terms = [
            # Brands
            'iPhone', 'Samsung', 'Google Pixel', 'Pixel', 'OnePlus', 'Xiaomi', 
            'Nothing Phone', 'Motorola', 'LG', 'Sony', 'Huawei', 'Realme',
            
            # Features
            'AI', 'camera', 'battery', 'display', 'screen', 'processor', 'chip',
            'performance', 'charging', 'wireless', 'fast charging', '5G', '4G',
            'RAM', 'storage', 'memory', 'speaker', 'audio', 'sound',
            
            # Software
            'iOS', 'Android', 'update', 'software', 'app', 'application',
            'feature', 'settings', 'mode', 'gesture', 'interface',
            
            # Hardware
            'foldable', 'glass', 'frame', 'button', 'port', 'USB-C', 'Lightning',
            'headphone jack', 'SD card', 'dual SIM', 'eSIM',
            
            # Camera specific
            'zoom', 'lens', 'ultrawide', 'telephoto', 'macro', 'portrait',
            'night mode', 'low light', 'HDR', 'OIS', 'stabilization',
            'megapixel', 'MP', 'sensor', 'aperture',
            
            # Battery specific
            'drain', 'health', 'capacity', 'mAh', 'power bank', 'adapter',
            'cable', 'charger', 'battery life', 'standby',
            
            # Display specific
            'OLED', 'AMOLED', 'LCD', 'resolution', 'refresh rate', 'Hz',
            'brightness', 'nits', 'punch hole', 'notch', 'bezels',
            
            # Performance
            'Snapdragon', 'MediaTek', 'Exynos', 'Tensor', 'A series',
            'benchmark', 'score', 'gaming', 'frame rate', 'FPS',
            
            # Issues
            'problem', 'issue', 'bug', 'error', 'crash', 'freeze',
            'overheat', 'lag', 'stutter', 'glitch'
        ]
        
        # Combine all text
        all_text = ' '.join(df['text'].tolist()).lower()
        
        # Count occurrences of each term
        term_counts = {}
        for term in tech_terms:
            # Count occurrences (case insensitive)
            count = all_text.count(term.lower())
            if count > 0:
                term_counts[term] = count
        
        # Sort by count (descending)
        sorted_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return as list of dictionaries
        return [{'term': t, 'count': c} for t, c in sorted_terms[:n]]
    
    @staticmethod
    def get_trending_hashtags(df, n=15):
        """
        Extract and count hashtags from text - FIXED VERSION
    
        Parameters:
        - df: DataFrame with 'text' column and optional 'hashtags' column
        - n: Number of top hashtags to return
    
        Returns:
        - List of dictionaries with 'hashtag' and 'count'
        """
        all_hashtags = []
    
    # Method 1: Extract from 'text' column using regex
        for text in df['text']:
            if text and isinstance(text, str):
                hashtags = re.findall(r'#(\w+)', text)
                all_hashtags.extend([h.lower() for h in hashtags])
    
    # Method 2: If dataframe has 'hashtags' column, use that too
        if 'hashtags' in df.columns:
            for hashtag_list in df['hashtags']:
                if hashtag_list and isinstance(hashtag_list, list):
                    all_hashtags.extend([h.lower() for h in hashtag_list])
    
    # Also check for hashtags in 'cleaned_text' if available
        if 'cleaned_text' in df.columns:
            for text in df['cleaned_text']:
                if text and isinstance(text, str):
                    hashtags = re.findall(r'#(\w+)', text)
                    all_hashtags.extend([h.lower() for h in hashtags])
    
    # Remove empty or single-character hashtags
        filtered_hashtags = [h for h in all_hashtags if len(h) > 2]
    
    # Count occurrences
        hashtag_counts = Counter(filtered_hashtags)
    
    # If still no hashtags, add some example hashtags based on content
        if len(hashtag_counts) == 0 and len(df) > 0:
        # Generate hashtags from key phrases
            all_text = ' '.join(df['text'].tolist()).lower()
            common_words = ['ai', 'tech', 'innovation', 'future', 'gadget', 'smartphone', 
                        'apple', 'google', 'samsung', 'microsoft', 'tesla', 'spacex']
            for word in common_words:
                if word in all_text:
                    hashtag_counts[word] = all_text.count(word) // 10 + 1
    
    # Sort and return top n
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
    
        result = [{'hashtag': h, 'count': c} for h, c in sorted_hashtags[:n]]
        print(f"Found {len(result)} hashtags")  # Debug print
        return result
    
    @staticmethod
    def detect_emerging_topics(df, growth_threshold=30):
        """
        Detect topics that are rapidly gaining popularity
        
        Parameters:
        - df: DataFrame with 'text' and 'date' columns
        - growth_threshold: Minimum growth percentage to consider as emerging
        
        Returns:
        - List of emerging topics with growth percentages
        """
        # Ensure date is datetime
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        now = datetime.now()
        
        # Split into recent (last 2 days) and older (3-5 days ago)
        recent = df[df['date'] > (now - timedelta(days=2))]
        older = df[(df['date'] <= (now - timedelta(days=2))) & 
                   (df['date'] > (now - timedelta(days=7)))]
        
        if len(recent) == 0 or len(older) == 0:
            return []
        
        # Get key phrases from both periods
        recent_phrases = TrendAnalyzer.extract_key_phrases(recent, 50)
        older_phrases = TrendAnalyzer.extract_key_phrases(older, 50)
        
        # Convert to dictionaries for easy lookup
        recent_dict = {p['term']: p['count'] for p in recent_phrases}
        older_dict = {p['term']: p['count'] for p in older_phrases}
        
        # Calculate growth rates
        emerging = []
        for term, recent_count in recent_dict.items():
            older_count = older_dict.get(term, 0)
            
            if older_count == 0:
                # Brand new topic
                growth = 100
            else:
                # Calculate percentage growth
                growth = ((recent_count - older_count) / older_count) * 100
            
            # Only include if growth exceeds threshold
            if growth >= growth_threshold:
                # Determine trend intensity
                if growth >= 200:
                    intensity = "🔥 VIRAL"
                elif growth >= 100:
                    intensity = "🚀 EXPLOSIVE"
                elif growth >= 50:
                    intensity = "📈 RISING FAST"
                else:
                    intensity = "📊 EMERGING"
                
                emerging.append({
                    'topic': term,
                    'recent_mentions': recent_count,
                    'older_mentions': older_count,
                    'growth_percentage': round(growth, 1),
                    'intensity': intensity
                })
        
        # Sort by growth percentage (highest first)
        return sorted(emerging, key=lambda x: x['growth_percentage'], reverse=True)
    
    @staticmethod
    def get_sentiment_distribution(df):
        """
        Analyze sentiment distribution using VADER
        
        Parameters:
        - df: DataFrame with 'text' column
        
        Returns:
        - Dictionary with sentiment counts and percentages
        """
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        analyzer = SentimentIntensityAnalyzer()
        
        positive = 0
        negative = 0
        neutral = 0
        
        sentiment_scores = []
        
        for text in df['text']:
            scores = analyzer.polarity_scores(text)
            compound = scores['compound']
            sentiment_scores.append(compound)
            
            if compound >= 0.05:
                positive += 1
            elif compound <= -0.05:
                negative += 1
            else:
                neutral += 1
        
        total = len(df)
        
        # Avoid division by zero
        if total == 0:
            return {
                'positive': 0, 'negative': 0, 'neutral': 0,
                'positive_pct': 0, 'negative_pct': 0, 'neutral_pct': 0,
                'average_score': 0,
                'sentiment_category': 'No Data'
            }
        
        avg_score = sum(sentiment_scores) / total if sentiment_scores else 0
        
        # Determine overall sentiment category
        if positive > negative * 1.5:
            sentiment_category = "Very Positive"
        elif positive > negative:
            sentiment_category = "Positive"
        elif negative > positive * 1.5:
            sentiment_category = "Very Negative"
        elif negative > positive:
            sentiment_category = "Negative"
        else:
            sentiment_category = "Mixed"
        
        return {
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_pct': round(positive / total * 100, 1),
            'negative_pct': round(negative / total * 100, 1),
            'neutral_pct': round(neutral / total * 100, 1),
            'average_score': round(avg_score, 3),
            'sentiment_category': sentiment_category,
            'total_posts': total
        }
    
    @staticmethod
    def get_time_series_data(df, group_by_column=None):
        """
        Get trend data over time for time series analysis
        
        Parameters:
        - df: DataFrame with 'date' column
        - group_by_column: Optional column to group by (e.g., 'platform', 'topic')
        
        Returns:
        - Dictionary with time series data
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Get date range
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        # Create date range
        date_range = pd.date_range(min_date, max_date, freq='D')
        
        if group_by_column and group_by_column in df.columns:
            # Group by date and specified column
            results = {}
            for group in df[group_by_column].unique():
                group_df = df[df[group_by_column] == group]
                daily_counts = group_df.groupby(group_df['date'].dt.date).size()
                
                counts = []
                for date in date_range:
                    date_key = date.date()
                    count = daily_counts.get(date_key, 0)
                    counts.append(count)
                
                results[group] = {
                    'dates': [d.strftime('%Y-%m-%d') for d in date_range],
                    'counts': counts,
                    'total': sum(counts)
                }
            return results
        else:
            # Just overall trend
            daily_counts = df.groupby(df['date'].dt.date).size()
            counts = []
            for date in date_range:
                date_key = date.date()
                count = daily_counts.get(date_key, 0)
                counts.append(count)
            
            return {
                'overall': {
                    'dates': [d.strftime('%Y-%m-%d') for d in date_range],
                    'counts': counts,
                    'total': sum(counts)
                }
            }
    
    @staticmethod
    def calculate_trend_momentum(df, topic_column=None):
        """
        Calculate trend momentum (acceleration/deceleration)
        
        Parameters:
        - df: DataFrame with 'date' column
        - topic_column: Column containing topic names
        
        Returns:
        - Dictionary with momentum data for each topic
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        now = datetime.now()
        
        # Last 3 days vs previous 3 days
        last_3_days = df[df['date'] > (now - timedelta(days=3))]
        previous_3_days = df[(df['date'] <= (now - timedelta(days=3))) & 
                              (df['date'] > (now - timedelta(days=6)))]
        
        if topic_column and topic_column in df.columns:
            # Calculate momentum per topic
            momentum = {}
            
            for topic in df[topic_column].unique():
                last_count = len(last_3_days[last_3_days[topic_column] == topic])
                prev_count = len(previous_3_days[previous_3_days[topic_column] == topic])
                
                if prev_count == 0:
                    momentum_change = 100 if last_count > 0 else 0
                else:
                    momentum_change = ((last_count - prev_count) / prev_count) * 100
                
                # Determine momentum status
                if momentum_change > 100:
                    status = "🚀 VIRAL MOMENTUM"
                    color = "#ff4757"
                elif momentum_change > 50:
                    status = "📈 STRONG ACCELERATION"
                    color = "#ffa502"
                elif momentum_change > 20:
                    status = "📊 ACCELERATING"
                    color = "#1e90ff"
                elif momentum_change > -20:
                    status = "➡️ STABLE"
                    color = "#2ed573"
                elif momentum_change > -50:
                    status = "📉 DECELERATING"
                    color = "#ff6b6b"
                else:
                    status = "⚠️ RAPID DECLINE"
                    color = "#ee5a24"
                
                momentum[topic] = {
                    'change_percentage': round(momentum_change, 1),
                    'status': status,
                    'status_color': color,
                    'last_count': last_count,
                    'prev_count': prev_count,
                    'direction': 'up' if momentum_change > 0 else 'down' if momentum_change < 0 else 'stable'
                }
            
            return momentum
        else:
            # Overall momentum
            last_count = len(last_3_days)
            prev_count = len(previous_3_days)
            
            if prev_count == 0:
                momentum_change = 100 if last_count > 0 else 0
            else:
                momentum_change = ((last_count - prev_count) / prev_count) * 100
            
            return {
                'overall': {
                    'change_percentage': round(momentum_change, 1),
                    'last_count': last_count,
                    'prev_count': prev_count
                }
            }
    
    @staticmethod
    def compare_topics(df, topics_to_compare):
        """
        Compare multiple topics/brands against each other
        
        Parameters:
        - df: DataFrame with 'text' and 'date' columns
        - topics_to_compare: List of topics to compare
        
        Returns:
        - Dictionary with comparison results
        """
        results = {}
        
        for topic in topics_to_compare:
            # Filter posts containing the topic (case insensitive)
            topic_df = df[df['text'].str.contains(topic, case=False, na=False)]
            
            if len(topic_df) > 0:
                # Get sentiment for this topic
                sentiment = TrendAnalyzer.get_sentiment_distribution(topic_df)
                
                # Calculate growth rate
                now = datetime.now()
                recent = topic_df[topic_df['date'] > (now - timedelta(days=3))]
                older = topic_df[topic_df['date'] <= (now - timedelta(days=3))]
                
                recent_count = len(recent)
                older_count = len(older)
                
                if older_count == 0:
                    growth = 100 if recent_count > 0 else 0
                else:
                    growth = ((recent_count - older_count) / older_count) * 100
                
                # Determine trend status
                if growth > 50:
                    trend_status = "🔥 Hot Trend"
                    trend_icon = "🔥"
                elif growth > 20:
                    trend_status = "📈 Rising"
                    trend_icon = "📈"
                elif growth > -20:
                    trend_status = "➡️ Steady"
                    trend_icon = "➡️"
                else:
                    trend_status = "📉 Declining"
                    trend_icon = "📉"
                
                results[topic] = {
                    'total_mentions': len(topic_df),
                    'sentiment_positive': sentiment['positive_pct'],
                    'sentiment_negative': sentiment['negative_pct'],
                    'sentiment_neutral': sentiment['neutral_pct'],
                    'sentiment_category': sentiment['sentiment_category'],
                    'growth_rate': round(growth, 1),
                    'trend_status': trend_status,
                    'trend_icon': trend_icon,
                    'recent_mentions': recent_count,
                    'older_mentions': older_count
                }
            else:
                results[topic] = {
                    'total_mentions': 0,
                    'sentiment_positive': 0,
                    'sentiment_negative': 0,
                    'sentiment_neutral': 0,
                    'sentiment_category': 'No Data',
                    'growth_rate': 0,
                    'trend_status': '❌ Not Found',
                    'trend_icon': '❌',
                    'recent_mentions': 0,
                    'older_mentions': 0
                }
        
        # Sort by total mentions (descending)
        return dict(sorted(results.items(), key=lambda x: x[1]['total_mentions'], reverse=True))
    
    @staticmethod
    def generate_topic_names(topics_dict):
        """
        Generate intelligent, human-readable names for topics
        
        Parameters:
        - topics_dict: Dictionary of topics with keywords
        
        Returns:
        - Dictionary with enhanced topic names and descriptions
        """
        topic_names = {}
        
        # Category definitions
        categories = {
            'camera': {
                'keywords': ['camera', 'photo', 'image', 'zoom', 'lens', 'night', 'portrait', 'pixel', 'sensor', 'aperture'],
                'name': '📸 Camera & Photography',
                'description': 'Discussions about camera quality, photo features, zoom capabilities, and image processing',
                'color': '#e84393'
            },
            'battery': {
                'keywords': ['battery', 'charge', 'drain', 'power', 'health', 'charging', 'adapter', 'cable', 'mAh', 'wireless'],
                'name': '🔋 Battery & Charging',
                'description': 'Concerns and discussions about battery life, charging speed, battery health, and power management',
                'color': '#f39c12'
            },
            'display': {
                'keywords': ['display', 'screen', 'brightness', 'refresh', 'foldable', 'smooth', 'OLED', 'AMOLED', 'resolution', 'Hz'],
                'name': '📱 Display & Screen',
                'description': 'Discussions about screen quality, refresh rates, brightness, and display technology',
                'color': '#3498db'
            },
            'performance': {
                'keywords': ['chip', 'processor', 'performance', 'speed', 'lag', 'game', 'snapdragon', 'tensor', 'exynos', 'benchmark'],
                'name': '⚡ Performance & Speed',
                'description': 'Discussions about processor performance, smoothness, gaming capabilities, and speed',
                'color': '#2ecc71'
            },
            'software': {
                'keywords': ['iOS', 'Android', 'update', 'software', 'app', 'feature', 'interface', 'gesture', 'settings'],
                'name': '💻 Software & Updates',
                'description': 'Discussions about operating systems, software updates, new features, and user interface',
                'color': '#9b59b6'
            },
            'design': {
                'keywords': ['design', 'build', 'material', 'glass', 'frame', 'color', 'feel', 'premium', 'durable'],
                'name': '🎨 Design & Build',
                'description': 'Discussions about phone design, build quality, materials, and aesthetics',
                'color': '#1abc9c'
            },
            'price': {
                'keywords': ['price', 'cost', 'expensive', 'cheap', 'value', 'budget', 'premium', 'affordable'],
                'name': '💰 Price & Value',
                'description': 'Discussions about pricing, value for money, and budget considerations',
                'color': '#e74c3c'
            }
        }
        
        for topic_id, topic_data in topics_dict.items():
            keywords = topic_data.get('keywords', [])
            keyword_set = set([k.lower() for k in keywords])
            
            # Find best matching category
            best_match = None
            best_score = 0
            
            for cat_name, cat_data in categories.items():
                matches = len(keyword_set & set(cat_data['keywords']))
                if matches > best_score:
                    best_score = matches
                    best_match = cat_data
            
            if best_match and best_score >= 2:
                topic_names[topic_id] = {
                    'name': best_match['name'],
                    'description': best_match['description'],
                    'color': best_match['color'],
                    'keywords': keywords[:8],
                    'confidence': min(best_score / 5, 1.0)
                }
            else:
                # Generic topic name based on top keywords
                top_keyword = keywords[0].capitalize() if keywords else "Discussion"
                topic_names[topic_id] = {
                    'name': f'💬 {top_keyword} & Related',
                    'description': f'Discussions related to {", ".join(keywords[:5])}',
                    'color': '#95a5a6',
                    'keywords': keywords[:8],
                    'confidence': 0.5
                }
        
        return topic_names
    
    @staticmethod
    def get_activity_patterns(df):
        """
        Analyze posting activity patterns
        
        Parameters:
        - df: DataFrame with 'date' column
        
        Returns:
        - Dictionary with activity patterns
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Hourly activity
        df['hour'] = df['date'].dt.hour
        hourly_activity = df.groupby('hour').size().to_dict()
        
        # Day of week activity
        df['day_of_week'] = df['date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_activity = df.groupby('day_of_week').size().reindex(day_order).to_dict()
        
        # Find peak hours
        if hourly_activity:
            peak_hour = max(hourly_activity, key=hourly_activity.get)
            peak_count = hourly_activity[peak_hour]
        else:
            peak_hour = 12
            peak_count = 0
        
        # Find peak day
        if daily_activity:
            peak_day = max(daily_activity, key=daily_activity.get)
        else:
            peak_day = "Unknown"
        
        return {
            'hourly': hourly_activity,
            'daily': daily_activity,
            'peak_hour': peak_hour,
            'peak_hour_count': peak_count,
            'peak_day': peak_day,
            'total_days': (df['date'].max() - df['date'].min()).days + 1
        }
    
    @staticmethod
    def get_summary_stats(df):
        """
        Generate comprehensive summary statistics
        
        Parameters:
        - df: DataFrame with 'text', 'platform', 'date' columns
        
        Returns:
        - Dictionary with summary statistics
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Basic stats
        total_posts = len(df)
        unique_platforms = df['platform'].nunique() if 'platform' in df.columns else 0
        
        # Date range
        date_range_days = (df['date'].max() - df['date'].min()).days + 1
        
        # Average post length
        avg_length = df['text'].str.len().mean()
        
        # Platform distribution
        platform_dist = df['platform'].value_counts().to_dict() if 'platform' in df.columns else {}
        
        # Time-based stats
        df['hour'] = df['date'].dt.hour
        most_active_hour = df['hour'].mode()[0] if not df['hour'].empty else 0
        
        df['day'] = df['date'].dt.day_name()
        most_active_day = df['day'].mode()[0] if not df['day'].empty else "Unknown"
        
        return {
            'total_posts': total_posts,
            'unique_platforms': unique_platforms,
            'date_range_days': date_range_days,
            'avg_post_length': round(avg_length, 1),
            'platform_distribution': platform_dist,
            'most_active_hour': int(most_active_hour),
            'most_active_day': most_active_day,
            'start_date': df['date'].min().strftime('%Y-%m-%d'),
            'end_date': df['date'].max().strftime('%Y-%m-%d')
        }