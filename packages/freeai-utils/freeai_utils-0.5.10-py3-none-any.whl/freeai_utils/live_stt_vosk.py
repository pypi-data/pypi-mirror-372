import time
import json
import numpy as np
import sounddevice as sd #need pip install sounddevice
from vosk import Model, KaldiRecognizer #need pip install vosk
from typing import Optional
import os
from freeai_utils.log_set_up import setup_logging
import logging
from typing import Union
import keyboard

#this model is for live transcription than using whisper model to transcribe a provided audio (speech to text)
class STT_Vosk:
    
    logger : logging.Logger
    _model : Model
    _rec : KaldiRecognizer
    _sample_rate : int
    _dtype : str
    _channels = int
    _frame_duration = Union[int,float]
    _blocksize = int
    __stream = sd.RawInputStream
    
    def __init__(self, model_name  : str = 'en_us_015', model_path : Optional[str] = None, sample_rate : int = 16000, dtype : str = "int16", channels  : int  = 1, frame_duration : float = 0.1) -> None:
        #check type before init
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(model_path, (str, type(None)), "model_path")
        self.__enforce_type(sample_rate, int, "sample_rate")
        self.__enforce_type(dtype, str, "dtype")
        self.__enforce_type(channels, int, "channels")
        self.__enforce_type(frame_duration, (int, float), "frame_duration")
        
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vosk_models")#use defualt downloaded
        model = os.path.join(model_path, model_name) #place where the folder is
        if not os.path.isdir(model):
            raise FileNotFoundError(f"Error, path not found or is not a directory. Path : {model}")
        
        self._model = Model(model)
        self._rec = KaldiRecognizer(self._model, sample_rate)
        self._sample_rate = sample_rate
        self._dtype = dtype
        self._channels = channels
        self._frame_duration = frame_duration
        self._blocksize = int(sample_rate * self._frame_duration)
        self.logger = setup_logging(self.__class__.__name__)
        self.__stream = sd.RawInputStream(
            samplerate=self._sample_rate,
            blocksize=self._blocksize,
            dtype=self._dtype,
            channels= self._channels
        )
        
        self.logger.info("Init completed")
    
    def live_transcribe_toggle(self, toggle_key : str = "`", join_with_newline : bool = False):
        #check type
        self.__enforce_type(toggle_key, str, "toggle_key")
        self.__enforce_type(join_with_newline, bool, "join_with_newline")
        
        listening = True #var to stop
        
        def toggle():
            nonlocal listening
            listening = False
            
        try:
            keyboard.add_hotkey(toggle_key, toggle)
        except Exception as e:
            self.logger.critical(f"Fail to add hotkey {toggle_key}! Error: {e}")
            keyboard.unhook_all() #ensure no binding left
            raise
        
        last_partial = ""
        last_len     = 0
        segments = []
        amount_last = 0
        
        self.__stream.start()
        print(f"Listening… press '{toggle_key}' to stop ")
        
        try:
            while listening:
                data, overflowed = self.__stream.read(self._blocksize)
                if overflowed:
                    self.logger.warning("Warning! Overflow detected!")
                    continue
                
                raw = bytes(data)
                final_chunk = self._rec.AcceptWaveform(raw)
                
                #collect immediately
                if final_chunk:
                        result = json.loads(self._rec.FinalResult())
                        text = result.get("text", "")
                        if text:
                            segments.append(text)
                            
                
                p = json.loads(self._rec.PartialResult()).get("partial", "")
                if p != last_partial:
                    amount_need_to_ignore = int(len(p) / 100) * 100
                    if amount_need_to_ignore != amount_last:
                        print() #break
                        amount_last = amount_need_to_ignore
                    p = p[amount_last:]
                    print(len(p), end  ="\r", flush=True)
                    text = f"SPEAK: {p}"
                    length = len(text)

                    if length > last_len:
                        print(text, end="\r", flush=True)
                        last_len = length
                    else:
                        if p == "":
                            print()
                        print(f"{text}", end="\r", flush=True)
                        last_len = length
                    last_partial = p
                    
        except KeyboardInterrupt:
            self.logger.info("\nInterrupted by user.")
        finally:
            keyboard.remove_hotkey(toggle_key)
            self.__stream.stop()
            
        #final text
        final_txt = json.loads(self._rec.FinalResult()).get("text", "")
        if final_txt:
            #this should only when it get interrupted by user
            print(f"Final before getting interrupted: {final_txt}")
            segments.append(final_txt)
            
        if join_with_newline:
            return "\n".join(segments).strip()
        
        return " ".join(segments).strip()
    
    def live_transcribe_until_silence(self, silence_thresh: float = 0.01, silence_duration: Union[int, float] = 4.0, join_with_newline : bool = False) -> str:
        #check type
        self.__enforce_type(silence_thresh, float, "silence_thresh")
        self.__enforce_type(silence_duration, (int, float), "silence_duration")
        self.__enforce_type(join_with_newline, bool, "join_with_newline")
        
        last_partial = ""
        last_len     = 0
        segments = []
        amount_last = 0
        
        self.__stream.start()
        print(f"Listening… (will stop after {silence_duration}s of silence)")
        last_voice = time.time()
        
        try:
            while True:
                data, overflowed = self.__stream.read(self._blocksize)
                if overflowed:
                    self.logger.warning("Warning! Overflow detected!")
                    continue
                
                raw = bytes(data)
                final_chunk = self._rec.AcceptWaveform(raw)
                
                #collect immediately
                if final_chunk:
                        result = json.loads(self._rec.FinalResult())
                        text = result.get("text", "")
                        if text:
                            segments.append(text)
                            
                
                p = json.loads(self._rec.PartialResult()).get("partial", "")
                if p != last_partial:
                    amount_need_to_ignore = int(len(p) / 100) * 100
                    if amount_need_to_ignore != amount_last:
                        print() #break
                        amount_last = amount_need_to_ignore
                    p = p[amount_last:]
                    print(len(p), end  ="\r", flush=True)
                    text = f"SPEAK: {p}"
                    length = len(text)

                    if length > last_len:
                        print(text, end="\r", flush=True)
                        last_len = length
                    else:
                        if p == "":
                            print()
                        print(f"{text}", end="\r", flush=True)
                        last_len = length
                    last_partial = p
                    
                # Silence detection
                audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                rms = self._rms(audio)
                if rms > silence_thresh:
                    last_voice = time.time()

                if time.time() - last_voice > float(silence_duration):
                    print("\nSilence reached, finalizing…")
                    break

        except KeyboardInterrupt:
            self.logger.info("\nInterrupted by user.")
        finally:
            self.__stream.stop()
            
        #final text
        final_txt = json.loads(self._rec.FinalResult()).get("text", "")
        if final_txt:
            #this should only when it get interrupted by user
            print(f"Final before getting interrupted: {final_txt}")
            segments.append(final_txt)
        
        if join_with_newline:
            return "\n".join(segments).strip()
        
        return " ".join(segments).strip()
    
    def _help_config(self) -> None:
        """Print guide on config for init of this class"""
        model_list = [
            {"name": "en_us_015", "description": "smallest model, only 40MB, best for live transcription but sacrifices accuracy"},
            {"name": "en_us_022_lgraph", "description": "Slightly bigger model than en_us_015, 128MB, better accuracy but slower for live transcription"},
            {"name": "en_us_022_largest", "description": "Extremely big compare to other model, 1.8gb, really good accuracy but much slower for live transcription"},
            {"name": "vn_04", "description": "Vietnamese transcription, really bad tho :("},
        ]
        print("*" * 40)
        print("Including default support_model:\n")
        for option in model_list:
            print(f"Name: {option['name']}\n    Description: {option['description']}")
        print("*" * 40)
        
    def _rms(self, data): #use for silence detect
        return np.sqrt(np.mean(np.square(data / np.iinfo(np.dtype(self._dtype)).max)))
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
    def __del__(self):
        if self.__stream:
            try:
                self.__stream.stop()
                self.__stream.close()
            except Exception as e:
                self.logger.critical(f"Can not close vosk model. Error: {e}")
                raise Exception
    
if __name__ == "__main__":
    live_Stt = STT_Vosk(model_name = 'en_us_015')
    # live_Stt._help_config() #guide default installation models
    talk = live_Stt.live_transcribe_until_silence(silence_duration = 4) #transcribe and turn off after a certain amount of seconds when silence
    print(talk)
    talk = live_Stt.live_transcribe_toggle(toggle_key = "`")#transcribe until toggle off
    print(talk)