# TruthLens - Project Summary

## 1. Project Overview
**TruthLens** is an Advanced Fake News Detection System designed to verify news claims in real-time. It uses a combination of web scraping, Natural Language Processing (NLP), and Machine Learning (ML) to cross-reference user queries against credible sources on the internet.

## 2. Technology Stack
*   **Framework:** Django (Python)
*   **Frontend:** HTML5, Bootstrap 5, Custom CSS
*   **Search Engine:** DuckDuckGo (via `duckduckgo-search`)
*   **Scraping:** `requests`, `BeautifulSoup4`
*   **NLP & ML Libraries:**
    *   `spacy` (En_core_web_md) - For word vectors and similarity.
    *   `sentence-transformers` (stsb-roberta-large) - For semantic embeddings.
    *   `transformers` (Hugging Face pipeline) - For Zero-Shot Classification.
    *   `sumy` (LSA Summarizer) - For text summarization.
    *   `wordcloud` - For visualization.

## 3. Architecture & Project Structure
The project follows the standard Django MVT (Model-View-Template) architecture, but with a dedicated **Service Layer** for business logic.

### Directory Structure
```text
.
├── manage.py
├── requirements.txt
├── summary.md
├── news_guardian/         # Project Configuration (was 'kavach')
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── facts/                 # Main Application
│   ├── services.py        # Service Layer (AI/Scraping Logic)
│   ├── views.py           # Controller (View Logic)
│   ├── urls.py
│   └── models.py
├── templates/             # Frontend
│   └── index.html
├── static/                # Assets (CSS, Images, JS)
├── research_prototypes/   # Experimental & Debug Code
│   └── debug_scraper.py
└── docs/                  # Project Documentation
```

## 4. Key Workflows

### The Fact-Checking Pipeline (`FactCheckerService`)
1.  **Input:** User enters a claim (e.g., "India is under world war").
2.  **Search:** The system searches DuckDuckGo for relevant articles.
    *   *Optimization:* Uses broad searches (no date restriction) to maximize recall.
3.  **Scrape & Filter:**
    *   Fetches the top 10 URLs.
    *   Extracts text using `BeautifulSoup`.
    *   Filters out snippets shorter than 50 characters to ensure quality.
4.  **Summarization:**
    *   Uses LSA (Latent Semantic Analysis) to shorten long articles into 100-sentence summaries.
5.  **Similarity Analysis:**
    *   Compares the User Query vs. Scraped Summaries using **Cosine Similarity** on SpaCy vectors.
6.  **Verdict Classification:**
    *   **Fake:** If Average Similarity < 0.38 OR if detected as 'Hate Speech'/'Profane'.
    *   **True:** If Similarity >= 0.38 and content is safe.
7.  **Visualization:** Generates a **WordCloud** from the scraped context.

## 5. Recent Refactoring & Improvements
*   **Renaming:** Project configuration folder renamed from `kavach` to `news_guardian` for professionalism.
*   **Scraping Fixes:**
    *   Switched from `googlesearch-python` to `duckduckgo-search` to bypass blocking.
    *   Implemented fallback searches and lowered scraping thresholds to fix "Insufficient Data" errors.
*   **Modularization:** Extracted monolithic logic from `views.py` into `FactCheckerService`.

## 6. How to Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python manage.py runserver
```
Access the application at: `http://127.0.0.1:8000/`
