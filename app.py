from flask import Flask, render_template
import os
import json
from urllib.parse import urlparse
import step_3_dashboard as dashboard

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


app = Flask(__name__)


@app.route("/health")
def health() -> str:
    return "ok"


@app.route("/")
def index():
    data_file = os.environ.get(
        "DATA_FILE",
        "static/data/sample_data.json",
    )

    data = []
    # Try S3 / HTTP(S) / local file in that order based on scheme
    parsed = urlparse(data_file)
    try:
        if parsed.scheme == "s3" and boto3 is not None:
            s3 = boto3.client("s3")
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            obj = s3.get_object(Bucket=bucket, Key=key)
            body = obj["Body"].read()
            data = json.loads(body)
        elif parsed.scheme in ("http", "https") and requests is not None:
            resp = requests.get(data_file, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        else:
            # Try local paths: as given, app root, and static/data
            candidate_paths = []
            candidate_paths.append(data_file)
            candidate_paths.append(os.path.join(app.root_path, data_file))
            static_folder = app.static_folder or os.path.join(app.root_path, "static")
            candidate_paths.append(os.path.join(static_folder, "data", os.path.basename(data_file)))
            candidate_paths.append(os.path.join(app.root_path, "static", "data", os.path.basename(data_file)))
            for path in candidate_paths:
                if os.path.exists(path):
                    data = dashboard.load_sentiment_data(path)
                    break
    except Exception:
        # Fall back to empty dataset
        data = []

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


