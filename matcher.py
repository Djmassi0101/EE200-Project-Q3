"""
matcher.py
==========

Song recognition module.

Responsibilities
----------------
1. Load fingerprint database.
2. Fingerprint a query song.
3. Compare fingerprints with the database.
4. Compute offset histogram.
5. Return the best matching song.

Author: <Your Name>
"""

from collections import Counter, defaultdict

from fingerprint import generate_fingerprints
from database import FingerprintDatabase


class SongMatcher:
    """
    Song recognition engine.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(self, database=None):
        """
        Parameters
        ----------
        database : FingerprintDatabase
            Optional database object.
        """

        if database is None:
            self.database = FingerprintDatabase()
        else:
            self.database = database

    # ==========================================================
    # Load Database
    # ==========================================================

    def load_database(self, database_path):
        """
        Load fingerprints.pkl
        """

        self.database.load(database_path)

    # ==========================================================
    # Identify Song
    # ==========================================================

    def identify(
    self,
    query_path=None,
    audio=None,
    sample_rate=None
):
        """
        Identify a query song.

        Parameters
        ----------
        query_path : str

        Returns
        -------
        Dictionary containing

        song
        votes
        confidence
        histogram
        top_matches
        """

       print("\nGenerating query fingerprints...")

query_fingerprints = generate_fingerprints(
    audio_path=query_path,
    audio=audio,
    sample_rate=sample_rate
)

print(f"{len(query_fingerprints)} fingerprints generated.\n")
        # ------------------------------------------------------
        # Store votes for every song
        # ------------------------------------------------------

        song_histograms = defaultdict(Counter)

        matched_hashes = 0

        # ------------------------------------------------------
        # Compare every query fingerprint with database
        # ------------------------------------------------------

        for fingerprint_hash, query_offset in query_fingerprints:

            matches = self.database.search(
                fingerprint_hash
            )

            if not matches:
                continue

            matched_hashes += 1

            for song_name, database_offset in matches:

                delta = database_offset - query_offset

                song_histograms[song_name][delta] += 1

        # ------------------------------------------------------
        # No matches
        # ------------------------------------------------------

        if len(song_histograms) == 0:

            return {

                "song": None,

                "votes": 0,

                "confidence": 0,

                "matched_hashes": 0,

                "query_hashes": len(query_fingerprints),

                "histogram": Counter(),

                "top_matches": []

            }

        # ------------------------------------------------------
        # Determine best song
        # ------------------------------------------------------

        best_song = None

        best_votes = 0

        best_histogram = None

        ranking = []

        for song_name, histogram in song_histograms.items():

            peak_votes = max(histogram.values())

            ranking.append(
                (song_name, peak_votes)
            )

            if peak_votes > best_votes:

                best_votes = peak_votes

                best_song = song_name

                best_histogram = histogram

        # ------------------------------------------------------
        # Sort ranking
        # ------------------------------------------------------

        ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )

        top_matches = ranking[:5]

        # ------------------------------------------------------
        # Confidence
        # ------------------------------------------------------

        if matched_hashes == 0:

            confidence = 0

        else:

            confidence = (
                best_votes /
                matched_hashes
            ) * 100

        # ------------------------------------------------------
        # Return results
        # ------------------------------------------------------

        return {

            "song": best_song,

            "votes": best_votes,

            "confidence": confidence,

            "matched_hashes": matched_hashes,

            "query_hashes": len(query_fingerprints),

            "histogram": best_histogram,

            "top_matches": top_matches

        }
          # ==========================================================
    # Plot Offset Histogram
    # ==========================================================

    def plot_histogram(self, histogram):
        """
        Plot the offset histogram of the best matching song.

        Parameters
        ----------
        histogram : Counter
            Histogram returned by identify().
        """

        import matplotlib.pyplot as plt

        if histogram is None or len(histogram) == 0:

            print("No histogram available.")

            return

        plt.figure(figsize=(12,5))

        plt.bar(
            histogram.keys(),
            histogram.values(),
            width=1.0,
            color="steelblue",
            edgecolor="black"
        )

        plt.title("Offset Histogram")

        plt.xlabel("Offset Difference")

        plt.ylabel("Votes")

        plt.grid(alpha=0.3)

        plt.tight_layout()

        plt.show()


    # ==========================================================
    # Print Recognition Results
    # ==========================================================

    def print_results(self, result):
        """
        Pretty-print recognition results.

        Parameters
        ----------
        result : dict
            Output from identify().
        """

        print("\n===================================")
        print("      AUDIO RECOGNITION RESULT")
        print("===================================\n")

        if result["song"] is None:

            print("No matching song found.")

            print("\n===================================\n")

            return

        print(f"Predicted Song     : {result['song']}")

        print(f"Matching Votes     : {result['votes']}")

        print(f"Confidence         : {result['confidence']:.2f}%")

        print(
            f"Matched Hashes     : "
            f"{result['matched_hashes']} / "
            f"{result['query_hashes']}"
        )

        print("\nTop Matches")

        print("-------------------------------")

        for i, (song, votes) in enumerate(result["top_matches"], 1):

            print(f"{i}. {song:<25} {votes}")

        print("\n===================================\n")


# ==============================================================
# Standalone Test
# ==============================================================

if __name__ == "__main__":

    DATABASE_PATH = "data/fingerprints.pkl"

    QUERY_FILE = "data/queries/query.mp3"

    matcher = SongMatcher()

    matcher.load_database(DATABASE_PATH)

    result = matcher.identify(QUERY_FILE)

    matcher.print_results(result)

    matcher.plot_histogram(result["histogram"])
