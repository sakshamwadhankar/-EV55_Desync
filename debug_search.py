import os
import django
from django.conf import settings

# Configure minimal Django settings for standalone script
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=['facts'],
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3'}},
    )
    django.setup()

from facts.services import FactCheckerService

query = "sit is in nagpur"
print(f"\n--- TESTING SEARCH FOR: '{query}' ---")

try:
    # 1. Test raw search
    urls = FactCheckerService.search_web(query)
    print(f"\n[STEP 1] Raw URLs found: {len(urls)}")
    for url in urls:
        print(f" - {url}")

    if not urls:
        print("\n[ERROR] DuckDuckGo returned 0 results. It might be rate-limited or the query is too obscure.")
    else:
        # 2. Test scraping
        print(f"\n[STEP 2] Scraping {len(urls)} URLs...")
        summaries, valid_urls = FactCheckerService.scrape_and_summarize(urls, query)
        print(f"\n[RESULT] Valid articles extracted: {len(valid_urls)}")
        
        if not valid_urls:
            print("[ERROR] URLs found but scraping failed (content too short or blocked).")

except Exception as e:
    print(f"\n[EXCEPTION] {e}")
