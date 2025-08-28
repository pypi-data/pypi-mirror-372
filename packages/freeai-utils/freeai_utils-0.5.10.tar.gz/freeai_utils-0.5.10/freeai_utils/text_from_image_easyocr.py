# Library for people who want to do ocr but don't want to download Tesseract OCR
# Weaker than Tesseract OCR

# need pip install pyautogui (use to screenshot)
try:
    import pyautogui
except ImportError:
    print("The 'pyautogui' library is required for this feature.")
    raise ImportError("Please install it with: pip install pyautogui")

import easyocr# need pip install easyocr (use to read text from image)
import time
from typing import Optional, List, Union
from freeai_utils.log_set_up import setup_logging
import logging

class Text_Extractor_EasyOCR:
    
    __slots__ = ("_reader", "_initialized", "logger", "_screen_width", "_screen_height", "_capture_region")
    _reader: easyocr.Reader
    _initialized: bool
    logger: logging.Logger
    _screen_height: int
    _screen_width: int
    _capture_region: tuple
    
    def __init__(self, language : Union[List[str], str, None] = None, prefer_device: str = 'cuda') -> None:
        #check type of the input
        if language is None:
            language = ['vi', 'en']
        self.__enforce_type(language, (str, list), "language")
        self.__enforce_type(prefer_device, str, "prefer_device")
        
        if isinstance(language, str): #ensure language is a list
            language = [language]

        # init not lock
        super().__setattr__("_initialized", False)
        
        #set up logger
        self.logger = setup_logging(self.__class__.__name__)
        
        self._reader = self._initialize_reader(language, prefer_device)
        self._screen_width, self._screen_height = pyautogui.size()
        self._capture_region = (0, 0, self._screen_width, self._screen_height) # default, capture fullscreen

        # lock
        super().__setattr__("_initialized", True)
        
    @property
    def capture_region(self) -> tuple:
        return self._capture_region
    
    @capture_region.setter
    def capture_region(self, value: tuple) -> None: #this to modify the region manually
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("capture_region must be a tuple of size 4.")
        self._capture_region = value
    
    @property
    def reader(self):
        return self._reader
    
    def _initialize_reader(self, language: List[str], prefer_device: str):
        """Initializes an easyocr.Reader instance."""
        if prefer_device.lower() == 'cuda':
            try:
                reader = easyocr.Reader(language, gpu=True)
                self.logger.info("EasyOCR initialized with CUDA.")
                return reader
            except Exception as e:
                self.logger.error(f"CUDA not available or initialization failed: {e}")
                self.logger.info("Falling back to CPU.")
                reader = easyocr.Reader(language, gpu=False)
                self.logger.info("Successfully initialized with CPU.")
                return reader
        elif prefer_device.lower() == 'cpu':
            reader = easyocr.Reader(language, gpu=False)
            self.logger.info("Successfully initialized with CPU.")
            return reader
        else:
            raise ValueError(f"Invalid prefer_device value: '{prefer_device}'. Must be 'cuda' or 'cpu'.")
    
    #this function asks for an image_path and perform ocr on it
    def get_text_from_image(self, image_path : str = None) -> str:
        """
        Takes a file path to an image and uses OCR to read and extract all text from it. 
        Returns the extracted text as a single string.
        """
        self.__enforce_type(image_path, str, "image_path")
        result = self._reader.readtext(image_path, detail=0)
        return " ".join(result)
        
    #this function will take a screenshot at your current screen and return the text from the screenshot
    def get_text_from_screenshot(self, capture_region: Optional[tuple] = None, image_name : Optional[str] = None) -> str:
        """
        Captures a screenshot of a specified screen region and performs OCR to extract the text from the image. 
        Returns the combined text as a single string.
        """
        __region = self._capture_region
        # Rationale: This design provides flexibility.  
        # The class's `self._capture_region` acts as a default, while the `capture_region` parameter allows for one-off, 
        # specific capture areas without altering the default setting. 
        # This avoids repetitive specification of the same region when capturing multiple screenshots with the default area.
        # image_name: will be used to name the screenshot when use the function
        
        if capture_region is not None: #if default, take base on config
            if len(capture_region) != 4:
                raise ValueError(f"capture_region must have size == 4")
            
            __region = capture_region
            
        #check type of the input
        self.__enforce_type(__region, tuple, "capture_region")
        if image_name is None:
            _temp_ID = (str)(round(time.time() * 10)) + ".png"   
        else: 
            self.__enforce_type(image_name, str, "image_name")
            _temp_ID = image_name
        screenshot = pyautogui.screenshot(region=__region)  #capture
        screenshot.save(_temp_ID) #careful if there is a file screenshot before run, it would replace that file
        result = self._reader.readtext(_temp_ID, detail=0)
        return " ".join(result)  #extract and return str

    #set capture region base on percentage instead of choosing specific size capture
    def set_capture_region(self, crop_left: float = 0, crop_right: float = 0, crop_up: float = 0, crop_down: float = 0) -> tuple:
        """
        Defines a specific region of the screen for capturing screenshots based on percentages. 
        It takes percentages to crop from the top, bottom, left, and right of the screen, 
        then calculates and sets the pixel coordinates for the capture area.
        """
        #check type of the input
        self.__enforce_type(crop_left, (int, float), "crop_left")
        self.__enforce_type(crop_right, (int, float), "crop_right")
        self.__enforce_type(crop_up, (int, float), "crop_up")
        self.__enforce_type(crop_down, (int, float), "crop_down")
        
         # Validate crop percentage values
        if not (0 <= crop_left <= 100):
            raise ValueError("crop_left must be between 0 and 100")
        if not (0 <= crop_right <= 100):
            raise ValueError("crop_right must be between 0 and 100")
        if not (0 <= crop_up <= 100):
            raise ValueError("crop_up must be between 0 and 100")
        if not (0 <= crop_down <= 100):
            raise ValueError("crop_down must be between 0 and 100")
        
        top_percentage_to_ignore = crop_up / 100
        bottom_percentage_to_ignore = crop_down / 100
        left_percentage_to_ignore = crop_left / 100
        right_percentage_to_ignore = crop_right / 100

        # Height of region to capture
        top_y = int(self._screen_height * top_percentage_to_ignore)
        bottom_y = int(self._screen_height * (1 - bottom_percentage_to_ignore))
        capture_height = bottom_y - top_y

        # The width of the region to capture
        left_x = int(self._screen_width * left_percentage_to_ignore)
        right_x = int(self._screen_width * (1 - right_percentage_to_ignore))
        capture_width = right_x - left_x 

        self._capture_region = (left_x, top_y, capture_width, capture_height)
        return (left_x, top_y, capture_width, capture_height)
        
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_reader", "_screen_width", "_screen_height"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
            
