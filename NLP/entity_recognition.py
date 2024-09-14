from pymongo import MongoClient, errors
import stanza
import time


# MongoDB connection
def connect_to_mongodb():
    print("Connecting to MongoDB...")
    while True:
        try:
            client = MongoClient('mongodb://localhost:27017/')  # Adjust connection string if necessary
            db = client['AlMayadeen']
            collection = db['articles']
            print("Connected to MongoDB.")
            return collection
        except errors.ConnectionFailure as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait 5 seconds before retrying


# Initialize MongoDB connection
collection = connect_to_mongodb()

# Initialize Stanza pipeline for Arabic NER
# print("Downloading Arabic model for Stanza (if not already downloaded)...")
# stanza.download('ar')  # Download the Arabic model
nlp = stanza.Pipeline(lang='ar', processors='tokenize,ner')
print("Stanza Arabic model and pipeline initialized.")


# Function to perform Named Entity Recognition on an article
def perform_entity_recognition(article):
    full_text = article.get('full_text', '')
    if not full_text:
        print(f"Article ID {article['_id']} has no text.")
        return []

    # Run the NER pipeline on the full text
    print(f"Performing NER on article ID {article['_id']}...")
    doc = nlp(full_text)

    # Extract entities and their types from the processed document
    entities = [{'text': ent.text, 'type': ent.type} for ent in doc.ents]

    return entities


# Process articles and update entities in MongoDB
def update_articles_with_entities(last_processed_id, collection):
    query = {'_id': {'$gt': last_processed_id}}  # Process articles with _id greater than last processed one
    total_articles = collection.count_documents(query)
    print(f"Found {total_articles} articles to process starting from ID > {last_processed_id}.")

    articles = collection.find(query)

    for idx, article in enumerate(articles, start=1):
        print(f"Processing article {idx}/{total_articles} (ID: {article['_id']})...")

        try:
            # Perform NER on the article content
            recognized_entities = perform_entity_recognition(article)

            # Update the article with recognized entities
            if recognized_entities:
                collection.update_one(
                    {'_id': article['_id']},
                    {'$set': {'entities': recognized_entities}}
                )
                print(f"Article ID {article['_id']} updated with entities.")
            else:
                print(f"No entities found for article ID {article['_id']}.")

            # Save progress to a file (optional)
            with open('../progress.txt', 'w') as f:
                f.write(str(article['_id']))

        except errors.ConnectionFailure:
            print(f"Connection lost while processing article {article['_id']}. Reconnecting...")
            collection = connect_to_mongodb()
            continue  # Retry the current article after reconnecting

    print("Entity recognition completed and all articles updated.")


# Set the last processed article _id (use the correct _id for article 2602)
last_processed_id = 'article8621'  # Replace with the actual _id you retrieved earlier

# Execute the function
update_articles_with_entities(last_processed_id, collection)
