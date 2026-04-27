import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

model = Model("model")
recognizer = KaldiRecognizer(model, 16000)

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    print("Listening... say bathroom or robotics lab")

    while True:
        data = q.get()

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            print("Heard:", text)

            if "bathroom" in text:
                print("Go LEFT")
                break

            elif "robotics" in text or "lab" in text:
                print("Go RIGHT")
                break