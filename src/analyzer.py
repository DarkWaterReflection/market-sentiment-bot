import os
import google.generativeai as genai
from dotenv import load_dotenv

class SentimentAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_headlines(self, headlines):
        """
        Analyzes a list of headlines and returns a sentiment score for each.
        
        Args:
            headlines (list): List of dictionaries with 'title' key.
            
        Returns:
            list: The input list with an added 'sentiment' (float) and 'reasoning' (str) key.
        """
        if not headlines:
            return []

        print(f"Analyzing {len(headlines)} headlines...")
        
        # Prepare the prompt
        titles = [h['title'] for h in headlines]
        prompt = f"""
        Analyze the sentiment of the following financial news headlines. 
        For each headline, provide a sentiment score between -1.0 (very negative) and 1.0 (very positive).
        Also provide a very brief reasoning (max 1 sentence).
        
        Headlines:
        {titles}
        
        Return the result as a JSON list of objects, where each object has:
        - "sentiment": float
        - "reasoning": string
        
        Do not allow any markdown code blocks in the response. Just the raw JSON.
        Review the safety settings and do not block the response unless absolutely necessary.
        """

        try:
            response = self.model.generate_content(prompt)
            # Basic cleaning if the model includes markdown blocks despite instructions
            text = response.text.replace('```json', '').replace('```', '').strip()
            
            import json
            results = json.loads(text)
            
            # Merge results back into headlines
            analyzed_headlines = []
            for i, headline in enumerate(headlines):
                if i < len(results):
                    headline['sentiment'] = results[i].get('sentiment', 0.0)
                    headline['reasoning'] = results[i].get('reasoning', 'No reasoning provided')
                    analyzed_headlines.append(headline)
            
            return analyzed_headlines
            
        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            # Fallback: add 0.0 sentiment but include error in reasoning
            error_msg = str(e)
            if "429" in error_msg:
                reasoning = "Error: API Quota Exceeded (Try again later)"
            elif "404" in error_msg:
                 reasoning = "Error: Model not found (Check API key/Region)"
            else:
                reasoning = f"Error: {error_msg[:50]}..."
                
            for h in headlines:
                h['sentiment'] = 0.0
                h['reasoning'] = reasoning
            return headlines

if __name__ == "__main__":
    # Test execution
    try:
        analyzer = SentimentAnalyzer()
        test_data = [{'title': 'Stock market crashes as uncertainty rises'}, {'title': 'Company reports record profits'}]
        results = analyzer.analyze_headlines(test_data)
        for r in results:
            print(f"{r['title']} -> {r['sentiment']} ({r['reasoning']})")
    except Exception as e:
        print(e)
