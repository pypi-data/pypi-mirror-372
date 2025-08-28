import pyaudio # need pip install pyaudio
import wave
import time
import numpy as np # need pip install numpy
import keyboard #need pip install keyboard
from lameenc import Encoder #need pip install lameenc (this is use for MP3Recorder)
import logging
import os

#Record with pyaudio
#3 function: fixed-duration recording, toggle-controlled recording, and silence-based recording.

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class WavRecorder:
    def __init__(self, channels=1, rate=44100, chunk=1024, fmt=pyaudio.paInt16):
        self._channels = channels
        self._rate = rate
        self._chunk = chunk
        self._format = fmt
        self._p = pyaudio.PyAudio()
        self._frames = []
        self._stream = None
        self._recording = False
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("NOTE: WavRecorder supports only .wav output files.")
    
    @property
    def channels(self):
        # Returns the number of audio channels.
        return self._channels

    @property
    def rate(self):
        # Returns the audio sample rate.
        return self._rate

    @property
    def chunk(self):
        # Returns the audio chunk size.
        return self._chunk

    @property
    def format(self):
        # Returns the audio format.
        return self._format
       
    def _open_stream(self):
        self._stream = self._p.open(format=self._format, channels=self._channels, rate=self._rate, input=True, frames_per_buffer=self._chunk)
        self._frames = []

    def _close_stream(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

    def _save_wave(self, filename):
        self.logger.debug(f"Tryint to save audio file as {filename}")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self._channels)
        wf.setsampwidth(self._p.get_sample_size(self._format))
        wf.setframerate(self._rate)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        self.logger.info(f"Audio saved as {filename}")

    def __rms(self, data):
        #switch from audioop to this because python 3.13 wont support it anymore
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float64)
        return np.sqrt(np.mean(samples**2))

    def record_fixed(self, duration : int, output_filename : str ="fixed_record.wav") -> None:  # duration in seconds
        """Records audio for a set duration in seconds and saves it to a WAV file."""
        self.__enforce_type(duration, int, "duration")
        self.__enforce_type(output_filename, str, "output_filename")
        
        # record audio for a fixed duration
        self._open_stream()
        self.logger.info(f"Recording for {duration} seconds...")
        
        try:
            for _ in range(0, int(self._rate / self._chunk * duration)):
                data = self._stream.read(self._chunk)
                self._frames.append(data)
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C .")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
        
        finally:
            self.logger.info("Fixed-time recording finished.")
            self._close_stream()
            self._save_wave(output_filename)

    def record_toggle(self, toggle_key : str ='`', output_filename : str ="toggle_record.wav") -> None:  # default toggle key: backtick
        """Records audio continuously until a specific keyboard key (the default is backtick `) is pressed to stop it."""
        #check type
        self.__enforce_type(toggle_key, str, "toggle_key")
        self.__enforce_type(output_filename, str, "output_filename")
        
        #Start recording until toggle_key is pressed again.
        self._open_stream()
        self._recording = True
        self.logger.info(f"Recording... press '{toggle_key}' to stop.")

        # Hotkey to toggle recording state
        keyboard.add_hotkey(toggle_key, lambda: setattr(self, '_recording', False))
        try:
            while self._recording:
                data = self._stream.read(self._chunk)
                self._frames.append(data)
                # slight sleep to allow key event processing
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
        
        finally:    
            self.logger.info("Toggle recording stopped.")
            keyboard.remove_hotkey(toggle_key)
            self._close_stream()
            self._save_wave(output_filename)

    def record_silence(self, silence_threshold : int = 800, max_silence_seconds : int = 3, output_filename : str ="silence_record.wav") -> None: 
        """
        Records audio and automatically stops after a period of silence that exceeds a specified duration and volume threshold.
        """
        #check type 
        self.__enforce_type(silence_threshold, int, "silence_threshold")
        self.__enforce_type(max_silence_seconds, int, "max_silence_seconds")
        self.__enforce_type(output_filename, str, "output_filename")
        
        #Record until a period of silence longer than max_silence_seconds is detected.
        self._open_stream()
        self.logger.info(f"Recording... will stop after silence of > {max_silence_seconds}s below threshold {silence_threshold}.")
        silence_start = None

        try:
            while True:
                data = self._stream.read(self._chunk)
                self._frames.append(data)

                rms_val = self.__rms(data)
                # print(rms_val) # check value it is hearing so you could adjust base on your need
                if rms_val < silence_threshold:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > max_silence_seconds:
                        self.logger.info("Silence detected. Stopping...")
                        break
                else:
                    silence_start = None
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
        
        finally:
            self._close_stream()
            self._save_wave(output_filename)

    def terminate(self):
        self._p.terminate()

    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")

