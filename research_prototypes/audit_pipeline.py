
import os
import sys
import django
import pandas as pd
import numpy as np
from statistics import mean

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_guardian.settings')
django.setup()

from facts.services import FactCheckerService

def analyze_datasets():
    print("\n" + "="*50)
    print("PHASE 1: DATASET BIAS CHECK")
    print("="*50)
    
    datasets = {
        'Politifact Fake': 'dataset/politifact_fake.csv',
        'Politifact Real': 'dataset/politifact_real.csv',
        'GossipCop Fake': 'dataset/gossipcop_fake.csv',
        'GossipCop Real': 'dataset/gossipcop_real.csv',
    }
    
    for name, path in datasets.items():
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, path)
        
        try:
            df = pd.read_csv(full_path)
            print(f"\nDATASET: {name}")
            print(f"   - Rows: {len(df)}")
            print(f"   - Columns: {list(df.columns)}")
            
            # Check for empty content
            if 'title' in df.columns:
                avg_len = df['title'].str.len().mean()
                print(f"   - Avg Title Length: {avg_len:.2f} chars")
            
        except Exception as e:
            print(f"   Error reading {name}: {e}")

def probe_pipeline():
    print("\n" + "="*50)
    print("PHASE 2: PIPELINE SANITY CHECK")
    print("="*50)
    
    test_cases = [
        ("India is under world war", "FAKE (Expected)", "India is under world war"),
        ("India launches Chandrayaan mission", "TRUE (Expected)", "India launches Chandrayaan mission"),
        ("COVID vaccines contain microchips", "FAKE (Expected)", "COVID vaccines contain microchips")
    ]
    
    for claim, expected, query in test_cases:
        print(f"\nCASE: '{claim}'")
        print(f"   Expectation: {expected}")
        
        # 1. Search
        print("   STEP 1: Search")
        search_query = FactCheckerService.get_date_range_query(query)
        urls = FactCheckerService.search_web(search_query)
        print(f"      Found {len(urls)} URLs")
        if not urls:
            print("      CRITICAL: Search returned 0 URLs. Pipeline checks failed.")
            continue
            
        # 2. Scrape & Summarize
        print("   STEP 2: Scrape & Summarize")
        summaries, valid_urls = FactCheckerService.scrape_and_summarize(urls, query)
        print(f"      Scraped {len(summaries)} valid summaries from {len(valid_urls)} URLs")
        
        if not summaries:
            print("      CRITICAL: Scraping failed to retrieve content.")
            continue

        # 3. Similarity
        print("   STEP 3: Similarity Check")
        # We need to access the logic inside verify_news, but since that's not exposed as a single granular method 
        # that returns the vector scores easily for printing without modification, 
        # we will use the public check_similarity method.
        matches = FactCheckerService.check_similarity(query, summaries)
        print(f"      Raw Scores: {matches}")
        
        if matches:
            avg_sim = mean(matches)
            max_sim = max(matches)
            print(f"      Average Similarity: {avg_sim:.4f}")
            print(f"      Max Similarity:     {max_sim:.4f}")
            
            # 4. Verdict
            print("   STEP 4: Verdict")
            verdict = FactCheckerService.classify_verdict(avg_sim, max_sim, len(valid_urls), query)
            print(f"      FINAL VERDICT: {verdict}")
        else:
            print("      No similarity scores generated.")

if __name__ == "__main__":
    analyze_datasets()
    probe_pipeline()
