"""
generate_ppt_report.py
Professional 11-slide presentation — no emojis, humanised language.
"""

import os
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_CSV_PATH  = os.path.join(BASE_DIR, "reports", "metrics_comparison.csv")
OUTPUT_PPTX_PATH  = os.path.join(BASE_DIR, "slides", "presentation.pptx")
FIGURES_DIR       = os.path.join(BASE_DIR, "reports", "figures")

# ── Colour palette ───────────────────────────────────────────────────────────
C_BG      = RGBColor( 13,  17,  38)   # deep navy background
C_CARD    = RGBColor( 22,  32,  58)   # card fill
C_BORDER  = RGBColor( 49,  67, 112)   # card border
C_WHITE   = RGBColor(236, 242, 255)   # primary text
C_MUTED   = RGBColor(150, 168, 210)   # secondary / body text
C_ACCENT  = RGBColor( 14, 165, 233)   # sky-blue accent (headings, labels)
C_GREEN   = RGBColor( 34, 197,  94)   # success highlight
C_RED     = RGBColor(220,  60,  60)   # danger / negative
C_GOLD    = RGBColor(245, 185,  40)   # best-result highlight

W = Inches(13.333)
H = Inches(7.5)


# ── Low-level helpers ────────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=C_BG):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def box(slide, l, t, w, h, fill=C_CARD, border=C_BORDER, bpt=1.2, rounded=True):
    shp = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shp, l, t, w, h)
    s.fill.solid();  s.fill.fore_color.rgb = fill
    s.line.color.rgb = border;  s.line.width = Pt(bpt)
    return s


def flat_rect(slide, l, t, w, h, fill):
    """Thin flat rectangle (no border) — for accent bars."""
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    s.fill.solid();  s.fill.fore_color.rgb = fill
    s.line.fill.background()
    return s


def tb(slide, l, t, w, h):
    tf = slide.shapes.add_textbox(l, t, w, h).text_frame
    tf.word_wrap = True
    return tf


def p_add(tf, text, font="Calibri", size=13, bold=False, italic=False,
          color=C_WHITE, align=PP_ALIGN.LEFT, sb=0, sa=5, first=False):
    """Add a paragraph (or reuse first paragraph)."""
    if first:
        p = tf.paragraphs[0]
        p.clear()
    else:
        p = tf.add_paragraph()
    r = p.add_run()
    r.text = text
    r.font.name   = font
    r.font.size   = Pt(size)
    r.font.bold   = bold
    r.font.italic = italic
    r.font.color.rgb = color
    p.alignment    = align
    p.space_before = Pt(sb)
    p.space_after  = Pt(sa)
    return p


def bullet_item(tf, label, detail, size=13):
    """One bullet: bold accent label + muted detail in same paragraph — properly separated."""
    p = tf.add_paragraph()
    p.space_before = Pt(0)
    p.space_after  = Pt(7)
    # label run
    rl = p.add_run()
    rl.text = label
    rl.font.name  = "Calibri"
    rl.font.size  = Pt(size)
    rl.font.bold  = True
    rl.font.color.rgb = C_ACCENT
    # detail run
    rd = p.add_run()
    rd.text = "  " + detail
    rd.font.name  = "Calibri"
    rd.font.size  = Pt(size)
    rd.font.bold  = False
    rd.font.color.rgb = C_MUTED


def plain_bullet(tf, text, size=13, color=C_WHITE):
    """A plain (non-labelled) bullet line."""
    p = tf.add_paragraph()
    p.space_before = Pt(0)
    p.space_after  = Pt(7)
    r = p.add_run()
    r.text = text
    r.font.name  = "Calibri"
    r.font.size  = Pt(size)
    r.font.color.rgb = color


def thin_rule(tf, color=C_BORDER):
    """Visual horizontal separator between heading and bullets."""
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = "\u2500" * 34
    r.font.name  = "Calibri"
    r.font.size  = Pt(7)
    r.font.color.rgb = color
    p.space_after = Pt(6)


