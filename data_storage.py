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

# Starting an ID counter
article_id_counter = 1


for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Assign custom ID to each article
        if isinstance(data, list):
            for article in data:
                article['_id'] = f"article{article_id_counter}"
                article_id_counter += 1
            collection.insert_many(data)
        else:
            data['_id'] = f"article{article_id_counter}"
            article_id_counter += 1
            collection.insert_one(data)

print("Data inserted into MongoDB successfully.")