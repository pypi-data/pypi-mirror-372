from langdetect import detect, detect_langs #need pip install langdetect
from typing import Union, Tuple
import os
os.environ.setdefault("translators_default_region", "EN") #need to use offline
import translators as ts
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, MBart50TokenizerFast, MBartForConditionalGeneration
import logging 
from freeai_utils.log_set_up import setup_logging

class LangTranslator:
    
    __slots__ = ("_local_translator", "local_status", "logger", "_initialized")
    _local_translator: Union["LocalTranslator", None]
    local_status: str
    logger: logging.Logger
    _initialized: bool

    def __init__(self, local_status : str = "backup", local_model_num : int = 1): 
        #check type before init
        self.__enforce_type(local_status, str, "local_status")
        self.__enforce_type(local_model_num, int, "local_model_num")
        
        #init
        super().__setattr__("_initialized", False)
        
        self._local_translator = None
        self.local_status = None
        self.logger = setup_logging(self.__class__.__name__)
        if local_status not in ["active", "inactive", "backup"]:
            raise ValueError(f"local_status could only be \'active\', \'inactive\', \'backup\'. Current value: {local_status}")
        
        if local_status in ["active", "backup"]:
            self._local_translator = LocalTranslator(local_model_num)
            self.local_status = local_status
        #local_status between active, inactive, backup where active will pioritize, inactive will unable it, backup will enable and use when online fail
        
        #lock
        super().__setattr__("_initialized", True)
        
        self.logger.info(f"Initialized completed")
    
    @property 
    def local_translator(self):
        return self._local_translator
    
    def translate(self, text_to_translate : str, tgt_lang : str = 'en', src_lang : Union[str, None] = None) -> str:
        """
        Translates text from one language to another. 
        Prioritizes a local translation model if status is active. 
        If not, it uses an online Google translator as a primary method and falls back to the local model if the online translation fails.
        
        Returns the translated text as a string.
        """
        if self.local_status == "active":
            return self._local_translator.translate(text_to_translate, src_lang=src_lang, tgt_lang=tgt_lang)
        else:
            try:
                answer = ts.translate_text(text_to_translate, translator='google',from_language=src_lang if src_lang else 'auto', to_language=tgt_lang)
                return answer
            except Exception as e:
                self.logger.error(f"Fail to use online google translator")
                if self.local_status == "backup":
                    self.logger.info(f"\'backup\' mode, using {self._local_translator.logger.name} to translate")
                    return self._local_translator.translate(text_to_translate, src_lang=src_lang, tgt_lang=tgt_lang)
            
    def detect_language(self, prompt) -> Tuple[str, float]:
        """Detects the language of a given text. It returns a tuple containing the language code and the confidence score of the detection."""
        detected_language = detect_langs(prompt)

        if detected_language:
            return detected_language[0].lang, detected_language[0].prob
        else: return "unknown", 0.0
    
    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_online_translator", "_local_translator"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
class LocalTranslator:
    
    __slots__ = ("_model", "logger", "_initialized")
    _model: Union["M2M100Translator", "MBartTranslator"]
    logger: logging.Logger
    _initialized: bool
    
    def __init__(self, local_model_num : int = 1, device : str = "cuda"):
        #secure type first
        self.__enforce_type(local_model_num, int, "local_model_num")
        self.__enforce_type(device, str, "device")
        
        #init
        super().__setattr__("_initialized", False)
        
        #auto counter for the number of models
        _amount_translator = _Class_Counter().get_count() - 3
        if local_model_num > _amount_translator or local_model_num < 1:
            raise ValueError(f"local_model_num could only between 1 and {_amount_translator}")
        
        self._model = None
        self.__init_local_translator(local_model_num, device)
        self.logger = setup_logging(self.__class__.__name__)
        #lock
        super().__setattr__("_initialized", True)
        self.logger.info(f"Initialized completed")

    @property
    def model(self):
        return self._model

    def translate(self, prompt : str, src_lang : Union[str, None] = None, tgt_lang : str = None) -> str:
        """
        Translates a given text prompt from a source language (src_lang) to a target language (tgt_lang). 
        
        Returns the translated text as a string.
        """
        self.__enforce_type(prompt, str, "prompt")
        self.__enforce_type(src_lang, (str, type(None)), "src_lang")
        self.__enforce_type(tgt_lang, str, "tgt_lang")
        return self._model.translate(prompt, src_lang = src_lang, tgt_lang = tgt_lang)
    
    def detect_language(self, prompt) -> Tuple[str, float]:
        """Returns a tuple containing the language code and a confidence score for the detection."""
        return self._model.detect_language(prompt)
        
    def __init_local_translator(self, num : int, device : str) -> None:
        """
        Initializes a local translation model based on the provided model number (num) and device (e.g., CPU or GPU). 
        Loads either the M2M100 or MBart translator
        """
        if num == 1:
            self._model = M2M100Translator(device = device)
        elif num == 2:
            self._model = MBartTranslator(device = device)   
        else:
            raise ValueError(f"Unknown model number: {num}")

    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
