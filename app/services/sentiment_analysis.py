from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load T5 model for summarization
t5_model = T5ForConditionalGeneration.from_pretrained("t5-base")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-base")

# Load a pre-trained sentiment analysis model and tokenizer
sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"  # You can choose any sentiment analysis model
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)

def summary(input_news_article):
    news_input = t5_tokenizer.encode("summarize: " + input_news_article, return_tensors="pt", max_length=150, truncation=True)
    
    # Generate the summarization output
    news_output = t5_model.generate(
        news_input, 
        max_length=150, 
        min_length=40, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True
    )
    
    # Decode the summary
    news_summary = t5_tokenizer.decode(news_output[0], skip_special_tokens=True)
    print(f"Episode Summary: {news_summary}")
    
    return news_summary

def sentiment_analysis(input_news_summary):
    inputs = sentiment_tokenizer(input_news_summary, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():  # Disable gradient calculation for inference
        outputs = sentiment_model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()  # Get the predicted class index
    confidence = torch.softmax(logits, dim=-1)  # Convert logits to probabilities
    return predicted_class, confidence[0][predicted_class].item()  # Return class and confidence score

# Test negative news
negative_news = ("U.S. stocks declined Monday following global equities lower, as concerns over an escalating COVID outbreak in China "
                 "added to jitters over U.S. economic growth in the face of heightened inflation and monetary policy tightening. "
                 "The S&P 500 fell by nearly 1% just after the opening bell as the index looked to add to last week's losses. "
                 "The Dow and Nasdaq each also dropped. U.S. Treasury yields dipped, and the benchmark 10-year yield hovered just "
                 "above 2.8%. West Texas intermediate crude oil futures fell more than 4% to trade below $98 per barrel, with fears "
                 "over the economic impact of broadening virus-related restrictions throughout China mounting. Beijing saw a spike "
                 "in COVID cases over the weekend that prompted more mandatory testing and some lockdowns in the region. And this "
                 "came as other populous cities including Shanghai have also recently grappled with fresh waves of infections, even "
                 "as the country works to abolish the virus under a zero-COVID policy.")
sum_news = summary(negative_news)
sentiment_label, sentiment_confidence = sentiment_analysis(sum_news)
print(f'Sentiment Analysis for stock news is: {sentiment_label}, Confidence: {sentiment_confidence}')

# Test positive news
positive_news = ("Tesla stock jumped 3.2% after the electric-vehicle maker earned 18.8 billion in sales in the first quarter "
                 "of the year. The record results firmly outpaced Wall Street’s expectations of EPS in the range of 2.30.")
sum_news = summary(positive_news)
sentiment_label, sentiment_confidence = sentiment_analysis(sum_news)
print(f'Sentiment Analysis for stock news is: {sentiment_label}, Confidence: {sentiment_confidence}')

# Example of sentiment analysis on a list of sentences
test_sentences = ["We are very happy to show you the 🤗 Transformers library.",
                  "We hope you don't hate it."]

for sentence in test_sentences:
    sentiment_label, sentiment_confidence = sentiment_analysis(sentence)
    print(f"Sentence: '{sentence}' - Label: {sentiment_label}, Confidence: {sentiment_confidence:.4f}")
