"""
Configuration parameters for the Audio Fingerprinting System
"""

# ============================================================
# Spectrogram Parameters
# ============================================================

# FFT window size
NPERSEG = 2048

# Number of overlapping samples
NOVERLAP = 512


# ============================================================
# Peak Detection Parameters
# ============================================================

# Size of local maximum search window
NEIGHBORHOOD_SIZE = 20

# Peaks within 35 dB of the maximum are retained
PEAK_THRESHOLD_DB = 35


# ============================================================
# Fingerprint Parameters
# ============================================================

# Number of neighbouring peaks connected to each anchor peak
FAN_OUT = 5

# Minimum and maximum time difference between paired peaks
MIN_TIME_DELTA = 1
MAX_TIME_DELTA = 10


# ============================================================
# Visualization
# ============================================================

MAX_DISPLAY_FREQ = 5000


# ============================================================
# Supported Audio Formats
# ============================================================

SUPPORTED_EXTENSIONS = (
    ".mp3",
    ".wav",
    ".flac"
)
