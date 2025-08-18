from flask import Flask, render_template
import os
import step_3_dashboard as dashboard


app = Flask(__name__)


@app.route("/health")
def health() -> str:
    return "ok"


@app.route("/")
def index():
    data_file = os.environ.get(
        "DATA_FILE",
        "nestle_threads_sentiment_analysis_2025-08-12.json",
    )

    data = dashboard.load_sentiment_data(data_file)

    if not data:
        figures_json = []
        stats = {
            "total_posts": 0,
            "negative_posts": 0,
            "neutral_posts": 0,
            "positive_posts": 0,
            "avg_confidence": 0.0,
            "date_range": "N/A",
            "negative_percentage": 0.0,
            "neutral_percentage": 0.0,
            "positive_percentage": 0.0,
            "extremely_negative": 0,
            "clearly_negative": 0,
            "somewhat_negative": 0,
            "neutral_detailed": 0,
            "somewhat_positive": 0,
            "clearly_positive": 0,
            "extremely_positive": 0,
        }
    else:
        df = dashboard.prepare_data(data)
        stats = dashboard.generate_summary_stats(df)
        figures = [
            dashboard.create_sentiment_timeline(df),
            dashboard.create_sentiment_distribution(df),
            dashboard.create_tweet_volume_chart(df),
            dashboard.create_monthly_sentiment_breakdown(df),
            dashboard.create_sentiment_by_tweet_length(df),
            dashboard.create_confidence_score_histogram(df),
            dashboard.create_word_analysis_chart(df),
        ]
        figures_json = [fig.to_json() for fig in figures]

    return render_template("dashboard.html", figures_json=figures_json, stats=stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


