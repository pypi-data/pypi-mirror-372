import torch
from transformers import T5ForConditionalGeneration
from transformers import T5TokenizerFast
from freeai_utils.log_set_up import setup_logging
import logging
from typing import Union

#function to use: 
# construct_sys_prompt
# decide
# _run_examples
class DecisionMaker:
    __slots__ = ("_model_name", "_tokenizer", "_model", "_system_prompt", "_initialized", "generation_params","_device", "logger")
    
    _model_name: str
    _tokenizer: T5TokenizerFast
    _model: T5ForConditionalGeneration
    _system_prompt: Union[str, None] # Or Optional[str]
    _initialized: bool
    generation_params: dict[str, Union[int, float, bool]]
    _device: str
    logger: logging.Logger
    
    #a model to answer yes no question
    #this class should only answer in 2 ways only
    def __init__(self, sample_ques_ans : str = None, positive_ans = "YES", negative_ans = "NO", model_name : str = "google/flan-t5-base", preferred_device : str = "cuda") -> None:
        #check type before setting
        self.__enforce_type(sample_ques_ans, (str, type(None)), "sample_ques_ans")
        self.__enforce_type(positive_ans, str, "positive_ans")
        self.__enforce_type(negative_ans, str, "negative_ans")
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(preferred_device, str, "preferred_device")
        
        # init not lock
        super().__setattr__("_initialized", False)
        
        self._model_name = model_name
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.info(f"Loading tokenizer and model: {model_name}...")
        try:
            self._model = T5ForConditionalGeneration.from_pretrained(model_name, local_files_only=True)
            self._tokenizer = T5TokenizerFast.from_pretrained(model_name, local_files_only=True)
        except:
            self.logger.info(f"Detect local model not found, attemp to download {model_name}")
            self._model = T5ForConditionalGeneration.from_pretrained(model_name)
            self._tokenizer = T5TokenizerFast.from_pretrained(model_name)
            
        self._system_prompt = None
        self.construct_sys_prompt(sample_ques_ans=sample_ques_ans, positive_ans=positive_ans, negative_ans=negative_ans)
        
        # Default generation parameters - tuned for a balance of accuracy and coherence
        self.generation_params = {
            "max_new_tokens": 100,              # allow up to ... tokens of new output
            "min_length": 1,                   # at least 1 token output
            "num_beams": 5,                    # beam-search 
            "early_stopping": True,            # stop beams on EOS early
            "repetition_penalty": 1.2,        
            "length_penalty": 1.0,             
            "no_repeat_ngram_size": 3,         # forbid repeating 3-grams
            "num_return_sequences": 1          # return only the best sequence
        }
        
        # devices choose
        candidates = []
        if preferred_device:
            candidates.append(preferred_device)
        for d in ("cuda", "cpu"):
            if d not in candidates:
                candidates.append(d)

        last_err = None
        for d in candidates:
            # skip cuda if not available
            if d.startswith("cuda") and not torch.cuda.is_available():
                self.logger.info(f"Skipping {d}: no CUDA available.")
                continue
            try:
                self._model.to(d)
                self._model.eval()
                self._device = d
                self.logger.info(f"Model successfully loaded on {d}.")
                break
            except Exception as e:
                self.logger.error(f"Failed to load on {d}: {e}")
                last_err = e
        else:
            raise RuntimeError(f"Could not load model on any device {candidates}. Last error: {last_err}")
        
        # init not lock
        super().__setattr__("_initialized", True)

    def construct_sys_prompt(self, sample_ques_ans : str = None, positive_ans : str = None, negative_ans : str = None) -> None:
        """constructs a system prompt for a language model to help it decide if a question requires an internet search. 
        It uses optional sample questions and answers to provide examples, and defines the specific strings for positive and negative answers.
        """
        #check type
        self.__enforce_type(sample_ques_ans, (str, type(None)), "sample_ques_ans")
        self.__enforce_type(negative_ans, str, "negative_ans")
        self.__enforce_type(positive_ans, str, "positive_ans")
        if sample_ques_ans is type(str) and sample_ques_ans.strip() == "": #ensure it makes a good prompt
            sample_ques_ans = None
            
        self._system_prompt = (
            "Analyze the following question and determine which result is better to answer it. "
            f"Respond with '{positive_ans}' or '{negative_ans}'.\n\n"
            f"Example:\n{sample_ques_ans or '<no example provided>'}"
        )
    
    def decide(self, user_question: str, temp_prompt : str = None) -> str:
        """Returns the model's decision as a capitalized string."""
        self.__enforce_type(user_question, str, "user_question")
        self.__enforce_type(temp_prompt, (str, type(None)), "temp_prompt")
        
        if temp_prompt:
            prompt = f"{temp_prompt}\nQuestion: {user_question} ->"
        else: prompt = f"{self._system_prompt}\nQuestion: {user_question} ->"
        
        input_ids = self._tokenizer(prompt, return_tensors="pt").input_ids
        input_ids = input_ids.to(self._device)

        output_ids = self._model.generate(input_ids, **self.generation_params)
        decision = self._tokenizer.decode(output_ids[0], skip_special_tokens=True).strip().upper()
        return decision

    @property
    def model_name(self):
        return self._model_name
    
    @property
    def tokenizer(self):
        return self._tokenizer
    
    @property
    def model(self):
        return self._model
    
    @property
    def system_prompt(self):
        return self._system_prompt
    
    @system_prompt.setter
    def system_prompt(self, prompt : str):
        self.__enforce_type(prompt, str, "prompt")
        self._system_prompt = prompt
    
    @property
    def device(self):
        return self._device
    
    def __setattr__(self, name, value):
        # once initialized, prevent changing core internals
        if getattr(self, "_initialized", False) and name in ("_model_name", "_tokenizer", "_model", "_device"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
    def _run_examples(self) -> None:
        """Print guide on config for this class"""
        print("This is the example of each field you would put in, to help you know how it works")
        print("*" * 100)
        print("DEMO")
        print("*" * 100)
        # Prebuilt system prompt with few-shot examples
        sample_ques_ans = (
            "Question: What is the weather like in London tomorrow? -> SEARCH_INTERNET\n"
            "Question: What is the capital of France? -> NO_SEARCH_NEEDED\n"
            "Question: What was the score of the latest football match between Real Madrid and Barcelona? -> SEARCH_INTERNET\n"
            "Question: What is the chemical formula for water? -> NO_SEARCH_NEEDED\n"
            "Question: Who is the current Prime Minister of Canada? -> SEARCH_INTERNET\n"
            "Question: What is the definition of photosynthesis? -> NO_SEARCH_NEEDED\n"
            "Question: What is the price of Bitcoin right now? -> SEARCH_INTERNET\n"
            "Question: What is the history of the Eiffel Tower? -> NO_SEARCH_NEEDED\n"
            "Question: What is the date today? -> SEARCH_INTERNET\n"
        )

        positive_ans, negative_ans = "SEARCH_INTERNET", "NO_SEARCH_NEEDED"
        print(f"FIELD [positive_ans]: {positive_ans}\n")
        print(f"FIELD [positive_ans]: {negative_ans}\n")
        
        print(f"FIELD [sample_ques_ans]:\n{sample_ques_ans}")
        sample_ques_ans = (
            "Analyze the following question and determine which result is better to answer it. "
            f"Respond with '{positive_ans}' or '{negative_ans}'.\n\n"
            "Examples:\n"
            f"{sample_ques_ans}"
        )
        
        example_questions = [
            "What is the capital of Germany?", #search
            "Whats the latest stock price of Tesla?", #search
            "Who won the World Cup in 2018?",#search
            "What is the weather like in London tomorrow?", #search
            "What is the capital of France", #search
            "What was the score of the latest football match between Manchester United and Arsenal", #search
            "What is photosynthesis?", #search
            "Who is the current President of the United States", #search
            "When was the Earth formed", #no
            "How to use Python 3.12",#search
            "What is the current time in Tokyo", #search
            "Who invented the light bulb" #search
        ]
        
        print(f"All demo questions:\n {example_questions}")
        
        print("*" * 100)
        print("ANS\n")
        for q in example_questions:
            decision = self.decide(q, sample_ques_ans)
            print(f"Question: {q}\nDecision: {decision}\n")
        print("*" * 100)
        
    def config_default_internet_search(self) -> None:
        sample_ques_ans = (
            "Question: What is the weather like in London tomorrow? -> SEARCH_INTERNET\n"
            "Question: What is the capital of France? -> NO_SEARCH_NEEDED\n"
            "Question: What was the score of the latest football match between Real Madrid and Barcelona? -> SEARCH_INTERNET\n"
            "Question: What is the chemical formula for water? -> NO_SEARCH_NEEDED\n"
            "Question: Who is the current Prime Minister of Canada? -> SEARCH_INTERNET\n"
            "Question: What is the definition of photosynthesis? -> NO_SEARCH_NEEDED\n"
            "Question: What is the price of Bitcoin right now? -> SEARCH_INTERNET\n"
            "Question: What is the history of the Eiffel Tower? -> NO_SEARCH_NEEDED\n"
            "Question: What is the date today? -> SEARCH_INTERNET\n"
        )
        positive_ans, negative_ans = "SEARCH_INTERNET", "NO_SEARCH_NEEDED"
        self.construct_sys_prompt(sample_ques_ans=sample_ques_ans, positive_ans=positive_ans, negative_ans=negative_ans)