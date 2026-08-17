import os
import sys
import time

# Ensure src dir is in system path for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_loader import download_dataset
from preprocessing import preprocess_dataset
from models import train_and_tune_models
from evaluate import evaluate_models

def run_pipeline():
    """
    Orchestrates the entire machine learning pipeline:
    1. Downloads or generates raw email dataset.
    2. Cleans and tokenizes text, removing stopwords.
    3. Fits feature extractor, splits data, and trains/tunes multiple models.
    4. Evaluates models, generates and saves metrics tables and visualization figures.
    """
    print("="*60)
    print("   AI-DRIVEN PHISHING EMAIL DETECTION - PIPELINE START   ")
    print("="*60)
    start_time = time.time()
    
    # Step 1: Data Loader
    print("\n--- STEP 1: Data Loading ---")
    raw_path = download_dataset()
    
    # Step 2: Preprocessing
    print("\n--- STEP 2: Data Preprocessing & Cleaning ---")
    cleaned_path = preprocess_dataset(raw_path)
    
    # Step 3: Model Training & Tuning
    print("\n--- STEP 3: Model Training & Cross-Validation Tuning ---")
    best_models, extractor, X_train, X_test, y_train, y_test = train_and_tune_models(cleaned_path)
    
    # Step 4: Model Evaluation
    print("\n--- STEP 4: Evaluation and Visualization Generation ---")
    df_results = evaluate_models()
    
    elapsed_time = time.time() - start_time
    print("\n" + "="*60)
    print(f"Pipeline executed successfully in {elapsed_time:.2f} seconds!")
    print("All models saved in 'models/' directory.")
    print("Evaluation tables and figures saved in 'reports/' directory.")
    print("="*60)
    
    return df_results

if __name__ == "__main__":
    run_pipeline()
