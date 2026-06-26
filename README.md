# EE200-Project-Q3


*fingerprint.py*
==============

Core audio fingerprint generation module.

This module is responsible for:

1. Loading audio
2. Computing the spectrogram
3. Detecting spectral peaks
4. Creating the constellation map
5. Generating Shazam-style fingerprint hashes

Every other module in the project (database, matcher,
experiments, Streamlit app) should use this module
instead of implementing their own fingerprinting logic.

*app.py*
======

Streamlit application for the Audio Fingerprinting project.

Features
--------
1. Upload an MP3 file
2. Identify the song
3. Display confidence score
4. Show top matches
5. Plot offset histogram


*database.py*
===========

Manages the audio fingerprint database.

Responsibilities
----------------
1. Build fingerprint database from a folder of songs.
2. Save the database to disk.
3. Load an existing database.
4. Provide lookup functions for the matcher.
5. Display useful statistics.

Database Structure
------------------

{
    fingerprint_hash : [
        (song_name, offset),
        (song_name, offset),
        ...
    ]
}



*experiments.py*
==============

Runs robustness experiments on the audio fingerprinting system.

Experiments Performed
---------------------
1. Original audio
2. Additive Gaussian Noise
3. Pitch Shift
4. Time Stretch

Results are saved as a CSV file for use in the project report.
