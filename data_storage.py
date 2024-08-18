import pymongo
import json
import os

# List of JSON file paths
json_files = [
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_03.json",
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_04.json",
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_05.json",
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_06.json",
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_07.json",
    r"D:\data science bootcamp '24\Data_science_bootcamp_Aya_Hazimeh\output\articles_2024_08.json"
]

# Function to generate custom _id
def generate_custom_id(prefix, index):
    return f"{prefix}{index + 1}"

#connecting to MongoDb
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["AlMayadeen"]
collection = db["articles"]

# Iterate over each file path
for file_path in json_files:
    # Extracting year and month from the file name
    base_name = os.path.basename(file_path)  # Get the file name
    collection_name = os.path.splitext(base_name)[0]  # Remove the extension to get collection name

    # Select the collection based on year and month
    collection = db[collection_name]

    # Open and load the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Check if the data is a list of articles
        if isinstance(data, list):
            for i, article in enumerate(data):
                # Assign a custom _id
                article['_id'] = generate_custom_id('article', i)
            collection.insert_many(data)
        else:
            # If it's a single article, assign a custom _id
            data['_id'] = generate_custom_id('article', 0)
            collection.insert_one(data)

    print(f"Data from {file_path} inserted into collection {collection_name} with custom IDs.")

print("All data inserted into MongoDB with custom IDs successfully.")