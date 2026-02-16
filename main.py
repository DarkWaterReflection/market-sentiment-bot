import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.scraper import NewsScraper
from src.analyzer import SentimentAnalyzer
from src.reporter import Reporter
import os
from dotenv import load_dotenv

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Market Sentiment Bot")
    parser.add_argument("ticker", help="Stock ticker to analyze (e.g., AAPL)")
    args = parser.parse_args()
    ticker = args.ticker.upper()

    console.print(f"[bold blue]Starting Market Sentiment Analysis for {ticker}[/bold blue]")

    # 1. Setup & Check API Key
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        console.print("[bold red]Error: GEMINI_API_KEY not found in .env file.[/bold red]")
        console.print("Please get an API key from https://aistudio.google.com/ and add it to the .env file.")
        sys.exit(1)

    scraper = NewsScraper()
    # Initialize analyzer (might fail if key is invalid, so we wrap it)
    try:
        analyzer = SentimentAnalyzer()
    except Exception as e:
        console.print(f"[bold red]Error initializing Analyzer: {e}[/bold red]")
        sys.exit(1)
        
    reporter = Reporter()

    # 2. Fetch News
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task1 = progress.add_task(description=f"Fetching news for {ticker}...", total=None)
        headlines = scraper.fetch_news(ticker)
        
    if not headlines:
        console.print(f"[bold red]No news found for {ticker}.[/bold red]")
        sys.exit(0)
    
    console.print(f"[green]Found {len(headlines)} headlines.[/green]")

    # 3. Analyze Sentiment
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task2 = progress.add_task(description="Analyzing sentiment with Gemini...", total=None)
        analyzed_data = analyzer.analyze_headlines(headlines)

    # 4. Report
    # save_to_csv now returns (filename, data_list) instead of (filename, df)
    csv_file, _ = reporter.save_to_csv(analyzed_data, ticker)
    reporter.generate_report(analyzed_data, ticker)

    # 5. Show Summary Table
    table = Table(title=f"Latest News & Sentiment for {ticker}")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Headline")
    table.add_column("Score", justify="right")
    table.add_column("Reasoning", style="italic")

    for item in analyzed_data[:5]: # Show top 5
        score_color = "green" if item['sentiment'] > 0 else "red" if item['sentiment'] < 0 else "yellow"
        table.add_row(
            item.get('published', '')[:16], # Truncate date
            item['title'],
            f"[{score_color}]{item['sentiment']:.2f}[/{score_color}]",
            item['reasoning'][:50] + "..."
        )

    console.print(table)
    if csv_file:
        console.print(f"\n[bold]Full report saved to:[/bold] {csv_file}")

if __name__ == "__main__":
    main()
