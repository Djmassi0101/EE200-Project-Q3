
import hashlib

import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi

from scipy import signal

from config import (
    NPERSEG,
    NOVERLAP,
    NEIGHBORHOOD_SIZE,
    PEAK_THRESHOLD_DB,
    FAN_OUT,
    MIN_TIME_DELTA,
    MAX_TIME_DELTA,
    MAX_DISPLAY_FREQ
)


# ============================================================
# AUDIO LOADING
# ============================================================

def load_audio(audio_path):
    """
    Load an audio file.

    Parameters
    ----------
    audio_path : str
        Path to an audio file.

    Returns
    -------
    audio : ndarray
        Mono audio signal.

    sample_rate : int
        Sampling frequency.
    """

    audio, sample_rate = librosa.load(
        audio_path,
        sr=None,
        mono=True
    )

    return audio, sample_rate


# ============================================================
# SPECTROGRAM
# ============================================================

def compute_spectrogram(audio, sample_rate):
    """
    Compute the magnitude spectrogram.

    Returns
    -------
    frequencies
    times
    spectrogram_db
    """

    frequencies, times, spectrum = signal.spectrogram(
        audio,
        sample_rate,
        nperseg=NPERSEG,
        noverlap=NOVERLAP
    )

    spectrum_db = 10 * np.log10(spectrum + 1e-10)

    return frequencies, times, spectrum_db


# ============================================================
# PEAK DETECTION
# ============================================================

def detect_peaks(spectrogram_db):
    """
    Detect local maxima in the spectrogram.

    Returns
    -------
    frequency_indices
    time_indices
    """

    threshold = np.max(spectrogram_db) - PEAK_THRESHOLD_DB

    local_max = ndi.maximum_filter(
        spectrogram_db,
        size=NEIGHBORHOOD_SIZE
    )

    maxima = (
        (spectrogram_db == local_max)
        &
        (spectrogram_db > threshold)
    )

    frequency_indices, time_indices = np.where(maxima)

    return frequency_indices, time_indices


# ============================================================
# CONSTELLATION MAP
# ============================================================

def create_constellation(time_indices, frequency_indices):
    """
    Convert peak indices into a time-sorted constellation.

    Returns
    -------
    peaks : list

    [(time_index, frequency_index), ...]
    """

    peaks = sorted(
        zip(time_indices, frequency_indices)
    )

    return peaks


# ============================================================
# VISUALIZATION
# ============================================================

def plot_constellation(
    frequencies,
    times,
    spectrogram_db,
    frequency_indices,
    time_indices
):
    """
    Display spectrogram and constellation peaks.
    """

    plt.figure(figsize=(12, 6))

    plt.pcolormesh(
        times,
        frequencies,
        spectrogram_db,
        shading="gouraud",
        cmap="magma"
    )

    plt.scatter(
        times[time_indices],
        frequencies[frequency_indices],
        color="cyan",
        s=15,
        edgecolors="black",
        label="Detected Peaks"
    )

    plt.title("Constellation Map")

    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

    plt.ylim(0, MAX_DISPLAY_FREQ)

    plt.legend()

    plt.tight_layout()

    plt.show()


# ============================================================
# HASH GENERATION
# ============================================================

def generate_hashes(peaks):
    """
    Generate Shazam-style fingerprint hashes.

    Parameters
    ----------
    peaks : list

    Returns
    -------
    fingerprints

    [
        (hash, anchor_time),
        ...
    ]
    """

    fingerprints = []

    for i in range(len(peaks)):

        anchor_time, anchor_frequency = peaks[i]

        for j in range(1, FAN_OUT + 1):

            if i + j >= len(peaks):
                break

            target_time, target_frequency = peaks[i + j]

            delta_time = target_time - anchor_time

            if MIN_TIME_DELTA <= delta_time <= MAX_TIME_DELTA:

                fingerprint_hash = hashlib.sha1(

                    f"{anchor_frequency}|"
                    f"{target_frequency}|"
                    f"{delta_time}"

                    .encode()

                ).hexdigest()[:20]

                fingerprints.append(
                    (
                        fingerprint_hash,
                        anchor_time
                    )
                )

    return fingerprints


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

def generate_fingerprints(
    audio_path=None,
    audio=None,
    sample_rate=None,
    visualize=False,
    return_debug=False
):
    """
    Generate fingerprints from either

    1. an audio file

    OR

    2. an already-loaded NumPy array.

    Examples
    --------

    generate_fingerprints(audio_path="song.wav")

    generate_fingerprints(
        audio=my_audio,
        sample_rate=44100
    )
    """

    # --------------------------------------------------------
    # Load audio if a file path was supplied
    # --------------------------------------------------------

    if audio is None:

        if audio_path is None:

            raise ValueError(
                "Provide either audio_path OR audio."
            )

        audio, sample_rate = load_audio(audio_path)

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if sample_rate is None:

        raise ValueError(
            "sample_rate must be supplied when audio is given."
        )

    # --------------------------------------------------------
    # Spectrogram
    # --------------------------------------------------------

    frequencies, times, spectrogram_db = compute_spectrogram(
        audio,
        sample_rate
    )

    # --------------------------------------------------------
    # Peak Detection
    # --------------------------------------------------------

    frequency_indices, time_indices = detect_peaks(
        spectrogram_db
    )

    # --------------------------------------------------------
    # Optional Visualization
    # --------------------------------------------------------

    if visualize:

        plot_constellation(
            frequencies,
            times,
            spectrogram_db,
            frequency_indices,
            time_indices
        )

    # --------------------------------------------------------
    # Constellation
    # --------------------------------------------------------

    peaks = create_constellation(
        time_indices,
        frequency_indices
    )

    # --------------------------------------------------------
    # Fingerprint Hashes
    # --------------------------------------------------------

    fingerprints = generate_hashes(peaks)

    # --------------------------------------------------------
    # Standard Output
    # --------------------------------------------------------

    if not return_debug:

        return fingerprints

    # --------------------------------------------------------
    # Debug Output
    # --------------------------------------------------------

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


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    TEST_AUDIO = "data/queries/query.wav"

    fingerprints, debug = generate_fingerprints(
        audio_path=TEST_AUDIO,
        visualize=True,
        return_debug=True
    )

    print(f"Generated {len(fingerprints)} fingerprints.")
