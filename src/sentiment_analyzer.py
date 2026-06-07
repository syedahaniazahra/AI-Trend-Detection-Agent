"""Sentiment analysis using VADER"""

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    """Performs sentiment analysis on text data"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze_single(self, text: str) -> dict:
        """Analyze sentiment of a single text"""
        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
            icon = '😊'
            label = 'Positive'
        elif compound <= -0.05:
            sentiment = 'negative'
            icon = '😞'
            label = 'Negative'
        else:
            sentiment = 'neutral'
            icon = '😐'
            label = 'Neutral'
        
        return {
            'sentiment': sentiment,
            'label': label,
            'icon': icon,
            'compound_score': round(compound, 3)
        }
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Add sentiment analysis to dataframe"""
        df = df.copy()
        sentiment_results = df[text_column].apply(self.analyze_single)
        
        df['sentiment'] = sentiment_results.apply(lambda x: x['sentiment'])
        df['sentiment_label'] = sentiment_results.apply(lambda x: x['label'])
        df['sentiment_icon'] = sentiment_results.apply(lambda x: x['icon'])
        df['compound_score'] = sentiment_results.apply(lambda x: x['compound_score'])
        
        return df
    
    def get_summary(self, df: pd.DataFrame) -> dict:
        """Get aggregated sentiment statistics"""
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        positive = sentiment_counts.get('positive', 0)
        negative = sentiment_counts.get('negative', 0)
        neutral = sentiment_counts.get('neutral', 0)
        
        if positive > negative:
            overall = 'positive'
            overall_label = 'Positive'
            overall_icon = '😊'
        elif negative > positive:
            overall = 'negative'
            overall_label = 'Negative'
            overall_icon = '😞'
        else:
            overall = 'neutral'
            overall_label = 'Neutral'
            overall_icon = '😐'
        
        return {
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'positive_percentage': round(positive / total * 100, 1),
            'negative_percentage': round(negative / total * 100, 1),
            'neutral_percentage': round(neutral / total * 100, 1),
            'total_posts': total,
            'overall_sentiment': overall,
            'overall_label': overall_label,
            'overall_icon': overall_icon,
            'average_compound': round(df['compound_score'].mean(), 3)
        }