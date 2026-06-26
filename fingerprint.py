import hashlib
import librosa
import numpy as np
import scipy.ndimage as ndi
from scipy import signal

# ============================================================
# CONFIGURATION CONSTANTS
# ============================================================

NPERSEG = 2048
NOVERLAP = 1024
NEIGHBORHOOD_SIZE = (45, 45)
PEAK_THRESHOLD_DB = 25
FAN_OUT = 5
MIN_TIME_DELTA = 0
MAX_TIME_DELTA = 500

# ============================================================
# DSP PIPELINE FUNCTIONS
# ============================================================

def load_audio(audio_path, target_sr=11025):
    """Loads audio and standardizes sampling frequency to optimize DSP performance."""
    audio, sample_rate = librosa.load(audio_path, sr=target_sr, mono=True)
    return audio, sample_rate

def compute_spectrogram(audio, sample_rate):
    """Computes the Short-Time Fourier Transform magnitude spectrum in dB scale."""
    frequencies, times, spectrum = signal.spectrogram(
        audio,
        sample_rate,
        nperseg=NPERSEG,
        noverlap=NOVERLAP
    )
    spectrum_db = 10 * np.log10(spectrum + 1e-10)
    return frequencies, times, spectrum_db

def detect_peaks(spectrogram_db):
    """Finds sparse standout local peaks using a maximum filtration neighborhood mask."""
    threshold = np.max(spectrogram_db) - PEAK_THRESHOLD_DB
    local_max = ndi.maximum_filter(spectrogram_db, size=NEIGHBORHOOD_SIZE)
    maxima = (spectrogram_db == local_max) & (spectrogram_db > threshold)
    frequency_indices, time_indices = np.where(maxima)
    return frequency_indices, time_indices

def create_constellation(time_indices, frequency_indices):
    """
    Groups coordinate indices into a time-sorted structural constellation.
    CRITICAL FIX: Explicitly pairs time first to ensure proper sorting and offset unpacking.
    """
    return sorted(zip(time_indices, frequency_indices))

def generate_hashes(peaks):
    """Pairs nearby structural anchor points into unique cryptographic fingerprint keys."""
    fingerprints = []
    for i in range(len(peaks)):
        anchor_time, anchor_freq = peaks[i]
        for j in range(1, FAN_OUT + 1):
            if i + j >= len(peaks):
                break
            target_time, target_freq = peaks[i + j]
            delta_time = target_time - anchor_time
            
            if MIN_TIME_DELTA <= delta_time <= MAX_TIME_DELTA:
                fingerprint_hash = hashlib.sha1(
                    f"{anchor_freq}|{target_freq}|{delta_time}".encode()
                ).hexdigest()[:20]
                
                fingerprints.append((fingerprint_hash, anchor_time))
    return fingerprints

# ============================================================
# MAIN INGESTION ENTRYPOINT
# ============================================================

def generate_fingerprints(audio_path=None, audio=None, sample_rate=None, return_debug=False):
    """Main ingestion wrapper supporting file paths or raw arrays."""
    if audio is None:
        if audio_path is None:
            raise ValueError("Provide either audio_path OR audio.")
        audio, sample_rate = load_audio(audio_path)
        
    if sample_rate is None:
        raise ValueError("sample_rate must be supplied when audio is given.")

    frequencies, times, spectrogram_db = compute_spectrogram(audio, sample_rate)
    frequency_indices, time_indices = detect_peaks(spectrogram_db)
    
    # CRITICAL ARGUMENT ORDER CHECK
    peaks = create_constellation(time_indices, frequency_indices)
    fingerprints = generate_hashes(peaks)

    if not return_debug:
        return fingerprints

    debug = {
        "audio": audio,
        "sample_rate": sample_rate,
        "frequencies": frequencies,
        "times": times,
        "spectrogram": spectrogram_db,
        "frequency_indices": frequency_indices,
        "time_indices": time_indices,
        "peaks": peaks
    }
    return fingerprints, debug