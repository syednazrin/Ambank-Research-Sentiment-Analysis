import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from collections import Counter
import re

def load_sentiment_data(filename):
    """Load sentiment analysis results from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} sentiment analysis results")
        return data
    except FileNotFoundError:
        print(f"Error: File {filename} not found!")
        return []
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def prepare_data(data):
    """Convert JSON data to pandas DataFrame with proper datetime parsing and confidence score categorization"""
    df_data = []
    
    for item in data:
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
        except:
            continue
            
        # Get confidence score (default to 0.5 if missing)
        confidence_score = item.get('confidence_score', 0.5)
        
        # Categorize based on confidence score ranges
        if 0.0 <= confidence_score <= 0.1:
            sentiment_category = 'Extremely Negative'
            sentiment_label = 'Extremely Negative'
        elif 0.1 < confidence_score <= 0.3:
            sentiment_category = 'Clearly Negative'
            sentiment_label = 'Clearly Negative'
        elif 0.3 < confidence_score <= 0.4:
            sentiment_category = 'Somewhat Negative'
            sentiment_label = 'Somewhat Negative'
        elif 0.4 < confidence_score <= 0.6:
            sentiment_category = 'Neutral'
            sentiment_label = 'Neutral'
        elif 0.6 < confidence_score <= 0.7:
            sentiment_category = 'Somewhat Positive'
            sentiment_label = 'Somewhat Positive'
        elif 0.7 < confidence_score <= 0.9:
            sentiment_category = 'Clearly Positive'
            sentiment_label = 'Clearly Positive'
        elif 0.9 < confidence_score <= 1.0:
            sentiment_category = 'Extremely Positive'
            sentiment_label = 'Extremely Positive'
        else:
            sentiment_category = 'Invalid Score'
            sentiment_label = 'Invalid Score'
        
        # Create broader categories for summary analysis
        if confidence_score <= 0.4:
            broad_category = 'Negative toward Nestle'
        elif confidence_score <= 0.6:
            broad_category = 'Neutral'
        else:
            broad_category = 'Positive toward Nestle'
        
        df_data.append({
            'timestamp': timestamp,
            'tweet': item['tweet'],
            'confidence_score': confidence_score,
            'reasoning': item.get('reasoning', 'No reasoning provided'),
            'sentiment_category': sentiment_category,
            'sentiment_label': sentiment_label,
            'broad_category': broad_category,
            'tweet_length': len(item['tweet']),
            'date': timestamp.date(),
            'month': timestamp.strftime('%Y-%m'),
            'day': timestamp.strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('timestamp')
    return df

def create_sentiment_timeline(df):
    """Create confidence score over time line chart"""
    # Group by day and calculate average confidence score
    daily_sentiment = df.groupby('date').agg({
        'confidence_score': 'mean',
        'tweet': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_sentiment['date'],
        y=daily_sentiment['confidence_score'],
        mode='lines+markers',
        name='Average Confidence Score',
        line=dict(color='#2E86C1', width=3),
        marker=dict(size=8),
        hovertemplate='Date: %{x}<br>Avg Confidence: %{y:.3f}<br>Posts: %{customdata}<extra></extra>',
        customdata=daily_sentiment['tweet']
    ))
    
    # Add horizontal lines for key thresholds
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                  annotation_text="Neutral (0.5)")
    fig.add_hline(y=0.3, line_dash="dot", line_color="red", 
                  annotation_text="Negative Threshold (0.3)")
    fig.add_hline(y=0.7, line_dash="dot", line_color="green", 
                  annotation_text="Positive Threshold (0.7)")
    
    fig.update_layout(
        title='Nestle Sentiment Confidence Over Time',
        xaxis_title='Date',
        yaxis_title='Average Confidence Score',
        yaxis=dict(range=[0, 1]),
        template='plotly_white',
        height=500,
        annotations=[
            dict(x=0.02, y=0.95, xref="paper", yref="paper", 
                 text="Lower scores = More negative toward Nestle<br>Higher scores = More positive toward Nestle",
                 showarrow=False, font=dict(size=10), bgcolor="rgba(255,255,255,0.8)")
        ]
    )
    
    return fig

def create_sentiment_distribution(df):
    """Create overall sentiment distribution pie chart using confidence score categories"""
    sentiment_counts = df['sentiment_category'].value_counts()
    
    # Color scheme for different sentiment levels (red to green gradient)
    color_map = {
        'Extremely Negative': '#8B0000',  # Dark red
        'Clearly Negative': '#DC143C',    # Crimson
        'Somewhat Negative': '#FF6347',   # Tomato
        'Neutral': '#FFD700',             # Gold
        'Somewhat Positive': '#90EE90',   # Light green
        'Clearly Positive': '#32CD32',    # Lime green
        'Extremely Positive': '#006400',  # Dark green
        'Invalid Score': '#808080'        # Gray
    }
    
    colors = [color_map.get(label, '#BDC3C7') for label in sentiment_counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent+value',
        hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Sentiment Distribution by Confidence Score',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_tweet_volume_chart(df):
    """Create tweet volume over time bar chart"""
    daily_volume = df.groupby('date').size().reset_index(name='tweet_count')
    
    fig = go.Figure(data=[go.Bar(
        x=daily_volume['date'],
        y=daily_volume['tweet_count'],
        marker_color='#3498DB',
        hovertemplate='Date: %{x}<br>Tweet Count: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Tweet Volume Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Tweets',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_monthly_sentiment_breakdown(df):
    """Create monthly sentiment breakdown stacked bar chart using confidence score categories"""
    monthly_sentiment = df.groupby(['month', 'sentiment_category']).size().reset_index(name='count')
    monthly_pivot = monthly_sentiment.pivot(index='month', columns='sentiment_category', values='count').fillna(0)
    
    fig = go.Figure()
    
    # Use the same color mapping as in distribution chart
    color_map = {
        'Extremely Negative': '#8B0000',  # Dark red
        'Clearly Negative': '#DC143C',    # Crimson
        'Somewhat Negative': '#FF6347',   # Tomato
        'Neutral': '#FFD700',             # Gold
        'Somewhat Positive': '#90EE90',   # Light green
        'Clearly Positive': '#32CD32',    # Lime green
        'Extremely Positive': '#006400',  # Dark green
        'Invalid Score': '#808080'        # Gray
    }
    
    for sentiment in monthly_pivot.columns:
        fig.add_trace(go.Bar(
            name=sentiment,
            x=monthly_pivot.index,
            y=monthly_pivot[sentiment],
            marker_color=color_map.get(sentiment, '#BDC3C7'),
            hovertemplate='Month: %{x}<br>%{fullData.name}: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Monthly Sentiment Breakdown by Confidence Score',
        xaxis_title='Month',
        yaxis_title='Number of Posts',
        barmode='stack',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_sentiment_by_tweet_length(df):
    """Create confidence score vs tweet length scatter plot"""
    color_map = {
        'Extremely Negative': '#8B0000',  # Dark red
        'Clearly Negative': '#DC143C',    # Crimson
        'Somewhat Negative': '#FF6347',   # Tomato
        'Neutral': '#FFD700',             # Gold
        'Somewhat Positive': '#90EE90',   # Light green
        'Clearly Positive': '#32CD32',    # Lime green
        'Extremely Positive': '#006400',  # Dark green
        'Invalid Score': '#808080'        # Gray
    }
    
    fig = px.scatter(
        df, 
        x='tweet_length', 
        y='confidence_score',
        color='sentiment_category',
        title='Confidence Score vs Post Length',
        labels={'tweet_length': 'Post Length (characters)', 'confidence_score': 'Confidence Score (0=Negative, 1=Positive)'},
        color_discrete_map=color_map,
        hover_data=['tweet', 'reasoning']
    )
    
    # Add horizontal reference lines
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=0.3, line_dash="dot", line_color="red", opacity=0.5)
    fig.add_hline(y=0.7, line_dash="dot", line_color="green", opacity=0.5)
    
    fig.update_layout(
        template='plotly_white',
        height=500,
        yaxis=dict(range=[0, 1])
    )
    
    return fig

def create_confidence_score_histogram(df):
    """Create histogram showing distribution of confidence scores"""
    fig = go.Figure(data=[go.Histogram(
        x=df['confidence_score'],
        nbinsx=20,
        marker_color='#3498DB',
        opacity=0.7,
        hovertemplate='Confidence Range: %{x}<br>Count: %{y}<extra></extra>'
    )])
    
    # Add vertical lines for key thresholds
    fig.add_vline(x=0.3, line_dash="dash", line_color="red", 
                  annotation_text="Negative Threshold")
    fig.add_vline(x=0.5, line_dash="dash", line_color="gray", 
                  annotation_text="Neutral")
    fig.add_vline(x=0.7, line_dash="dash", line_color="green", 
                  annotation_text="Positive Threshold")
    
    fig.update_layout(
        title='Distribution of Confidence Scores',
        xaxis_title='Confidence Score (0=Negative, 1=Positive)',
        yaxis_title='Number of Posts',
        template='plotly_white',
        height=500,
        xaxis=dict(range=[0, 1])
    )
    
    return fig

def extract_common_words(tweets, min_length=4):
    """Extract common words from tweets"""
    all_text = ' '.join(tweets).lower()
    # Remove common words and extract meaningful words
    words = re.findall(r'\b[a-zA-Z]{' + str(min_length) + r',}\b', all_text)
    # Filter out common words
    common_words = ['nestle', 'that', 'this', 'with', 'they', 'have', 'from', 'their', 'would', 'been', 'said', 'each', 'more', 'some', 'what', 'them']
    words = [word for word in words if word not in common_words]
    return Counter(words)

def create_word_analysis_chart(df):
    """Create word frequency comparison between negative and positive sentiment categories"""
    # Use broad categories for better comparison
    negative_tweets = df[df['broad_category'] == 'Negative toward Nestle']['tweet'].tolist()
    positive_tweets = df[df['broad_category'] == 'Positive toward Nestle']['tweet'].tolist()
    
    negative_words = extract_common_words(negative_tweets)
    positive_words = extract_common_words(positive_tweets)
    
    # Get top 10 words from each category
    top_negative = dict(negative_words.most_common(10))
    top_positive = dict(positive_words.most_common(10))
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Most Common Words in Negative Posts', 'Most Common Words in Positive Posts'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Negative sentiment words
    if top_negative:
        fig.add_trace(
            go.Bar(
                x=list(top_negative.keys()),
                y=list(top_negative.values()),
                name='Negative toward Nestle',
                marker_color='#DC143C'
            ),
            row=1, col=1
        )
    
    # Positive sentiment words
    if top_positive:
        fig.add_trace(
            go.Bar(
                x=list(top_positive.keys()),
                y=list(top_positive.values()),
                name='Positive toward Nestle',
                marker_color='#32CD32'
            ),
            row=1, col=2
        )
    
    fig.update_layout(
        title='Word Frequency Analysis by Sentiment (Confidence-Based)',
        template='plotly_white',
        height=500,
        showlegend=False
    )
    
    return fig

def generate_summary_stats(df):
    """Generate summary statistics based on confidence scores"""
    total_posts = len(df)
    
    # Count posts by broad categories
    negative_posts = len(df[df['broad_category'] == 'Negative toward Nestle'])
    neutral_posts = len(df[df['broad_category'] == 'Neutral'])
    positive_posts = len(df[df['broad_category'] == 'Positive toward Nestle'])
    
    # Calculate average confidence score
    avg_confidence = df['confidence_score'].mean()
    
    # Count posts by detailed sentiment categories
    extremely_negative = len(df[df['sentiment_category'] == 'Extremely Negative'])
    clearly_negative = len(df[df['sentiment_category'] == 'Clearly Negative'])
    somewhat_negative = len(df[df['sentiment_category'] == 'Somewhat Negative'])
    neutral_detailed = len(df[df['sentiment_category'] == 'Neutral'])
    somewhat_positive = len(df[df['sentiment_category'] == 'Somewhat Positive'])
    clearly_positive = len(df[df['sentiment_category'] == 'Clearly Positive'])
    extremely_positive = len(df[df['sentiment_category'] == 'Extremely Positive'])
    
    date_range = f"{df['date'].min()} to {df['date'].max()}"
    
    return {
        'total_posts': total_posts,
        'negative_posts': negative_posts,
        'neutral_posts': neutral_posts,
        'positive_posts': positive_posts,
        'avg_confidence': avg_confidence,
        'date_range': date_range,
        'negative_percentage': (negative_posts / total_posts) * 100 if total_posts > 0 else 0,
        'neutral_percentage': (neutral_posts / total_posts) * 100 if total_posts > 0 else 0,
        'positive_percentage': (positive_posts / total_posts) * 100 if total_posts > 0 else 0,
        # Detailed breakdown
        'extremely_negative': extremely_negative,
        'clearly_negative': clearly_negative,
        'somewhat_negative': somewhat_negative,
        'neutral_detailed': neutral_detailed,
        'somewhat_positive': somewhat_positive,
        'clearly_positive': clearly_positive,
        'extremely_positive': extremely_positive
    }

def create_dashboard_html(figures, stats):
    """Create HTML dashboard with all figures"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nestle Sentiment Analysis Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f8f9fa;
            }}
            .header {{
                text-align: center;
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .stat-label {{
                color: #7f8c8d;
                margin-top: 5px;
            }}
            .chart-container {{
                background: white;
                margin-bottom: 30px;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Nestle Sentiment Analysis Dashboard</h1>
            <p>Confidence Score Analysis of {stats['total_posts']} posts from {stats['date_range']}</p>
            <p style="font-size: 14px; margin-top: 10px;">Confidence scores: 0.0 = Extremely Negative, 0.5 = Neutral, 1.0 = Extremely Positive</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_posts']}</div>
                <div class="stat-label">Total Posts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['negative_posts']}</div>
                <div class="stat-label">Negative toward Nestle</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['neutral_posts']}</div>
                <div class="stat-label">Neutral</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['positive_posts']}</div>
                <div class="stat-label">Positive toward Nestle</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['avg_confidence']:.3f}</div>
                <div class="stat-label">Average Confidence Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['negative_percentage']:.1f}%</div>
                <div class="stat-label">Negative %</div>
            </div>
        </div>
    """
    
    # Add each figure to the HTML
    for i, fig in enumerate(figures):
        html_content += f"""
        <div class="chart-container">
            <div id="chart{i}"></div>
        </div>
        """
    
    html_content += """
        <script>
    """
    
    # Add JavaScript to render each figure
    for i, fig in enumerate(figures):
        fig_json = fig.to_json()
        html_content += f"""
            var figure{i} = {fig_json};
            Plotly.newPlot('chart{i}', figure{i}.data, figure{i}.layout);
        """
    
    html_content += """
        </script>
    </body>
    </html>
    """
    
    return html_content

def main():
    # Load data
    data = load_sentiment_data("nestle_threads_sentiment_analysis_2025-08-12.json")
    
    if not data:
        print("No data loaded. Exiting.")
        return
    
    # Prepare data
    df = prepare_data(data)
    print(f"Prepared {len(df)} records for visualization")
    
    # Generate summary statistics
    stats = generate_summary_stats(df)
    
    # Create visualizations
    print("Creating visualizations...")
    figures = []
    
    # 1. Sentiment over time
    figures.append(create_sentiment_timeline(df))
    
    # 2. Sentiment distribution
    figures.append(create_sentiment_distribution(df))
    
    # 3. Tweet volume over time
    figures.append(create_tweet_volume_chart(df))
    
    # 4. Monthly sentiment breakdown
    figures.append(create_monthly_sentiment_breakdown(df))
    
    # 5. Sentiment vs tweet length
    figures.append(create_sentiment_by_tweet_length(df))
    
    # 6. Confidence score histogram
    figures.append(create_confidence_score_histogram(df))
    
    # 7. Word analysis
    figures.append(create_word_analysis_chart(df))
    
    # Generate HTML dashboard
    print("Generating HTML dashboard...")
    html_content = create_dashboard_html(figures, stats)
    
    # Save HTML file
    output_filename = "nestle_sentiment_dashboard.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Dashboard saved as {output_filename}")
    print(f"\nSummary Statistics:")
    print(f"- Total posts analyzed: {stats['total_posts']}")
    print(f"- Negative toward Nestle: {stats['negative_posts']} ({stats['negative_percentage']:.1f}%)")
    print(f"- Neutral: {stats['neutral_posts']} ({stats['neutral_percentage']:.1f}%)")
    print(f"- Positive toward Nestle: {stats['positive_posts']} ({stats['positive_percentage']:.1f}%)")
    print(f"- Average confidence score: {stats['avg_confidence']:.3f}")
    print(f"- Date range: {stats['date_range']}")
    print(f"\nDetailed Breakdown:")
    print(f"- Extremely Negative: {stats['extremely_negative']}")
    print(f"- Clearly Negative: {stats['clearly_negative']}")
    print(f"- Somewhat Negative: {stats['somewhat_negative']}")
    print(f"- Neutral: {stats['neutral_detailed']}")
    print(f"- Somewhat Positive: {stats['somewhat_positive']}")
    print(f"- Clearly Positive: {stats['clearly_positive']}")
    print(f"- Extremely Positive: {stats['extremely_positive']}")

if __name__ == "__main__":
    main()
