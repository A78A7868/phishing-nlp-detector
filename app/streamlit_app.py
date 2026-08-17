import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Add src to sys.path so we can import PhishingFeatureExtractor and clean_text
import sys
sys.path.append(SRC_DIR)

from preprocessing import clean_text
from feature_engineering import PhishingFeatureExtractor

# Configure Streamlit page
st.set_page_config(
    page_title="AI Phishing Email Detector",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Premium UI Styling using Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #555555;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        margin-bottom: 1.5rem;
    }
    
    .safe-result {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        border-radius: 12px;
        padding: 20px;
        color: #0f5132;
        font-weight: 600;
        text-align: center;
        font-size: 1.4rem;
        border: 1px solid #badbcc;
    }
    
    .phish-result {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
        border-radius: 12px;
        padding: 20px;
        color: #842029;
        font-weight: 600;
        text-align: center;
        font-size: 1.4rem;
        border: 1px solid #f8d7da;
    }
    
    .metric-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# App Title & Subtitle
st.markdown("<div class='main-title'>🛡️ AI-Driven Phishing Email Detector</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Analyze text content and structural patterns to identify cybersecurity email threats live.</div>", unsafe_allow_html=True)

# Helper function to check if models exist
@st.cache_resource
def load_ml_resources():
    extractor_path = os.path.join(MODELS_DIR, "feature_extractor.joblib")
    if not os.path.exists(extractor_path):
        return None, {}
        
    extractor = joblib.load(extractor_path)
    
    models = {}
    model_names = ["LogisticRegression", "RandomForest", "NaiveBayes", "NeuralNetwork", "VotingEnsemble"]
    for name in model_names:
        model_path = os.path.join(MODELS_DIR, f"{name}_best_model.joblib")
        if os.path.exists(model_path):
            models[name] = joblib.load(model_path)
            
    return extractor, models

# Sidebar controls
st.sidebar.markdown("### ⚙️ Model Controls")
extractor, models = load_ml_resources()

if extractor is None or not models:
    st.sidebar.error("⚠️ No models detected! Run the pipeline in the terminal first to train the classifiers.")
    st.info("💡 Get started by running `python src/train_pipeline.py` in your terminal to train and serialize the models, then refresh this page.")
else:
    selected_model_name = st.sidebar.selectbox(
        "Select ML Classifier:",
        list(models.keys()),
        index=list(models.keys()).index("VotingEnsemble") if "VotingEnsemble" in models else 0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🔬 Features Extracted
    The models analyze combined text (TF-IDF) and **12 custom structural indicators**:
    - **URL indicators**: Presence and count of links.
    - **Urgency signals**: Count of high-stress words (e.g. *verify*, *urgent*, *limited*).
    - **Formatting patterns**: Exclamation density, all-caps words, and punctuation rates.
    - **Sender domain info**: Email counts and suspicious suffixes.
    """)

# User input text area
st.markdown("### 📝 Paste Email Message")
email_input = st.text_area(
    "Paste the full email headers and body below for instant classification analysis:",
    height=220,
    placeholder="Dear customer, your bank account has been limited due to unusual activity. Click here to verify: http://secure-verify.net/auth..."
)

if st.button("🚀 Run Threat Analysis", use_container_width=True):
    if not email_input.strip():
        st.warning("Please paste some email text first.")
    elif extractor is None:
        st.error("Cannot run prediction because feature extractor and models are missing. Please build the pipeline first.")
    else:
        # 1. Clean the text
        cleaned_text = clean_text(email_input)
        
        # 2. Structure as DataFrame for feature extractor
        input_df = pd.DataFrame([{
            "Email Text": email_input,
            "Cleaned Text": cleaned_text
        }])
        
        # 3. Extract features using custom extractor
        with st.spinner("Extracting linguistic and structural metadata features..."):
            features_matrix = extractor.transform(input_df)
            meta_features = extractor.extract_metadata_features(input_df["Email Text"])[0]
            feature_names = extractor.get_metadata_feature_names()
            
        # 4. Predict using selected model
        model = models[selected_model_name]
        prediction = model.predict(features_matrix)[0]
        
        # Get probability/confidence score
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features_matrix)[0]
            confidence = probs[prediction]
        else:
            confidence = 1.0 # fallback if probability is not supported
            
        # 5. Display Prediction Result
        st.markdown("### 🔍 Classification Result")
        if prediction == 1:
            st.markdown(f"<div class='phish-result'>🚨 Warning: Classified as PHISHING EMAIL<br><span style='font-size:0.95rem; font-weight:normal;'>Confidence Score: {confidence*100:.2f}% ({selected_model_name})</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='safe-result'>✅ Clear: Classified as LEGITIMATE EMAIL<br><span style='font-size:0.95rem; font-weight:normal;'>Confidence Score: {confidence*100:.2f}% ({selected_model_name})</span></div>", unsafe_allow_html=True)
            
        # 6. Detailed Feature Metrics Breakdown
        st.markdown("### 📊 Extracted Metadata Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"<div class='metric-box'>🔗 Link Count<br><span class='metric-value'>{int(meta_features[0])}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'>🚨 Urgency Score<br><span class='metric-value'>{int(meta_features[3])}</span></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'>❗ Exclamation count<br><span class='metric-value'>{int(meta_features[6])}</span></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-box'>🔤 CAPS Ratio<br><span class='metric-value'>{meta_features[10]*100:.1f}%</span></div>", unsafe_allow_html=True)
            
        # Complete metadata table
        df_meta_display = pd.DataFrame({
            "Metadata Attribute": [
                "Total URL Count", "URL Presence (Binary)", "Email Address Count",
                "Urgency Pattern Matches", "Character Length", "Word Count",
                "Exclamation Mark Count", "Exclamation Density", "Punctuation Count",
                "Punctuation Density", "Uppercase Letter Ratio", "Suspicious Domain Matches"
            ],
            "Raw Value": [
                int(meta_features[0]), "Yes" if meta_features[1] == 1 else "No", int(meta_features[2]),
                int(meta_features[3]), int(meta_features[4]), int(meta_features[5]),
                int(meta_features[6]), f"{meta_features[7]*100:.3f}%", int(meta_features[8]),
                f"{meta_features[9]*100:.3f}%", f"{meta_features[10]*100:.1f}%", int(meta_features[11])
            ],
            "Threat Significance": [
                "Phishing links mimic target brands or host exploit kits",
                "Legitimate transactional mail rarely includes arbitrary login links",
                "Attackers use contact emails to divert communication channels",
                "Fake urgency forces immediate clicks, bypassing safety checks",
                "Long emails often indicate formal text; short ones indicate rapid instructions",
                "Word counts help calculate vocabulary and punctuation densities",
                "High exclamation usage creates emotional manipulation",
                "Proportion of exclamations to character length",
                "Suspicious punctuation marks are often used to split words",
                "Ratio of total punctuation marks relative to overall text length",
                "High CAPS indicates urgency/threat statements (e.g. ATTENTION)",
                "Matches suspicious extensions (e.g. .xyz, .info, .tk)"
            ]
        })
        
        st.dataframe(df_meta_display, use_container_width=True)
        
        # Preprocessed Text View
        with st.expander("👁️ View preprocessed text passed to NLP layer"):
            st.write(f"**Cleaned Text (stopwords and punctuation removed):**")
            st.code(cleaned_text if cleaned_text else "[Empty after cleaning]")
