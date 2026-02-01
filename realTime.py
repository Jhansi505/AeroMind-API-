import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel

# Settings
samplerate = 16000
block_duration = 0.5 #seconds
chunk_duration=2 #seconds
channels=1

frames_per_block = int(samplerate * block_duration)
frames_per_chunk = int(samplerate * chunk_duration)

audio_queue = queue.Queue()
audio_buffer = []

#Model setup: medium.en + float16 (optimized for 3088)
model = WhisperModel("large-v3", device="cpu", compute_type="float32")

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def recorder():
    try:
        # Check for available input devices
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            print("No audio input devices found. Cannot record live audio.")
            print("Consider uploading an audio file and modifying the `transcriber` function to process it.")
            return

        # Use the default input device if found
        # If you have multiple devices, you might need to specify device=input_devices[0]['name'] or similar
        with sd.InputStream(samplerate=samplerate, channels=channels,
                            blocksize=frames_per_block, callback=audio_callback):
            print(" Listening... Press Ctrl+C to stop.")
            while True:
                sd.sleep(100)
    except sd.PortAudioError as e:
        print(f"Error initializing audio input: {e}")
        print("This often happens in environments like Google Colab where direct microphone access is restricted.")
        print("You might need to provide audio input via a pre-recorded file or a browser-based recording method.")
    except Exception as e:
        print(f"An unexpected error occurred in the recorder: {e}")


def transcriber():
    global audio_buffer
    while True:
        block = audio_queue.get()
        audio_buffer.append(block)
        total_frames = sum(len(block) for block in audio_buffer)
        if total_frames >= frames_per_chunk:
            audio_data = np.concatenate(audio_buffer)[:frames_per_chunk]
            audio_buffer = [] # Clear buffer
            audio_data = audio_data.flatten().astype(np.float32)

            #Transcription without timestamps
            segments, _ = model.transcribe(
                audio_data,
                language="en",
                beam_size=1 # Max speed
            )

            for segment in segments:
                print(f"{segment.text}")

#Start threads
threading.Thread(target=recorder, daemon=True).start()
transcriber()