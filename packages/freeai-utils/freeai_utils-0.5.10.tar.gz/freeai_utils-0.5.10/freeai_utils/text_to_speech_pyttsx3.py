import pyttsx3 #need pip install pyttsx3

class Text_To_Speech_Pyttsx3:
    def __init__(self, rate=170, volume=1.0, voice_index=0) -> None:
        self.__engine = pyttsx3.init()
        self.config_voice(rate, volume, voice_index)

    @property
    def engine(self):
        return self.__engine

    def config_voice(self, rate: float = 170, volume: float = 1.0, voice_index: int = 0) -> None:
        """Adjust the speech rate, volume, and select a specific voice using its numerical index."""
        if not isinstance(rate, (int, float)):
            raise TypeError("Rate must be a number.")
        if not (0.0 <= volume <= 1.0):
            raise ValueError("Volume must be between 0.0 and 1.0.")
        
        voices = self.__engine.getProperty('voices')
        if not isinstance(voice_index, int) or not (0 <= voice_index < len(voices)):
            raise ValueError(f"Voice index must be between 0 and {len(voices)-1}")
        
        self.__engine.setProperty('rate', rate)
        self.__engine.setProperty('volume', volume)
        self.__engine.setProperty('voice', voices[voice_index].id)

    def speak(self, text: str) -> None:
        """Takes a string of text and converts it into spoken audio. It uses the voice settings configured by config_voice to speak the text. The function will not proceed until all the text has been spoken."""
        if not isinstance(text, str):
            raise ValueError(f"The provided text is not string!")
        self.__engine.say((text))
        self.__engine.runAndWait()

    def stop(self) -> None:
        self.__engine.stop()