class MP3Recorder:
    def __init__(self, channels=1, rate=44100, chunk=1024, bitrate=192):
        self._channels = channels
        self._rate = rate
        self._chunk = chunk
        self._bitrate = bitrate

        # Reinitialize lame encoder
        self.encoder = Encoder()
        self.encoder.set_bit_rate(self._bitrate)
        self.encoder.set_in_sample_rate(self._rate)
        self.encoder.set_channels(self._channels)
        self.encoder.set_quality(2)  # 2 = high quality

        self._p = pyaudio.PyAudio()
        self._frames = []  # raw PCM frames
        self._stream = None
        self._recording = False
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("NOTE: MP3Recorder supports only .mp3 output files.")

    @property
    def channels(self):
        # Returns the number of audio channels.
        return self._channels

    @property
    def rate(self):
        # Returns the audio sample rate.
        return self._rate

    @property
    def chunk(self):
        # Returns the audio chunk size.
        return self._chunk

    @property
    def bitrate(self):
        # Returns the audio bitrate.
        return self._bitrate

    def _open_stream(self):
        self._stream = self._p.open(
            format=pyaudio.paInt16,
            channels=self._channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk
        )
        self._frames = []

    def _close_stream(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

    def _save_mp3(self, filename):
    # Reinitialize the encoder before use
        self.encoder = Encoder()
        self.encoder.set_bit_rate(self._bitrate)
        self.encoder.set_in_sample_rate(self._rate)
        self.encoder.set_channels(self._channels)
        self.encoder.set_quality(2)  # 2 = high quality

        self.logger.debug(f"Trying to save audio file as {filename}")
        with open(filename, 'wb') as f:
            for chunk in self._frames:
                mp3_data = self.encoder.encode(chunk)
                if mp3_data:
                    f.write(mp3_data)
            # flush encoder
            f.write(self.encoder.flush())
        self.logger.info(f"Audio saved as {filename}")

    def __rms(self, data):
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float64)
        return np.sqrt(np.mean(samples**2))

    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")

    def record_fixed(self, duration: int, output_filename: str ="fixed_record.mp3") -> None:
        """Records audio for a set duration in seconds and saves it to a MP3 file."""
        self.__enforce_type(duration, int, "duration")
        self.__enforce_type(output_filename, str, "output_filename")

        self._open_stream()
        self.logger.info(f"Recording for {duration} seconds...")
        
        try:
            for _ in range(int(self._rate / self._chunk * duration)):
                data = self._stream.read(self._chunk)
                self._frames.append(data)
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
                    
        finally:        
            self.logger.info("Fixed-time recording finished.")
            self._close_stream()
            self._save_mp3(output_filename)

    def record_toggle(self, toggle_key: str ='`', output_filename: str ="toggle_record.mp3") -> None:
        """Records audio continuously until a specific keyboard key (the default is backtick ') is pressed to stop it."""
        self.__enforce_type(toggle_key, str, "toggle_key")
        self.__enforce_type(output_filename, str, "output_filename")

        self._open_stream()
        self._recording = True
        self.logger.info(f"Recording... press '{toggle_key}' to stop.")
        keyboard.add_hotkey(toggle_key, lambda: setattr(self, '_recording', False))
        
        try: 
            while self._recording:
                data = self._stream.read(self._chunk)
                self._frames.append(data)
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
            
        finally:
            self.logger.info("Toggle recording stopped.")
            keyboard.remove_hotkey(toggle_key)
            self._close_stream()
            self._save_mp3(output_filename)

    def record_silence(self, silence_threshold: int = 800, max_silence_seconds: int = 3, output_filename: str ="silence_record.mp3") -> None:
        """
        Records audio and automatically stops after a period of silence that exceeds a specified duration and volume threshold.
        """
        self.__enforce_type(silence_threshold, int, "silence_threshold")
        self.__enforce_type(max_silence_seconds, int, "max_silence_seconds")
        self.__enforce_type(output_filename, str, "output_filename")

        self._open_stream()
        self.logger.info(f"Recording... will stop after >{max_silence_seconds}s below threshold {silence_threshold}.")
        silence_start = None
        try:
            while True:
                data = self._stream.read(self._chunk)
                self._frames.append(data)
                rms_val = self.__rms(data)
                if rms_val < silence_threshold:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > max_silence_seconds:
                        self.logger.info("Silence detected. Stopping...")
                        break
                else:
                    silence_start = None
        except KeyboardInterrupt:
            self.logger.critical("Recording stopped manually using CTRL + C.")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise
            
        finally:
            self._close_stream()
            self._save_mp3(output_filename)

    def terminate(self):
        self._p.terminate()

