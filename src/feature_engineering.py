import re
import os
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from gensim.models import Word2Vec
import joblib

# Urgency keywords list
URGENCY_KEYWORDS = [
    r"\burgent(ly)?\b", r"\bimmediate(ly)?\b", r"\baction required\b", 
    r"\bverify your\b", r"\bsuspended\b", r"\baccount blocked\b", 
    r"\bsecurity alert\b", r"\blimited access\b", r"\brestricted\b", 
    r"\bclick here\b", r"\bconfirm your\b", r"\bupdate your password\b", 
    r"\brefund claim\b", r"\bwinner\b", r"\bcongratulations\b", 
    r"\bfree gift\b", r"\bimportant notice\b", r"\battention\b",
    r"\bverification\b", r"\bexpiration\b"
]

class PhishingFeatureExtractor:
    def __init__(self, max_text_features=5000, w2v_vector_size=100):
        self.max_text_features = max_text_features
        self.w2v_vector_size = w2v_vector_size
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_text_features, 
            ngram_range=(1, 3), 
            sublinear_tf=True, 
            min_df=2, 
            max_df=0.95
        )
        self.scaler = MinMaxScaler()
        self.w2v_scaler = MinMaxScaler()
        self.w2v_model = None
        self.feature_names = []
        
    def extract_metadata_features(self, raw_text_series):
        """
        Extracts structural, lexical, and metadata features from raw email text.
        """
        features_list = []
        
        for text in raw_text_series:
            text = str(text)
            
            # 1. URL metrics
            urls = re.findall(r'https?://[^\s]+|www\.[^\s]+', text)
            url_count = len(urls)
            url_present = 1.0 if url_count > 0 else 0.0
            
            # 2. Email Address metrics
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            email_count = len(emails)
            
            # 3. Urgency and Threat patterns
            urgency_score = 0.0
            for pattern in URGENCY_KEYWORDS:
                urgency_score += len(re.findall(pattern, text, re.IGNORECASE))
                
            # 4. Text structural properties
            char_len = float(len(text))
            word_count = float(len(text.split())) if char_len > 0 else 0.0
            
            # 5. Punctuation and Exclamation statistics
            excl_count = float(text.count("!"))
            excl_density = excl_count / char_len if char_len > 0 else 0.0
            
            punct_count = float(len(re.findall(r'[.,\/#!$%\^&\*;:{}=\-_`~()?]', text)))
            punct_density = punct_count / char_len if char_len > 0 else 0.0
            
            # 6. Lexical shape (ALL CAPS indicator)
            caps_count = float(sum(1 for c in text if c.isupper()))
            caps_ratio = caps_count / char_len if char_len > 0 else 0.0
            
            # 7. Suspicious Domain extensions
            suspicious_ext_count = 0.0
            susp_patterns = [r"\.xyz\b", r"\.club\b", r"\.info\b", r"\.top\b", r"\.tk\b", r"\.cf\b", r"\.ga\b"]
            for pattern in susp_patterns:
                suspicious_ext_count += len(re.findall(pattern, text, re.IGNORECASE))
                
            features_list.append([
                url_count,
                url_present,
                email_count,
                urgency_score,
                char_len,
                word_count,
                excl_count,
                excl_density,
                punct_count,
                punct_density,
                caps_ratio,
                suspicious_ext_count
            ])
            
        return np.array(features_list)
    
    def get_metadata_feature_names(self):
        return [
            "url_count", "url_present", "email_count", "urgency_score",
            "char_len", "word_count", "excl_count", "excl_density",
            "punct_count", "punct_density", "caps_ratio", "suspicious_ext_count"
        ]

    def _get_w2v_vectors(self, cleaned_texts):
        """
        Computes the averaged Word2Vec vector representation for each email text.
        """
        vectors = []
        for text in cleaned_texts:
            words = str(text).split()
            valid_vectors = [self.w2v_model.wv[w] for w in words if w in self.w2v_model.wv]
            
            if valid_vectors:
                # Average word vectors
                vectors.append(np.mean(valid_vectors, axis=0))
            else:
                # Return zero vector if no words are in Word2Vec vocabulary
                vectors.append(np.zeros(self.w2v_vector_size))
                
        return np.array(vectors)

    def fit_transform(self, df):
        """
        Fits text vectorizers, scales metadata, and returns a combined feature matrix.
        df must contain "Email Text" and "Cleaned Text".
        """
        print("Extracting metadata features from raw text...")
        metadata = self.extract_metadata_features(df["Email Text"])
        scaled_metadata = self.scaler.fit_transform(metadata)
        
        print("Fitting TF-IDF on preprocessed text...")
        tfidf_features = self.vectorizer.fit_transform(df["Cleaned Text"])
        
        print("Training custom Word2Vec model on cleaned tokens...")
        tokenized_sentences = [str(text).split() for text in df["Cleaned Text"]]
        self.w2v_model = Word2Vec(
            sentences=tokenized_sentences,
            vector_size=self.w2v_vector_size,
            window=5,
            min_count=1,
            workers=4,
            epochs=10
        )
        
        w2v_vectors = self._get_w2v_vectors(df["Cleaned Text"])
        scaled_w2v = self.w2v_scaler.fit_transform(w2v_vectors)
        
        # Combine TF-IDF, Word2Vec averages, and MinMaxScaler-scaled metadata
        combined = hstack([tfidf_features, csr_matrix(scaled_w2v), csr_matrix(scaled_metadata)])
        
        # Compile feature names list for model interpretability/coefficients
        text_names = self.vectorizer.get_feature_names_out().tolist()
        w2v_names = [f"w2v_dim_{i}" for i in range(self.w2v_vector_size)]
        meta_names = self.get_metadata_feature_names()
        self.feature_names = text_names + w2v_names + meta_names
        
        print(f"Combined feature matrix dimensions: {combined.shape}")
        return combined

    def transform(self, df):
        """
        Transforms new data using the fitted vectorizers and scaler.
        """
        metadata = self.extract_metadata_features(df["Email Text"])
        scaled_metadata = self.scaler.transform(metadata)
        
        tfidf_features = self.vectorizer.transform(df["Cleaned Text"])
        w2v_vectors = self._get_w2v_vectors(df["Cleaned Text"])
        scaled_w2v = self.w2v_scaler.transform(w2v_vectors)
        
        combined = hstack([tfidf_features, csr_matrix(scaled_w2v), csr_matrix(scaled_metadata)])
        return combined

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"Saved custom feature extractor to {filepath}")

    @staticmethod
    def load(filepath):
        extractor = joblib.load(filepath)
        print(f"Loaded custom feature extractor from {filepath}")
        return extractor