def slide_header(slide, title, sub="CYBERSECURITY  \u00b7  NLP  \u00b7  MACHINE LEARNING"):
    # Category label
    tf_c = tb(slide, Inches(0.8), Inches(0.28), Inches(12.0), Inches(0.3))
    p_add(tf_c, sub, font="Calibri", size=8, bold=True,
          color=C_ACCENT, first=True)
    # Thin rule under category
    flat_rect(slide, Inches(0.8), Inches(0.60), Inches(12.0), Pt(1.0), C_BORDER)
    # Slide title
    tf_t = tb(slide, Inches(0.8), Inches(0.62), Inches(12.0), Inches(0.95))
    p_add(tf_t, title, font="Trebuchet MS", size=28, bold=True,
          color=C_WHITE, first=True, sa=0)


def card_heading(tf, title, color=C_ACCENT, size=17):
    """Clean card heading — bold, accent colour, on its own paragraph."""
    p = tf.paragraphs[0]
    p.clear()
    r = p.add_run()
    r.text = title
    r.font.name  = "Trebuchet MS"
    r.font.size  = Pt(size)
    r.font.bold  = True
    r.font.color.rgb = color
    p.space_after = Pt(8)


# ── Metrics loader ───────────────────────────────────────────────────────────

def load_metrics():
    m = {
        "LR": {"Acc": "98.26%", "Prec": "97.28%", "Rec": "98.09%", "F1": "97.68%"},
        "RF": {"Acc": "98.00%", "Prec": "97.04%", "Rec": "97.64%", "F1": "97.34%"},
        "NB": {"Acc": "97.15%", "Prec": "96.54%", "Rec": "95.80%", "F1": "96.17%"},
        "NN": {"Acc": "98.29%", "Prec": "98.30%", "Rec": "97.10%", "F1": "97.70%"},
        "VE": {"Acc": "98.52%", "Prec": "98.09%", "Rec": "97.94%", "F1": "98.02%"},
    }
    if os.path.exists(METRICS_CSV_PATH):
        df = pd.read_csv(METRICS_CSV_PATH)
        km = {"LogisticRegression": "LR", "RandomForest": "RF",
              "NaiveBayes": "NB", "NeuralNetwork": "NN", "VotingEnsemble": "VE"}
        for _, row in df.iterrows():
            k = km.get(row["Model"])
            if k:
                m[k] = {
                    "Acc":  f"{row['Accuracy']*100:.2f}%",
                    "Prec": f"{row['Precision']*100:.2f}%",
                    "Rec":  f"{row['Recall']*100:.2f}%",
                    "F1":   f"{row['F1-Score']*100:.2f}%",
                }
    return m


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def s1_title(prs):
    """Slide 1 — Title"""
    s = blank(prs);  bg(s)
    # Outer frame
    box(s, Inches(0.45), Inches(0.45), Inches(12.43), Inches(6.6),
        fill=RGBColor(18, 26, 50), border=C_BORDER)
    # Top accent bar
    flat_rect(s, Inches(0.45), Inches(0.45), Inches(12.43), Inches(0.1), C_ACCENT)

    # Main title
    tf = tb(s, Inches(1.2), Inches(1.5), Inches(10.9), Inches(2.0))
    p_add(tf, "AI-Driven Phishing Email Detection",
          font="Trebuchet MS", size=44, bold=True, color=C_WHITE, first=True, sa=4)
    p_add(tf, "Using NLP  (Natural Language Processing)",
          font="Trebuchet MS", size=32, bold=False, color=C_ACCENT, sa=0)

    # Tagline
    tf2 = tb(s, Inches(1.2), Inches(3.65), Inches(10.9), Inches(0.6))
    p_add(tf2, "A comparative study of hybrid text-feature and metadata-driven ensemble classifiers "
               "for automated cyber-threat filtering.",
          font="Calibri", size=15, italic=True, color=C_MUTED, first=True)

    # Separator
    flat_rect(s, Inches(1.2), Inches(4.45), Inches(5.0), Pt(1.2), C_ACCENT)

    # Author block
    tf3 = tb(s, Inches(1.2), Inches(4.6), Inches(10.9), Inches(1.9))
    p_add(tf3, "Anand Krishna G R Nair",
          font="Trebuchet MS", size=18, bold=True, color=C_WHITE, first=True, sa=3)
    p_add(tf3, "Registration No: 596563     |     anandkrishnag.rnair@gmail.com",
          font="Calibri", size=13, color=C_ACCENT, sa=3)
    p_add(tf3, "Department of Computer Science and Engineering  \u00b7  IICT, New Delhi \u2014 110092",
          font="Calibri", size=12, color=C_MUTED, sa=2)
    p_add(tf3, "Tools: Python  \u00b7  Scikit-Learn  \u00b7  Gensim Word2Vec  \u00b7  Streamlit  \u00b7  NLTK  \u00b7  spaCy",
          font="Calibri", size=11, italic=True, color=C_MUTED, sa=0)


