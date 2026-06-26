import os
import pickle
from collections import defaultdict
from tqdm import tqdm

# Import your corrected, operational DSP pipeline
from fingerprint import generate_fingerprints

def build_production_database():
    library_dir = "data/library"
    output_path = "data/fresh_fingerprints.pkl"
    
    # Clean out any old index versions if they exist
    if os.path.exists(output_path):
        os.remove(output_path)
        print("🗑️ Removed old database index.")
        
    database_dict = defaultdict(list)
    supported_formats = (".mp3", ".wav", ".m4a", ".flac")
    
    # Ensure the source directory exists
    if not os.path.exists(library_dir):
        os.makedirs(library_dir)
        print(f"📁 Created missing source folder at '{library_dir}'. Please add your tracks.")
        return
    
    audio_files = [f for f in os.listdir(library_dir) if f.lower().endswith(supported_formats)]
    
    if not audio_files:
        print(f"❌ ERROR: No reference tracks found in '{library_dir}'.")
        return

    print(f"Indexing reference library: Compiling {len(audio_files)} tracks...")
    
    for filename in tqdm(audio_files, desc="Processing Tracks"):
        file_path = os.path.join(library_dir, filename)
        song_name = os.path.splitext(filename)[0]
        
        try:
            # This automatically tracks the synchronized 2048 window configurations from fingerprint.py
            fingerprints = generate_fingerprints(audio_path=file_path)
            
            for fingerprint_hash, anchor_time in fingerprints:
                # CRITICAL: Force cast the offset to a native standard Python int
                database_dict[fingerprint_hash].append((song_name, int(anchor_time)))
        except Exception as e:
            print(f"\n⚠️ Skipping track '{filename}' due to execution error: {e}")
            continue

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write out the clean database index matrix
    with open(output_path, "wb") as f:
        pickle.dump(dict(database_dict), f, protocol=pickle.HIGHEST_PROTOCOL)
        
    print(f"\n✅ Production index cleanly built at: {output_path}")

if __name__ == "__main__":
    build_production_database()