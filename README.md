# EE200-Project-Q3

"""
fingerprint.py
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
"""
