from flask import Flask, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# Connecting to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['AlMayadeen']
collection = db['articles']

# Route for Top Keywords
@app.route('/top_keywords', methods=['GET'])
def top_keywords():
    pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "keyword": "$_id", "occurrences": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Top Authors
@app.route('/top_authors', methods=['GET'])
def top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "author": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Date
@app.route('/articles_by_date', methods=['GET'])
def articles_by_date():
    pipeline = [
        {
            "$project": {
                "publication_date_only": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",  # Format to extract date part only
                        "date": {
                            "$dateFromString": {
                                "dateString": "$publication_date"  # Convert string to date
                            }
                        }
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$publication_date_only",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}},  # Sort by date
        {"$project": {"_id": 0, "date": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Word Count
@app.route('/articles_by_word_count', methods=['GET'])
def articles_by_word_count():
    pipeline = [
        {"$group": {"_id": "$word_count", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "word_count": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Language
@app.route('/articles_by_language', methods=['GET'])
def articles_by_language():
    pipeline = [
        {"$group": {"_id": "$lang", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "lang": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Category
@app.route('/articles_by_classes', methods=['GET'])
def articles_by_classes():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.key": "class2"}},  # Filter to include only class2 entries
        {"$group": {
            "_id": "$classes.value",  # Group by the value of class2
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},  # Sort by the count in descending order
        {"$project": {
            "_id": 0,
            "category": "$_id",
            "articles_count": "$count"
        }}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


# Route for Recent Articles
@app.route('/recent_articles', methods=['GET'])
def recent_articles():
    pipeline = [
        {"$sort": {"publication_date": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Keyword
@app.route('/articles_by_keyword/<keyword>', methods=['GET'])
def articles_by_keyword(keyword):
    query = {"keywords": keyword}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify(result)

# Route for Articles by Author
@app.route('/articles_by_author/<author_name>', methods=['GET'])
def articles_by_author(author_name):
    query = {"author": author_name}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify(result)

# Route for Top Classes
@app.route('/top_classes', methods=['GET'])
def top_classes():
    pipeline = [
        {"$unwind": "$classes"},  # Deconstruct the classes array
        {"$match": {"classes.key": "class2"}},  # Filter to include only class2 entries
        {"$group": {
            "_id": "$classes.value",  # Group by the value of class2
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},  # Sort by count in descending order
        {"$limit": 10},  # Limit the results to the top 10
        {"$project": {
            "_id": 0,
            "category": "$_id",  # Rename _id to category
            "articles_count": "$count"  # Include the count of articles
        }}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


# Route for Article Details
@app.route('/article_details/<post_id>', methods=['GET'])
def article_details(post_id):
    # Define the query to match the article by its postid
    query = {"post_id": post_id}

    # Define the fields to include in the response
    projection = {
        "_id": 0,  # Exclude the MongoDB internal _id field
        "url": 1,  # Include the article URL
        "title": 1,  # Include the article title
        "keywords": 1,  # Include the article keywords
        "publication_date": 1,  # Include the publication date
        "content": 1  # Include the article content (assuming you need this as well)
    }

    # Find the article document that matches the query
    result = collection.find_one(query, projection)

    # If no article is found, return a 404 error with a message
    if result is None:
        return jsonify({"error": "Article not found"}), 404

    return jsonify(result)


# Route for Articles Containing Video
@app.route('/articles_with_video', methods=['GET'])
def articles_with_video():
    query = {"video_duration": {"$ne": None}}
    projection = {"_id": 0, "title": 1, "url":1}
    result = list(collection.find(query, projection))
    return jsonify(result)

# Route for Articles by Publication Year
@app.route('/articles_by_year/<year>', methods=['GET'])
def articles_by_year(year):
    pipeline = [
        {"$match": {"publication_date": {"$regex": f"^{year}"}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "year": year, "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Longest Articles
@app.route('/longest_articles', methods=['GET'])
def longest_articles():
    pipeline = [
        {"$sort": {"word_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1, "word_count": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Shortest Articles
@app.route('/shortest_articles', methods=['GET'])
def shortest_articles():
    pipeline = [
        {"$sort": {"word_count": 1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1, "word_count": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Keyword Count
@app.route('/articles_by_keyword_count', methods=['GET'])
def articles_by_keyword_count():
    pipeline = [
        {"$project": {"keyword_count": {"$size": "$keywords"}, "title": 1}},
        {"$group": {"_id": "$keyword_count", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "keyword_count": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles with Thumbnail
@app.route('/articles_with_thumbnail', methods=['GET'])
def articles_with_thumbnail():
    query = {"thumbnail": {"$ne": None}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify(result)

# Route for Articles Updated After Publication
@app.route('/articles_updated_after_publication', methods=['GET'])
def articles_updated_after_publication():
    query = {"$expr": {"$gt": ["last_updated_date", "$publication_date"]}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify(result)

# Route for Articles by Coverage
@app.route('/articles_by_coverage/<coverage>', methods=['GET'])
def articles_by_coverage(coverage):
    # Define the query to match articles where class5's value equals the given coverage
    query = {"classes": {"$elemMatch": {"key": "class5", "value": coverage}}}

    # Define the fields to include in the response
    projection = {"_id": 0, "title": 1}

    # Find the articles that match the query
    result = list(collection.find(query, projection))

    return jsonify(result)


# Route for Popular Keywords in the Last X Days
@app.route('/popular_keywords_last_X_days/<int:days>', methods=['GET'])
def popular_keywords_last_X_days(days):
    # Calculate the start date for the query
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Format the dates to ISO 8601 format
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    pipeline = [
        {"$match": {"publication_date": {"$gte": start_date_str, "$lte": end_date_str}}},
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "keyword": "$_id", "occurrences": "$count"}}
    ]

    result = list(collection.aggregate(pipeline))
    return jsonify(result)

# Route for Articles by Published Month
@app.route('/articles_by_month/<int:year>/<int:month>', methods=['GET'])
def articles_by_month(year, month):
    # Calculate the start and end dates for the given year and month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)  # Next year's January 1st
    else:
        end_date = datetime(year, month + 1, 1)  # Next month's 1st

    # Format dates to ISO 8601 strings
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    pipeline = [
        {"$match": {"publication_date": {"$gte": start_date_str, "$lt": end_date_str}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "year": year, "month": month, "articles_count": "$count"}}
    ]

    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#Articles by Word Count Range
@app.route('/articles_by_word_count_range/<int:min>/<int:max>', methods=['GET'])
def articles_by_word_count_range(min, max):
    pipeline = [
        {"$match": {"word_count": {"$gte": min, "$lte": max}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "word_count_range": f"{min} to {max}", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#Articles with Specific Keyword Count
@app.route('/articles_with_specific_keyword_count/<int:count>', methods=['GET'])
def articles_with_specific_keyword_count(count):
    pipeline = [
        {"$match": {"$expr": {"$eq": [{"$size": "$keywords"}, count]}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "keyword_count": count, "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#Articles by Specific Date
@app.route('/articles_by_specific_date/<date>', methods=['GET'])
def articles_by_specific_date(date):
    query = {"publication_date": {"$regex": f"^{date}"}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"date": date, "articles": result})

#Articles Containing Specific Text
@app.route('/articles_containing_text/<text>', methods=['GET'])
def articles_containing_text(text):
    # Create a regex pattern for case-insensitive search
    regex_pattern = re.compile(text, re.IGNORECASE)

    # Query for articles containing the specified text in 'full_text' field
    query = {"full_text": {"$regex": regex_pattern}}

    # Specify the fields to return in the response
    projection = {
        "_id": 0,
        "title": 1
    }

    # Fetch the results from MongoDB
    result = list(collection.find(query, projection))

    # Return the response in the desired format
    return jsonify({"text": text, "articles": result})

#Articles with More than N Words
@app.route('/articles_with_more_than/<int:word_count>', methods=['GET'])
def articles_with_more_than(word_count):
    query = {"word_count": {"$gt": word_count}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"more_than": word_count, "articles": result})

#Articles Grouped by Coverage
@app.route('/articles_grouped_by_coverage', methods=['GET'])
def articles_grouped_by_coverage():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.key": "class5"}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "coverage": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#Articles Published in Last X Hours
@app.route('/articles_last_X_hours/<int:hours>', methods=['GET'])
def articles_last_X_hours(hours):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    # Define the aggregation pipeline
    pipeline = [
        # Match articles published within the last X hours
        {"$match": {"publication_date": {"$gte": start_time.isoformat(), "$lt": end_time.isoformat()}}},
        # Project fields to include in the results
        {"$project": {"_id": 0, "title": 1}},
        # Optionally sort by publication_date if you want the most recent articles first
        {"$sort": {"publication_date": -1}},
        # Collect the results
    ]

    # Execute the aggregation pipeline
    result = list(collection.aggregate(pipeline))

    # Return the response with article titles
    return jsonify({"last_hours": hours, "articles": result})

#Articles by Length of Title
@app.route('/articles_by_title_length', methods=['GET'])
def articles_by_title_length():
    pipeline = [
        {"$project": {"title_length": {"$strLenCP": "$title"}}},
        {"$group": {"_id": "$title_length", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "title_length": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#Most Updated Articles (Needs update on the google doc)

if __name__ == '__main__':
    app.run(debug=True)
