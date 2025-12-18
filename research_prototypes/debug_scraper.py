from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

def test_scraper():
    query = "Hello World"
    print(f"Testing query: {query}")
    try:
        r = requests.get("https://www.google.com", timeout=5)
        print(f"Google Reachable: {r.status_code}")
    except Exception as e:
        print(f"Google Unreachable: {e}")
    
    # 1. Search
    try:
        urls = []
        with DDGS() as ddgs:
            try:
                query = "Thailand bombs near Cambodia's Poipet border crossing"
                print(f"Testing Query: {query}")
                
                results = ddgs.text(query, max_results=5)
                results_list = list(results)
                for r in results_list:
                        urls.append(r['href'])
            except Exception as e:
                print(f"Search EXCEPTION within DDGS context: {e}")
        
        print(f"Search results: {len(urls)}")
        for url in urls:
            print(f" - {url}")
        
        results = urls # Alias for compatibility with rest of script
    except Exception as e:
        print(f"Search EXCEPTION: {e}")
        return

    if not results:
        print("No results found.")
        return

    # 2. Scrape
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    for url in results:
        print(f"\nScraping {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = soup.find_all('p')
                text = ' '.join(p.get_text() for p in paragraphs)
                print(f"Extracted Length: {len(text)}")
                if len(text) < 100:
                    print("Skipped: Text too short")
            else:
                print("Skipped: Bad status code")
                
        except Exception as e:
            print(f"Scrape EXCEPTION: {e}")

if __name__ == "__main__":
    test_scraper()
