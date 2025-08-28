import torch
from diffusers import AutoPipelineForText2Image #for sdxl_turbo
from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker #safety check
from transformers import CLIPImageProcessor #for safety check
import os
from diffusers import StableDiffusionPipeline #for sd1.5
from transformers import CLIPTokenizer #for sd1.5
from freeai_utils.log_set_up import setup_logging
import logging
from typing import Union, Optional
import random
import time

class SDXL_TurboImage:
    
    __slots__ = ("_model", "_device", "logger", "_initialized")
    
    _model: AutoPipelineForText2Image
    _device: str
    logger: logging.Logger
    _initialized: bool
    
    def __init__(self, model_name : str = "stabilityai/sdxl-turbo", device : str = None):
        #check type
        self.__enforce_type(model_name, str, "model_name")
        
        #init
        super().__setattr__("_initialized", False)
        
        self.logger = setup_logging(self.__class__.__name__)
        #init the var to hold device available
        preferred_devices = []
        self._model = None
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
        
        for dev in preferred_devices:
            dtype = torch.float32 if dev == "cpu" else torch.float16
            try:
                self.logger.info(f"Loading '{model_name}' on {dev}")
                self._model = AutoPipelineForText2Image.from_pretrained(model_name, torch_dtype=dtype,).to(dev)
                self._device = dev
                self.logger.info(f"Successfully loaded on {dev}")
                break
            except Exception as e:
                self.logger.error(f"Failed to load on {dev}: {e}")
                
        if self._model is None:
            raise RuntimeError(f"Cannot load '{model_name}' on any of: {preferred_devices}")
        
        #lock
        super().__setattr__("_initialized", True)
        
        self.logger.info("Fast image generator, sacrifice quality for speed")

    @property
    def device(self):
        return self._device
    
    @property
    def model(self):
        return self._model

    def generate_images(self, prompt : str = None, 
                    negative_prompt : str = """lowres, text, error, missing fingers, extra digit, missing libs, cropped, bad mouth, bad lips
                                                worst quality, lowres, (bad anatomy), (bad hands), text, missing finger, 
                                                extra digits, 2 eyes color, blurry, bad eyes, low quality, 3d, sepia, painting, 
                                                cartoons, sketch, signature, watermark, username""", 
                    steps : int = 2,
                    number_of_images : int = 2,
                    image_name : str = "generated_image",
                    output_dir : str = "generated_images") -> None:
        
        """
        Creates images from a positive prompt (what you want to see) and a negative prompt (what you want to avoid). 
        It saves the generated images to a specified directory.
        """
        #check type
        self.__enforce_type(prompt, str, "prompt")
        self.__enforce_type(negative_prompt, str, "negative_prompt")
        self.__enforce_type(steps, int, "steps")
        self.__enforce_type(number_of_images, int, "number_of_images")
        self.__enforce_type(image_name, str, "image_name")
        self.__enforce_type(output_dir, str, "output_dir")
        
        #make the folder exists
        os.makedirs(output_dir, exist_ok=True)
        try:
            output = self._model(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=0.0,
                num_images_per_prompt=number_of_images
            )
        except RuntimeError:
            raise RuntimeError(f"""Look like your computer can't handle the image generation. Please lower your 'steps' and 'number_of_images'.
                                 Your current input for steps: {steps}
                                 Your current input for images per generation: {number_of_images}
                                 """)
        except Exception as e:
            self.logger.critical(f"Error: {e}")
            raise
        
        images = output.images  # a list of PIL images
        current_time = int(time.time())
        
        for i, img in enumerate(images):
            file_path = os.path.join(output_dir, f"{image_name}{current_time + i}.png")
            img.save(file_path) #will add time later to not be overload
            print(f"Save : {file_path}")
        print(f"Saved {len(images)} images.")

    def __setattr__(self, name, value):
        # once initialized, block these core attributes
        if getattr(self, "_initialized", False) and name in ("_model", "_device"):
            raise AttributeError(f"Cannot reassign '{name}' after initialization")
        super().__setattr__(name, value)
        
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")

