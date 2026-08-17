import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Styling configuration for plots
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 0.8,
    'figure.facecolor': 'white',
    'grid.color': '#eeeeee'
})

def evaluate_models():
    """
    Loads test set, models, and feature extractor. Runs evaluation on each model,
    saves confusion matrices and feature importance charts, and prints/returns comparative summary.
    """
    test_path = os.path.join(BASE_DIR, "data", "processed", "test_set.csv")
    extractor_path = os.path.join(BASE_DIR, "models", "feature_extractor.joblib")
    
    if not (os.path.exists(test_path) and os.path.exists(extractor_path)):
        raise FileNotFoundError("Missing test set or feature extractor. Run models.py first.")
        
    test_df = pd.read_csv(test_path)
    extractor = joblib.load(extractor_path)
    
    # Extract features from test set
    X_test = extractor.transform(test_df)
    y_test = test_df["Label"].values
    
    model_names = ["LogisticRegression", "RandomForest", "NaiveBayes", "NeuralNetwork", "VotingEnsemble"]
    results = []
    
    # Ensure figures dir exists
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # For ROC curve comparison plotting
    plt.figure(figsize=(8, 6))
    
    for name in model_names:
        model_path = os.path.join(BASE_DIR, "models", f"{name}_best_model.joblib")
        if not os.path.exists(model_path):
            print(f"Warning: Model file for {name} not found. Skipping.")
            continue
            
        model = joblib.load(model_path)
        y_pred = model.predict(X_test)
        
        # Check if model supports predict_proba
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            # For models that might not (though MLP, LR, RF, NB all do in scikit-learn)
            y_prob = y_pred
            
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1
        })
        
        # Plot ROC curve for this model
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.4f})')
        
        # 1. Plot and save Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues", cbar=False,
            xticklabels=["Safe", "Phishing"], yticklabels=["Safe", "Phishing"],
            annot_kws={"size": 14, "weight": "bold"}
        )
        plt.title(f"Confusion Matrix - {name}", fontsize=14, pad=15, weight="bold", color="#111111")
        plt.ylabel("Actual Label", fontsize=12, labelpad=10)
        plt.xlabel("Predicted Label", fontsize=12, labelpad=10)
        plt.tight_layout()
        
        cm_fig_path = os.path.join(FIGURES_DIR, f"confusion_matrix_{name}.png")
        plt.savefig(cm_fig_path, dpi=300)
        plt.close()
        print(f"Saved confusion matrix plot for {name} to {cm_fig_path}")
        
        # 2. Plot Feature Importance (for Logistic Regression coefficients and Random Forest importance)
        if name in ["LogisticRegression", "RandomForest"]:
            feature_names = extractor.feature_names
            
            if name == "LogisticRegression":
                # Coefficients for binary classification (shape: 1, n_features)
                importances = model.coef_[0]
                title = "Logistic Regression Feature Coefficients"
                # Use magnitude for plotting importances, but keep sign for info
                indices = np.argsort(np.abs(importances))[::-1][:15] # Top 15 features
            else:
                importances = model.feature_importances_
                title = "Random Forest Feature Importance"
                indices = np.argsort(importances)[::-1][:15] # Top 15 features
                
            top_features = [feature_names[i] for i in indices]
            top_importances = importances[indices]
            
            plt.figure(figsize=(10, 6))
            colors = ["#1f77b4" if x >= 0 else "#d62728" for x in top_importances] if name == "LogisticRegression" else "#2ca02c"
            
            # Label bars
            bars = plt.barh(range(len(indices)), top_importances, color=colors, align="center")
            plt.yticks(range(len(indices)), top_features, fontsize=10)
            plt.gca().invert_yaxis() # Top features at the top
            
            # Format titles
            plt.title(title + " (Top 15)", fontsize=14, pad=15, weight="bold", color="#111111")
            plt.xlabel("Coefficient Value" if name == "LogisticRegression" else "Gini Importance Score", fontsize=12, labelpad=10)
            plt.tight_layout()
            
            imp_fig_path = os.path.join(FIGURES_DIR, f"feature_importance_{name}.png")
            plt.savefig(imp_fig_path, dpi=300)
            plt.close()
            print(f"Saved feature importance plot for {name} to {imp_fig_path}")

    # Finalize and save the ROC curve comparison plot
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12, labelpad=10)
    plt.ylabel('True Positive Rate', fontsize=12, labelpad=10)
    plt.title('ROC Curve Comparison', fontsize=14, pad=15, weight="bold", color="#111111")
    plt.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    roc_fig_path = os.path.join(FIGURES_DIR, "roc_curve_comparison.png")
    plt.savefig(roc_fig_path, dpi=300)
    plt.close()
    print(f"Saved ROC curve comparison plot to {roc_fig_path}")

    # Generate summary comparison table
    df_results = pd.DataFrame(results)
    summary_path = os.path.join(REPORTS_DIR, "metrics_comparison.csv")
    df_results.to_csv(summary_path, index=False)
    
    print("\n" + "="*50)
    print("             MODEL EVALUATION SUMMARY             ")
    print("="*50)
    print(df_results.to_string(index=False, formatters={
        "Accuracy": "{:.4f}".format,
        "Precision": "{:.4f}".format,
        "Recall": "{:.4f}".format,
        "F1-Score": "{:.4f}".format
    }))
    print("="*50 + "\n")
    
    return df_results

if __name__ == "__main__":
    evaluate_models()
