from transformers import AutoProcessor, AutoModelForImageTextToText # need pip install transformers 
from PIL import Image # need pip install torch
import torch # need pip install torch
import logging
from typing import Optional
from .log_set_up import setup_logging

#Another model_name : "Salesforce/blip-image-captioning-base"

class ImageCaptioner:
    
    __slots__ = ("_device", "_processor", "_model", "logger", "_initialized")
    _device: str
    _processor: AutoProcessor
    _model: AutoModelForImageTextToText
    logger: logging.Logger
    _initialized: bool
    
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-large", device: Optional[str] = None):
        #check input type
        self.__enforce_type(model_name, str, "model_name")
        
        #init
        super().__setattr__("_initialized", False)
        #logger 
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.info("Note: This class takes an image path as input and generates a caption. It is not designed for question answering.")
        
        try:
            self._processor = AutoProcessor.from_pretrained(model_name, use_fast=True, local_files_only = True)
            self._model = AutoModelForImageTextToText.from_pretrained(model_name, local_files_only = True)
        except Exception:
            self.logger.info(f"Detect local model not found, attemp to download {model_name}")
            self._processor = AutoProcessor.from_pretrained(model_name, use_fast=True)
            self._model = AutoModelForImageTextToText.from_pretrained(model_name)
                
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
                self.logger.info(f"Loading '{model_name}' model on {dev}.")
                self._device = dev
                self._model.to(self._device)
                self._model.eval()
                self.logger.info(f"Successfully loaded on {dev}.")
                break
            except RuntimeError as e:
                last_err = e
                self.logger.error(f"Failed to load on {dev}: {e}")
            except Exception as e: 
                last_err = e
                self.logger.error(f"An unexpected error occurred while loading model on {dev}: {e}")
        
        if self._model is None: #check if nothing works, then raise error
            raise RuntimeError(f"Could not load model on any device. Last error:\n{last_err}")
            
        #stop
        super().__setattr__("_initialized", True)
        
    @property
    def device(self):
        return self._device

    @property
    def processor(self):
        return self._processor

    @property
    def model(self):
        return self._model

    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_device", "_processor", "_model"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
        
    def write_caption(self, image_path: str, max_length: int = 100, num_beams: int = 3, early_stopping: bool = True) -> str:
        """
        Generates a descriptive caption for an image.
        """
        #check type
        self.__enforce_type(image_path, str, "image_path")
        self.__enforce_type(max_length, int, "max_length")
        self.__enforce_type(num_beams, int, "num_beams")
        self.__enforce_type(early_stopping, bool, "early_stopping")
        
        #check num_beam >= 2
        if num_beams < 2:
            raise ValueError(f"num_beams must be >= 2, but got {num_beams}") #Added the value to the error
        
        # load image
        try:
            image = Image.open(image_path).convert("RGB")
        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {image_path}")

        inputs = self._processor(images=image, return_tensors="pt").to(self._device)
        with torch.no_grad():
            outputs = self._model.generate(**inputs, max_length=max_length, num_beams=num_beams, early_stopping=early_stopping)

        # text return
        return self._processor.decode(outputs[0], skip_special_tokens=True)

    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")