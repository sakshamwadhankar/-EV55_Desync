import requests
import os

print(f"Current Working Directory: {os.getcwd()}")
print("🚀 Starting Data Download Pipeline...")

# Ye links reliable GitHub repository ke hain jahan ISOT dataset hosted hai
# (Note: Hum Kaggle use nahi kar rahe, ye Open Source GitHub data hai)
URL_TRUE = "https://raw.githubusercontent.com/laxmimerit/fake-real-news-dataset/main/data/True.csv"
URL_FAKE = "https://raw.githubusercontent.com/laxmimerit/fake-real-news-dataset/main/data/Fake.csv"

def download_file(url, filename):
    print(f"⬇️ Downloading {filename} from Cloud...")
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for errors
        print(f"   -> Content size: {len(response.content)} bytes")
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"✅ Success! {filename} saved to {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

# Download True.csv
download_file(URL_TRUE, "True.csv")

# Download Fake.csv
download_file(URL_FAKE, "Fake.csv")

print("\n🎉 DATA SETUP COMPLETE!")
print("Ab tum 'preprocessing.py' aur 'train_model.py' run kar sakte ho.")
