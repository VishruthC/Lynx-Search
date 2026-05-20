import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize our existing ChromaDB setup
chroma_client = chromadb.PersistentClient(path="./search_index")
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="my_documents", 
    embedding_function=embedding_model
)

class WebCrawler:
    def __init__(self, seed_url, max_pages=10):
        self.seed_url = seed_url
        self.max_pages = max_pages
        self.base_domain = urlparse(seed_url).netloc
        self.visited_urls = set()
        self.queue = [seed_url]

    def clean_text(self, soup):
        """Strips scripts, styles, and extracts clean, readable text."""
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
        
        # Get text and join lines cleanly
        text = soup.get_text(separator=" ")
        lines = [line.strip() for line in text.splitlines()]
        chunks = [phrase for phrase in lines if phrase]
        return " ".join(chunks)

    def extract_links(self, soup, current_url):
        """Finds all valid internal links on the page."""
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Convert relative links (like /about) to full absolute URLs
            full_url = urljoin(current_url, href)
            
            # Ensure the link stays within the same domain and isn't already visited
            if urlparse(full_url).netloc == self.base_domain:
                # Strip fragments like #section-name to avoid crawling the same page twice
                clean_url = full_url.split("#")[0]
                if clean_url not in self.visited_urls and clean_url not in self.queue:
                    links.append(clean_url)
        return links

    def chunk_text(self, text, chunk_size=600, overlap=100):
        """Splits a long string of text into smaller overlapping chunks."""
        chunks = []
        text_len = len(text)
        current_idx = 0
        
        while current_idx < text_len:
            # Grab a slice of text based on character length
            end_idx = min(current_idx + chunk_size, text_len)
            chunk = text[current_idx:end_idx].strip()
            
            if len(chunk) >= 50:  # Ignore tiny trailing fragments
                chunks.append(chunk)
                
            # Move the window forward, but step back by the overlap amount to keep context
            current_idx += (chunk_size - overlap)
            
        return chunks

    def crawl_and_index(self):
        """Runs the main crawling loop, chunks the text, and stores them in the Vector DB."""
        print(f"Starting crawl on domain: {self.base_domain}\n")
        pages_crawled = 0

        while self.queue and pages_crawled < self.max_pages:
            url = self.queue.pop(0)
            
            if url in self.visited_urls:
                continue

            print(f"[{pages_crawled + 1}/{self.max_pages}] Fetching: {url}")
            self.visited_urls.add(url)

            try:
                # Add a User-Agent header so servers don't immediately block us as a bot
                headers = {"User-Agent": "MySearchEngineBot/1.0 (+http://localhost)"}
                response = requests.get(url, headers=headers, timeout=5)
                
                # Only parse HTML pages
                if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                page_text = self.clean_text(soup)

                # Skip pages with barely any content
                if len(page_text.strip()) < 100:
                    continue

                # Break the long page text into manageable 600-character blocks
                text_chunks = self.chunk_text(page_text)
                
                documents = []
                metadatas = []
                ids = []
                
                for idx, chunk in enumerate(text_chunks):
                    documents.append(chunk)
                    metadatas.append({"source": url, "chunk_index": idx})
                    # Unique ID for each chunk (e.g., "https://example.com#chunk_0")
                    ids.append(f"{url}#chunk_{idx}")

                # Index all the text chunks belonging to this specific page
                collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
                
                pages_crawled += 1

                # Gather new links from this page and add them to the queue
                new_links = self.extract_links(soup, url)
                self.queue.extend(new_links)

            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        print(f"\n Crawl finished. Successfully chunked and indexed {pages_crawled} web pages!")

if __name__ == "__main__":
    # Targeting the Formula One Wikipedia page to get rich text layout data
    TARGET_SITE = "https://en.wikipedia.org/wiki/Formula_One" 
    
    # Keeping it to 3 pages for a quick, safe testing run
    crawler = WebCrawler(seed_url=TARGET_SITE, max_pages=3)
    crawler.crawl_and_index()