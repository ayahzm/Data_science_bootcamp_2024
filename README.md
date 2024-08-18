The article scraping process from the Al Mayadeen website involved several steps, implemented through Python classes and functions.
Below is a detailed breakdown of the coding steps:

A) Sitemap Parsing:

First with the SitemapParser class, which is initialized with the sitemap URL (https://www.almayadeen.net/sitemaps/all.xml). This class contains methods to parse the sitemap and extract article URLs.
The get_monthly_sitemap_urls method retrieves the main sitemap, parsing it with BeautifulSoup to extract monthly sitemap URLs, which contain the actual article URLs.
The get_article_urls_from_sitemap method is used to parse each monthly sitemap, extracting all the individual article URLs.
These URLs are extracted up to a specified limit (max_articles) because the total nb of articles detected was about 215k, which is too much.

B) Article Data Extraction:

For each article URL retrieved, the get_script_info_from_article method is responsible for extracting the article's metadata.
This method sends an HTTP GET request to each article's URL and uses BeautifulSoup to parse the HTML content.
It searches for a specific <script> tag with the type text/tawsiyat as asked in the task, which contains JSON data.

Note: To handle the large number of articles efficiently, the scraper uses the ThreadPoolExecutor from Python's concurrent.futures module.
The get_all_script_info method initiates concurrent requests to retrieve and process article data from multiple URLs simultaneously to try and decrease the 
execution time.

C) Data Storage:

Once the article data is collected, the FileUtility class is used to save the data into JSON files. The save_articles_to_json method organizes the articles by their publication date.
Articles are grouped into directories based on their year and month of publication. Each group is then saved as a separate JSON file in the specified output directory making easy to
navigate through said articles.

D) Execution:

The entire scraping process is encapsulated in a main function, which initializes the SitemapParser and FileUtility classes with appropriate parameters (like max_articles and max_workers).
The function then begins the retrieval of article URLs, extraction of article data, and saving of the data to JSON files.
Note: It also handles any exceptions that might occur during the process, ensuring a smooth and controlled execution.

NOTE: i added a convert python file that has code that converts keyword attribute content from comma seperated strings to arrays of strings to be more organized as required from you.