######################################### Use only for providing number for possible local model Class #########################################
import inspect
import sys
import ast
import os

class _Class_Counter:
    def __init__(self):
        self.class_count = 0
        self.classes = []

        file_path = None
        try:
            file_path = inspect.getsourcefile(self.__class__)
            if file_path is None:
                module = sys.modules.get(self.__class__.__module__)
                if module and hasattr(module, '__file__'):
                    file_path = module.__file__
            if file_path:
                file_path = os.path.abspath(file_path)

        except Exception as e:
            raise Exception(f"Error determining source file for Counter class: {e}")
        if not file_path:
            raise Exception("Could not determine the source file for this class. Cannot count classes.")

        #print(f"Counting classes in the file where Counter is defined: {file_path}") 
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            tree = ast.parse(source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.class_count += 1
                    self.classes.append(node.name)

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Source file '{file_path}' not found during AST parsing.")
        except Exception as e:
            raise Exception(f"Error parsing AST of file '{file_path}': {e}")

    def get_count(self):
        return self.class_count

    def get_class_names(self):
        return self.classes
    
#################################################################################################################################################

class M2M100Translator:
    
    __slots__ = ("_model", "_tokenizer", "_device", "logger", "_initialized")
    
    _tokenizer: M2M100Tokenizer
    _model: M2M100ForConditionalGeneration
    _device: str
    _initialized: bool
    logger: logging.Logger
    
    #use for model that is m2m100 family
    #other model: facebook/m2m100_1.2B
    def __init__(self, model_name : str = 'facebook/m2m100_418M', device: Union[str, None] = None):
        #check type
        self.__enforce_type(model_name, str, "model_name")
        
        #init
        super().__setattr__("_initialized", False)
        self.logger = setup_logging(self.__class__.__name__)
        
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
        
        # Load tokenizer and model
        try:
            self._tokenizer = M2M100Tokenizer.from_pretrained(model_name,local_files_only=True)
            self._model = M2M100ForConditionalGeneration.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            self.logger.info(f"Detect models not found, attempt to download {model_name}")
            self._tokenizer = M2M100Tokenizer.from_pretrained(model_name)
            self._model = M2M100ForConditionalGeneration.from_pretrained(model_name)
            
        last_err = None
        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading '{model_name}' model on {dev}...")
                self._model.to(dev)
                self._device = dev
                self._model.eval()
                self.logger.info(f"Model successfully loaded on {dev}.")
                break
            except Exception as e:
                last_err = e
                self.logger.error(f"Fail to load {model_name} on {dev}. Reason: {e}")
        else:
            raise RuntimeError(f"Could not move model to any device {preferred_devices}. Last error: {last_err}")
        
        #lock
        super().__setattr__("_initialized", True)
    
    @property
    def model(self):
        return self._model
    
    @property
    def device(self):
        return self._device
    
    @property
    def tokenizer(self):
        return self._tokenizer
       
    def translate(self, text: str, src_lang: Union[str, None] = None, tgt_lang: str = None, seed_num : int = 42) -> str:
        """Translates text from a source language to a target language. It automatically detects the source language if it's not specified."""
        self.__enforce_type(text, str, "text")
        self.__enforce_type(src_lang, (str, type(None)), "src_lang")
        self.__enforce_type(tgt_lang, str, "tgt_lang")
        self.__enforce_type(seed_num, int, "seed_num")
        
        # 1) Determine source language
        if not src_lang:
            src_lang = detect(text)  # e.g. "vi", "fr", "de"
        # assign to tokenizer
        self._tokenizer.src_lang = src_lang
        self._tokenizer.tgt_lang = tgt_lang

        # 2) Tokenize
        encoded = self._tokenizer(text, return_tensors='pt', truncation=True, max_length=1000)
        encoded = {k: v.to(self._device) for k, v in encoded.items()}

        # 3) Look up forced BOS token for target
        forced_bos_id = self._tokenizer.get_lang_id(tgt_lang)

        torch.manual_seed(seed_num)
        if self._device == 'cuda':
            torch.cuda.manual_seed_all(seed_num)
        # 4) Generate under inference mode
        with torch.inference_mode():
            generated_tokens = self._model.generate(
                **encoded,
                forced_bos_token_id=forced_bos_id,
                early_stopping=True
            )

        # 5) Decode and return
        return self._tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

    def detect_language(self, text) -> str:
        """Identifies the language of a given text."""
        return detect(text)
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")

    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model", "_device", "_tokenizer"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
class MBartTranslator:
    
    __slots__ = ("_model", "_tokenizer", "_device", "logger", "_initialized", "_iso_to_tag")
    
    _tokenizer: MBart50TokenizerFast
    _model: MBartForConditionalGeneration
    _device: str
    _initialized: bool
    logger:logging.Logger
    _iso_to_tag: dict
    
    #use for model that is mbart family
    def __init__(self, model_name :str = "facebook/mbart-large-50-many-to-many-mmt", device : Union[str, None] = None):
        self.__enforce_type(model_name, str, "model_name")
        
        #init
        super().__setattr__("_initialized", False)
        
        self.logger = setup_logging(self.__class__.__name__)
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
        
        try:
            self._tokenizer = MBart50TokenizerFast.from_pretrained(model_name, local_files_only=True)
            self._model     = MBartForConditionalGeneration.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            self.logger.info(f"Detect local model not found, attemp to download {model_name}")
            self._tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
            self._model     = MBartForConditionalGeneration.from_pretrained(model_name)
        
        last_err = None
        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading '{model_name}' model on {dev}...")
                self._model.to(dev)
                self._device = dev
                self._model.eval()
                self.logger.info(f"Model successfully loaded on {dev}.")
                break
            except Exception as e:
                last_err = e
                self.logger.error(f"Fail to load {model_name} on {dev}. Reason: {e}")
        else:
            raise RuntimeError(f"Could not move model to any device {preferred_devices}. Last error: {last_err}")
        
        # Build a quick map from plain ISO to MBART tag:
        self._iso_to_tag = {iso.split("_")[0]: iso for iso in self._tokenizer.lang_code_to_id}
        
        #lock
        super().__setattr__("_initialized", True)

    @property
    def model(self):
        return self._model
    
    @property
    def device(self):
        return self._device
    
    @property
    def tokenizer(self):
        return self._tokenizer
    
    def translate(self, text: str, src_lang : Union[str, None] = None, tgt_lang: str = None) -> str:
        """
        Translates text from a source language to a target language. 
        The source language is automatically detected if not provided
        """
        self.__enforce_type(text, str, "text")
        self.__enforce_type(src_lang, (str, type(None)), "src_lang")
        self.__enforce_type(tgt_lang, str, "tgt_lang")
        
        if not src_lang:
            iso = detect(text)
            src_tag = self._resolve_lang_tag(iso)
        else:
            src_tag = self._resolve_lang_tag(src_lang)
        self._tokenizer.src_lang = src_tag

        # Resolve target language
        if not tgt_lang:
            raise ValueError("tgt_lang must be specified")
        tgt_tag = self._resolve_lang_tag(tgt_lang)
        forced_bos = self._tokenizer.lang_code_to_id[tgt_tag]
        
        # prepare inputs forced BOS
        inputs = self._tokenizer(text, return_tensors="pt", truncation=True, max_length=1000).to(self._device)

        # generate
        with torch.inference_mode():
            out = self._model.generate(
                **inputs,
                forced_bos_token_id=forced_bos,
                early_stopping=True
            )
        return self._tokenizer.decode(out[0], skip_special_tokens=True)

    def detect_language(self, text) -> str:
        """Identifies the language of a given text."""
        return detect(text)
    
    def supported_lang_id(self) -> None:
        """Prints a list of all supported language IDs for translation."""
        print("*" * 100)
        print("Supported Language ISO ID (If you wanna know, or just use those id like langdetect, it would still works :D )")
        print("*" * 100)
        print(self._tokenizer.lang_code_to_id.keys())
    
    def _resolve_lang_tag(self, lang_code: str) -> str:
        """a helper function that converts a language code (like "en" or "fr") into the correct internal tag used by the tokenizer."""
        # If it's already a valid mBART tag
        if lang_code in self._tokenizer.lang_code_to_id:
            return lang_code
        # If it's an ISO code and mapped
        if lang_code in self._iso_to_tag:
            return self._iso_to_tag[lang_code]
        # If neither, raise error
        raise ValueError(f"Unknown language code or tag: '{lang_code}'")

    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model", "_device", "_tokenizer", "_iso_to_tag"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
if __name__ == "__main__":
    text3 = "Đây là một đoạn văn bản mẫu bằng tiếng Việt."
    trans = LangTranslator()
    print(trans.detect_language(text3))
    print(trans.translate(text3))
    
    local = LocalTranslator(local_model_num=1, device= "cpu")
    print(local.translate(text3, tgt_lang="en"))
    print(local.detect_language(text3))
    
    mb = MBartTranslator()
    print(mb.detect_language(text3))
    print(mb.translate(text3, tgt_lang='en'))
    mb.supported_lang_id() #print support in ISO ID
    
    m1 = M2M100Translator()
    print(m1.detect_language(text3))
    print(m1.translate(text3, tgt_lang='en'))
        
    trans_local = LangTranslator(local_status="active", local_model_num=2)
    print(trans_local.detect_language(text3))
    print(trans_local.translate(text3))