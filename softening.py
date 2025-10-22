import os
from pydub import AudioSegment, effects

# Input and output folders
input_folder = "new_audio"
output_folder = os.path.join(input_folder, "softened")

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process every .mp3 file in the folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(input_folder, filename)
        print(f"Processing {filename}...")

        # Load the audio file
        sound = AudioSegment.from_file(file_path, format="mp3")

        # --- Softening operations ---
        # 1. Low-pass filter to remove sharp highs
        sound = sound.low_pass_filter(6000)   # cutoff around 6 kHz

        # 2. Light compression to smooth the transient click
        sound = effects.compress_dynamic_range(
            sound,
            threshold=-20.0,   # start compressing above -20 dB
            ratio=3.0,         # moderate compression
            attack=5.0,        # ms
            release=100.0      # ms
        )

        # 3. Reduce overall volume (make quieter)
        sound = sound - 5  # lower by 5 dB

        # 4. Export softened version to new folder
        out_path = os.path.join(output_folder, filename)
        sound.export(out_path, format="mp3")
        print(f"Saved softened sound to: {out_path}")

print("✅ All sounds processed and softened!")