class SD15_Image:
    
    logger : logging.Logger
    _model : StableDiffusionPipeline
    _tokenizer : CLIPTokenizer
    
    def __init__(self, preferred_device : Optional[str] = None ,support_model : str = "" , model_path : str = None, scheduler : str = "default", safety : bool = False, reduce_memory : bool = False, embed_default : bool = True):
        #check type before start
        self.__enforce_type(support_model, str, "support_model")
        self.__enforce_type(safety, bool, "safety")
        self.__enforce_type(reduce_memory, bool, "reduce_memory")
        self.__enforce_type(embed_default, bool, "embed_default")
        
        #model path is to check whether get from lib or get from running folder
        #support_model is for use or not
        #reduce_memory for enable slicing
        self.logger = setup_logging(self.__class__.__name__)
        self.logger.info("Init...")
        self._device = None
        self._model = None
        
        if model_path is None:
            self._model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_models")
        else:
            self.__enforce_type(model_path, str, "model_path")
            self._model_path = model_path
            
        path = os.path.join(self._model_path, support_model) #init the path to model
        
        preferred_devices = []

        #try input first
        if preferred_device is not None:
            self.__enforce_type(preferred_device, str, "device")
            preferred_devices.append(preferred_device)
        # try cuda second 
        if torch.cuda.is_available() and "cuda" not in preferred_devices:
            preferred_devices.append("cuda")
        # fall back to CPU if not already there
        if "cpu" not in preferred_devices:
            preferred_devices.append("cpu")
        
        if support_model.strip() == "":
            self.logger.info("No support_model specify, using default stable-diffusion-v1-5, skipping all other configures..")
            self._default_setup(preferred_devices, reduce_memory=reduce_memory, embed_default = embed_default)
        else:
            self.logger.info("Custom setup for SD1.5")
            self._custom_setup(preferred_devices = preferred_devices, path = path, scheduler = scheduler, safety=safety, reduce_memory=reduce_memory, embed_default = embed_default)
        #embeded support
        
        if self._model is None:
            raise RuntimeError(f"Could not load model on any device: {preferred_devices}")
        else:
            self.logger.info(f"Successfully loaded on {self._device}")
    
    @property
    def device(self):
        return self._device
    
    @property
    def model(self):
        return self._model
    
    def generate_images(self,
                        positive_prompt : str = None, 
                        negative_prompt : str = "<easynegative:0.8>, <negativehand:2.1>, <badprompt:1.4> (hands:1.2)",
                        image_name : str = "generated_image", 
                        output_dir : str = "generated_images",
                        width : int = 512, 
                        height : int = 512, 
                        steps : int = 30, 
                        guidance_scale : float = 8, 
                        number_of_images : int = 2, 
                        clip_skip : int = 0,
                        extra_detail : Union[int, float, None] = None,
                        seed : int = -1,
                        **optional_kwargs) -> None:
        """
        Creates images from a positive prompt (what you want to see) and a negative prompt (what you want to avoid). 
        It saves the generated images to a specified directory. You can control various aspects of the image generation process:
        
        ARGS: 
        - positive prompt: The main description of what you want the image to contain. This is the core instruction for the model.
        - negative prompt: A description of what you want to exclude from the generated image. By default, it includes common negative prompts to help avoid artifacts like bad hands and poor composition.
        - image_name: The base name for the generated image files. A timestamp will be appended to each filename to ensure they are unique.
        - output_dir: The directory where the generated images will be saved. The function will create this directory if it doesn't already exist.
        - width, height: image pixels
        - number of images: The number of images to generate per call.
        - clip_skip: Controls how many layers of the CLIP text encoder to skip. Skipping layers can alter the stylistic output of the image.
        - steps:  The number of diffusion steps to run. A higher number of steps can lead to a more detailed and refined image but will take longer to generate.
        - guidance scale: A value that influences how strongly the model adheres to the positive_prompt. Higher values make the output more closely match the prompt but can sometimes reduce image quality.
        - extra_detail: This is the strength of the lora applied
        - seed: A value used to initialize the random number generator. Using a fixed seed will produce the exact same image(s) for the same prompts and parameters, which is useful for reproducibility. If set to -1 (the default), a random seed will be used for each generation.
        - **optional_kwargs: Additional keyword arguments that can be passed directly to the underlying model for advanced control.
        """
        #check type before proceed
        self.__enforce_type(positive_prompt, str, "positive_prompt")
        self.__enforce_type(negative_prompt, str, "negative_prompt")
        self.__enforce_type(image_name, str, "image_name")
        self.__enforce_type(output_dir, str, "output_dir")
        self.__enforce_type(width, int, "width")
        self.__enforce_type(height, int, "height")
        self.__enforce_type(steps, int, "steps")
        self.__enforce_type(guidance_scale, (int, float), "guidance_scale")
        self.__enforce_type(number_of_images, int, "number_of_images")
        self.__enforce_type(clip_skip, int, "clip_skip")
        self.__enforce_type(seed, int, "seed")
        self.__enforce_type(extra_detail, (int, float, type(None)), "extra_detail") #lora support 
        
        if extra_detail is not None :
            if (extra_detail > 2 or extra_detail < -2):
                raise ValueError(f"extra_detail value can only be in range -2 to 2. Current setting: {extra_detail}")
            self._model.enable_lora()
            try:
                self._model.set_adapters("add_detail", adapter_weights=extra_detail)
            except:
                try: # load loar file to the model
                    self._model.load_lora_weights(self._model_path, weight_name="add_detail.safetensors", adapter_name="add_detail")
                except FileNotFoundError:
                    self.logger.critical(f"Fail to load default lora file.\n May be you wanna try command line: 'freeai-utils setup ICE' to download the file?")
                    raise
                except Exception as e:
                        raise Exception(e)
                self._model.set_adapters("add_detail", adapter_weights=extra_detail)
        else: self._model.disable_lora()
         
        #random seed generator
        if seed == -1:
            seed = random.randint(0, 2**32 - 1) 
            print(f"Using random seed: {seed}")
            
        generator = torch.Generator(self._device).manual_seed(seed)
        os.makedirs(output_dir, exist_ok=True) #make the dir exists
        try:
            with torch.inference_mode():
                output = self._model(
                    prompt= positive_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps= steps, 
                    guidance_scale= guidance_scale,
                    num_images_per_prompt= number_of_images,
                    clip_skip= clip_skip,
                    generator=generator,
                    **optional_kwargs
                )
        except RuntimeError:
            raise RuntimeError(f"""Look like your computer can't handle the image generation. Please lower your 'steps' or 'guidance_scale' or 'number_of_images'.
                                If that didn't work, please use another 'device'.
                                 Your current input for steps: {steps}
                                 Your current input for guidance_scale : {guidance_scale}
                                 Your current input for images per generation: {number_of_images}
                                 Your current device: {self.device}
                                 """)
        except Exception as e:
            self.logger.critical(f"Error: {e}")
            raise
            
        current_time = int(time.time())
        for i, img in enumerate(output.images):
            file_path = os.path.join(output_dir, f"{image_name}{current_time + i}.png")
            img.save(file_path) #will add time later to not be overload
            print(f"Save : {file_path}")
        print(f"Saved {len(output.images)} images.")
    
    def _help_config(self) -> None:
        """Print guide on config for init of this class"""
        model_list = [
            {"name": "anime_pastal_dream.safetensors", "description": "Anime: Dreamy aesthetic with soft, pastel colors."},
            {"name": "meinapastel.safetensors", "description": "Anime: 2D illustrations with good lighting, shadows, and vibrant colors."},
            {"name": "reality.safetensors", "description": "Realistic: Photorealistic images."},
            {"name": "annylora_checkpoint.safetensors", "description": "Just a style..."},
        ]
        scheduler_list = [
            {"name": "default", "description": "Euler (deterministic): General purpose, good for realistic and anime, consistent results."},
            {"name": "SDE Karras", "description": "DPM++ SDE Karras (stochastic single-step): good for diversity, requires even steps."},
            {"name": "DPM++ 2M Karras", "description": "DPM++ 2M Karras (deterministic multi-step): High quality, excellent for fast generation, very popular."},
            {"name": "Euler A", "description": "Euler Ancestral (stochastic): Good for exploration, diverse outputs, more artistic feel."},
        ]
        
        print("*" * 40)
        print("Including default support_model:\n")
        for option in model_list:
            print(f"Name: {option['name']}\n    Description: {option['description']}")
        print("*" * 40)
        
        print("Including default supported schedulers:\n")
        for option in scheduler_list:
            print(f"Name: {option['name']}\n    Description: {option['description']}")
        print("*" * 40)
        print("NOTE: You could still download model and load safetensors file")
        print("*" * 40)
        print("SD 1.5 Prompting Guide:\n")
        print("    Idea: '1 girl in the middle the street, blue hair, black eyes'")
        print("    Needs modification for SD 1.5. Try this:")
        print("(masterpiece, best quality, ultra-detailed:1.3), **dynamic angle**, 1girl, ((vibrant blue hair:1.4)), **very long hair**, ((intense black eyes:1.3)), she is in the middle the street, (beautiful and detailed eyes:1.1), urban background.")
        print("\nRemember a Negative Prompt is also crucial (if you set 'embed_default' = true, you already have load some embed files to help)")
        print("Tip: Use generative AI to reprompt your ideas for SD 1.5.")
        print("Note: Max prompt token count is 77 (positive/negative).")
        print("*" * 40)
        
    def _default_setup(self, preferred_devices : str, reduce_memory : bool, embed_default : bool) -> None:
        """
        Sets up the image generation pipeline with a default Stable Diffusion 1.5 model.
        Can optionally enable memory reduction and load default negative embeddings.
        """
        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading on {dev}")
                self._model = StableDiffusionPipeline.from_pretrained(
                    "stable-diffusion-v1-5/stable-diffusion-v1-5",
                    torch_dtype=torch.float32 if dev == "cpu" else torch.float16,
                ).to(dev)
                self._device = dev
                if reduce_memory:
                    self.logger.info("Enable attention slicing, reduce memory usage")
                    self._model.enable_attention_slicing()
                if embed_default:
                    self._load_default_embed_and_lora()
                break
            except FileNotFoundError:
                raise
            except Exception as e:
                self.logger.error(f"Failed to load on {dev}: {e}")

    def _custom_setup(self, preferred_devices : list, path : str, scheduler : str, safety : bool, reduce_memory : bool, embed_default : bool) -> None:
        """
        Sets up the image generation pipeline using a custom model from a local file path. 
        Can configure specific scheduler, enable or disable an NSFW safety checker, and reduce memory usage.
        """
        if not os.path.exists(path):
            self.logger.critical(f"Fail to load model at {path}.\n If you're trying the default models, may be you wanna try command line: 'freeai-utils setup ICF' to download the file?")
            raise FileNotFoundError(f"File not found at: {path}")
        
        self.logger.info(f"Loading support model at {path}")
        # Load tokenizer
        self._tokenizer = CLIPTokenizer.from_pretrained(
            "stable-diffusion-v1-5/stable-diffusion-v1-5",
            subfolder="tokenizer"
        )
        
        if safety:#disable nsfw 
            safety_checker = StableDiffusionSafetyChecker.from_pretrained(
                "CompVis/stable-diffusion-safety-checker"
            )
            feature_extractor = CLIPImageProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )
        else:
            safety_checker = None
            feature_extractor = None
            self.logger.warning("Safety is not enabled. I recommend starting with 'safety=True' and then deactivating it if not needed, as this will preload the necessary components.")
                 
        #iterate through to see which allow
        for dev in preferred_devices:
            try:
                self.logger.info(f"Loading on {dev}")
                self._model = StableDiffusionPipeline.from_single_file( #init model
                    path,
                    tokenizer=self._tokenizer,
                    safety_checker     = safety_checker,
                    feature_extractor  = feature_extractor,
                    torch_dtype=torch.float32 if dev == "cpu" else torch.float16,
                    mean_resizing = False,
                ).to(dev)
                self._device = dev
                if reduce_memory:
                    self.logger.info("Enable attention slicing, reduce memory usage")
                    self._model.enable_attention_slicing() #reduce size
                if embed_default:
                    self._load_default_embed_and_lora()
                break
            except FileNotFoundError: 
                raise
            except Exception as e:
                self.logger.error(f"Failed to load on {dev}: {e}")
        
        if self._model is None:
            raise RuntimeError(f"Could not load model on any device: {preferred_devices}") #raise before config scheduler
        #safety check
        self._custom_scheduler(scheduler = scheduler)
        self.logger.info("Initalized completed")
        
    def _custom_scheduler(self, scheduler : str) -> None:
        """Modifies the diffusion scheduler of the image generation model. 
        
        Supports several scheduler types: including SDE Karras, DPM++ 2M Karras, and Euler A.
        Defaults to Euler if the provided scheduler is not supported.
        """
        self.__enforce_type(scheduler, str, "scheduler")
        scheduler = scheduler.strip()
        self.logger.info(f"Loading scheduler: {scheduler if scheduler != 'default' else 'Euler'}")
        #schedule type
        new_scheduler = None
        if scheduler == "SDE Karras":
            from diffusers import DPMSolverSinglestepScheduler
            # build the DPM++ SDE Karras scheduler
            new_scheduler  = DPMSolverSinglestepScheduler.from_config( #this requires number of step to be even
                self._model.scheduler.config,
                use_karras_sigmas=True,
                lower_order_final=True
            )
            
        elif scheduler == "DPM++ 2M Karras":
            from diffusers import DPMSolverMultistepScheduler
            new_scheduler  = DPMSolverMultistepScheduler.from_config( 
                self._model.scheduler.config,
                use_karras_sigmas=True,
                solver_order=2,
                algorithm_type="dpmsolver++",
                lower_order_final=True 
            ) 
            
        elif scheduler == "Euler A":
            from diffusers import EulerAncestralDiscreteScheduler
            new_scheduler  = EulerAncestralDiscreteScheduler.from_config(self._model.scheduler.config, use_karras_sigmas=True,
                lower_order_final = True)
            
        else: #default euler
            if scheduler != "default": self.logger.info("The given scheduler name is not supported. Redirecting to default Euler.")
            self.logger.info(f"Using default: Euler")
            from diffusers import EulerDiscreteScheduler
            new_scheduler = EulerDiscreteScheduler.from_config(self._model.scheduler.config, use_karras_sigmas=True,
                lower_order_final = True)
        
        if new_scheduler is None:
            raise RuntimeError(f"Fail to modify to new_scheduler")
        self._model.scheduler = new_scheduler #set scheduler
        
    def _load_default_embed_and_lora(self) -> None:
        """
        Loads default textual inversion embeddings and a LoRA model into the pipeline. 
        These are used to enhance the quality of the generated images.
        """
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_models")
        embedding_paths = {
            "easynegative": os.path.join(path, "easynegative.safetensors"),
            "badprompt": os.path.join(path, "bad_prompt.pt"),
            "negativehand": os.path.join(path, "negative_hand.pt"),
        }
        
        for token_name, epath in embedding_paths.items(): #load embeded path to model
            if not os.path.exists(epath):#check if path exist before try running
                self.logger.critical(f"Fail to load {token_name} at {epath}.\n May be you wanna try command line: 'freeai-utils setup ICE' to download the file?")
                raise FileNotFoundError(f"File not found at: {epath}")
            try:
                self._model.load_textual_inversion(epath, token=token_name, local_files_only =True)
            except Exception as e:
                raise Exception(e)
        
        lora_path = os.path.join(path, "add_detail.safetensors")
        
        if not os.path.exists(lora_path):#check if path exist before try running
            self.logger.critical(f"Fail to load default lora file.\n May be you wanna try command line: 'freeai-utils setup ICE' to download the file?")
            raise FileNotFoundError(f"LoRA file not found at: {lora_path}")
        try: # load lora file to the model
            self._model.load_lora_weights(path, weight_name=lora_path, adapter_name="add_detail")
        except Exception as e:
                raise Exception(e)
    
    def enable_safety(self) -> None:
        """Enables a NSFW safety checker to prevent the generation of inappropriate content."""
        safety_checker = StableDiffusionSafetyChecker.from_pretrained(
            "CompVis/stable-diffusion-safety-checker"
        ).to(self._device)
        feature_extractor = CLIPImageProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )
        self._model.safety_checker = safety_checker
        self._model.feature_extractor = feature_extractor
        
    def disable_safety(self) -> None:
        """Disables the NSFW safety checker."""
        self._model.safety_checker = None
        self._model.feature_extractor = None
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")

