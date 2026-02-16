import csv
import os
from datetime import datetime

class Reporter:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def save_to_csv(self, headlines, ticker):
        """Saves the analyzed headlines to a CSV file."""
        if not headlines:
            print("No data to save.")
            return None, None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"{ticker}_sentiment_{timestamp}.csv")
        
        try:
            keys = headlines[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(headlines)
            
            print(f"Data saved to {filename}")
            return filename, headlines
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return None, None

    def generate_report(self, data, ticker):
        """Generates a summary report (text only)."""
        if not data:
            return

        sentiments = [h.get('sentiment', 0) for h in data]
        if not sentiments:
            return

        avg_sentiment = sum(sentiments) / len(sentiments)
        positive = sum(1 for s in sentiments if s > 0)
        negative = sum(1 for s in sentiments if s < 0)
        neutral = sum(1 for s in sentiments if s == 0)

        print(f"\n--- Sentiment Report for {ticker} ---")
        print(f"Average Sentiment: {avg_sentiment:.2f}")
        print(f"Positive: {positive}")
        print(f"Negative: {negative}")
        print(f"Neutral: {neutral}")
        print("-------------------------------------")

if __name__ == "__main__":
    # Test execution
    data = [
        {'title': 'Good news', 'sentiment': 0.8},
        {'title': 'Bad news', 'sentiment': -0.6},
        {'title': 'Okay news', 'sentiment': 0.1}
    ]
    reporter = Reporter()
    f, df = reporter.save_to_csv(data, "TEST")
    reporter.generate_report(df, "TEST")