def s2_objectives(prs):
    """Slide 2 — Project Objectives"""
    s = blank(prs);  bg(s)
    slide_header(s, "Project Objectives")

    cols = [
        ("Proactive Threat Defense", C_ACCENT, Inches(0.5), [
            ("Objective",
             "Build a classifier that detects phishing emails before they reach the user's inbox."),
            ("Gap addressed",
             "Signature-based blacklists fail against zero-day and spear-phishing variants."),
            ("Design goal",
             "The system must generalise to unseen email text without manual rule updates."),
        ]),
        ("Hybrid Feature Engineering", C_GOLD, Inches(4.75), [
            ("Text semantics",
             "TF-IDF extracts vocabulary patterns across unigrams, bigrams, and trigrams."),
            ("Word embeddings",
             "Custom Word2Vec captures latent intent that simple word counts miss."),
            ("Structural signals",
             "Metadata features (link density, urgency score) add behavioural context."),
        ]),
        ("Model Comparison", C_GREEN, Inches(9.0), [
            ("Scope",
             "Four classic ML classifiers are trained, tuned, and benchmarked side by side."),
            ("Ensemble",
             "A soft-voting classifier combines model outputs for maximum stability."),
            ("Target",
             "Achieve above 98% F1-Score on the stratified holdout test set."),
        ]),
    ]

    cw = Inches(3.85);  ch = Inches(5.45);  ct = Inches(1.68)
    for (title, color, x, items) in cols:
        box(s, x, ct, cw, ch)
        tf = tb(s, x + Inches(0.18), ct + Inches(0.18),
                cw - Inches(0.36), ch - Inches(0.36))
        card_heading(tf, title, color=color, size=16)
        thin_rule(tf)
        for lbl, det in items:
            bullet_item(tf, lbl, det, size=12)


