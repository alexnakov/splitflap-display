import os
from pydub import AudioSegment, effects

# Folder containing your sounds
folder = "new_audio"

# Loop through every .mp3 file in the folder
for filename in os.listdir(folder):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(folder, filename)
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

        # 3. Reduce overall volume
        sound = sound - 5  # lower by 5 dB

        # Overwrite the original file in place
        sound.export(file_path, format="mp3")
        print(f"Overwritten: {file_path}")

print("✅ All sounds softened and overwritten in 'new_audio/'")
