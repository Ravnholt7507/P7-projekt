import pandas as pd
import pyttsx3

timeIntervals = 10
readLimit = 50000
output_CSV = pd.DataFrame()
tts = 0


class TextToSpeech:
    def __init__(self, voice_id=None, speed=100):
        self.voice_id = voice_id
        self.speed = speed
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
<<<<<<< Updated upstream
        self.set_voice(self.voice_id)
        self.set_speed(self.speed)
=======
        self.set_voice(voice_id)
        self.set_speed(speed)
>>>>>>> Stashed changes
        self.speech_enabled = True

    def toggle_speech(self, enable=True):
        self.speech_enabled = enable

    def set_voice(self, voice_id):
        if voice_id is not None and 0 <= voice_id < len(self.voices):
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
            self.engine.setProperty('voice', self.voices[voice_id].id)

    def set_speed(self, speed):
        self.engine.setProperty('rate', speed)

<<<<<<< Updated upstream
    def speak(self, text, *variables):
        if self.speech_enabled:
            variable_strings = [str(variable) for variable in variables]
            speech_text = text.format(*variable_strings)
=======

    def speak(self, text, variables):
        if self.speech_enabled == True:
            variable_strings = [str(variable) for variable in variables]
            speech_text = text.format(variable_strings)
>>>>>>> Stashed changes
            print(speech_text)
            self.engine.say(speech_text)
            self.engine.runAndWait()