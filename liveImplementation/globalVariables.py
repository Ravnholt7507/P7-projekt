import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pyttsx3

timeIntervals = 10
readLimit = 50000
output_CSV = pd.DataFrame()
scaler = MinMaxScaler()

class TextToSpeech:
    def init(self, voice_id=None, speed=100):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.set_voice(voice_id)
        self.set_speed(speed)
        self.speech_enabled = True