def s3_threat(prs):
    """Slide 3 — Threat Landscape"""
    s = blank(prs);  bg(s)
    slide_header(s, "The Threat Landscape  and  the NLP Solution")

    # Left card
    box(s, Inches(0.5), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_l = tb(s, Inches(0.68), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_l, "Limitations of Conventional Filters", color=C_RED, size=16)
    thin_rule(tf_l, C_RED)
    bullet_item(tf_l, "Scale of the problem",
                "Over 90% of network intrusions begin with a phishing email.", 13)
    bullet_item(tf_l, "Blacklist failure",
                "Attackers rotate domains and URLs faster than signature databases can update.", 13)
    bullet_item(tf_l, "Human targeting",
                "Social engineering exploits cognitive biases, not software vulnerabilities.", 13)
    bullet_item(tf_l, "Zero-day gap",
                "No static rule can block a threat it has never seen before.", 13)

    # Arrow
    arr = tb(s, Inches(6.5), Inches(3.6), Inches(0.7), Inches(0.55))
    p_add(arr, "\u2192", font="Trebuchet MS", size=34, bold=True,
          color=C_ACCENT, align=PP_ALIGN.CENTER, first=True)

    # Right card
    box(s, Inches(7.05), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_r = tb(s, Inches(7.23), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_r, "Why NLP Changes the Game", color=C_GREEN, size=16)
    thin_rule(tf_r, C_GREEN)
    bullet_item(tf_r, "Semantic understanding",
                "TF-IDF and Word2Vec surface urgency triggers that rules can never capture.", 13)
    bullet_item(tf_r, "Vocabulary resilience",
                "Dense embeddings generalise across synonyms without retraining.", 13)
    bullet_item(tf_r, "Behavioural indicators",
                "Capitalisation ratios, link counts, and punctuation density expose automated templates.", 13)
    bullet_item(tf_r, "Ensemble power",
                "Combining four models via soft-voting minimises individual classifier weaknesses.", 13)


def s4_pipeline(prs):
    """Slide 4 — Data Processing Pipeline"""
    s = blank(prs);  bg(s)
    slide_header(s, "Data Processing Pipeline")

    steps = [
        ("Step 1", "Data Ingestion", [
            ("Source",     "18,650 raw emails from the public Kaggle Phishing Email dataset."),
            ("Handling",   "Missing email bodies are detected and removed before processing."),
            ("Dedup",      "1,115 duplicate texts are dropped to prevent train/test data leakage."),
        ]),
        ("Step 2", "HTML Stripping", [
            ("Parser",     "BeautifulSoup parses and removes all HTML markup and inline styles."),
            ("Scope",      "Script, style, and formatting tags are eliminated entirely."),
            ("Output",     "Clean plaintext email body is extracted for downstream use."),
        ]),
        ("Step 3", "Tokenisation", [
            ("Splitting",  "Email body is split into individual word tokens per message."),
            ("Normalise",  "All tokens are lowercased to ensure case-insensitive matching."),
            ("Filter",     "Punctuation marks and non-alphabetic characters are discarded."),
        ]),
        ("Step 4", "Stopword Removal", [
            ("Remove",     "Common English stopwords such as 'the', 'is', and 'at' are stripped."),
            ("Retain",     "Meaningful content-bearing tokens are preserved for vectorisation."),
            ("Result",     "17,535 clean, deduplicated email records saved to processed CSV."),
        ]),
    ]

    cw = Inches(2.9);  ch = Inches(5.45);  ct = Inches(1.68)
    for i, (num_lbl, title, items) in enumerate(steps):
        x = Inches(0.4) + i * Inches(3.15)
        box(s, x, ct, cw, ch)

        # Step number badge
        badge = box(s, x + Inches(0.15), ct + Inches(0.15),
                    Inches(0.92), Inches(0.42),
                    fill=C_ACCENT, border=C_ACCENT, rounded=False)
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0];  p_b.clear()
        rb = p_b.add_run();  rb.text = num_lbl
        rb.font.name = "Trebuchet MS";  rb.font.size = Pt(11)
        rb.font.bold = True;  rb.font.color.rgb = C_BG
        p_b.alignment = PP_ALIGN.CENTER

        # Card body
        tf = tb(s, x + Inches(0.14), ct + Inches(0.7),
                cw - Inches(0.28), ch - Inches(0.88))
        p_add(tf, title, font="Trebuchet MS", size=14, bold=True,
              color=C_WHITE, first=True, sa=8)
        thin_rule(tf)
        for lbl, det in items:
            bullet_item(tf, lbl, det, size=11)

        # Flow arrow
        if i < len(steps) - 1:
            arr = tb(s, x + cw + Inches(0.08), ct + Inches(2.45),
                     Inches(0.2), Inches(0.45))
            p_add(arr, "\u25b6", font="Calibri", size=15, bold=True,
                  color=C_ACCENT, align=PP_ALIGN.CENTER, first=True)


def s5_features(prs):
    """Slide 5 — Feature Engineering"""
    s = blank(prs);  bg(s)
    slide_header(s, "Feature Engineering:  The Hybrid Feature Matrix")

    # Summary strip
    flat_rect(s, Inches(0.5), Inches(1.57), Inches(12.5), Inches(0.28),
              RGBColor(20, 36, 72))
    tf_sum = tb(s, Inches(0.5), Inches(1.58), Inches(12.5), Inches(0.28))
    p_add(tf_sum,
          "Combined feature space:  5,000 TF-IDF dimensions  +  100 Word2Vec dimensions  "
          "+  12 Structural Metadata features  =  5,112 total features per email",
          font="Calibri", size=12, italic=True, color=C_GOLD,
          align=PP_ALIGN.CENTER, first=True, sa=0)

    cols = [
        ("TF-IDF Text Vectors", C_ACCENT, Inches(0.5), [
            ("N-gram range",    "(1, 3) — captures unigrams, bigrams, and trigrams simultaneously."),
            ("Vocabulary cap",  "Top 5,000 terms retained after frequency-based filtering."),
            ("Scaling",         "Sublinear TF scaling compresses the effect of high-frequency words."),
            ("Output",          "Sparse 5,000-dimension matrix; one row per cleaned email."),
        ]),
        ("Word2Vec Embeddings", C_GOLD, Inches(4.8), [
            ("Training",        "Custom gensim Word2Vec model trained on the cleaned token stream."),
            ("Dimensionality",  "Each unique word is represented as a 100-dimensional dense vector."),
            ("Aggregation",     "Per-email vector = mean of all constituent word vectors."),
            ("Normalisation",   "MinMaxScaler maps all values to [0, 1] for classifier stability."),
        ]),
        ("Structural Metadata", C_GREEN, Inches(9.1), [
            ("URL signals",     "Raw URL count and binary link-presence flag per email."),
            ("Urgency score",   "Frequency match against 20 known phishing urgency keywords."),
            ("Formatting",      "Exclamation density, capitalisation ratio, punctuation density."),
            ("Scaling",         "All 12 features MinMax scaled before concatenation into matrix."),
        ]),
    ]

    cw = Inches(3.85);  ch = Inches(5.05);  ct = Inches(1.93)
    for (title, color, x, items) in cols:
        box(s, x, ct, cw, ch)
        tf = tb(s, x + Inches(0.18), ct + Inches(0.18),
                cw - Inches(0.36), ch - Inches(0.36))
        card_heading(tf, title, color=color, size=15)
        thin_rule(tf)
        for lbl, det in items:
            bullet_item(tf, lbl, det, size=12)


def s6_models(prs):
    """Slide 6 — Model Selection and Tuning"""
    s = blank(prs);  bg(s)
    slide_header(s, "Model Selection  and  Hyperparameter Tuning")

    box(s, Inches(0.5), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_l = tb(s, Inches(0.68), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_l, "Classifiers Under Evaluation", color=C_ACCENT, size=16)
    thin_rule(tf_l)
    bullet_item(tf_l, "Logistic Regression",
                "Linear baseline; fast training with high interpretability.", 13)
    bullet_item(tf_l, "Random Forest",
                "Bagging ensemble of 200 decision trees; handles non-linear feature interactions.", 13)
    bullet_item(tf_l, "Multinomial Naive Bayes",
                "Probabilistic model well-suited to sparse TF-IDF feature distributions.", 13)
    bullet_item(tf_l, "MLP Neural Network",
                "Three-layer perceptron with ReLU activations and early stopping regularisation.", 13)
    plain_bullet(tf_l,
                 "All classifiers trained on the identical 5,112-feature hybrid matrix.",
                 size=12, color=C_MUTED)

    box(s, Inches(7.05), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_r = tb(s, Inches(7.23), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_r, "Cross-Validation and Ensemble Strategy", color=C_GREEN, size=16)
    thin_rule(tf_r, C_GREEN)
    bullet_item(tf_r, "Train / Test split",
                "Stratified 80/20 split preserves the natural class imbalance ratio.", 13)
    bullet_item(tf_r, "Grid Search CV",
                "5-fold Stratified Cross-Validation sweeps hyperparameter combinations per model.", 13)
    bullet_item(tf_r, "Class balancing",
                "class_weight='balanced' corrects for the 62.6% safe / 37.4% phishing skew.", 13)
    bullet_item(tf_r, "Soft-Voting Ensemble",
                "Aggregates predicted class probabilities from all four models; majority wins.", 13)
    plain_bullet(tf_r,
                 "Voting Ensemble — 98.52% Accuracy  |  98.02% F1-Score",
                 size=13, color=C_GOLD)


def s7_results(prs, metrics):
    """Slide 7 — Results Table"""
    s = blank(prs);  bg(s)
    slide_header(s, "Experimental Results  and  Model Comparison")

    rows_data = [
        ("Logistic Regression",    metrics["LR"]),
        ("Random Forest",          metrics["RF"]),
        ("Multinomial Naive Bayes",metrics["NB"]),
        ("Neural Network (MLP)",   metrics["NN"]),
        ("Voting Ensemble  (Best)",metrics["VE"]),
    ]
    headers  = ["Classifier Model", "Accuracy", "Precision", "Recall", "F1-Score"]
    col_ws   = [Inches(4.1), Inches(1.9), Inches(1.9), Inches(1.9), Inches(1.9)]
    tbl_l, tbl_t = Inches(0.55), Inches(1.72)
    tbl_w = sum(col_ws);  tbl_h = Inches(4.6)

    tbl_shape = s.shapes.add_table(len(rows_data) + 1, 5, tbl_l, tbl_t, tbl_w, tbl_h)
    tbl = tbl_shape.table
    for ci, cw in enumerate(col_ws):
        tbl.columns[ci].width = cw

    # Header row
    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = h
        cell.fill.solid();  cell.fill.fore_color.rgb = RGBColor(8, 24, 62)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.runs[0] if p.runs else p.add_run()
        r.font.name = "Trebuchet MS";  r.font.size = Pt(13)
        r.font.bold = True;  r.font.color.rgb = C_ACCENT

    # Data rows
    for ri, (name, m) in enumerate(rows_data):
        best = (ri == len(rows_data) - 1)
        row_fill = RGBColor(18, 40, 85) if best else (
                   C_CARD if ri % 2 == 0 else RGBColor(17, 27, 52))
        vals = [name, m["Acc"], m["Prec"], m["Rec"], m["F1"]]
        for ci, val in enumerate(vals):
            cell = tbl.cell(ri + 1, ci)
            cell.text = val
            cell.fill.solid();  cell.fill.fore_color.rgb = row_fill
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.runs[0] if p.runs else p.add_run()
            r.font.name  = "Calibri";  r.font.size = Pt(13)
            r.font.bold  = best
            r.font.color.rgb = C_GOLD if best else C_WHITE

    # Note
    tf_n = tb(s, Inches(0.55), Inches(6.43), Inches(12.15), Inches(0.42))
    p_add(tf_n,
          "Note: Adding custom Word2Vec embeddings alongside MinMaxScaler-normalised structural metadata "
          "raised the ensemble F1-Score to 98.02%, outperforming every individual classifier.",
          font="Calibri", size=12, italic=True, color=C_MUTED, first=True)


def s8_figures(prs):
    """Slide 8 — Confusion Matrix and Feature Importance"""
    s = blank(prs);  bg(s)
    slide_header(s, "Feature Importance  and  Confusion Matrix Analysis")

    ve_cm = os.path.join(FIGURES_DIR, "confusion_matrix_VotingEnsemble.png")
    rf_fi = os.path.join(FIGURES_DIR, "feature_importance_RandomForest.png")

    box(s, Inches(0.5), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_l = tb(s, Inches(0.65), Inches(1.72), Inches(5.6), Inches(0.52))
    p_add(tf_l, "Voting Ensemble \u2014 Confusion Matrix",
          font="Trebuchet MS", size=13, bold=True, color=C_WHITE, first=True)
    if os.path.exists(ve_cm):
        s.shapes.add_picture(ve_cm, Inches(0.7), Inches(2.28),
                             width=Inches(5.55), height=Inches(4.52))

    box(s, Inches(7.05), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_r = tb(s, Inches(7.2), Inches(1.72), Inches(5.6), Inches(0.52))
    p_add(tf_r, "Random Forest \u2014 Top 15 Feature Importance Drivers",
          font="Trebuchet MS", size=13, bold=True, color=C_WHITE, first=True)
    if os.path.exists(rf_fi):
        s.shapes.add_picture(rf_fi, Inches(7.2), Inches(2.28),
                             width=Inches(5.6), height=Inches(4.52))


def s9_roc(prs):
    """Slide 9 — ROC Validation Curves"""
    s = blank(prs);  bg(s)
    slide_header(s, "Validation Curves:  ROC Curve Comparison")

    roc = os.path.join(FIGURES_DIR, "roc_curve_comparison.png")

    box(s, Inches(0.5), Inches(1.65), Inches(7.3), Inches(5.5))
    tf_l = tb(s, Inches(0.65), Inches(1.72), Inches(7.0), Inches(0.5))
    p_add(tf_l, "Receiver Operating Characteristic (ROC) \u2014 All Classifiers",
          font="Trebuchet MS", size=13, bold=True, color=C_WHITE, first=True)
    if os.path.exists(roc):
        s.shapes.add_picture(roc, Inches(0.65), Inches(2.25),
                             width=Inches(7.0), height=Inches(4.55))

    box(s, Inches(7.95), Inches(1.65), Inches(5.0), Inches(5.5))
    tf_r = tb(s, Inches(8.12), Inches(1.83), Inches(4.65), Inches(5.14))
    card_heading(tf_r, "Validation Curve Interpretation", color=C_ACCENT, size=15)
    thin_rule(tf_r)
    bullet_item(tf_r, "FPR vs TPR",
                "Plots the classifier's sensitivity against specificity across all decision thresholds.", 12)
    bullet_item(tf_r, "AUC score",
                "A higher area under the curve indicates stronger discriminative power.", 12)
    bullet_item(tf_r, "Leading model",
                "The Voting Ensemble consistently achieves the highest AUC across all folds.", 12)
    bullet_item(tf_r, "CV robustness",
                "Stratified 5-fold validation ensures the results generalise beyond the training set.", 12)
    bullet_item(tf_r, "Deployment",
                "Threshold can be adjusted live via the Streamlit dashboard probability sliders.", 12)


def s10_ethics(prs):
    """Slide 10 — Ethical Trade-offs"""
    s = blank(prs);  bg(s)
    slide_header(s, "Ethical Trade-offs  and  Production Considerations")

    box(s, Inches(0.5), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_l = tb(s, Inches(0.68), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_l, "Precision vs. Recall Dilemma", color=C_ACCENT, size=16)
    thin_rule(tf_l)
    bullet_item(tf_l, "High Recall",
                "Captures more threats but increases the risk of quarantining legitimate business mail.", 13)
    bullet_item(tf_l, "High Precision",
                "Protects inbox delivery but allows sophisticated phishing messages to pass undetected.", 13)
    bullet_item(tf_l, "Routing strategy",
                "Emails scoring above 90% phishing confidence are quarantined; borderline cases are "
                "flagged for manual analyst review.", 13)
    plain_bullet(tf_l,
                 "The Streamlit dashboard exposes adjustable thresholds for operator control.",
                 size=12, color=C_MUTED)

    box(s, Inches(7.05), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_r = tb(s, Inches(7.23), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_r, "Bias and Deployment Risks", color=C_GOLD, size=16)
    thin_rule(tf_r, C_GOLD)
    bullet_item(tf_r, "Training bias",
                "Overemphasis on formatting cues may flag international newsletters as phishing.", 13)
    bullet_item(tf_r, "Vocabulary drift",
                "The Word2Vec model requires periodic retraining as attacker language evolves.", 13)
    bullet_item(tf_r, "Transparency",
                "Automated filtering decisions must be auditable and disputable by end-users.", 13)
    bullet_item(tf_r, "Data privacy",
                "Email body analysis must comply with GDPR and applicable enterprise data policies.", 13)


def s11_conclusion(prs):
    """Slide 11 — Summary and Future Work"""
    s = blank(prs);  bg(s)
    slide_header(s, "Summary  and  Future Work")

    box(s, Inches(0.5), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_l = tb(s, Inches(0.68), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_l, "Key Takeaways", color=C_ACCENT, size=17)
    thin_rule(tf_l)
    bullet_item(tf_l, "Hybrid pipeline",
                "Combining TF-IDF, Word2Vec, and structural metadata yields state-of-the-art performance.", 13)
    bullet_item(tf_l, "Best classifier",
                "The soft-voting ensemble achieved 98.52% Accuracy and 98.02% F1-Score on the test set.", 13)
    bullet_item(tf_l, "Data quality",
                "Removing 1,115 duplicate emails was critical to prevent test-data contamination.", 13)
    bullet_item(tf_l, "Validation",
                "Stratified 5-fold cross-validation and ROC curves confirm strong generalisation.", 13)
    plain_bullet(tf_l,
                 "The project demonstrates that classical ML with careful feature engineering "
                 "can rival deep-learning approaches at a fraction of the inference cost.",
                 size=12, color=C_MUTED)

    box(s, Inches(7.05), Inches(1.65), Inches(5.9), Inches(5.5))
    tf_r = tb(s, Inches(7.23), Inches(1.83), Inches(5.54), Inches(5.14))
    card_heading(tf_r, "Future Directions", color=C_GREEN, size=17)
    thin_rule(tf_r, C_GREEN)
    bullet_item(tf_r, "DistilBERT",
                "Replace static Word2Vec with contextual transformer embeddings for multi-sentence intent.", 13)
    bullet_item(tf_r, "Email headers",
                "Integrate SPF, DKIM, and DMARC authentication results as additional metadata features.", 13)
    bullet_item(tf_r, "REST API",
                "Expose a FastAPI inference endpoint for direct integration at the enterprise email gateway.", 13)
    bullet_item(tf_r, "Active learning",
                "Continuously retrain on analyst-labelled uncertain predictions to reduce drift over time.", 13)


# ── Main ─────────────────────────────────────────────────────────────────────

def generate_presentation():
    print("Generating professional PPT presentation (no emojis, humanised language)...")
    metrics = load_metrics()
    prs = new_prs()

    s1_title(prs)
    s2_objectives(prs)
    s3_threat(prs)
    s4_pipeline(prs)
    s5_features(prs)
    s6_models(prs)
    s7_results(prs, metrics)
    s8_figures(prs)
    s9_roc(prs)
    s10_ethics(prs)
    s11_conclusion(prs)

    os.makedirs(os.path.dirname(OUTPUT_PPTX_PATH), exist_ok=True)
    prs.save(OUTPUT_PPTX_PATH)
    print(f"  Saved: {OUTPUT_PPTX_PATH}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    generate_presentation()
