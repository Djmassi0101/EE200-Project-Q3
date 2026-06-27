#  EE200 Project: Audio Fingerprinting & Recognition Engine

A robust, production-grade automated audio identification platform inspired by the industrial Shazam landmarking algorithm. This system handles discrete Short-Time Fourier Transform (STFT) spectrogram analyses, processes sparse peak constellation mappings, and performs temporal synchronization voting. It features an interactive, web-accessible interface built with Streamlit and optimized for cloud execution environments.

---

##  Live Platform Links
* **Live Web Application URL:** `https://<YOUR-APP-NAME>.streamlit.app/`
* **Production Source Code Repository:** `https://github.com/Djmassi0101/EE200-Project-Q3`

---

##  System Architecture & Pipeline

The recognition framework processes target query audio through an identical pipeline to the reference library:

1. **Downsampling Layer:** Incoming waveforms are converted to a uniform `11,025 Hz` single-channel time series to eliminate structural grid resolution mismatches.
2. **Short-Time Fourier Transform (STFT):** Computes time-varying spectral frames utilizing a Hann window configuration ($N_{\text{perseg}} = 2048$, $N_{\text{overlap}} = 1024$).
3. **Constellation Map Generation:** A 2D localized maximum filter selects dominant structural peak coordinates while rejecting uniform background noise.
4. **Combinatorial Hash Pairing:** Anchors are bound to forward-looking target keys inside a dynamic bounding region to generate cryptographic tokens via SHA-1, dramatically slashing random library collisions.
5. **Temporal Alignment Scoring:** Aligns query match tokens across library timelines via a delta offset histogram ($t_{\text{database}} - t_{\text{query}}$). The true track surfaces as a dominant vertical alignment spike.

---

##  Project Repository Tree

```text
EE200-Project-Q3/
│
├── data/
│   ├── reference_library/       # Local storage folder for reference .mp3/.wav files
│   └── fresh_fingerprints.pkl   # Pre-compiled production database lookup matrix
│
├── app.py                      # Interactive Streamlit frontend UI
├── matcher.py                  # Core timeline synchronization alignment engine
├── fingerprint.py              # Front-end DSP pipeline (STFT, Constellation, Hashing)
├── index_database.py           # Reference library crawling and serializing script
├── requirements.txt            # Python dependencies manifest for deployment
└── packages.txt                # OS-level Linux dependencies (FFmpeg audio codecs)
