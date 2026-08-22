import streamlit as st
import re

# Page Configuration
st.set_page_config(
    page_title="Misinformation & Propaganda Radar",
    page_icon="🛡️",
    layout="centered"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #090d16; color: #f8fafc; }
    .stTextArea textarea { background-color: #111827; color: #f3f4f6; border: 1px solid #1f2937; border-radius: 0.75rem; }
    .metric-card { background-color: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ Misinformation & Propaganda Radar")
st.p("Analyze text in real-time for emotional manipulation, urgency bias, and algorithmic clickbait structures.")

# Text Input Area
user_text = st.text_area(
    "Paste news excerpt, headline, or post text below:",
    placeholder="Type or paste content here...",
    height=150
)

if st.button("Run Content Analysis", type="primary", use_container_width=True):
    if not user_text or len(user_text.strip()) < 10:
        st.warning("⚠️ Please enter at least 10 characters of text to scan.")
    else:
        with st.spinner("Evaluating psychological triggers and syntax patterns..."):
            
            # Analysis Logic
            red_flags = [
                'shocking', 'they don\'t want you to know', 'miracle', 'exposed', 
                'mainstream media won\'t tell', '100% proof', 'conspiracy', 'secret cure',
                'you won\'t believe', 'elite', 'hoax', 'banned', 'urgent', 'cover-up'
            ]
            
            lower_text = user_text.lower()
            score = 0
            detected_triggers = []
            
            for word in red_flags:
                if word in lower_text:
                    score += 15
                    detected_triggers.append(word)
            
            # Check for excessive capitalization (Shouting / Panic)
            uppercase_count = sum(1 for c in user_text if c.isupper())
            if len(user_text) > 0 and (uppercase_count / len(user_text)) > 0.25:
                score += 25
                detected_triggers.append("Excessive Caps / Panic Framing")
                
            # Check for repeated exclamation marks
            if re.search(r'!{2,}', user_text):
                score += 15
                detected_triggers.append("Multiple Exclamation Marks (Emotional Bait)")
                
            # Calculate final risk index
            final_risk = min(max(score + 10, 5), 95)
            
            # Render Results UI
            st.markdown("---")
            st.subheader("Analysis Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Manipulation Threat Index", value=f"{final_risk}%")
            with col2:
                if final_risk > 70:
                    st.error("Verdict: High Risk / Misinformation Bait")
                elif final_risk > 35:
                    st.warning("Verdict: Moderately Sensationalized")
                else:
                    st.success("Verdict: Credible / Balanced Tone")
                    
            # Progress bar visualizer
            st.progress(final_risk / 100)
            
            # Trigger tags container
            if detected_triggers:
                st.write("**Detected Manipulation Vectors:**")
                chips_html = "".join([f"<span style='background-color: #451a03; color: #f87171; border: 1px solid #7f1d1d; padding: 4px 12px; border-radius: 16px; font-size: 12px; margin-right: 6px; display: inline-block; margin-bottom: 6px;'>{t}</span>" for t in detected_triggers])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.info("No structural manipulation vectors or high-risk clickbait keywords found.")
