"""
build_database.py
=================

Builds the fingerprint database.

Usage:

python build_database.py
"""

from database import FingerprintDatabase

SONG_FOLDER = "data/song_database"

OUTPUT_DATABASE = "data/fingerprints.pkl"

db = FingerprintDatabase()

db.build(SONG_FOLDER)

db.statistics()

db.save(OUTPUT_DATABASE)