#SUPPORTED LANG easyocr:
# Abaza	abq
# Adyghe	ady
# Afrikaans	af
# Angika	ang
# Arabic	ar
# Assamese	as
# Avar	ava
# Azerbaijani	az
# Belarusian	be
# Bulgarian	bg
# Bihari	bh
# Bhojpuri	bho
# Bengali	bn
# Bosnian	bs
# Simplified Chinese	ch_sim
# Traditional Chinese	ch_tra
# Chechen	che
# Czech	cs
# Welsh	cy
# Danish	da
# Dargwa	dar
# German	de
# English	en
# Spanish	es
# Estonian	et
# Persian (Farsi)	fa
# French	fr
# Irish	ga
# Goan Konkani	gom
# Hindi	hi
# Croatian	hr
# Hungarian	hu
# Indonesian	id
# Ingush	inh
# Icelandic	is
# Italian	it
# Japanese	ja
# Kabardian	kbd
# Kannada	kn
# Korean	ko
# Kurdish	ku
# Latin	la
# Lak	lbe
# Lezghian	lez
# Lithuanian	lt
# Latvian	lv
# Magahi	mah
# Maithili	mai
# Maori	mi
# Mongolian	mn
# Marathi	mr
# Malay	ms
# Maltese	mt
# Nepali	ne
# Newari	new
# Dutch	nl
# Norwegian	no
# Occitan	oc
# Pali	pi
# Polish	pl
# Portuguese	pt
# Romanian	ro
# Russian	ru
# Serbian (cyrillic)	rs_cyrillic
# Serbian (latin)	rs_latin
# Nagpuri	sck
# Slovak	sk
# Slovenian	sl
# Albanian	sq
# Swedish	sv
# Swahili	sw
# Tamil	ta
# Tabassaran	tab
# Telugu	te
# Thai	th
# Tajik	tjk
# Tagalog	tl
# Turkish	tr
# Uyghur	ug
# Ukranian	uk
# Urdu	ur
# Uzbek	uz
# Vietnamese	vi