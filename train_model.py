import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import re
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# Ensure NLTK data is downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    # Convert to string and lowercase
    text = str(text).lower()
    # Remove special characters and punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove stopwords
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

def main():
    print("Loading data...")
    try:
        true_df = pd.read_csv('True.csv')
        fake_df = pd.read_csv('Fake.csv')
    except FileNotFoundError:
        print("Error: 'True.csv' or 'Fake.csv' not found. Please ensure they are in the current directory.")
        return

    # Add labels
    true_df['class'] = 1
    fake_df['class'] = 0

    # Combine and shuffle
    print("Preprocessing data...")
    df = pd.concat([true_df, fake_df], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Clean text
    print("Cleaning text (this might take a while)...")
    df['text'] = df['text'].apply(clean_text)

    # Feature Extraction
    print("Extracting features...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(df['text'])
    y = df['class']

    # Split Data
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model Training
    print("Training model...")
    model = PassiveAggressiveClassifier(max_iter=50)
    model.fit(X_train, y_train)

    # Evaluation
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy Score: {accuracy:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Fake', 'True'], yticklabels=['Fake', 'True'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig('viz_6_confusion_matrix.png')
    print("Confusion Matrix saved as 'viz_6_confusion_matrix.png'")

    # Save Model and Vectorizer
    print("Saving model and vectorizer...")
    with open('model.pkl', 'wb') as model_file:
        pickle.dump(model, model_file)
    
    with open('vectorizer.pkl', 'wb') as vec_file:
        pickle.dump(vectorizer, vec_file)

    print("Model created! Files saved: model.pkl, vectorizer.pkl")

if __name__ == "__main__":
    main()
