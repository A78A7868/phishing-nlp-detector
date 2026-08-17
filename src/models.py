import os
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
import numpy as np
import joblib

# Import custom feature extractor
from feature_engineering import PhishingFeatureExtractor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_tune_models(cleaned_csv_path):
    """
    Loads preprocessed dataset, splits into train/test, extracts features,
    tunes hyperparameters using Stratified K-Fold CV, and saves the best models.
    """
    df = pd.read_csv(cleaned_csv_path)
    
    # 1. Split into features and label
    X_raw = df[["Email Text", "Cleaned Text"]]
    y = df["Email Type"].apply(lambda x: 1 if x == "Phishing Email" else 0).values
    
    # 2. Stratified Train-Test Split (80/20)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # Save the test set raw data for final evaluation/notebook usage
    test_df = pd.concat([X_test_raw, pd.Series(y_test, name="Label", index=X_test_raw.index)], axis=1)
    test_df.to_csv(os.path.join(BASE_DIR, "data", "processed", "test_set.csv"), index=False)
    
    # 3. Check and print class balance
    train_phish_count = np.sum(y_train)
    train_safe_count = len(y_train) - train_phish_count
    print(f"\nTraining Class Balance - Safe: {train_safe_count} ({train_safe_count/len(y_train)*100:.1f}%), Phishing: {train_phish_count} ({train_phish_count/len(y_train)*100:.1f}%)")
    
    # Fit and apply PhishingFeatureExtractor on training data
    print("\nFitting feature extractor and generating train features (TF-IDF 5000 features + Word2Vec + Metadata)...")
    extractor = PhishingFeatureExtractor(max_text_features=5000)
    X_train = extractor.fit_transform(X_train_raw)
    
    # Save the feature extractor (needed for app and evaluation scripts)
    extractor_path = os.path.join(MODELS_DIR, "feature_extractor.joblib")
    extractor.save(extractor_path)
    
    # Transform test features
    X_test = extractor.transform(X_test_raw)
    
    # 4. Define models and parameter grids
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    model_configs = {
        "LogisticRegression": {
            "model": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
            "params": {
                "C": [1.0, 10.0, 100.0],
                "solver": ["liblinear"]
            }
        },
        "RandomForest": {
            "model": RandomForestClassifier(class_weight='balanced', random_state=42),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 20, None],
                "min_samples_leaf": [1, 2]
            }
        },
        "NaiveBayes": {
            "model": MultinomialNB(),
            "params": {
                "alpha": [0.001, 0.01, 0.1, 1.0]
            }
        },
        "NeuralNetwork": {
            "model": MLPClassifier(random_state=42, early_stopping=True),
            "params": {
                "hidden_layer_sizes": [(100,), (100, 50), (50, 25)],
                "alpha": [0.0001, 0.001, 0.01],
                "learning_rate_init": [0.001]
            }
        }
    }
    
    best_models = {}
    
    # 5. Perform Grid Search and Train
    for name, config in model_configs.items():
        print(f"\nTuning hyperparameters for {name} using Grid Search CV...")
        grid = GridSearchCV(
            estimator=config["model"],
            param_grid=config["params"],
            cv=cv,
            scoring="f1",
            n_jobs=-1,
            verbose=1
        )
        grid.fit(X_train, y_train)
        
        print(f"Best parameters found for {name}: {grid.best_params_}")
        print(f"Best CV F1-Score: {grid.best_score_:.4f}")
        
        # Save the best model
        best_model = grid.best_estimator_
        model_path = os.path.join(MODELS_DIR, f"{name}_best_model.joblib")
        joblib.dump(best_model, model_path)
        print(f"Saved {name} best model to {model_path}")
        
        best_models[name] = best_model
        
    # 6. Train soft-voting Ensemble
    from sklearn.ensemble import VotingClassifier
    print("\nTraining Soft-Voting Ensemble Classifier...")
    ensemble_clf = VotingClassifier(
        estimators=[
            ('lr', best_models['LogisticRegression']),
            ('rf', best_models['RandomForest']),
            ('nb', best_models['NaiveBayes']),
            ('nn', best_models['NeuralNetwork'])
        ],
        voting='soft'
    )
    ensemble_clf.fit(X_train, y_train)
    
    ensemble_path = os.path.join(MODELS_DIR, "VotingEnsemble_best_model.joblib")
    joblib.dump(ensemble_clf, ensemble_path)
    print(f"Saved VotingEnsemble model to {ensemble_path}")
    best_models["VotingEnsemble"] = ensemble_clf
        
    return best_models, extractor, X_train, X_test, y_train, y_test

if __name__ == "__main__":
    cleaned_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_emails.csv")
    if os.path.exists(cleaned_path):
        train_and_tune_models(cleaned_path)
    else:
        print(f"Cleaned data file not found at {cleaned_path}. Run preprocessing.py first.")
