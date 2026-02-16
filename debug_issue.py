import os
from dotenv import load_dotenv
from src.scraper import NewsScraper
from src.analyzer import SentimentAnalyzer

# Load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key start: {api_key[:4]}...")

def debug_pipeline(ticker):
    print(f"\n--- Debugging for {ticker} ---")
    
    # 1. Test Scraper
    print("1. Testing Scraper...")
    scraper = NewsScraper()
    headlines = scraper.fetch_news(ticker)
    
    if not headlines:
        print("ERROR: No headlines found. Scraper might be blocked or broken.")
        return
    
    print(f"SUCCESS: Found {len(headlines)} headlines.")
    print(f"Sample: {headlines[0]}")
    
    # 2. Test Analyzer
    print("\n2. Testing Analyzer...")
    try:
        analyzer = SentimentAnalyzer()
        results = analyzer.analyze_headlines(headlines[:3]) # Test only 3
        
        for i, res in enumerate(results):
            print(f"Result {i+1}: {res.get('sentiment')} - {res.get('reasoning')}")
            
    except Exception as e:
        print(f"ERROR in Analyzer: {e}")

if __name__ == "__main__":
    debug_pipeline("AAPL")
