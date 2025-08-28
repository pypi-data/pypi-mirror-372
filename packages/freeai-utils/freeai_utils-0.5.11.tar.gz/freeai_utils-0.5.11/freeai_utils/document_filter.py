from collections import Counter
import os
os.environ["HF_HUB_OFFLINE"] = "1"
from haystack import Document
from haystack.components.readers import ExtractiveReader
from haystack.utils.device import ComponentDevice
from typing import List, Optional, Dict, Tuple
from .pdf_docx_reader import PDF_DOCX_Reader
from freeai_utils.log_set_up import setup_logging
import torch
import re

#smaller model: deepset/roberta-base-squad2
class AIDocumentSearcher:
    """
    AI-driven approach to document search. 
    It uses an extractive question-answering model to understand the meaning and intent behind a query. 
    Instead of just looking for keywords, 
    it can find relevant answers even if they are paraphrased or semantically related to the query.
    """
    
    __slots__ = ("_reader", "threshold", "max_per_doc", "top_k", "_documents", "_initialized", "logger")
    
    _initialized: bool
    _reader: ExtractiveReader
    threshold: float
    max_per_doc: int
    top_k: int
    _documents: List[Document]
    
    def __init__(self, model_name="deepset/tinyroberta-squad2", path : Optional[str] = None, threshold : float = 0.4, max_per_doc : int = 2, top_answer : int = 4, device: str = "cuda", auto_init : bool = True) -> None:
        #check type first
        self.__enforce_type(threshold, float, "threshold")
        self.__enforce_type(max_per_doc, int, "max_per_doc")
        self.__enforce_type(top_answer, int, "top_answer")
        self.__enforce_type(auto_init, bool, "auto_init")
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.propagate = False  # Prevent propagation to the root logger
        
        # init not lock
        super().__setattr__("_initialized", False)
        # set core reader
        self._reader = None
        
        preferred_devices = []
        if device is not None:
            self.__enforce_type(device, str, "device")
            preferred_devices.append(device)
        if torch.cuda.is_available() and "cuda" not in preferred_devices:
            preferred_devices.append("cuda")
        if "cpu" not in preferred_devices:
            preferred_devices.append("cpu")
        
        load_success = False 
        for dev in preferred_devices:
            if load_success: break
            for offline in (True, False):
                if offline:
                    os.environ["HF_HUB_OFFLINE"] = "1"
                    mode = "offline"
                else:
                    os.environ.pop("HF_HUB_OFFLINE", None)
                    mode = "online"
                try:
                    device_obj = ComponentDevice.from_str(dev)
                    reader = ExtractiveReader(model=model_name, device=device_obj)
                    reader.warm_up()
                    self._reader = reader
                    load_success = True
                    self.logger.info(f"Successfully runs on {dev} with mode {mode}")
                    break
                except Exception as e:
                    self.logger.info(f"Failed to initialize on device='{dev}' in {mode} mode: {e}")
        
        if self._reader is None:
            raise RuntimeError(f"Could not load model on any device.")
        
        # lock down, reader can't be modified
        super().__setattr__("_initialized", True)
    
        self.threshold = threshold
        self.max_per_doc = max_per_doc
        self.top_k = top_answer
        self._documents: List[Document] = [] #init var to hold document
        if path is None:
            path = os.getcwd()
        if not os.path.exists(path):
            raise FileNotFoundError(f"The path '{path}' does not exist.")
        if auto_init:
            self.__init_documents(path) #init documents from the path
        self.logger.info(f"Initialize successfully at path {path}")
    
    @property
    def reader(self):
        return self._reader
    
    @property
    def documents(self):
        return self._documents
       
    def __setattr__(self, name, value):
        # once initialized, prevent changing core internals
        if getattr(self, "_initialized", False) and name in ("_reader"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
    def search_document(self, prompt : str = None) -> List[Tuple]: #content text, score, and doc.id
        """Searches a collection of documents for answers to a given prompt,
        then filters the results based on a threshold score, a limit per document, and uniqueness.\n
        Returns a list of tuples containing the text, score, and document ID.
        """
        self.__enforce_type(prompt, str, "prompt") #check type before start
        
        result = self._reader.run(query=prompt, documents=self._documents, top_k=self.top_k)
        
        seen_texts = set()
        counts = Counter()
        filtered_answers = []
        
        for ans in result["answers"]:
            if ans.score < self.threshold:
                continue
            if ans.document is None:
                continue
            text = ans.document.content
            doc_id = ans.document.id
        
            if counts[doc_id] >= self.max_per_doc:
                continue
            if text in seen_texts:
                continue
                
            filtered_answers.append((text, ans.score, doc_id))
            seen_texts.add(text)
            counts[doc_id] += 1
        
        #content text, score, and doc.id
        return filtered_answers #return list of document with ranking score that > threshold

    def __init_documents(self, directory : str = "") -> None:
        """
        Initializes and loads documents from a specified directory. 
        It finds and extracts text from all PDF and DOCX files in the directory to prepare them for searching.
        """
        #get from here
        self._documents.clear()
        pdf_urls, docx_urls = collect_file_paths(directory)
        
        reader = PDF_DOCX_Reader() #init reader
        
        #extract from docx
        for doc in docx_urls:
            text = reader.extract_ordered_text(doc)
            self._documents.append(Document(content=text))
            
        #extract from pdf
        for pdf in pdf_urls:
            text = reader.extract_ordered_text(pdf)
            self._documents.append(Document(content=text))
    
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")
        
class DocumentFilter:
    """
    Designed for efficient, keyword-based search across a collection of documents. 
    It functions by indexing the raw text of PDF and DOCX files, 
    allowing it to quickly identify and filter documents containing a specific keyword or phrase.
    """
    def __init__(self, path: Optional[str] = None, auto_init: bool = True) -> None:
        self.__enforce_type(auto_init, bool, "auto_init")
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.propagate = False

        self._documents: Dict[str, str] = {}  # Changed to a dictionary
        if path is None:
            path = os.getcwd()
        if not os.path.exists(path):
            raise FileNotFoundError(f"The path '{path}' does not exist.")
        if auto_init:
            self.__init_documents(path)
        self.logger.info(f"Initialize successfully at path {path}")

    @property
    def documents(self):
        return self._documents
       
    def search_keyword(self, keyword: str) -> Dict[str, List[str]]:
        """
        Searches a collection of documents for answers to a given keyword,
        \n
        Returns a Dict of str,list with str is the path, and list is the place it occurs the matched keyword
        """
        results = {}
        
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        
        for path, text in self._documents.items():
            # Split the document into sentences using '.'
            sentences = text.split('.')
            matches = []
            
            for sentence in sentences:
                if pattern.search(sentence):
                    # Add the matching sentence to the list for this file
                    matches.append(sentence.strip())
            
            # Only add the file to the results if a match was found
            if matches:
                results[path] = matches
                
        return results
    
    def __init_documents(self, directory: str = "") -> None:
        """
        Initializes and loads documents from a specified directory.
        It finds and extracts text from all PDF and DOCX files in the directory.
        """
        self._documents.clear()
        pdf_urls, docx_urls = collect_file_paths(directory)

        reader = PDF_DOCX_Reader()

        for doc_path in docx_urls:
            text = reader.extract_ordered_text(doc_path)
            self._documents[doc_path] = text

        for pdf_path in pdf_urls:
            text = reader.extract_ordered_text(pdf_path)
            self._documents[pdf_path] = text

    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")
        
def collect_file_paths(directory : str)-> Tuple[List[str], List[str]]:
        """a helper that scans a directory for all PDF and DOCX files and returns their file paths in two separate lists."""
        pdf_urls = []
        docx_urls = []
    
        # Walk through all directories and files
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file).replace('\\', '/')  # normalize path
                if file.lower().endswith('.pdf'):
                    pdf_urls.append(file_path)
                elif file.lower().endswith('.docx'):
                    docx_urls.append(file_path)
        
        return pdf_urls, docx_urls