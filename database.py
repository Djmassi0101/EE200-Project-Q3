"""
database.py
===========

Creates, loads, saves, and manages the audio fingerprint database.

The database structure is:

{
    fingerprint_hash : [
        (song_name, offset),
        (song_name, offset),
        ...
    ]
}

Author: <Your Name>
"""

import os
import pickle
from collections import defaultdict

from fingerprint import generate_fingerprints


class FingerprintDatabase:
    """
    Audio fingerprint database manager.
    """

    def __init__(self):
        """
        Initialize an empty fingerprint database.
        """

        self.database = defaultdict(list)

        self.song_count = 0

        self.total_fingerprints = 0

    # ==========================================================
    # Build Database
    # ==========================================================

    def build(self, song_directory):
        """
        Build a fingerprint database from every supported audio
        file inside a directory.

        Parameters
        ----------
        song_directory : str
            Folder containing the songs.
        """

        self.database.clear()

        self.song_count = 0

        self.total_fingerprints = 0

        files = sorted(os.listdir(song_directory))

        print("\nBuilding fingerprint database...\n")

        for file in files:

            if not file.lower().endswith(
                (".wav", ".mp3", ".flac")
            ):
                continue

            song_path = os.path.join(song_directory, file)

            song_name = os.path.splitext(file)[0]

            print(f"Processing: {song_name}")

            fingerprints = generate_fingerprints(song_path)

            self.song_count += 1

            self.total_fingerprints += len(fingerprints)

            for fingerprint_hash, offset in fingerprints:

                self.database[fingerprint_hash].append(
                    (song_name, offset)
                )

            print(
                f"   {len(fingerprints)} fingerprints generated."
            )

        print("\nDatabase build complete.\n")

    # ==========================================================
    # Save Database
    # ==========================================================

    def save(self, output_path):
        """
        Save the fingerprint database.

        Parameters
        ----------
        output_path : str
        """

        with open(output_path, "wb") as file:

            pickle.dump(dict(self.database), file)

        print(f"Database saved to:\n{output_path}")

    # ==========================================================
    # Load Database
    # ==========================================================

    def load(self, input_path):
        """
        Load a previously generated database.

        Parameters
        ----------
        input_path : str
        """

        with open(input_path, "rb") as file:

            loaded = pickle.load(file)

        self.database = defaultdict(list, loaded)

        print(f"Database loaded from:\n{input_path}")

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self):
        """
        Display database statistics.
        """

        unique_hashes = len(self.database)

        print("\n========== Database Statistics ==========")

        print(f"Songs Processed      : {self.song_count}")

        print(
            f"Total Fingerprints   : {self.total_fingerprints}"
        )

        print(f"Unique Hashes        : {unique_hashes}")

        print("=========================================\n")

    # ==========================================================
    # Database Size
    # ==========================================================

    def __len__(self):
        """
        Number of unique hashes.
        """

        return len(self.database)
