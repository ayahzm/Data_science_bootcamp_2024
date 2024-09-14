from flask import Flask, jsonify,render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
import re

app = Flask(__name__)

# Connecting to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['AlMayadeen']
collection = db['articles']

# Helper function to query articles by sentiment
def get_articles_by_sentiment(sentiment):
    articles = collection.find({"sentiment": sentiment})
    return list(articles)  # Convert cursor to list

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

@app.route('/')
def about():
    return render_template('base_template.html')

@app.route('/topkeywords')
def wordcloud():
    return render_template('top_keywords.html')

# Route for Top Authors --> bar chart
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
@app.route('/topauthors')
def topauthors():
    return render_template('top_authors.html')
# Route for Articles by Date --> line chart
# Route for Articles by Date --> line chart
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

@app.route('/articlesbydate')
def articlesbydate():
    return render_template('articles_by_date.html')

# Route for Articles by Word Count --> histogram
@app.route('/articles_by_word_count', methods=['GET'])
def articles_by_word_count():
    pipeline = [
        {"$group": {"_id": "$word_count", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "word_count": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articlesbywordcount')
def articlesbywordcount():
    return render_template('articles_by_word_count.html')

# Route for Articles by Language --> pie chart
@app.route('/articles_by_language', methods=['GET'])
def articles_by_language():
    pipeline = [
        {"$group": {"_id": "$lang", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "lang": "$_id", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articlesbylanguage')
def articlesbylanguage():
    return render_template('articles_by_language.html')

# Route for Articles by Category --> Stacked Bar Chart
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
@app.route('/articlesbyclasses')
def articlesbyclasses():
    return render_template('articles_by_classes.html')

# Route for Recent Articles --> Table
@app.route('/recent_articles', methods=['GET'])
def recent_articles():
    pipeline = [
        {"$sort": {"publication_date": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1, "author":1,"publication_date":1, "word_count":1, "description":1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)
@app.route('/recentarticles')
def recentarticles():
    return render_template('recent_articles.html')

# Route for Articles by Keyword --> Tag Cloud
@app.route('/articles_by_keyword/<keyword>', methods=['GET'])
def articles_by_keyword(keyword):
    query = {"keywords": keyword}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify(result)

@app.route('/articlesbykeyword')
def articlesbykeyword():
    return render_template('articles_by_keyword.html')

# Route for Articles by Author --> Bar Chart
@app.route('/articles_by_author/<author_name>', methods=['GET'])
def articles_by_author(author_name):
    query = {"author": author_name}
    projection = {"_id": 0, "title": 1}

    # Find articles by the specific author
    articles = list(collection.find(query, projection))

    # Count the number of articles by the author
    count = len(articles)

    # Create the response object
    response = {
        "count": count,
        "articles": articles
    }

    return jsonify(response)
@app.route('/articlesbyauthor')
def articlesbyauthor():
    return render_template('articles_by_author.html')

# Route for Top Classes --> Pie Chart
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

@app.route('/topclasses')
def topclasses():
    return render_template('top_classes.html')

# Route for Article Details --> Table
@app.route('/article_details/<post_id>', methods=['GET'])
def article_details(post_id):
    # Define the query to match the article by its postid
    query = {"post_id": post_id}

    # Define the fields to include in the response
    projection = {
        "_id": 0,
        "author":1,  # Exclude the MongoDB internal _id field
        "title": 1,
        "word_count":1,
        "keywords": 1,  # Include the article keywords
        "publication_date": 1,  # Include the publication date
        "content": 1,
        "url": 1  # Include the article content (assuming you need this as well)
    }

    # Find the article document that matches the query
    result = collection.find_one(query, projection)

    # If no article is found, return a 404 error with a message
    if result is None:
        return jsonify({"error": "Article not found"}), 404

    return jsonify(result)
@app.route('/articledetails')
def articledetails():
    return render_template('article_details.html')

# Route for Articles Containing Video --> Bar Chart
@app.route('/articles_with_video', methods=['GET'])
def articles_with_video():
    query = {"video_duration": {"$ne": None}}
    projection = {"_id": 0, "title": 1, "url":1}
    result = list(collection.find(query, projection))
    return jsonify(result)
@app.route('/articleswithvideo')
def articleswithvideo():
    return render_template('articles_with_video.html')

# Route for Articles by Publication Year --> Bar Chart
@app.route('/articles_by_year/<year>', methods=['GET'])
def articles_by_year(year):
    pipeline = [
        {"$match": {"publication_date": {"$regex": f"^{year}"}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "year": year, "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    # Ensure at least one result for the bar chart
    if not result:
        result = [{"year": year, "articles_count": 0}]
    return jsonify(result)
@app.route('/articlesbyyear')
def articlesbyyear():
    return render_template('articles_by_year.html')

# Route for Longest Articles --> Bar Chart
@app.route('/longest_articles', methods=['GET'])
def longest_articles():
    pipeline = [
        {"$sort": {"word_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1, "word_count": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)
@app.route('/longestarticles')
def longestarticles():
    return render_template('longest_articles.html')

# Route for Shortest Articles --> Bar Chart
@app.route('/shortest_articles', methods=['GET'])
def shortest_articles():
    pipeline = [
        {"$sort": {"word_count": 1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "title": 1, "word_count": 1}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)
@app.route('/shortestarticles')
def shortestarticles():
    return render_template('shortest_articles.html')


# Route for Articles by Keyword Count --> Histogram
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
@app.route('/articlesbykeywordcount')
def articlesbykeywordcount():
    return render_template('articles_by_keyword_count.html')

# Route for Articles with Thumbnail --> Pie Chart
@app.route('/articles_with_thumbnail', methods=['GET'])
def articles_with_thumbnail():
    query = {"thumbnail": {"$ne": None}}
    article_count = collection.count_documents(query)
    return jsonify({"count": article_count})
@app.route('/articleswiththumbnail')
def articleswiththumbnail():
    return render_template('articles_with_thumbnail.html')

# Route for Articles Updated After Publication --> Bar Chart
@app.route('/articles_updated_after_publication', methods=['GET'])
def articles_updated_after_publication():
    query = {"$expr": {"$gt": ["$last_updated_date", "$publication_date"]}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))

    count = len(result)  # Get the count of articles
    response_data = {
        "titles": [article["title"] for article in result],  # Keep titles
        "count": count  # Add count to response
    }

    return jsonify(response_data)
@app.route('/articlesupdatedafterpublication')
def articlesupdatedafterpublication():
    return render_template('articles_updated_after_publication.html')

# Route for Articles by Coverage -->  Stacked Bar Chart
@app.route('/articles_by_coverage/<coverage>', methods=['GET'])
def articles_by_coverage(coverage):
    # Define the query to match articles where class5's value equals the given coverage
    query = {"classes": {"$elemMatch": {"key": "class5", "value": coverage}}}

    # Define the fields to include in the response
    projection = {"_id": 0, "title": 1}

    # Find the articles that match the query
    result = list(collection.find(query, projection))

    # Get the count of articles
    count = len(result)

    # Return the titles and the count
    response_data = {
        "titles": [article["title"] for article in result],
        "count": count,
        "coverage": coverage  # Include coverage name for the chart
    }

    return jsonify(response_data)
@app.route('/articlesbycoverage')
def articlesbycoverage():
    return render_template('articles_by_coverage.html')


# Route for Popular Keywords in the Last X Days -->  Line Chart
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
@app.route('/popularkeywordslastXdays')
def popularkeywordslastXdays():
    return render_template('popular_keywords_last_X_days.html')

# Route for Articles by Published Month --> Column Chart
@app.route('/articles_by_month/<int:year>/<int:month>', methods=['GET'])
def articles_by_month(year, month):
    # Convert the month to a two-digit format (e.g., "01" for January)
    month_str = f"{month:02d}"

    # Create a regular expression to match the publication_date
    date_regex = f"^{year}-{month_str}"

    pipeline = [
        {"$match": {"publication_date": {"$regex": date_regex}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {
            "$project": {
                "_id": 0,
                "year": year,
                "month": month,
                "articles_count": "$count"
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    # Ensure the result includes both year and month
    if not result:
        result = [{"year": year, "month": month, "articles_count": 0}]

    return jsonify(result)

@app.route('/articlesbymonth')
def articlesbymonth():
    return render_template('articles_by_month.html')
#Articles by Word Count Range --> Histogram
@app.route('/articles_by_word_count_range/<int:min>/<int:max>', methods=['GET'])
def articles_by_word_count_range(min, max):
    pipeline = [
        {"$match": {"word_count": {"$gte": min, "$lte": max}}},
        {"$group": {"_id": None, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "word_count_range": f"{min} to {max}", "articles_count": "$count"}}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articlesbywordcountrange')
def articlesbywordcountrange():
    return render_template('articles_by_word_count_range.html')

#Articles with Specific Keyword Count -->  Pie Chart
@app.route('/articles_with_specific_keyword_count/<int:count>', methods=['GET'])
def articles_with_specific_keyword_count(count):
    pipeline = [
        {"$match": {"$expr": {"$eq": [{"$size": "$keywords"}, count]}}},
        {"$group": {
            "_id": None,  # Group all matching documents together
            "articles_count": {"$sum": 1}  # Count the number of articles
        }},
        {"$project": {
            "_id": 0,  # Exclude _id
            "keyword_count": {"$literal": count},  # Use $literal to set the keyword count
            "articles_count": 1  # Include the articles count
        }}
    ]

    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articleswithspecifickeywordcount')
def articleswithspecifickeywordcount():
    return render_template('articles_with_specific_keyword_count.html')

#Articles by Specific Date --> Line Chart
@app.route('/articles_by_specific_date/<date>', methods=['GET'])
def articles_by_specific_date(date):
    query = {"publication_date": {"$regex": f"^{date}"}}
    projection = {"_id": 0, "title": 1, "publication_date":1}
    result = list(collection.find(query, projection))
    return jsonify({"date": date, "articles": result})

@app.route('/articlesbyspecificdate')
def articlesbyspecificdate():
    return render_template('articles_by_specific_date.html')

#Articles Containing Specific Text -->  Bar Chart
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
@app.route('/articlescontainingtext')
def articlescontainingtext():
    return render_template('articles_containing_text.html')

#Articles with More than N Words --> Bar Chart
@app.route('/articles_with_more_than/<int:word_count>', methods=['GET'])
def articles_with_more_than(word_count):
    query = {"word_count": {"$gt": word_count}}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))

    # Count the number of articles
    article_count = len(result)

    # Return the response with the count and articles
    return jsonify({"more_than": word_count, "article_count": article_count, "articles": result})

@app.route('/articleswithmorethan')
def articleswithmorethan():
    return render_template('articles_with_more_than.html')

#Articles Grouped by Coverage --> stacked Bar Chart
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

@app.route('/articlesgroupedbycoverage')
def articlesgroupedbycoverage():
    return render_template('articles_grouped_by_coverage.html')

#Articles Published in Last X Hours --> Bar Chart
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

@app.route('/articleslastXhours')
def articleslastXhours():
    return render_template('articles_last_X_hours.html')

#Articles by Length of Title --> Histogram
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

@app.route('/articlesbytitlelength')
def articlesbytitlelength():
    return render_template('articles_by_title_length.html')

# Route for Articles by Sentiment (Positive) --> Pie Chart
@app.route('/articles_by_sentiment/positive', methods=['GET'])
def articles_by_sentiment_positive():
    result = get_articles_by_sentiment("positive")
    return jsonify(result)

# Route for Articles by Sentiment (Neutral) --> Pie Chart
@app.route('/articles_by_sentiment/neutral', methods=['GET'])
def articles_by_sentiment_neutral():
    result = get_articles_by_sentiment("neutral")
    return jsonify(result)

# Route for Articles by Sentiment (Negative) --> Pie Chart
@app.route('/articles_by_sentiment/negative', methods=['GET'])
def articles_by_sentiment_negative():
    result = get_articles_by_sentiment("negative")
    return jsonify(result)

# Route for Articles by Sentiment (Mixed) --> Pie Chart
@app.route('/articles_by_sentiment/mixed', methods=['GET'])
def articles_by_sentiment_mixed():
    result = get_articles_by_sentiment("mixed")
    return jsonify(result)

def get_articles_by_entity(entity):
    query = {
        "$or": [
            {"entities.people": entity},
            {"entities.places": entity},
            {"entities.organizations": entity}
        ]
    }
    articles = collection.find(query)
    return list(articles)  # Convert cursor to list

# Existing routes...

# Route for Articles by Entity --> Example: /articles_by_entity/Israel
@app.route('/articles_by_entity/<entity>', methods=['GET'])
def articles_by_entity(entity):
    result = get_articles_by_entity(entity)
    return jsonify(result)

@app.route('/articles_by_country/<country>', methods=['GET'])
def articles_by_country(country):
    query = {"entities.countries": country}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"country": country, "articles": result})

@app.route('/articles_by_organization/<organization>', methods=['GET'])
def articles_by_organization(organization):
    query = {"entities.organizations": organization}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"organization": organization, "articles": result})

@app.route('/articles_by_person/<person>', methods=['GET'])
def articles_by_person(person):
    query = {"entities.people": person}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"person": person, "articles": result})

@app.route('/articles_by_location/<location>', methods=['GET'])
def articles_by_location(location):
    query = {"entities.locations": location}
    projection = {"_id": 0, "title": 1}
    result = list(collection.find(query, projection))
    return jsonify({"location": location, "articles": result})


if __name__ == '__main__':
    app.run(debug=True)
