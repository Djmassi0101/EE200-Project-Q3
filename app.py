import os
import tempfile

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
# Recognition
# ==========================================================

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as temp:

        temp.write(uploaded_file.read())

        temp_path = temp.name

    st.success("Audio uploaded successfully.")

    if st.button("Recognize Song"):

        with st.spinner("Generating fingerprints..."):

            result = matcher.identify(
                query_path=temp_path
            )

        st.success("Recognition Complete!")

        st.divider()

        # ------------------------------------------
        # Results
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Predicted Song",
            result["song"]
            if result["song"] is not None
            else "Not Found"
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
        # Top Matches
        # ------------------------------------------

        st.subheader("Top Matches")

        if result["top_matches"]:

            for rank, (song, votes) in enumerate(
                result["top_matches"],
                start=1
            ):

                st.write(
                    f"**{rank}. {song}** — {votes} votes"
                )

        else:

            st.warning("No matches found.")

        st.divider()

        # ------------------------------------------
        # Histogram
        # ------------------------------------------

        if st.checkbox("Show Offset Histogram"):

            import matplotlib.pyplot as plt

            histogram = result["histogram"]

            if histogram:

                fig, ax = plt.subplots(figsize=(10,4))

                ax.bar(
                    histogram.keys(),
                    histogram.values()
                )

                ax.set_title(
                    "Offset Histogram"
                )

                ax.set_xlabel(
                    "Offset Difference"
                )

                ax.set_ylabel(
                    "Votes"
                )

                ax.grid(True)

                st.pyplot(fig)

            else:

                st.warning(
                    "No histogram available."
                )

    os.remove(temp_path)
