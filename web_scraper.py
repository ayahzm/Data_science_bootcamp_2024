import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import json
import os


@dataclass
class Article:
    url: str
    post_id: Optional[str] = None
    title: Optional[str] = None
    keywords: Optional[str] = None
    thumbnail: Optional[str] = None
    publication_date: Optional[str] = None
    last_updated_date: Optional[str] = None
    author: Optional[str] = None
    full_text: Optional[str] = None


class SitemapParser:
    def __init__(self, sitemap_url: str, max_articles: int = 12000, max_workers: int = 10):
        self.sitemap_url = sitemap_url
        self.max_articles = max_articles
        self.max_workers = max_workers

    def get_monthly_sitemap_urls(self) -> List[str]:
        response = requests.get(self.sitemap_url)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve sitemap: {self.sitemap_url}")

        soup = BeautifulSoup(response.content, 'xml')
        sitemap_tags = soup.find_all('sitemap')

        sitemap_urls = [sitemap.find('loc').text for sitemap in sitemap_tags]
        return sitemap_urls

    def get_article_urls_from_sitemap(self, monthly_sitemap_url: str) -> List[str]:
        response = requests.get(monthly_sitemap_url)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve monthly sitemap: {monthly_sitemap_url}")

        soup = BeautifulSoup(response.content, 'xml')
        url_tags = soup.find_all('url')

        article_urls = [url.find('loc').text for url in url_tags]
        return article_urls

    def get_all_article_urls(self) -> List[str]:
        all_article_urls = []
        monthly_sitemap_urls = self.get_monthly_sitemap_urls()

        for sitemap_url in monthly_sitemap_urls:
            if len(all_article_urls) >= self.max_articles:
                break
            article_urls = self.get_article_urls_from_sitemap(sitemap_url)
            all_article_urls.extend(article_urls)
            if len(all_article_urls) >= self.max_articles:
                all_article_urls = all_article_urls[:self.max_articles]
                break

        return all_article_urls

    def get_script_info_from_article(self, article_url: str) -> Optional[Article]:
        try:
            response = requests.get(article_url)
            if response.status_code != 200:
                print(f"Failed to retrieve article: {article_url}")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', {'type': 'text/tawsiyat'})

            # Extract text from all <p> tags
            full_text = ' '.join([p.get_text() for p in soup.find_all('p')])

            if script_tag:
                # Extract full_text and parse as JSON
                script_content = script_tag.string
                if script_content:
                    try:
                        article_data = json.loads(script_content)
                        # Extract and map values from the parsed JSON
                        article = Article(
                            url=article_url,
                            post_id=article_data.get('postid'),
                            title=article_data.get('title'),
                            keywords=article_data.get('keywords'),
                            thumbnail=article_data.get('thumbnail'),
                            publication_date=article_data.get('published_time'),
                            last_updated_date=article_data.get('last_updated'),
                            author=article_data.get('author'),
                            full_text=full_text  # Assign text content from <p> tags
                        )
                        return article
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON from article {article_url}: {e}")
                        return None
                else:
                    print(f"Script content is empty for article: {article_url}")
                    return None
            else:
                print(f"No <script> tag with type='text/tawsiyat' found in: {article_url}")
                return None
        except Exception as e:
            print(f"Error retrieving article {article_url}: {e}")
            return None

    def get_all_script_info(self) -> List[Article]:
        all_article_urls = self.get_all_article_urls()
        all_script_info = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.get_script_info_from_article, url): url for url in all_article_urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    script_info = future.result()
                    if script_info:
                        all_script_info.append(script_info)
                except Exception as e:
                    print(f"Exception occurred for URL {url}: {e}")

        return all_script_info


class FileUtility:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_articles_to_json(self, articles: List[Article]):
        articles_by_date = {}
        for article in articles:
            date_str = article.publication_date if article.publication_date else 'Unknown'
            if date_str != 'Unknown':
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                    year_month = date_obj.strftime('%Y-%m')
                except ValueError:
                    print(f"Invalid publication date format for article: {article.url}")
                    year_month = 'Unknown'
            else:
                year_month = 'Unknown'

            if year_month not in articles_by_date:
                articles_by_date[year_month] = []
            articles_by_date[year_month].append(article.__dict__)

        for year_month, articles_list in articles_by_date.items():
            year, month = (year_month.split('-') + ['Unknown'])[:2]
            file_path = os.path.join(self.output_dir, f"{year}_{month}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(articles_list, f, ensure_ascii=False, indent=4)

        print(f"Saved articles to JSON files in {self.output_dir}")


def main():
    sitemap_url = 'https://www.almayadeen.net/sitemaps/all.xml'
    output_dir = '../Data_science_bootcamp_Aya_Hazimeh/output/output'  # Directory to save JSON files
    max_articles = 10000
    max_workers = 20

    parser = SitemapParser(sitemap_url, max_articles=max_articles, max_workers=max_workers)
    file_utility = FileUtility(output_dir)

    try:
        print("Starting to retrieve article URLs...")
        all_articles = parser.get_all_script_info()

        if all_articles:
            print(f"Retrieved {len(all_articles)} articles.")
            print("Saving articles to JSON files...")
            file_utility.save_articles_to_json(all_articles)
        else:
            print("No articles retrieved.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
