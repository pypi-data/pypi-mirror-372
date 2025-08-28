from transformers import AutoModelForCausalLM, AutoTokenizer
from freeai_utils.log_set_up import setup_logging
import logging
import torch
from typing import Union

#other model: Qwen/Qwen3-4B, or any models that is Qwen
class LocalLLM:
    __slots__ = ("_model", "_tokenizer", "_device", "logger", "_initialized", "_history", "_max_length")
    
    _model: AutoModelForCausalLM
    _tokenizer: AutoTokenizer
    _device: str
    _logger: logging.Logger
    _initialized: bool
    _history: list
    _max_length: int
    
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", preferred_device: str = "cuda", memories_length: int = 4):
        #check type
        self.__enforce_type(preferred_device, str, "preferred_device")
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(memories_length, int, "memories_length")
        
        #init
        super().__setattr__("_initialized", False)
        self.logger = setup_logging(self.__class__.__name__)
        
        preferred_devices = []
        if preferred_device is not None:
            self.__enforce_type(preferred_device, str, "device")
            preferred_devices.append(preferred_device)
        if torch.cuda.is_available() and "cuda" not in preferred_devices:
            preferred_devices.append("cuda")
        if "cpu" not in preferred_devices:
            preferred_devices.append("cpu")
        
        #download if not founnd
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        except Exception:
            self.logger.info(f"Detect model not found, attempt to download {model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        self._model = None
        self._device = None
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",   
            low_cpu_mem_usage=True 
        )
        model.eval()

        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading '{model_name}' model on {dev}...")
                model_on_dev = model.to(dev)
                self._model = model_on_dev
                self._device = dev
                self.logger.info(f"Model successfully running on {dev}.")
                break
            except Exception as e:
                self.logger.error(f"Failed to move model to {dev}: {e}")
        
        if self._model is None:
            raise RuntimeError(f"Could not load model on any device: {preferred_devices}")
    
        self._history = []
        self._max_length = memories_length
        
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
    
    @property
    def memories_length(self):
        return self._max_length
    
    @memories_length.setter
    def memories_length(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("memories_length must be a non-negative integer.")
        self._max_length = value
    
    def ask(self, messages: Union[list, str]):
        """Sends a prompt to Qwen model and Returns the text response."""
        self.__enforce_type(messages, (list, str), "messages")
        
        if type(messages) is str:
            sent_mes = [{"role": "user", "content": messages}]
        else: sent_mes = messages
        text = self._tokenizer.apply_chat_template(
            sent_mes,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        
        model_inputs = self._tokenizer([text], return_tensors="pt").to(self._device)
        with torch.inference_mode():
            generated_ids = self._model.generate(
                **model_inputs,
                max_new_tokens=32768
            )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            
        try:
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0
    
        thinking_content = self._tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self._tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        return content, thinking_content
        
    def ask_with_memories(self, prompt: str) -> tuple[str, str]:
        """ 
        Sends a prompt to a language model, 
        including the history of the conversation to provide context, 
        then stores the new turn in its memory.
        """
        self.__enforce_type(prompt, str, "prompt")
        
        messages = []
        line = "Here's our previous conversation:\n"
        if self._history:
            for turn in self._history:
                line += f"User: {turn['question']}\nAI: {turn['answer']}\n"
        line += "Now, continue the conversation:\n"
        line += prompt
        messages.append({"role": "user", "content": line})

        content, thinking_content = self.ask(messages)
        self.__add_turn(prompt, content)
        return content, thinking_content
        
    def _clear_history(self) -> None:
        """helper function that clears the entire conversation history."""
        if self._history:
            self._history.clear()
    
    def __add_turn(self, question, answer) -> None:
        """
        Appends a new question-answer pair to the conversation history. 
        Removing the oldest entry if the history exceeds a maximum length.
        """
        self.__enforce_type(question, str, "question")
        self.__enforce_type(answer, str, "answer")
    
        while len(self._history) >= self._max_length:
            self._history.pop(0)
        self._history.append({"question": question, "answer": answer})
    
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
    
if __name__ == "__main__":
    lm = LocalLLM()
    print(lm.ask("Hi, how are you?"))
    print(lm.ask([{"role": "user", "content": "This is a test of connecting. Please just answer \'yes\'"}]))
    print(lm.ask_with_memories("Hi, my name is Andy, what is your favorite animal")[0])
    print(lm.ask_with_memories("Hi, do you remember our conversation,could you tell me about it?")[0])