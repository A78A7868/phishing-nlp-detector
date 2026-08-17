import re
import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK data is downloaded
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except Exception as e:
    print(f"Warning: Failed to download NLTK packages dynamically: {e}")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
PROCESSED_FILE_PATH = os.path.join(PROCESSED_DATA_DIR, "cleaned_emails.csv")

def clean_text(text):
    """
    Cleans raw email text by:
    1. Stripping HTML tags.
    2. Lowercasing.
    3. Tokenizing.
    4. Removing punctuation and non-alphabetic characters.
    5. Removing NLTK English stopwords.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 2. Lowercase
    text = text.lower()
    
    # 3. Tokenize
    try:
        tokens = word_tokenize(text)
    except Exception:
        # Fallback to simple split if word_tokenize fails
        tokens = text.split()
        
    # 4. Remove punctuation and stopwords
    stop_words = set(stopwords.words('english'))
    cleaned_tokens = []
    
    for token in tokens:
        # Keep only alphabetic tokens and discard single characters unless they are meaningful
        token_clean = re.sub(r'[^a-z]', '', token)
        if token_clean and token_clean not in stop_words and len(token_clean) > 1:
            cleaned_tokens.append(token_clean)
            
    return " ".join(cleaned_tokens)

def preprocess_dataset(raw_csv_path):
    """
    Loads raw CSV, cleans email text, and saves the cleaned dataset.
    """
    print(f"Loading raw dataset from {raw_csv_path} for cleaning...")
    df = pd.read_csv(raw_csv_path)
    
    # Ensure raw columns exist, handle missing values
    df = df.dropna(subset=["Email Text"])
    df = df.drop_duplicates(subset=["Email Text"])
    
    print("Preprocessing text data (HTML stripping, tokenization, stopword removal)...")
    df["Cleaned Text"] = df["Email Text"].apply(clean_text)
    
    # Drop rows with empty text after cleaning to avoid issues with vectorization
    df = df[df["Cleaned Text"].str.strip() != ""]
    
    # Save processed dataset
    df.to_csv(PROCESSED_FILE_PATH, index=False)
    print(f"Successfully saved cleaned dataset to {PROCESSED_FILE_PATH} (Shape: {df.shape})")
    return PROCESSED_FILE_PATH

if __name__ == "__main__":
    # Test script locally
    raw_path = os.path.join(BASE_DIR, "data", "raw", "Phishing_Email.csv")
    if os.path.exists(raw_path):
        preprocess_dataset(raw_path)
    else:
        print(f"Raw data file not found at {raw_path}. Run data_loader.py first.")
