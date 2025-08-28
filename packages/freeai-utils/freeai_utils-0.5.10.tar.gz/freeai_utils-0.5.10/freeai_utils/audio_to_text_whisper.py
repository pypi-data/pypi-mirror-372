import warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"whisper\.transcribe",
)
import whisper #need pip install openai-whisper
import numpy as np # need pip install numpy
import torch # need pip install torch
from typing import Dict, Any, List
from typing import Optional
from freeai_utils.log_set_up import setup_logging
import ffmpeg #need pip install ffmpeg-python
import imageio_ffmpeg as iioff #need pip install imageio-ffmpeg

# 4 function use: transcribe -> return Dict (return everything and you choose which to get)
#                 get_lang_detect -> return str (return the language)
#                 get_transcription -> return str (return the transcription only, for people who doesnt care what language or anything else)
#                 get_time_transcription -> return a list of list containing 3 item each: start_time, end_time, and the text

class OpenAIWhisper:
    
    __slots__ = ("_model", "_initialized", "logger", "_device", "_sample_rate")
    
    def __init__(self, model: str = "medium", sample_rate: int = 16000, device : Optional[str]  = None) -> None:
        #check type
        self.__enforce_type(sample_rate, int, sample_rate)
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.propagate = False 
        # init not lock
        super().__setattr__("_initialized", False)
        
        # model: Whisper model size ("tiny", "base", "small", "medium", "large")
        self._sample_rate = sample_rate
        self._model = None 
        self._device = None 
        
        #init the var to hold device available
        preferred_devices = []
        
        #try input first
        if device is not None:
            self.__enforce_type(device, str, "device")
            preferred_devices.append(device)
        
        # try cuda second 
        if torch.cuda.is_available() and "cuda" not in preferred_devices:
            preferred_devices.append("cuda")

        # fall back to CPU if not already there
        if "cpu" not in preferred_devices:
            preferred_devices.append("cpu")

        last_err = None
        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading '{model}' model on {dev}...")
                self._model = whisper.load_model(model, device=dev)
                self._model.eval()
                self._device = dev
                self.logger.info(f"Model successfully loaded on {dev}.")
                break
            except RuntimeError as e:
                last_err = e
                self.logger.error(f"Failed to load on {dev}: {e}")
            except Exception as e: 
                last_err = e
                self.logger.error(f"An unexpected error occurred while loading model on {dev}: {e}")
        
        if self._model is None: #check if nothing works, then raise error
            raise RuntimeError(f"Could not load model on any device. Last error:\n{last_err}")
        
        # lock
        super().__setattr__("_initialized", True)
        
    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def model(self):
        return self._model

    @property
    def device(self):
        return self._device

    def _load_media(self, path: str) -> np.ndarray:
        #Load ANY audio/video file via the private FFmpeg bundled by imageio-ffmpeg,
        # get the path to the ffmpeg binary that imageio_ffmpeg downloaded
        ffmpeg_exe = iioff.get_ffmpeg_exe()

        out, _ = (ffmpeg.input(path).output(
                'pipe:',
                format='f32le',       # 32-bit float samples
                ar=self._sample_rate, 
                ac=1                  # mono
                ).run(cmd=ffmpeg_exe, capture_stdout=True, capture_stderr=True)
            )

        # convert raw bytes to NumPy array
        audio = np.frombuffer(out, dtype=np.float32).copy()
        return audio

    def transcribe(self, audio_path: str, fp16: bool = False, **transcribe_kwargs: Any) -> Dict[str, Any]:
        """
        Transcribes an audio file from a given file path. 
        Returns a dictionary with the transcription results, including text, and other data.
        """
        # Transcribes audio from a file path.
        # param audio_path: Path to the audio file.
        # param fp16: Whether to use fp16 precision (GPU only).
        # param transcribe_kwargs: Additional arguments dokter for whisper.model.transcribe().
        # return: A dictionary containing the transcription results.
        
        self.__enforce_type(audio_path, str, "audio_path")
        self.__enforce_type(fp16, bool, "fp16")
        
        try:
            audio_data = self._load_media(audio_path)
                
            # get the np.ndarray to the transcribe
            self.logger.info(f"Transcribing audio from {audio_path} on {self._device}...")
            result = self._model.transcribe(audio_data, fp16=fp16 if self._device == "cuda" else False, **transcribe_kwargs)
            self.logger.info(f"Transcription successful.")
            return result #return result
        except Exception as e:
            self.logger.error(f"Transcription failed for {audio_path}: {e}")
            raise

    def get_time_transcription(self, audio_path: str, fp16: bool = False, **transcribe_kwargs: Any) -> List[List[Any]]:
        """
        Transcribes an audio file and returns a list of lists, where each inner list contains the start time, end time, and transcribed text.
        """
        result = self.transcribe(audio_path=audio_path, fp16=fp16 if self._device == "cuda" else False, **transcribe_kwargs)
        segments = result.get("segments", [])
        return [
            [seg["start"], seg["end"], seg["text"]]
            for seg in segments
        ]
    
    def get_transcription(self, audio_path: str, fp16: bool = False, **transcribe_kwargs: Any) -> str:
        """
        Transcribes an audio file and returns only the full transcribed text as a single string, without any additional data.
        """
        text = self.transcribe(audio_path=audio_path, fp16=fp16, **transcribe_kwargs)["text"]
        return text

    def get_lang_detect(self, audio_path: str, fp16: bool = False, **transcribe_kwargs: Any) -> str:
        """
        Transcribes an audio file to determine the language of the audio and returns the detected language as a string.
        """
        language = self.transcribe(audio_path=audio_path, fp16=fp16, **transcribe_kwargs)["language"]
        return language
    
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")
    
    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model", "_device"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)