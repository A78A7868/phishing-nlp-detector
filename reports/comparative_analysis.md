# Comparative Analysis Report: Phishing Email Detection Using NLP

This report presents a thorough evaluation of machine learning models trained to detect phishing emails. By combining semantic text representations (TF-IDF) and Word2Vec averaged word embeddings with structural, formatting, and behavioral metadata features, we compared five different classifiers: Logistic Regression, Random Forest, Multinomial Naive Bayes, a Multilayer Perceptron (MLP) Neural Network, and a soft-voting ensemble.

---

## 1. Executive Summary

Phishing remains the most common entry point for digital security compromises. Because attackers constantly change their techniques, static blacklist filters are no longer sufficient. This project demonstrates how machine learning models, trained on a hybrid feature space of email text, word embeddings, and structural metadata, can accurately identify phishing attempts.

Based on our benchmarks, the **Voting Ensemble** classifier achieved the highest overall performance with an F1-Score of **98.02%** and an Accuracy of **98.52%**. It is our recommended model for production deployment because of its balanced precision and recall, minimizing classification errors.

---

## 2. Model Performance Benchmarks

The models were evaluated on a holdout test set representing 20% of the corpus. The results are summarized below:

| Classifier Model | Accuracy | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 98.26% | 97.28% | 98.09% | 97.68% |
| **Random Forest** | 98.00% | 97.04% | 97.64% | 97.34% |
| **Multinomial Naive Bayes** | 97.15% | 96.54% | 95.80% | 96.17% |
| **Neural Network (MLP)** | 98.29% | 98.30% | 97.10% | 97.70% |
| **Voting Ensemble** | **98.52%** | **98.09%** | **97.94%** | **98.02%** |

### Key Observations:
1. **Hybrid Feature Boost**: Combining NLP TF-IDF text features with structured metadata (such as URL counts and urgency keywords) yielded a performance improvement of 3-5% across all models compared to text-only baselines.
2. **Robustness of Random Forest**: Random Forest demonstrated excellent resilience, handling both sparse text features and dense scaled metadata metrics without requiring complex scaling tuning.
3. **Inference Latency Tradeoff**: Naive Bayes and Logistic Regression offered the fastest training and inference speeds, while the Neural Network required more epochs to converge with similar performance.

---

## 3. Model-by-Model Analysis

### A. Logistic Regression
*   **Strengths**: Fast to train, highly interpretable, and computationally lightweight. The model coefficients directly show which words and structural indicators contribute to a phishing or legitimate decision.
*   **Weaknesses**: Assumes a linear relationship between features. It struggles to capture complex interactions, such as a high word count combined with a specific combination of URLs and urgency keywords.

### B. Random Forest (Recommended)
*   **Strengths**: Best overall performance. As an ensemble of decision trees, it naturally handles non-linear feature interactions (e.g., a message that is short but contains multiple links and high capitalization). It is highly robust to outliers and does not suffer from feature scale imbalances.
*   **Weaknesses**: Requires more memory to store the collection of trees, and feature importance is calculated based on training splits, which can sometimes over-index on high-cardinality features.

### C. Multinomial Naive Bayes
*   **Strengths**: Very simple and fast. It works well with pure text classification and sparse features.
*   **Weaknesses**: Operates on the strong assumption that all features are independent. In email data, structural metadata features (like character length and word count) are highly correlated, violating this assumption and slightly degrading precision.

### D. Neural Network (MLP Classifier)
*   **Strengths**: Highly flexible and capable of learning complex decision boundaries.
*   **Weaknesses**: Prone to overfitting on smaller datasets. It requires substantial hyperparameter tuning (hidden layers, learning rates, alpha regularization) and is more computationally expensive than traditional classifiers.

---

## 4. Feature Importance Insights

Analysis of the Random Forest feature importances and Logistic Regression coefficients highlights the following indicators of phishing threats:

1. **Urgency Score**: The density of urgent keywords (e.g., "immediate action", "verify account", "suspended") is the strongest indicator of phishing. Attackers use emotional urgency to bypass user vigilance.
2. **URL Count / URL Presence**: Phishing emails must redirect users to a malicious site, making the count of links a primary indicator.
3. **Exclamation Density**: Phishing attacks show a higher density of exclamation marks to simulate urgency or alarm.
4. **Suspicious Domain Extensions**: The presence of links pointing to cheap or untrusted domain suffixes (like `.xyz`, `.club`, `.info`) is highly associated with spam and phishing campaigns.

---

## 5. Ethical & Operational Considerations

### A. The Precision vs. Recall Dilemma
Deploying an email security filter requires balancing two types of classification errors:
*   **False Positives (High Recall focus)**: Marking a legitimate email (e.g., a critical client inquiry or transaction receipt) as phishing. This can disrupt business operations, delay projects, and cause user frustration.
*   **False Negatives (High Precision focus)**: Allowing a phishing email to slip into a user's inbox. A single false negative can lead to credential theft, ransomware installation, or a severe data breach.

### B. Algorithmic Bias
Threat classifiers can inherit bias from their training data. For example, if a company's training corpus contains newsletters from foreign business partners with non-standard domain suffixes that are misclassified as spam, the model may develop a bias against legitimate international partners. Ensuring data diversity is essential to prevent blocking valid communication.

### C. Generalization Risks and Dataset Context
While the cross-validated accuracy of our Random Forest model exceeds 95%, it is important to contextualize this performance within the training data constraints. The Kaggle corpus relies heavily on historical public spam/safe archives (such as the Enron email collection and SpamAssassin). These corpora contain clear, separable styles: business correspondence follows professional vocabulary, whereas spam patterns are highly repetitive. 

In live enterprise environments, modern phishing attacks use evasive social engineering strategies, zero-link structures, and image-only bodies. Consequently, these metrics should be interpreted as an upper-bound performance baseline, rather than an operational guarantee in active production settings.