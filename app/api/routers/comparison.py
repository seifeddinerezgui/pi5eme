import json
from fastapi import APIRouter, HTTPException
import requests
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict
from pydantic import BaseModel
import finnhub

router = APIRouter()

class BestPeerResponse(BaseModel):
    best_peer: str
    sentiment_score: float
    interpretation: str

class CompareTickersResponse(BaseModel):
    better_ticker: str
    sentiment_score: float
    interpretation: str

# Load models
t5_model = T5ForConditionalGeneration.from_pretrained("t5-base")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-base")
sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)

# Initialize Finnhub client
FINNHUB_API_KEY = "cs5c8u9r01qo1hu1debgcs5c8u9r01qo1hu1dec0"
NEWS_API_KEY = "9529f5bef2b04ddcb3965ba5774a45a0"

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# JSON file paths
BEST_PEER_FILE = "best_peer.json"
COMPARE_TICKERS_FILE = "compare_tickers.json"

# Load JSON data helper function
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save JSON data helper function
def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Fetch peers
def fetch_peers(ticker: str) -> List[str]:
    try:
        return finnhub_client.company_peers(ticker)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching peers: {str(e)}")

# Fetch news articles for a ticker
def fetch_market_news(api_key: str, ticker: str) -> List[Dict]:
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles[:10]
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching market news.")

# Summarization function
def summary(input_news_article):
    news_input = t5_tokenizer.encode("summarize: " + input_news_article, return_tensors="pt", max_length=150, truncation=True)
    news_output = t5_model.generate(
        news_input, 
        max_length=150, 
        min_length=40, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True
    )
    news_summary = t5_tokenizer.decode(news_output[0], skip_special_tokens=True)
    return news_summary

# Sentiment analysis function
def sentiment_analysis(input_news_summary):
    inputs = sentiment_tokenizer(input_news_summary, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = sentiment_model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()
    confidence = torch.softmax(logits, dim=-1)
    return predicted_class, confidence[0][predicted_class].item()

# Generate interpretation based on sentiment score
def interpret_sentiment(score: float) -> str:
    if score >= 0.05:
        return "Positive sentiment detected. Consider buying or holding."
    elif score <= -0.05:
        return "Negative sentiment detected. Consider selling or avoiding."
    else:
        return "Neutral sentiment detected. Monitor the stock closely."

# Get the best peer sentiment
@router.get("/best-peer/{ticker}", response_model=BestPeerResponse)
def get_best_peer(ticker: str) -> Dict[str, float]:
    # Load existing data
    best_peer_data = load_json(BEST_PEER_FILE)
    
    # Check if data for the ticker already exists
    if ticker in best_peer_data:
        return best_peer_data[ticker]

    # Fetch and calculate data if not found
    peers = fetch_peers(ticker)
    market_data = {peer: fetch_market_news(NEWS_API_KEY, peer) for peer in peers}
    
    sentiment_scores = {}
    for peer in peers:
        descriptions = [article['description'] for article in market_data[peer] if article['description']]
        combined_text = " ".join(descriptions)
        if combined_text:
            news_summary = summary(combined_text)
            _, sentiment_confidence = sentiment_analysis(news_summary)
            sentiment_scores[peer] = sentiment_confidence

    best_peer = max(sentiment_scores, key=sentiment_scores.get)
    sentiment_score = sentiment_scores[best_peer]
    interpretation = interpret_sentiment(sentiment_score)
    
    # Store and return data
    best_peer_data[ticker] = {
        "best_peer": best_peer,
        "sentiment_score": sentiment_score,
        "interpretation": interpretation
    }
    save_json(BEST_PEER_FILE, best_peer_data)
    return best_peer_data[ticker]

# Compare two tickers' sentiment
@router.get("/compare-tickers/{ticker1}/{ticker2}", response_model=CompareTickersResponse)
def compare_tickers(ticker1: str, ticker2: str) -> Dict[str, float]:
    # Load existing data
    compare_data = load_json(COMPARE_TICKERS_FILE)

    # Check if comparison data already exists
    comparison_key = f"{ticker1}_{ticker2}"
    if comparison_key in compare_data:
        return compare_data[comparison_key]

    # Fetch and calculate data if not found
    market_data = {
        ticker1: fetch_market_news(NEWS_API_KEY, ticker1),
        ticker2: fetch_market_news(NEWS_API_KEY, ticker2)
    }
    
    sentiment_scores = {}
    for ticker in [ticker1, ticker2]:
        descriptions = [article['description'] for article in market_data[ticker] if article['description']]
        combined_text = " ".join(descriptions)
        if combined_text:
            news_summary = summary(combined_text)
            _, sentiment_confidence = sentiment_analysis(news_summary)
            sentiment_scores[ticker] = sentiment_confidence
        else:
            sentiment_scores[ticker] = 0

    better_ticker = max(sentiment_scores, key=sentiment_scores.get)
    sentiment_score = sentiment_scores[better_ticker]
    interpretation = interpret_sentiment(sentiment_score)

    # Store and return data
    compare_data[comparison_key] = {
        "better_ticker": better_ticker,
        "sentiment_score": sentiment_score,
        "interpretation": interpretation
    }
    save_json(COMPARE_TICKERS_FILE, compare_data)
    return compare_data[comparison_key]
