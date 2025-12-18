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
from statistics import mean

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

        # Strategy 4: Entity & Noun Extraction (Spacy)
        if not urls:
            try:
                print("DEBUG: Attempt 4 - Entity/Noun Extraction")
                doc = nlp(query)
                # Keep significant words: Proper nouns, nouns, verbs (excluding stop words)
                keywords = [token.text for token in doc if not token.is_stop and token.pos_ in ['PROPN', 'NOUN', 'VERB']]
                entity_query = " ".join(keywords)
                
                print(f"DEBUG: Extracted Keywords: {entity_query}")
                
                if entity_query and len(entity_query.split()) > 0:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(entity_query, max_results=num_results))
                        urls = [r['href'] for r in results]
            except Exception as e:
                print(f"DEBUG: Attempt 4 Failed: {e}")

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
        """Calculates cosine similarity using SentenceTransformer (SBERT)."""
        if not summaries:
            return []
            
        similarities = []
        print("DEBUG: Calculating Similarities (SBERT)...")
        
        try:
            # Encode query and all summaries in one batch for speed
            # sentence_model.encode returns numpy arrays
            q_emb = sentence_model.encode(str(query))
            s_embs = sentence_model.encode(summaries)
            
            # Calculate cosine similarity
            # cosine_similarity expects 2D arrays. 
            # q_emb.reshape(1, -1) vs s_embs (n, 1024)
            sim_scores = cosine_similarity([q_emb], s_embs)[0]
            
            # Convert to float list
            similarities = [float(s) for s in sim_scores]
            
            print(f"DEBUG: SBERT Scores: {[f'{s:.3f}' for s in similarities]}")
            return similarities

        except Exception as e:
            print(f"DEBUG: SBERT Similarity Error: {e}")
            return [0.0] * len(summaries)

    @staticmethod
    def classify_verdict(avg_similarity, max_similarity, source_count, query):
        """
        Robust Verdict Classification with 5-Tier Confidence Logic.
        
        Tiers:
        1. Strong True: max_sim >= 0.45 and sources >= 1
        2. Likely True: avg_sim >= 0.25 and max_sim >= 0.30
        3. Unverified: Default safe state (low confidence, ambiguity)
        4. Strong Fake: max_sim <= 0.15 and sources >= 3 (Negative Confirmation)
        5. Insufficient Data: sources == 0 (Handled by caller usually)
        """
        print(f"DEBUG: Verdict Check - Avg: {avg_similarity:.4f}, Max: {max_similarity:.4f}, Sources: {source_count}")
        
        # Default State
        verdict = "Unverified: No strong confirmation or contradiction found."
        rule_triggered = "Default (Unverified)"

        try:
            # 1. Strong True
            if max_similarity >= 0.45 and source_count >= 1:
                verdict = "The News is True (High Confidence)"
                rule_triggered = "Strong True (Max >= 0.45)"
            
            # 2. Likely True
            elif avg_similarity >= 0.25 and max_similarity >= 0.30:
                verdict = "The News is Likely True (Medium Confidence)"
                rule_triggered = "Likely True (Avg >= 0.25, Max >= 0.30)"
            
            # 4. Strong Fake (Negative Confirmation)
            # We ONLY return Fake if we found plenty of sources (3+) and NONE of them matched well.
            # This implies the claim is likely made up or not reflected in reputable news.
            elif max_similarity <= 0.15 and source_count >= 3:
                verdict = "We can classify the news as Fake (Low Similarity across multiple sources)"
                rule_triggered = "Strong Fake (Max <= 0.15, Sources >= 3)"
            
            # Additional Safety Checks (Keep existing classifiers BUT treat them as modifiers)
            # Note: We prioritize the similarity verdict, but if text classification flags hate/profanity, 
            # we might want to append that warning or override if it's very dangerous.
            # For now, let's keep the user's logic pure: "Fake requires NEGATIVE CONFIRMATION".
            # Hate speech is a property of the text, not its truthfulness, but often correlated with Fake.
            # We will perform these checks only if we haven't already marked it as True.
            
            if "True" not in verdict:
                 # Secondary: Hate Speech
                try:
                    labels = ['hate speech', 'non-hate speech']
                    result = classifier(query, labels)
                    if result['labels'][0] == 'hate speech':
                        verdict = "We can classify the news as Fake (Hate Speech Detected)"
                        rule_triggered = "Hate Speech Classifier"
                except Exception as e:
                     print(f"DEBUG: Classifier Error (Hate Speech): {e}")

                # Tertiary: Profanity
                try:
                    labels_profanity = ['Not Profane', 'Profane']
                    result_profanity = classifier(query, labels_profanity)
                    if result_profanity['labels'][0] == 'Profane':
                        verdict = "We can classify the news as Fake (Profanity Detected)"
                        rule_triggered = "Profanity Classifier"
                except Exception as e:
                     print(f"DEBUG: Classifier Error (Profanity): {e}")

            print(f"DEBUG: Final Verdict: '{verdict}' | Rule: {rule_triggered}")
            return verdict

        except Exception as e:
            print(f"DEBUG: General Verdict Error: {e}")
            return "Unable to Verify (System Error)"
