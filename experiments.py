import os

import librosa
import numpy as np
import pandas as pd

from matcher import SongMatcher


# ==========================================================
# Add Gaussian Noise
# ==========================================================

def add_noise(audio, snr_db):
    """
    Add Gaussian noise to an audio signal.

    Parameters
    ----------
    audio : ndarray

    snr_db : float
        Desired Signal-to-Noise Ratio.

    Returns
    -------
    noisy_audio : ndarray
    """

    signal_power = np.mean(audio ** 2)

    noise_power = signal_power / (10 ** (snr_db / 10))

    noise = np.random.normal(
        0,
        np.sqrt(noise_power),
        audio.shape
    )

    return audio + noise


# ==========================================================
# Pitch Shift
# ==========================================================

def pitch_shift(audio, sample_rate, semitones):
    """
    Shift the pitch of an audio signal.

    Parameters
    ----------
    semitones : int

    Returns
    -------
    shifted_audio
    """

    return librosa.effects.pitch_shift(
        audio,
        sr=sample_rate,
        n_steps=semitones
    )


# ==========================================================
# Time Stretch
# ==========================================================

def time_stretch(audio, rate):
    """
    Stretch or compress an audio signal.

    Parameters
    ----------
    rate : float

    Returns
    -------
    stretched_audio
    """

    return librosa.effects.time_stretch(
        audio,
        rate=rate
    )


# ==========================================================
# Run All Experiments
# ==========================================================

def run_all_experiments(
    query_file,
    database_file,
    output_csv="results/experiment_results.csv"
):
    """
    Run all robustness experiments.

    Parameters
    ----------
    query_file : str

    database_file : str

    output_csv : str

    Returns
    -------
    pandas.DataFrame
    """

    matcher = SongMatcher()

    matcher.load_database(database_file)

    audio, sample_rate = librosa.load(
        query_file,
        sr=None,
        mono=True
    )

    results = []

    print("\n==============================")
    print(" ORIGINAL AUDIO")
    print("==============================")

    result = matcher.identify(
        audio=audio,
        sample_rate=sample_rate
    )

    matcher.print_results(result)

    results.append({
        "Experiment": "Original",
        "Parameter": "-",
        "Prediction": result["song"],
        "Confidence (%)": round(result["confidence"], 2),
        "Votes": result["votes"]
    })

    # ======================================================
    # Noise Robustness
    # ======================================================

    print("\n==============================")
    print(" NOISE ROBUSTNESS")
    print("==============================")

    for snr in [30, 20, 10, 5]:

        noisy_audio = add_noise(
            audio,
            snr
        )

        result = matcher.identify(
            audio=noisy_audio,
            sample_rate=sample_rate
        )

        matcher.print_results(result)

        results.append({

            "Experiment": "Noise",

            "Parameter": f"{snr} dB",

            "Prediction": result["song"],

            "Confidence (%)": round(
                result["confidence"],
                2
            ),

            "Votes": result["votes"]

        })

    # ======================================================
    # Pitch Robustness
    # ======================================================

    print("\n==============================")
    print(" PITCH SHIFT")
    print("==============================")

    for semitone in [-2, -1, 1, 2]:

        shifted_audio = pitch_shift(
            audio,
            sample_rate,
            semitone
        )

        result = matcher.identify(
            audio=shifted_audio,
            sample_rate=sample_rate
        )

        matcher.print_results(result)

        results.append({

            "Experiment": "Pitch",

            "Parameter": f"{semitone} semitones",

            "Prediction": result["song"],

            "Confidence (%)": round(
                result["confidence"],
                2
            ),

            "Votes": result["votes"]

        })

    # ======================================================
    # Time Stretch Robustness
    # ======================================================

    print("\n==============================")
    print(" TIME STRETCH")
    print("==============================")

    for rate in [0.90, 0.95, 1.05, 1.10]:

        stretched_audio = time_stretch(
            audio,
            rate
        )

        result = matcher.identify(
            audio=stretched_audio,
            sample_rate=sample_rate
        )

        matcher.print_results(result)

        results.append({

            "Experiment": "Stretch",

            "Parameter": f"{rate:.2f}x",

            "Prediction": result["song"],

            "Confidence (%)": round(
                result["confidence"],
                2
            ),

            "Votes": result["votes"]

        })

    # ======================================================
    # Save Results
    # ======================================================

    os.makedirs("results", exist_ok=True)

    df = pd.DataFrame(results)

    df.to_csv(
        output_csv,
        index=False
    )

    print("\n======================================")
    print("EXPERIMENTS COMPLETED")
    print("======================================")

    print(f"\nResults saved to:\n{output_csv}")

    print("\nSummary\n")

    print(df)

    return df


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    QUERY_FILE = "data/queries/query.mp3"

    DATABASE_FILE = "data/fingerprints.pkl"

    run_all_experiments(
        QUERY_FILE,
        DATABASE_FILE
    )
