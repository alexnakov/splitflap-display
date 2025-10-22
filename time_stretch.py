import librosa
import soundfile as sf
import os

directory = "./new_audio"

# Time stretch rate
rate = 1.4

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".mp3"):
        file_path = os.path.join(directory, filename)
        print(f"Processing {filename}...")

        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)

        # Apply time-stretching
        y_stretched = librosa.effects.time_stretch(y, rate=rate)

        # Save (overwrite) with same name
        sf.write(file_path, y_stretched, sr)

print("✅ Done: all sounds have been time-stretched.")
