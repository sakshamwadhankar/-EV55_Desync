
import os
import sys
import django

# Setup Django environment to allow importing services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_guardian.settings')
django.setup()

from facts.services import FactCheckerService

def test_pipeline():
    query = "India is under world war"
    print(f"--- Testing Pipeline for Query: '{query}' ---")
    
    # 1. Prepare Query
    search_query = FactCheckerService.get_date_range_query(query)
    print(f"Generated Search Query: {search_query}")
    
    # 2. Search
    print("\n--- Step 1: Searching ---")
    urls = FactCheckerService.search_web(search_query)
    print(f"URLs Found: {len(urls)}")
    for url in urls:
        print(f" - {url}")

    if not urls:
        print("FAILURE: No URLs found. Search returned empty list.")
        return

    # 3. Scrape
    print("\n--- Step 2: Scraping ---")
    summaries, valid_urls = FactCheckerService.scrape_and_summarize(urls, query)
    print(f"Summaries Generated: {len(summaries)}")
    print(f"Valid URLs: {len(valid_urls)}")
    
    if not summaries:
        print("FAILURE: Scraping returned no valid text (insufficient length or blocking).")
    else:
        print("SUCCESS: Pipeline produced summaries.")

if __name__ == "__main__":
    test_pipeline()
