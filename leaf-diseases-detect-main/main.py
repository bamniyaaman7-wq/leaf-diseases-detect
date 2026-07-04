
import os
import requests
import streamlit as st

st.set_page_config(page_title="LeafCare AI", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #f4fff6 0%, #eef6ff 100%); }
    .hero-card { background: rgba(255,255,255,0.95); border-radius: 24px; padding: 1.7rem; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }
    .info-pill { display: inline-block; background: #eaf7ee; color: #206b3e; border-radius: 999px; padding: 0.35rem 0.7rem; margin-right: 0.4rem; margin-bottom: 0.4rem; font-size: 0.92rem; }
    .result-card { background: white; border-left: 6px solid #2e7d32; border-radius: 16px; padding: 1.2rem; margin-top: 1rem; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='hero-card'>
        <h1 style='margin-bottom: 0.2rem; color: #134e4a;'>LeafCare AI</h1>
        <p style='font-size: 1.05rem; color: #475569; margin-top: 0;'>A more practical way to inspect plant leaf health with fast AI-assisted feedback.</p>
        <div>
            <span class='info-pill'>🌿 Leaf health checks</span>
            <span class='info-pill'>🧠 AI guidance</span>
            <span class='info-pill'>💡 Actionable next steps</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("How it works")
    st.write("1. Upload a clear photo of a leaf.")
    st.write("2. The app sends it to the analysis service.")
    st.write("3. You receive a health summary, severity, and recommendations.")

    st.header("Helpful tips")
    st.write("- Use daylight or bright indoor lighting.")
    st.write("- Keep the leaf centered and in focus.")
    st.write("- Avoid blurry or heavily shadowed images.")

api_url = os.getenv("API_URL", "http://localhost:8000")

col1, col2 = st.columns([1, 2], gap="large")
with col1:
    uploaded_file = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Preview", use_container_width=True)

with col2:
    if uploaded_file is not None:
        if st.button("Analyze leaf", use_container_width=True):
            with st.spinner("Checking the image and preparing a report..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{api_url}/disease-detection-file", files=files, timeout=90)

                    if response.status_code == 200:
                        result = response.json()
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(f"<h3 style='margin-top:0; color:#166534;'>🧾 {result.get('quick_summary', 'Report ready')}</h3>", unsafe_allow_html=True)

                        if result.get("disease_type") == "invalid_image":
                            st.warning("The uploaded image does not appear to be a clear leaf photo.")
                        elif result.get("disease_detected"):
                            st.success(f"Likely issue: {result.get('disease_name', 'Plant stress')}")
                        else:
                            st.success("No obvious disease signs were detected.")

                        st.write(f"Type: {result.get('disease_type', 'unknown')}")
                        st.write(f"Severity: {result.get('severity', 'unknown')}")
                        st.write(f"Confidence: {result.get('confidence', 'unknown')}%")

                        if result.get("symptoms"):
                            st.write("**Symptoms**")
                            for symptom in result.get("symptoms", []):
                                st.write(f"- {symptom}")

                        if result.get("possible_causes"):
                            st.write("**Possible causes**")
                            for cause in result.get("possible_causes", []):
                                st.write(f"- {cause}")

                        if result.get("treatment"):
                            st.write("**Suggested next steps**")
                            for item in result.get("treatment", []):
                                st.write(f"- {item}")

                        st.caption(result.get("analysis_timestamp") or "Analysis complete")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"The service returned an error: {response.status_code}")
                        st.write(response.text)
                except Exception as exc:
                    st.error(f"Something went wrong: {exc}")
    else:
        st.info("Upload a leaf image to begin the analysis.")

st.markdown("---")
st.caption("LeafCare AI is designed to make plant health checks faster, more approachable, and easier to understand.")
