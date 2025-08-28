# freeai_utils/__init__.py
import importlib
from typing import TYPE_CHECKING

# all class/functions available
_module_to_names = {
    'audio_record': ['WavRecorder','MP3Recorder','check_wav_length_and_size','check_mp3_length_and_size'],
    'audio_to_text_whisper': ['OpenAIWhisper'],
    'audio_to_text_vn': ['VN_Whisper'],
    'clean_text_for_tts': ['clean_ai_text_for_tts'],
    'cleaner': ['Cleaner'],
    'decider': ['DecisionMaker'],
    'document_filter': ['AIDocumentSearcher', 'DocumentFilter', 'collect_file_paths'],
    'geminiAPI': ['GeminiChatBot', 'GeminiClient'],
    'google_search': ['WebScraper'],
    'image_to_text': ['ImageCaptioner'],
    'text_from_image_easyocr': ['Text_Extractor_EasyOCR'],
    'text_to_speech_gtts': ['gtts_print_supported_languages', 'gtts_speak'],
    'text_to_speech_pyttsx3': ['Text_To_Speech_Pyttsx3'],
    'pdf_docx_reader': ['PDF_DOCX_Reader'],
    'wrapper': ['time_it'],
    'language_detection': ['LangTranslator', 'LocalTranslator', 'MBartTranslator', 'M2M100Translator'],
    'localLLM': ['LocalLLM'],
    'image_creator': ['SDXL_TurboImage', 'SD15_Image'],
    'live_stt_vosk': ['STT_Vosk']
}

# make a map from the list: a lookup to import specific files for needed tools, avoiding full library load.
_lazy_mapping = {}
for module_name, symbols in _module_to_names.items():
    for symbol in symbols:
        _lazy_mapping[symbol] = module_name

# all class/functions available when do import freeai_utils
__all__ = sorted(_lazy_mapping.keys())

def __getattr__(name: str):
    if name in _lazy_mapping:
        # Import only the module that contains the requested symbol
        module = importlib.import_module(f"{__name__}.{_lazy_mapping[name]}")
        value = getattr(module, name)
        globals()[name] = value  # Cache in namespace for future calls
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return __all__

#for IDEs suggestions
if TYPE_CHECKING:
    from .audio_record             import WavRecorder, MP3Recorder, check_wav_length_and_size, check_mp3_length_and_size
    from .audio_to_text_whisper    import OpenAIWhisper
    from .audio_to_text_vn         import VN_Whisper
    from .clean_text_for_tts       import clean_ai_text_for_tts
    from .cleaner                  import Cleaner
    from .document_filter          import AIDocumentSearcher, DocumentFilter, collect_file_paths
    from .geminiAPI                import GeminiChatBot, GeminiClient
    from .google_search            import WebScraper
    from .image_to_text            import ImageCaptioner
    from .text_from_image_easyocr  import Text_Extractor_EasyOCR
    from .text_to_speech_gtts      import gtts_print_supported_languages, gtts_speak
    from .text_to_speech_pyttsx3   import Text_To_Speech_Pyttsx3
    from .pdf_docx_reader          import PDF_DOCX_Reader
    from .wrapper                  import time_it
    from .decider                  import DecisionMaker
    from .language_detection       import LangTranslator, LocalTranslator, MBartTranslator, M2M100Translator
    from .localLLM                 import LocalLLM
    from .image_creator            import SDXL_TurboImage, SD15_Image
    from .live_stt_vosk            import STT_Vosk