from mutagen.mp3 import MP3, MutagenError

def check_wav_length_and_size(file_path: str, period: float = 5.0, allowed_logger : bool = True) -> bool:
    """
    Checks if a given WAV audio file's duration is less than or equal to a specified time period. 
    It returns True if it is and False if it isn't. The function also logs the file's duration and size.
    """
    logger = logging.getLogger("WAV Checker")
    if allowed_logger:
        logger.setLevel(logging.INFO)
    else: logger.setLevel(logging.ERROR)
    try:
        with wave.open(file_path, 'rb') as wf:
            frame_rate = wf.getframerate()
            num_frames = wf.getnframes()
            duration = num_frames / float(frame_rate)

        file_size_bytes = os.path.getsize(file_path)

        if duration <= period:
            logger.info("'%s' is less than or equal to %.2f seconds long (duration: %.2f seconds).", 
                        file_path, period, duration)
            logger.info("File size: %d bytes.", file_size_bytes)
            return True
        else:
            logger.info("'%s' is %.2f seconds long, which exceeds %.2f seconds.", 
                           file_path, duration, period)
            return False
    except wave.Error as e:
        logger.error(f"Error opening or reading WAV file '{file_path}': {e}")
        raise
    except FileNotFoundError:
        logger.error(f"Error: File not found at '{file_path}'")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

def check_mp3_length_and_size(file_path: str, period: float = 5.0, allowed_logger : bool = True) -> bool:
    """
    Checks if a given MP3 audio file's duration is less than or equal to a specified time period. 
    It returns True if it is and False if it isn't. The function also logs the file's duration and size.
    """
    logger = logging.getLogger("MP3 Checker")
    if allowed_logger:
        logger.setLevel(logging.INFO)
    else: logger.setLevel(logging.ERROR)
    try:
        audio = MP3(file_path)
        duration = audio.info.length  # length in seconds
        file_size_bytes = os.path.getsize(file_path)

        if duration <= period:
            logger.info("'%s' is less than or equal to %.2f seconds long (duration: %.2f seconds).", 
                        file_path, period, duration)
            logger.info("File size: %d bytes.", file_size_bytes)
            return True
        else:
            logger.info("'%s' is %.2f seconds long, which exceeds %.2f seconds.", 
                           file_path, duration, period)
            return False
    except MutagenError as e:
        logger.error("Mutagen error reading MP3 file '%s': %s", file_path, e)
        raise
    except FileNotFoundError:
        logger.error(f"Error: File not found at '{file_path}'")
        raise
    except Exception as e:
        logger.error("Error processing MP3 file '%s': %s", file_path, e)
        raise

#EXAMPLE
def _test_function():
    _rec = WavRecorder()
    _rec.record_toggle()
        
if __name__ == "__main__":
    import multiprocessing
    _p = multiprocessing.Process(target=_test_function)
    _p.start()
    # Simulate later termination, this would not provide you any audio output
    time.sleep(5)
    _p.terminate()  
    _p.join()
    
    _d = multiprocessing.Process(target=function) #this would pause until you actually press ` to stop recording
    _d.start()
    _d.join()
    
    _rec = WavRecorder() # you could just use as normal if you dont need to interrupt midway 
    _rec.record_fixed(3) 
    
    _rec = MP3Recorder()
    _rec.record_fixed(4)
    