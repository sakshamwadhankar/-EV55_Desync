---
title: Truthlens Backend
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# TruthLens 🔍
> **Advanced Real-Time Fake News Detection & Verification System**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-4.1%2B-092E20?style=for-the-badge&logo=django)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**TruthLens** (formerly *News Guardian*) is a robust web application designed to combat misinformation. It leverages advanced **Web Scraping**, **Natural Language Processing (NLP)**, and **Machine Learning** to verify news claims in real-time by cross-references them against credible sources on the live internet.

---

## 🚀 Key Features

*   **Real-Time Verification**: Instantly verifies claims by searching the live web using DuckDuckGo.
*   **Intelligent Scraping**: Robustly extracts content from diverse news sources, handling partial data and anti-bot measures.
*   **AI-Powered Analysis**:
    *   **Semantic Similarity**: Uses `SpaCy` and `Sentence-Transformers` to compare claims with gathered evidence.
    *   **Summarization**: Automatically condenses long articles into digestible summaries using LSA.
    *   **Zero-Shot Classification**: Detects hate speech, profanity, and other harmful content patterns.
*   **Visual Context**: Generates dynamic **WordClouds** to visualize the key themes of the verified news.
*   **Graceful Degradation**: Smart fallback logic ensures users get results even if some data sources fail.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend Framework** | Django (Python) |
| **Frontend** | HTML5, Bootstrap 5, Custom CSS |
| **Search Engine** | DuckDuckGo (`duckduckgo-search`) |
| **Scraping** | `requests`, `BeautifulSoup4` |
| **NLP Core** | `spaCy` (`en_core_web_md`), `sumy` (LSA) |
| **Machine Learning** | `sentence-transformers` (RoBERTa), Hugging Face Pipeline |
| **Visualization** | `wordcloud`, `matplotlib` |

---

## 🏗️ Architecture

TruthLens follows a clean **Service-Oriented Architecture** within the standard Django MVT pattern:

*   **Service Layer (`facts/services.py`)**: Encapsulates all complex business logic (Search, Scrape, NLP, Verification). This ensures the views remain lightweight and the logic is reusable.
*   **Controller (`facts/views.py`)**: Handles HTTP requests, orchestrates the service calls, and manages the data flow to the template.
*   **Prototypes (`research_prototypes/`)**: Contains isolated scripts for debugging and testing the search/scrape pipeline independently.

---

## 💻 Installation & Usage

### Prerequisites
*   Python 3.10 or higher
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/sakshamwadhankar/-EV55_Desync.git
cd -EV55_Desync
```

### 2. Install Dependencies
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Start the Server
```bash
python manage.py runserver
```
Access the application at **`http://127.0.0.1:8000/`**

---

## 📝 How it Works

1.  **Input**: User enters a news headline or claim (e.g., *"India is under world war"*).
2.  **Search**: The system queries DuckDuckGo for relevant, recent articles.
3.  **Process**:
    *   Top URLs are scrapped for content.
    *   Text is filtered, cleaned, and summarized.
4.  **Verify**:
    *   Cosine similarity checks alignment between the claim and the evidence.
    *   Safety classifiers check for hate speech or profanity.
5.  **Result**: The user receives a **True/Fake verdict**, a confidence summary, source links, and a context word cloud.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open-source and available under the MIT License.
