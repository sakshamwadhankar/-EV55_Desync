from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sentence_transformers import SentenceTransformer
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import numpy as np
import datetime
import time

# Load models globally to avoid reloading on every request (Singleton pattern)
try:
    nlp = spacy.load("en_core_web_md")
    # Using a lighter model or caching it is recommended for production
    sentence_model = SentenceTransformer('stsb-roberta-large')
    classifier = pipeline('zero-shot-classification')
except Exception as e:
    print(f"Warning: Models failed to load. Ensure dependencies are installed. Error: {e}")

class FactCheckerService:
    @staticmethod
    def get_date_range_query(query):
        """Returns the query as-is. Date range filters often reduce recall on free search APIs."""
        return query

    @staticmethod
    def search_web(query, num_results=10):
        """
        Searches DuckDuckGo with fallback strategies.
        1. Exact query
        2. Simple query (no date/special chars)
        3. Keyword based query
        """
        print(f"DEBUG: Starting Search for '{query}'")
        urls = []
        
        # Strategy 1: Direct Query
        try:
            print(f"DEBUG: Attempt 1 - Direct Query: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                urls = [r['href'] for r in results]
        except Exception as e:
            print(f"DEBUG: Attempt 1 Failed: {e}")

        # Strategy 2: Fallback (Remove punctuation/quotes)
        if not urls:
            print("DEBUG: Attempt 2 - Simplified Query")
            simple_query = ''.join(e for e in query if e.isalnum() or e.isspace())
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(simple_query, max_results=num_results))
                    urls = [r['href'] for r in results]
            except Exception as e:
                print(f"DEBUG: Attempt 2 Failed: {e}")

        # Strategy 3: Keywords
        if not urls:
            print("DEBUG: Attempt 3 - Keyword Append")
            keyword_query = f"{query} news fact check"
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(keyword_query, max_results=num_results))
                    urls = [r['href'] for r in results]
            except Exception as e:
                print(f"DEBUG: Attempt 3 Failed: {e}")

        print(f"DEBUG: Total URLs Found: {len(urls)}")
        return list(set(urls)) # Deduplicate

    @staticmethod
    def scrape_and_summarize(urls, query_text):
        """Scrapes URLs with robust error handling and lower thresholds."""
        # Rotating User-Agents could be added here, but a standard modern one usually works
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        summaries = []
        valid_urls = []
        
        print(f"DEBUG: Scraping {len(urls)} URLs...")
        
        for url in urls:
            try:
                # Timeout is crucial to prevent hanging
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract text from p, h1, h2, article tags
                    paragraphs = soup.find_all(['p', 'h1', 'h2', 'article'])
                    text_content = []
                    
                    for p in paragraphs:
                        clean_text = p.get_text().strip()
                        if len(clean_text) > 30: # Lowered threshold from 50/100
                            text_content.append(clean_text)
                    
                    full_text = ' '.join(text_content)
                    
                    if len(full_text) > 100: # Ensure we have at least some substantial content
                        # Summarization Safety Block
                        try:
                            parser = HtmlParser.from_string(full_text, None, Tokenizer("english"))
                            summarizer = LsaSummarizer()
                            summarizer.stop_words = [' ']
                            # Limit sentences to avoid huge blobs
                            summary = summarizer(parser.document, 10) 
                            
                            summary_text = " ".join([str(s) for s in summary])
                            
                            if summary_text:
                                summaries.append(summary_text)
                                valid_urls.append(url)
                                print(f"DEBUG: Successfully scraped & summarized: {url}")
                            else:
                                # Fallback to raw text if summary fails but text exists
                                summaries.append(full_text[:5000]) # Truncate large text
                                valid_urls.append(url)
                                print(f"DEBUG: LSA Empty, used raw text: {url}")
                                
                        except Exception as sum_e:
                            print(f"DEBUG: Summarization Error for {url}: {sum_e}")
                            # Fallback to raw text
                            summaries.append(full_text[:5000])
                            valid_urls.append(url)
                    else:
                        print(f"DEBUG: Skipped {url} - Content too short ({len(full_text)} chars)")
                else:
                    print(f"DEBUG: Skipped {url} - Status Code {response.status_code}")
                    
            except Exception as e:
                print(f"DEBUG: Error scraping {url}: {e}")
                continue
                
        print(f"DEBUG: Total VALID Summaries: {len(summaries)}")
        return summaries, valid_urls

    @staticmethod
    def check_similarity(query, summaries):
        """Calculates cosine similarity with safety checks."""
        if not summaries:
            return []
            
        similarities = []
        print("DEBUG: Calculating Similarities...")
        
        for i, summary in enumerate(summaries):
            try:
                # Ensure query and summary are strings
                q_vec = nlp(str(query)).vector
                s_vec = nlp(str(summary)).vector
                
                # Check for zero vectors (empty models or unknown words)
                if np.all(q_vec == 0) or np.all(s_vec == 0):
                   print(f"DEBUG: Zero vector for item {i}")
                   similarities.append(0.0)
                   continue

                sim = cosine_similarity([q_vec], [s_vec])[0][1]
                similarities.append(float(sim))
            except Exception as e:
                print(f"DEBUG: Similarity Error for item {i}: {e}")
                similarities.append(0.0)
                
        return similarities

    @staticmethod
    def classify_verdict(avg_similarity, query):
        """Robust Verdict Classification."""
        threshold = 0.38
        print(f"DEBUG: Verdict Check - Avg Sim: {avg_similarity}")
        
        try:
            if avg_similarity < threshold:
                 return "We can classify the news as Fake"
            else:
                # Secondary: Hate Speech
                try:
                    labels = ['hate speech', 'non-hate speech']
                    result = classifier(query, labels)
                    if result['labels'][0] == 'hate speech':
                        return "We can classify the news as Fake (Hate Speech Detected)"
                except Exception as e:
                     print(f"DEBUG: Classifier Error (Hate Speech): {e}")

                # Tertiary: Profanity
                try:
                    labels_profanity = ['Not Profane', 'Profane']
                    result_profanity = classifier(query, labels_profanity)
                    if result_profanity['labels'][0] == 'Profane':
                        return "We can classify the news as Fake (Profanity Detected)"
                except Exception as e:
                     print(f"DEBUG: Classifier Error (Profanity): {e}")
                
                return "The News is True"
        except Exception as e:
            print(f"DEBUG: General Verdict Error: {e}")
            return "Unable to Verify (System Error)"
