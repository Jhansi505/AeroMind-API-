from faster_whisper import WhisperModel

model_size = "small.en"

model = WhisperModel (model_size, device="cpu", compute_type="float32")

segments, _ = model.transcribe("audio.mp3", language="en", beam_size=5)

for segment in segments:
    print(segment.text)