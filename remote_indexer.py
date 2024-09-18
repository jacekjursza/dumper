# remote_indexer.py

import logging
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RemoteIndexer:

    def __init__(self, urls, depth, db_manager, css_selectors=None):
        self.urls = urls
        self.depth = depth
        self.db_manager = db_manager
        self.visited = set()
        self.pages = []
        self.css_selectors = [selector.strip() for selector in css_selectors.split(';') if selector.strip()] if css_selectors else []

    def reindex(self):
        for url in self.urls:
            normalized_url = self.normalize_url(url)
            self.fetch_page(normalized_url, self.depth)
        self.db_manager.update_remote_pages(self.pages)

    def normalize_url(self, url):
        # Usunięcie fragmentu (#...) z URL
        url, _ = urldefrag(url)
        return url

    def fetch_page(self, url, depth):
        if url in self.visited or depth < 0:
            return
        self.visited.add(url)
        logging.debug(f"Fetching URL: {url} at depth {depth}")
        try:
            response = requests.get(url)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch {url}: Status code {response.status_code}")
                return
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string.strip() if soup.title else ''
            self.pages.append({'url': url, 'title': title, 'include_in_dump': 1})
            if depth > 0:
                domain = urlparse(url).netloc
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    full_url = self.normalize_url(full_url)  # Usunięcie fragmentu
                    parsed_full_url = urlparse(full_url)
                    if parsed_full_url.netloc != domain:
                        continue  # Ignorowanie linków spoza domeny
                    if full_url not in self.visited:
                        self.fetch_page(full_url, depth - 1)
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")

