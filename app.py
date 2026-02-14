from flask import Flask, render_template, request, jsonify
import os
from src.scraper import NewsScraper
from src.analyzer import SentimentAnalyzer
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize components
scraper = NewsScraper()

# Helper to generate plot as base64 string
def generate_plot(df, ticker):
    if df.empty:
        return None
    
    avg_sentiment = df['sentiment'].mean()
    plt.figure(figsize=(10, 6))
    plt.hist(df['sentiment'], bins=20, color='skyblue', edgecolor='black')
    plt.title(f"Sentiment Distribution for {ticker}")
    plt.xlabel("Sentiment Score (-1 to +1)")
    plt.ylabel("Frequency")
    plt.axvline(avg_sentiment, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {avg_sentiment:.2f}')
    plt.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

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
            
            # 3. Process Data
            df = pd.DataFrame(analyzed_data)
            
            # 4. Generate Plot
            plot_url = generate_plot(df, ticker)
            
            # 5. Stats
            stats = {
                "avg": df['sentiment'].mean(),
                "positive": len(df[df['sentiment'] > 0]),
                "negative": len(df[df['sentiment'] < 0]),
                "neutral": len(df[df['sentiment'] == 0])
            }
            
            return render_template("results.html", 
                                   ticker=ticker, 
                                   headlines=analyzed_data, 
                                   plot_url=plot_url, 
                                   stats=stats)

        except Exception as e:
            return render_template("index.html", error=f"An error occurred: {str(e)}", ticker=ticker)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
