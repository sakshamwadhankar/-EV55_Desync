import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

# --- CONFIGURATION ---
TRUE_DATA_PATH = 'True.csv'
FAKE_DATA_PATH = 'Fake.csv'

def load_and_clean_data():
    """Loads datasets, adds labels, merges, and cleans data."""
    print("⏳ Loading Datasets...")
    
    # Check if files exist
    if not os.path.exists(TRUE_DATA_PATH) or not os.path.exists(FAKE_DATA_PATH):
        print(f"❌ Error: Files not found! Ensure '{TRUE_DATA_PATH}' and '{FAKE_DATA_PATH}' are in this folder.")
        return None

    try:
        # Load Data
        df_true = pd.read_csv(TRUE_DATA_PATH)
        df_fake = pd.read_csv(FAKE_DATA_PATH)
        
        # Add Labels (1 = Real, 0 = Fake)
        df_true['class'] = 1
        df_fake['class'] = 0
        
        # Merge and Shuffle
        df = pd.concat([df_true, df_fake]).reset_index(drop=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Basic Cleaning
        initial_count = len(df)
        df.dropna(inplace=True)
        cleaned_count = len(df)
        
        print(f"✅ Data Loaded & Merged. Rows: {cleaned_count} (Dropped {initial_count - cleaned_count} missing rows)")
        return df
        
    except Exception as e:
        print(f"❌ Unexpected Error during loading: {e}")
        return None

def generate_visualizations(df):
    """Generates and saves 5 key visualizations for Round 2."""
    print("🎨 Generating Visualizations...")
    sns.set_style("darkgrid")
    
    # 1. Class Balance Bar Plot
    plt.figure(figsize=(6, 4))
    sns.countplot(x='class', data=df, palette='viridis')
    plt.title('Distribution of Real (1) vs Fake (0) News')
    plt.xlabel('Class (1=Real, 0=Fake)')
    plt.savefig('viz_1_balance.png')
    plt.close()
    print("   -> Saved viz_1_balance.png")

    # 2. Subject Count Plot
    plt.figure(figsize=(12, 6))
    # Order by count to make it look cleaner
    sns.countplot(y='subject', data=df, order=df['subject'].value_counts().index, palette='coolwarm')
    plt.title('News Articles by Subject')
    plt.savefig('viz_2_subjects.png')
    plt.close()
    print("   -> Saved viz_2_subjects.png")

    # 3. WordCloud for FAKE News
    print("   -> Generating Fake News WordCloud (Please wait)...")
    fake_text = " ".join(df[df['class'] == 0]['title'].astype(str).tolist())
    wc_fake = WordCloud(width=800, height=400, background_color='black', colormap='Reds').generate(fake_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc_fake, interpolation='bilinear')
    plt.axis('off')
    plt.title("Most Frequent Words in FAKE NEWS")
    plt.savefig('viz_3_fake_cloud.png')
    plt.close()

    # 4. WordCloud for REAL News
    print("   -> Generating Real News WordCloud (Please wait)...")
    real_text = " ".join(df[df['class'] == 1]['title'].astype(str).tolist())
    wc_real = WordCloud(width=800, height=400, background_color='white', colormap='Greens').generate(real_text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc_real, interpolation='bilinear')
    plt.axis('off')
    plt.title("Most Frequent Words in REAL NEWS")
    plt.savefig('viz_4_real_cloud.png')
    plt.close()

    # 5. Article Length Distribution
    # Calculate word count for each article
    df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='word_count', hue='class', kde=True, bins=50, palette='Set1')
    plt.title('Article Length Distribution (Real vs Fake)')
    plt.xlabel('Number of Words')
    plt.xlim(0, 2000) # Limiting x-axis to focus on main distribution
    plt.savefig('viz_5_length.png')
    plt.close()
    print("   -> Saved viz_5_length.png")

def main():
    df = load_and_clean_data()
    if df is not None:
        generate_visualizations(df)
        print("\n🎉 SUCCESS: All visualizations generated! Check your folder.")
        print(f"Final Dataset Size: {df.shape}")

if __name__ == "__main__":
    main()
