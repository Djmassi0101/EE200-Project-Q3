import os
import pickle
from collections import defaultdict
from tqdm import tqdm
from config import SUPPORTED_EXTENSIONS
from fingerprint import generate_fingerprints


class FingerprintDatabase:
    """
    Audio Fingerprint Database.
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
        Build a fingerprint database from every song in a folder.

        Parameters
        ----------
        song_directory : str
            Folder containing the audio files.
        """

        if not os.path.exists(song_directory):
            raise FileNotFoundError(
                f"Folder not found:\n{song_directory}"
            )

        self.database.clear()

        self.song_count = 0
        self.total_fingerprints = 0

        files = sorted(os.listdir(song_directory))

        audio_files = [

            file

            for file in files

            if file.lower().endswith(SUPPORTED_EXTENSIONS):

        ]

        print("\nBuilding fingerprint database...\n")

        for file in tqdm(audio_files,
                         desc="Fingerprinting Songs"):

            song_path = os.path.join(
                song_directory,
                file
            )

            song_name = os.path.splitext(file)[0]

            fingerprints = generate_fingerprints(
                audio_path=song_path
            )

            self.song_count += 1

            self.total_fingerprints += len(fingerprints)

            for fingerprint_hash, offset in fingerprints:

                self.database[fingerprint_hash].append(

                    (song_name, offset)

                )

        print("\nDatabase successfully built.\n")

    # ==========================================================
    # Save Database
    # ==========================================================

    def save(self, output_file):
        """
        Save database to disk.

        Parameters
        ----------
        output_file : str
        """

        with open(output_file, "wb") as file:

            pickle.dump(
                dict(self.database),
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        print(f"\nDatabase saved to:\n{output_file}")

    # ==========================================================
    # Load Database
    # ==========================================================

    def load(self, input_file):
        """
        Load database from disk.

        Parameters
        ----------
        input_file : str
        """

        if not os.path.exists(input_file):

            raise FileNotFoundError(
                f"Database not found:\n{input_file}"
            )

        with open(input_file, "rb") as file:

            loaded_database = pickle.load(file)

        self.database = defaultdict(
            list,
            loaded_database
        )

        print(f"\nDatabase loaded from:\n{input_file}")

    # ==========================================================
    # Search
    # ==========================================================

    def search(self, fingerprint_hash):
        """
        Search for a fingerprint.

        Parameters
        ----------
        fingerprint_hash : str

        Returns
        -------
        list

        [
            (song_name, offset),
            ...
        ]
        """

        return self.database.get(
            fingerprint_hash,
            []
        )

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(self):
        """
        Print database statistics.
        """

        print("\n========== DATABASE ==========")

        print(f"Songs Processed      : {self.song_count}")

        print(
            f"Total Fingerprints   : "
            f"{self.total_fingerprints}"
        )

        print(
            f"Unique Hashes        : "
            f"{len(self.database)}"
        )

        print("==============================\n")

    # ==========================================================
    # Number of Unique Hashes
    # ==========================================================

    def __len__(self):

        return len(self.database)

    # ==========================================================
    # String Representation
    # ==========================================================

    def __repr__(self):

        return (
            f"FingerprintDatabase("
            f"songs={self.song_count}, "
            f"hashes={len(self.database)})"
        )
