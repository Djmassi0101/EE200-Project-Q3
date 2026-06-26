import os
from collections import Counter, defaultdict
from fingerprint import generate_fingerprints

class SongMatcher:
    def __init__(self, database=None):
        if database is None:
            # Fallback initialization placeholder
            from database import FingerprintDatabase
            self.database = FingerprintDatabase()
        else:
            self.database = database

    def load_database(self, database_path):
        """Loads the serialized dictionary/pickle database index into memory."""
        self.database.load(database_path)

    def identify(self, query_path=None, audio=None, sample_rate=None):
        """Identifies a track by analyzing temporal offsets across database hits."""
        query_fingerprints = generate_fingerprints(
            audio_path=query_path,
            audio=audio,
            sample_rate=sample_rate
        )
        
        song_histograms = defaultdict(Counter)
        matched_hashes = 0

        for fingerprint_hash, query_offset in query_fingerprints:
            matches = self.database.search(fingerprint_hash)
            if not matches:
                continue

            matched_hashes += 1
            for song_name, database_offset in matches:
                # Enforce baseline rule: strip out file extension extensions cleanly
                clean_song_name = os.path.splitext(song_name)[0]
                delta = database_offset - query_offset
                song_histograms[clean_song_name][delta] += 1

        if len(song_histograms) == 0:
            return {
                "song": None, "votes": 0, "confidence": 0, "matched_hashes": 0,
                "query_hashes": len(query_fingerprints), "histogram": Counter(), "top_matches": []
            }

        best_song = None
        best_votes = 0
        best_histogram = None
        ranking = []

        for song_name, histogram in song_histograms.items():
            peak_votes = max(histogram.values())
            ranking.append((song_name, peak_votes))

            if peak_votes > best_votes:
                best_votes = peak_votes
                best_song = song_name
                best_histogram = histogram

        ranking.sort(key=lambda x: x[1], reverse=True)
        top_matches = ranking[:5]
        confidence = (best_votes / matched_hashes) * 100 if matched_hashes > 0 else 0

        return {
            "song": best_song,
            "votes": best_votes,
            "confidence": confidence,
            "matched_hashes": matched_hashes,
            "query_hashes": len(query_fingerprints),
            "histogram": best_histogram,
            "top_matches": top_matches
        }
