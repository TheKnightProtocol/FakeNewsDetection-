import streamlit as st
import re

# Page Configuration
st.set_page_config(
    page_title="Cognitive Immunity & Propaganda Radar",
    page_icon="🧠",
    layout="centered"
)

# Professional Dark Cyber-Security UI Styling
st.markdown("""
    <style>
    .main { background-color: #07090e; color: #f1f5f9; }
    .stTextArea textarea { 
        background-color: #0f172a; 
        color: #f8fafc; 
        border: 1px solid #1e293b; 
        border-radius: 0.75rem; 
        font-size: 15px;
    }
    .metric-container { 
        background-color: #0f172a; 
        border: 1px solid #1e293b; 
        padding: 16px; 
        border-radius: 12px; 
    }
    .vector-badge {
        background-color: #1e1b4b;
        color: #818cf8;
        border: 1px solid #312e81;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }
    .inoculation-box {
        background-color: #064e3b;
        color: #a7f3d0;
        border: 1px solid #047857;
        padding: 16px;
        border-radius: 10px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🧠 Cognitive Immunity & Propaganda Radar")
st.write("An advanced linguistic framework shifting from simple classification to **psychological manipulation vector analysis**.")

# Input Form
user_text = st.text_area(
    "Input News Excerpt, Social Media Post, or Headline:",
    placeholder="Paste text here to evaluate psychological manipulation vectors...",
    height=160
)

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_triggered = st.button("Run Cognitive Diagnostic", type="primary", use_container_width=True)

if analyze_triggered:
    if not user_text or len(user_text.strip()) < 15:
        st.warning("⚠️ Please input at least 15 characters for a robust psycholinguistic scan.")
    else:
        with st.spinner("Deconstructing syntax matrices and emotional trigger vectors..."):
            
            text_lower = user_text.lower()
            
            # Multi-vector classification dictionaries
            vectors = {
                "Outrage & Fear Bait": ['shocking', 'terrifying', 'horrific', 'panic', 'disaster', 'crisis', 'danger'],
                "Conspiratorial Framing": ['they don\'t want you to know', 'mainstream media won\'t tell', 'secret cure', 'elite cover-up', 'hoax', 'banned', 'matrix', 'deep state'],
                "Absolute Certainty Traps": ['100% proof', 'undeniable truth', 'guaranteed', 'proven fact', 'always', 'never fail'],
                "Urgency Manipulation": ['act now', 'before it\'s deleted', 'hurry', 'urgent warning', 'breaking news alert']
            }
            
            vector_scores = {}
            detected_tags = []
            total_matches = 0
            
            for category, keywords in vectors.items():
                matches = [kw for kw in keywords if kw in text_lower]
                if matches:
                    vector_scores[category] = len(matches) * 20
                    total_matches += len(matches)
                    detected_tags.extend(matches)
                else:
                    vector_scores[category] = 0

            # Stylometric structural anomalies
            caps_ratio = sum(1 for c in user_text if c.isupper()) / max(len(user_text), 1)
            if caps_ratio > 0.22:
                total_matches += 2
                detected_tags.append("Excessive Capitalization (Shouting Matrix)")
                
            exclamation_storms = len(re.findall(r'!{2,}', user_text))
            if exclamation_storms > 0:
                total_matches += 2
                detected_tags.append("Punctuation Storm (Synthetic Urgency)")

            # Final Risk Calculation
            risk_index = min(max((total_matches * 18) + 5, 4), 98)

            # --- RENDER RESULTS ---
            st.markdown("---")
            st.subheader("Diagnostic Breakdown")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Manipulation Index", f"{risk_index}%")
            with m2:
                st.metric("Vector Count", f"{total_matches} Identified")
            with m3:
                status_label = "High Risk" if risk_index > 65 else ("Moderate" if risk_index > 30 else "Clean")
                st.metric("Cognitive Status", status_label)

            st.progress(risk_index / 100)

            # Detailed Vector Analysis Cards
            if detected_tags:
                st.markdown("### 🧬 Trigger Vectors Isolated")
                tags_html = "".join([f"<span class='vector-badge'>#{tag.upper()}</span>" for tag in detected_tags])
                st.markdown(tags_html, unsafe_allow_html=True)
            
            # Novelty Feature: Psychological Inoculation / Prebunking Advice
            st.markdown("### 🛡️ Prebunking & Cognitive Inoculation Counter-Measure")
            if risk_index > 65:
                st.markdown("""
                    <div class='inoculation-box'>
                    <b>Inoculation Insight:</b> This text leverages <b>affective polarization</b> and anti-institutional framing. 
                    It attempts to bypass critical filtering by inducing immediate emotional panic or tribal alignment. 
                    <i>Counter-strategy:</i> Separate the emotional adjectives from the core factual claims and trace the primary source registry.
                    </div>
                """, unsafe_allow_html=True)
            elif risk_index > 30:
                st.markdown("""
                    <div class='inoculation-box' style='background-color: #422006; border-color: #854d0e; color: #fde047;'>
                    <b>Inoculation Insight:</b> Mild sensationalism detected. The phrasing leans on exaggerated descriptive elements rather than neutral reporting. Approach with baseline structural skepticism.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='inoculation-box' style='background-color: #02233b; border-color: #0369a1; color: #bae6fd;'>
                    <b>Inoculation Insight:</b> The text follows a balanced, non-manipulative linguistic distribution. No immediate systemic panic triggers or synthetic outrage patterns were flagged.
                    </div>
                """, unsafe_allow_html=True)
