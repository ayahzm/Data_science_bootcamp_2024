from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['AlMayadeen']
collection = db['articles']

# Define the new fields with default values
new_fields = {
    "sentiment": None,  # Can be updated with sentiment analysis results
    "entities": []      # Can be updated with extracted entities
}

# Update all documents by adding the new fields
result = collection.update_many({}, {"$set": new_fields})

print(f"Modified {result.modified_count} documents to include new fields.")
