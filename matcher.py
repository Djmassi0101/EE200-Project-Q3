import pickle
from collections import defaultdict
# Import the corrected fingerprint pipeline directly
from fingerprint import generate_fingerprints

class SongMatcher:
    def __init__(self):
        self.database = {}

    def load_database(self, database_path):
        """Loads the serialized fingerprint database mapping dictionary into memory."""
        with open(database_path, "rb") as f:
            self.database = pickle.load(f)

    def identify(self, query_path=None, audio=None, sample_rate=None):
        """
        Identifies an unknown audio clip by aligning fingerprint time-offsets.
        """
        # CRITICAL FIX: Extract fingerprints using the file path to preserve the 11025 Hz downsampling
        if query_path is not None:
            query_fingerprints = generate_fingerprints(audio_path=query_path)
        else:
            query_fingerprints = generate_fingerprints(audio=audio, sample_rate=sample_rate)

        total_query_hashes = len(query_fingerprints)
        
        if total_query_hashes == 0:
            return {"song": "Unknown (No Hashes Found)", "confidence": 0.0, "votes": 0, "histogram": {}}

        # Song name -> Offset Delta Bins -> Vote Count
        song_histograms = defaultdict(lambda: defaultdict(int))
        matched_hashes_count = 0

        # Scan through every fingerprint extracted from the query clip
        for q_hash, q_offset in query_fingerprints:
            if q_hash in self.database:
                matched_hashes_count += 1
                # Retrieve all library matches for this specific hash token
                for song_name, db_offset in self.database[q_hash]:
                    # CRITICAL FIX: Explicitly cast both offsets to native standard Python ints
                    delta_offset = int(db_offset) - int(q_offset)
                    song_histograms[song_name][delta_offset] += 1

        if not song_histograms:
            return {"song": "Unknown (No Database Matches)", "confidence": 0.0, "votes": 0, "histogram": {}}

        best_song = None
        best_offset = None
        max_votes = -1
        target_histogram = {}

        # Find the single highest alignment spike across all candidate songs
        for song_name, offsets_dict in song_histograms.items():
            for offset_bin, vote_count in offsets_dict.items():
                if vote_count > max_votes:
                    max_votes = vote_count
                    best_song = song_name
                    best_offset = offset_bin
                    target_histogram = dict(offsets_dict)

        # Confidence metric calculation: percentage of matched query items aligning to the peak bin
        confidence = (max_votes / total_query_hashes) * 100

        return {
            "song": best_song,
            "confidence": confidence,
            "votes": max_votes,
            "histogram": target_histogram
        }