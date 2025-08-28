from __future__ import annotations
import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoiceInput:
    def __init__(self, model_dir: str, sample_rate: int = 16000):
        self.model = Model(model_dir)
        self.rate = sample_rate
        self.q = queue.Queue()

    def _callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_once(self, prompt: str = "Speak now...") -> str:
        print(prompt)
        rec = KaldiRecognizer(self.model, self.rate)
        with sd.RawInputStream(samplerate=self.rate, blocksize=8000, dtype='int16',
                               channels=1, callback=self._callback):
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    return res.get("text", "")
