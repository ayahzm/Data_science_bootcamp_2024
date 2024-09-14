from pymongo import MongoClient
import nltk
from nltk.tokenize import word_tokenize
import arabic_reshaper
from bidi.algorithm import get_display

# Download the punkt tokenizer if not already downloaded
nltk.download('punkt')

# Example Arabic sentiment lexicon (you can expand these lists with more words)
positive_words = ['سعيد', 'ممتاز', 'رائع', 'جميل', 'مبهج']
negative_words = ['حزين', 'سيء', 'كئيب', 'محبط', 'مزعج']

def analyze_sentiment_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)  # Fix Arabic display issues
    bidi_text = get_display(reshaped_text)  # Correct right-to-left text display

    tokens = word_tokenize(bidi_text)

    positive_score = sum(1 for word in tokens if word in positive_words)
    negative_score = sum(1 for word in tokens if word in negative_words)

    if positive_score > negative_score:
        return "positive"
    elif negative_score > positive_score:
        return "negative"
    else:
        return "neutral"

# MongoDB connection details
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['AlMayadeen']
collection = db['articles']

def store_article_with_sentiment(text):
    sentiment = analyze_sentiment_arabic(text)
    article = {
        'text': text,
        'sentiment': sentiment
    }
    print(f"Inserting article with sentiment: {sentiment}")
    # Insert the article into MongoDB
    collection.insert_one(article)
    print(f"Inserted: {article}")


# Example usage
if __name__ == "__main__":
    # Example Arabic text
    text = "أنا سعيد جدا اليوم، الجو رائع!"
    store_article_with_sentiment(text)
    print("Article stored with sentiment.")
