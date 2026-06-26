import os
import tempfile
import matplotlib.pyplot as plt
import streamlit as st

from matcher import SongMatcher

# ==========================================================
# Page Configuration
# ==========================================================
st.set_page_config(
    page_title="Audio Fingerprinting",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 Audio Fingerprinting using DSP")
st.write(
    "Upload a short MP3 clip and identify the matching song "
    "using audio fingerprinting."
)

st.divider()

# ==========================================================
# Load Database (Only Once)
# ==========================================================
@st.cache_resource
def load_matcher():
    matcher = SongMatcher()
    matcher.load_database("data/fingerprints.pkl")
    return matcher

matcher = load_matcher()

# ==========================================================
# Upload Section
# ==========================================================
uploaded_file = st.file_uploader(
    "Upload an MP3 File",
    type=["mp3"]
)

# ==========================================================
# Recognition & UI Logic
# ==========================================================
if uploaded_file is not None:
    # Use st.session_state to persist results across interface interactions (like toggling checkboxes)
    if "recognition_result" not in st.session_state:
        st.session_state.recognition_result = None

    st.success("Audio uploaded successfully.")
    
    if st.button("Recognize Song", type="primary"):
        with st.spinner("Generating fingerprints..."):
            # Safe temporary file handling with explicit block containment
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
                temp.write(uploaded_file.read())
                temp_path = temp.name

            try:
                # Perform DSP calculation
                st.session_state.recognition_result = matcher.identify(
                    query_path=temp_path
                )
            finally:
                # Clean up disk space immediately after identification is done
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        st.success("Recognition Complete!")

    # Render results if they exist in session state
    if st.session_state.recognition_result is not None:
        result = st.session_state.recognition_result
        st.divider()

        # ------------------------------------------
        # Metrics Display
        # ------------------------------------------
        col1, col2, col3 = st.columns(3)
        
        col1.metric(
            "Predicted Song",
            result["song"] if result["song"] is not None else "Not Found"
        )
        col2.metric(
            "Confidence",
            f"{result['confidence']:.2f}%"
        )
        col3.metric(
            "Votes",
            result["votes"]
        )

        st.divider()

        # ------------------------------------------
        # Top Matches Side-by-Side with Visuals
        # ------------------------------------------
        match_col, hist_col = st.columns([1, 1])

        with match_col:
            st.subheader("Top Matches")
            if result["top_matches"]:
                for rank, (song, votes) in enumerate(result["top_matches"], start=1):
                    st.write(f"**{rank}. {song}** — `{votes} votes`")
            else:
                st.warning("No matches found.")

        with hist_col:
            st.subheader("Alignment Visualizer")
            if st.checkbox("Show Offset Histogram", value=True):
                histogram = result["histogram"]
                
                if histogram:
                    # Explicitly use standard styling elements to fit light/dark themes cleanly
                    fig, ax = plt.subplots(figsize=(10, 4.5))
                    ax.bar(
                        list(histogram.keys()),
                        list(histogram.values()),
                        width=1.0,
                        color="deepskyblue",
                        edgecolor="none"
                    )
                    ax.set_title("Offset Histogram (Time Alignment Peak)")
                    ax.set_xlabel("Offset Difference (Bins)")
                    ax.set_ylabel("Votes")
                    ax.grid(True, linestyle="--", alpha=0.5)
                    
                    st.pyplot(fig)
                else:
                    st.warning("No histogram data generated.")