if __name__ == "__main__":
    import gc
    prompt = "dynamic angle,ultra-detailed, close-up 1girl, (fantasy:1.4), ((purple eyes)),Her eyes shone like dreamy stars,(glowing eyes:1.233),(beautiful and detailed eyes:1.1),(Silver hair:1.14),very long hair"
    models = ["anime_pastal_dream.safetensors", "meinapastel.safetensors", "reality.safetensors", "annylora_checkpoint.safetensors"]
    schedulers = ["default", "SDE Karras", "DPM++ 2M Karras", "Euler A"]
    model = "meinapastel.safetensors"
    sc = "Euler A"
    imgGen = SD15_Image(support_model=model, scheduler=sc, reduce_memory=True, preferred_device="cuda")
    imgGen._help_config()
    imgGen.generate_images(prompt, seed=5000, image_name=f"nosafe")
    imgGen.enable_safety()
    imgGen.generate_images(prompt, seed=5000, image_name=f"save")
    # for model in models:
    #     for sc in schedulers:
    #         imgGen = SD15_Image(support_model=model, scheduler=sc)
    #         imgGen.generate_images(prompt, seed=5000, image_name=f"{model.split('.')[0]}_{sc}")
    #         imgGen.generate_images(prompt, seed=5000, image_name=f"{model.split('.')[0]}_{sc}_extra", extra_detail=1)
    #         imgGen = None
    #         gc.collect()
    #         time.sleep(1)