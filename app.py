import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from matcher import SongMatcher
from fingerprint import generate_fingerprints

# ==========================================================
# Application Global Setup
# ==========================================================
st.set_page_config(
    page_title="Audio Fingerprinting System",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 Audio Fingerprinting Recognition Platform")
st.write("EE200 Project Q3 Engine — Compute intermediate structural steps or evaluate massive batches.")
st.divider()

# Cache the database load operation so the workspace stays snappy
@st.cache_resource
def load_cached_matcher():
    matcher = SongMatcher()
    # Updated to load the clean database file containing the fixed native integers
    matcher.load_database("data/fresh_fingerprints.pkl")
    return matcher

try:
    matcher = load_cached_matcher()
except Exception as e:
    st.error("Could not find database pickle file at 'data/fresh_fingerprints.pkl'. Please ensure it runs within your root folder workspace context.")
    st.stop()

# Mode Toggles
mode = st.sidebar.radio("Navigation Modes", ["Single-Clip Mode", "Batch Mode"])

# ==========================================================
# Mode A: Single-Clip Pipeline Visualization
# ==========================================================
if mode == "Single-Clip Mode":
    st.header("Single-Clip Analysis Window")
    uploaded_file = st.file_uploader("Ingest individual target audio file", type=["mp3", "wav"])

    if uploaded_file is not None:
        st.success("Audio data successfully staged.")
        
        if st.button("Execute Identification Process", type="primary"):
            # Determine suffix cleanly based on file name extension
            file_suffix = f".{uploaded_file.name.split('.')[-1]}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp:
                temp.write(uploaded_file.read())
                temp_path = temp.name

            try:
                with st.spinner("Extracting parameters and running DSP pipeline..."):
                    # CRITICAL FIX: Pass the temporary file path directly to the matcher.
                    # This ensures both query and database share the exact same sample rate downsampling.
                    result = matcher.identify(query_path=temp_path)
                    
                    # Run debug feature extraction standalone solely to generate pristine UI plots
                    fingerprints, debug = generate_fingerprints(audio_path=temp_path, return_debug=True)
                
                st.success("Processing Complete!")
                st.divider()

                # Metrics Layout Row
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Predicted Target Song", str(result["song"]))
                m_col2.metric("Matching Core Confidence", f"{result['confidence']:.2f}%")
                m_col3.metric("Peak Histogram Votes", int(result["votes"]))
                st.divider()

                # Mandatory Intermediate Visualizations
                st.subheader("Intermediate DSP Step Extractions")
                plot_col1, plot_col2 = st.columns(2)

                with plot_col1:
                    st.write("**1. Spectrogram & Extracted Peak Constellation**")
                    fig1, ax1 = plt.subplots(figsize=(10, 5))
                    im = ax1.pcolormesh(
                        debug["times"], 
                        debug["frequencies"], 
                        debug["spectrogram"], 
                        shading="gouraud", 
                        cmap="magma"
                    )
                    ax1.scatter(
                        debug["times"][debug["time_indices"]],
                        debug["frequencies"][debug["frequency_indices"]],
                        color="cyan", s=10, edgecolors="black", linewidths=0.5, label="Sparse Maxima"
                    )
                    ax1.set_ylim(0, 5000)
                    ax1.set_xlabel("Time (s)")
                    ax1.set_ylabel("Frequency (Hz)")
                    ax1.legend()
                    fig1.colorbar(im, ax=ax1, label="Power Density (dB)")
                    st.pyplot(fig1)

                with plot_col2:
                    st.write("**2. Temporal Alignment Offset Histogram**")
                    if result["histogram"]:
                        fig2, ax2 = plt.subplots(figsize=(10, 5))
                        ax2.bar(
                            list(result["histogram"].keys()), 
                            list(result["histogram"].values()), 
                            width=1.0, color="steelblue"
                        )
                        ax2.set_title(f"Target Sync Alignment: {result['song']}")
                        ax2.set_xlabel("Offset Bins Delta")
                        ax2.set_ylabel("Accumulated Match Count")
                        ax2.grid(True, linestyle="--", alpha=0.5)
                        st.pyplot(fig2)
                    else:
                        st.warning("No offset mapping histogram available for display.")

            finally:
                # Continuous file system cleaning guard
                if os.path.exists(temp_path):
                    os.remove(temp_path)

# ==========================================================
# Mode B: Automatic Batch Evaluation Mode
# ==========================================================
else:
    st.header("Automated Batch Evaluation Mode")
    st.write("Upload multiple query audio clips. The app will generate the exact evaluation standard `results.csv` file.")
    
    uploaded_files = st.file_uploader(
        "Select batch folder files to ingest simultaneously", 
        type=["mp3", "wav"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(f"Staged {len(uploaded_files)} files for evaluation.")
        
        if st.button("Run Batch Processing Pipeline", type="primary"):
            results_registry = []
            progress_bar = st.progress(0)
            
            for index, uploaded_file in enumerate(uploaded_files):
                file_suffix = f".{uploaded_file.name.split('.')[-1]}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp:
                    temp.write(uploaded_file.read())
                    temp_path = temp.name

                try:
                    # CRITICAL FIX: Pass query_path directly for uniform pipeline execution
                    result = matcher.identify(query_path=temp_path)
                    prediction_output = result["song"] if result["song"] is not None else "Unknown"
                    
                    # Maintain strict dictionary constraints matching evaluation specifications
                    results_registry.append({
                        "filename": uploaded_file.name,
                        "prediction": prediction_output
                    })
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                progress_bar.progress((index + 1) / len(uploaded_files))
            
            # Format cleanly as a pandas table
            df_outputs = pd.DataFrame(results_registry)
            st.subheader("Computed Prediction Log Matrix")
            st.dataframe(df_outputs, use_container_width=True)
            
            # Formulate structural bytes to ship down instantly
            csv_bytes = df_outputs.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download results.csv",
                data=csv_bytes,
                file_name="results.csv",
                mime="text/csv"
            )