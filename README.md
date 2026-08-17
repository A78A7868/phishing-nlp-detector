# AI-Driven Phishing Email Detection Using NLP and Machine Learning

This repository implements a complete, working machine learning project to detect phishing emails using natural language processing (NLP) and structural metadata features. It trains and compares multiple classic machine learning models to identify threat patterns.

---

## 🛡️ Project Overview

Phishing attacks remain one of the most critical cybersecurity threat vectors. Since attackers constantly adapt, standard static signature filters are insufficient. This project builds a hybrid machine learning classifier that analyzes:
1.  **Linguistic Semantics (NLP)**: Vocabulary, terminology, and syntax extracted via TF-IDF bigrams.
2.  **Structural & Formatting Metadata**: Behavioral signals including URL densities, email address counts, panic/urgency keyword frequencies, uppercase usage, and exclamation mark counts.

---

## 📁 Repository Structure

```
phishing-nlp-detector/
├── app/
│   └── streamlit_app.py          # Interactive Streamlit classification dashboard
├── data/
│   ├── raw/                      # Downloaded/generated raw corpus
│   └── processed/                # Preprocessed and cleaned dataset
├── models/                       # Saved serializers (.joblib models and vectorizers)
├── notebooks/
│   └── phishing_detection.ipynb  # Executable Jupyter Notebook demonstrating the pipeline
├── reports/
│   ├── comparative_analysis.md   # Written report comparing classifiers and tradeoffs
│   ├── IEEE_Report.docx          # Academic research paper (IEEE two-column layout)
│   └── figures/                  # Generated performance charts (CM, Feature Importance)
├── slides/
│   └── presentation_outline.md   # Slide-by-slide bullet content and speaker notes
├── src/
│   ├── data_loader.py            # Dataset retriever with fallback synthetic generation
│   ├── preprocessing.py          # HTML stripping, tokenization, and stopword removal
│   ├── feature_engineering.py    # Hybrid TF-IDF + metadata feature matrix compiler
│   ├── models.py                 # Stratified split and hyperparameter CV grid search
│   ├── evaluate.py               # Accuracy/Precision/Recall/F1 metrics and visualization
│   ├── train_pipeline.py         # Main orchestration pipeline coordinator
│   ├── generate_docx_report.py   # Programmatically compiles IEEE Word Report
│   └── generate_markdown_report.py # Programmatically compiles Markdown report
├── requirements.txt              # Package dependencies list
└── README.md                     # Project documentation
```

---

## ⚙️ Installation & Setup

Ensure you have **Python 3.10+** installed. Clone the repository and follow these instructions:

1.  **Navigate to the project root**:
    ```bash
    cd phishing-nlp-detector
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

---

## 🚀 Running the Project

### 1. Run the ML Pipeline (Data -> Clean -> Train -> Evaluate)
Execute the orchestrator script to run the entire pipeline end-to-end. This loads data, preprocesses text, tunes model parameters with Stratified 5-Fold Cross-Validation, saves the models, generates plots, and programmatically compiles both the markdown and IEEE DOCX reports:
```bash
python src/train_pipeline.py
```

### 2. Launch the Streamlit Live Demo App
Query your trained models in real-time. Paste email bodies, view extracted indicators, choose different classifiers, and check prediction confidence:
```bash
streamlit run app/streamlit_app.py
```

### 3. Open the Jupyter Notebook
Run the step-by-step pipeline visually:
```bash
jupyter notebook notebooks/phishing_detection.ipynb
```

---

## 🔬 Learning Outcomes

This project demonstrates several core concepts at the intersection of cybersecurity and artificial intelligence:

*   **NLP in threat intelligence**: How text representation and vectorization extract security features from unstructured communication channels.
*   **Feature Combination**: Merging sparse text matrices (TF-IDF) with dense scaled numerical metadata columns using MinMax scaling, showing how hybrid models outperform text-only baselines.
*   **Model Trade-offs**: Evaluating classifiers based not only on accuracy but also on inference speed (critical for live email gateway filtering) and interpretability (e.g., Logistic Regression coefficients).
*   **Ethical Trade-offs**:
    *   *False Positives* block legitimate emails, causing operational delays and user frustration.
    *   *False Negatives* allow phishing attempts to slip through, risking security compromises.
    *   *Data Bias* can result in filters disproportionately flag legitimate international mails or newsletter variations if training sets are unbalanced.
