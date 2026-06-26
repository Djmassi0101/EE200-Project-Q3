"""
build_database.py
=================

Build the fingerprint database.

Run:

python build_database.py
"""

from database import FingerprintDatabase


SONG_FOLDER = "data/song_database"

OUTPUT_DATABASE = "data/fingerprints.pkl"


def main():

    db = FingerprintDatabase()

    db.build(SONG_FOLDER)

    db.statistics()

    db.save(OUTPUT_DATABASE)


if __name__ == "__main__":

    main()
