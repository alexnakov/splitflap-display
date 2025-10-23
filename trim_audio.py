from pydub import AudioSegment

audio = AudioSegment.from_file(r"/Users/user/repos/splitflap-display/alum_flap.mp3")

start_time = 30 * 1000   # e.g. 30 seconds
end_time = 45 * 1000     # e.g. 45 seconds

start_time = 1.186 * 1000   
end_time = 1.251 * 1000     

cut_audio = audio[start_time:end_time]
cut_audio.export("./audio/sf-2.mp3", format="mp3")

print("Audio trimmed and saved as output.mp3")
