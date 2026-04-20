import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class AnalyticsAgent:
    def __init__(self, progress_df):
        self.df = progress_df

    def get_score_trends(self):
        if self.df.empty:
            return None
        self.df['completed_at'] = pd.to_datetime(self.df['completed_at'])
        fig = px.line(self.df, x='completed_at', y='score', color='subject', title="Score Trends Over Time")
        return fig

    def get_subject_performance(self):
        if self.df.empty:
            return None
        perf = self.df.groupby('subject')['score'].mean().reset_index()
        fig = px.bar(perf, x='subject', y='score', title="Average Score by Subject", color='score', color_continuous_scale='Viridis')
        return fig

    def get_weak_areas(self):
        if self.df.empty:
            return "No data yet."
        avg_scores = self.df.groupby(['subject', 'topic'])['score'].mean().reset_index()
        weak = avg_scores[avg_scores['score'] < 60]
        if weak.empty:
            return "Great job! No specific weak areas identified (all above 60%)."
        return weak
