from flask import Flask, render_template, request, jsonify
import os
from src.scraper import NewsScraper
from src.analyzer import SentimentAnalyzer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize components
scraper = NewsScraper()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper()
        if not ticker:
            return render_template("index.html", error="Please enter a ticker symbol.")
        
        try:
            # check API key
            if not os.getenv("GEMINI_API_KEY"):
                return render_template("index.html", error="GEMINI_API_KEY not configured on server.")

            # 1. Fetch News
            headlines = scraper.fetch_news(ticker)
            if not headlines:
                return render_template("index.html", error=f"No news found for {ticker}.", ticker=ticker)

            # 2. Analyze
            try:
                analyzer = SentimentAnalyzer()
                analyzed_data = analyzer.analyze_headlines(headlines)
            except Exception as e:
                return render_template("index.html", error=f"Error initializing Analyzer: {str(e)}", ticker=ticker)
            
            # 3. Stats & Data Preparation
            if analyzed_data:
                sentiments = [h.get('sentiment', 0) for h in analyzed_data]
                avg_sentiment = sum(sentiments) / len(sentiments)
                positive = sum(1 for s in sentiments if s > 0)
                negative = sum(1 for s in sentiments if s < 0)
                neutral = sum(1 for s in sentiments if s == 0)
            else:
                sentiments = []
                avg_sentiment = 0
                positive = 0
                negative = 0
                neutral = 0
            
            stats = {
                "avg": avg_sentiment,
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            }
            
            # Extract just sentiments for the chart
            chart_data = sentiments

            return render_template("results.html", 
                                   ticker=ticker, 
                                   headlines=analyzed_data, 
                                   stats=stats,
                                   chart_data=chart_data)

        except Exception as e:
            return render_template("index.html", error=f"An error occurred: {str(e)}", ticker=ticker)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
