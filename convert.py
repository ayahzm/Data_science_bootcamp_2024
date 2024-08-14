import json
import os


json_file = r"D:\data science bootcamp '24\pythonProject\output\2024_08.json"


print(f"Looking for the file at: {json_file}")

# Checking if the file exists
if os.path.exists(json_file):
    print("File found, loading...")
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("File loaded successfully.")


        print("Data before modification:", data)

        # list of JSON objects
        if isinstance(data, list):
            for item in data:
                if 'keywords' in item and isinstance(item['keywords'], str):
                    # Converting the comma-separated string into a list
                    item['keywords'] = [keyword.strip() for keyword in item['keywords'].split(',')]
                    print("Keywords after modification:", item['keywords'])  # Debugging line

        # Saving the modified data back to the file
        with open(json_file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
            print("File updated successfully.")
else:
    print(f"File not found: {json_file}")
