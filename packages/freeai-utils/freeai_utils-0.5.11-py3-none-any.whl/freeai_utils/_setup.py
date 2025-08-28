import gc
import os
import requests
from tqdm import tqdm
import re
import shutil
import urllib.request
import zipfile
import subprocess
import sys
import importlib.util
import click
from packaging.version import parse
from importlib.metadata import version

def install_model(target : str, auto_confirm: bool = False):
    target =target.strip().upper() if target is str else target
    install_linux_dependencies() #for linux system-level
    _setup_collab_environment() #for google collab to fix xauthority
    #add extra libs cant pip install on google collab
    install_library("pyaudio")
    install_library("pyautogui")
    if target is None or target == "A" or target == "":
        install_default_model(auto_confirm)  # Installs all default models (excluding image generation)
    elif target == "S":
        print("Downloading default models for speech-to-text")
        download_transcription()
    elif target == "D":
        print("Downloading default models for document processing")
        download_document_related()
    elif target == "I":
        print("Downloading default models for OCR and image captioning")
        download_image_related()
    elif target == "T":
        print("Downloading default models for translation")
        download_translation()
    elif target == "L":
        print("Downloading default models for local LLMs")
        download_LLM()
    elif target == "ICF":
        if not auto_confirm:
            decision = input(
                "This function will download all included models and extra style safetensors files used for SDXL_Turbo and SD15.\n"
                "The process can take a significant amount of time, so feel free to take a break.\n"
                "Would you like to proceed with the download? (Y/n): ").strip().lower()

            if decision != "y":
                print("Download cancelled.")
                return
        
        print("Downloading all models for image creating")
        print("*" * 100)
        print("Recommend to use AUTOMATIC 1111 instead for better speed and UI")
        print("*" * 100)
        download_image_creation_related()
        download_from_civitai()
        print("*" * 100)
        print("Note: Please recheck if any files were not downloaded completely due to connection loss or anything.")
        print("If so, please rerun the command line again.")
        print("*" * 100)
    elif target == "EICF":
        if not auto_confirm:
            decision = input(
                "This function will download extra style safetensors files used for SDXL_Turbo and SD15.\n"
                "The process can take a significant amount of time, so feel free to take a break.\n"
                "Would you like to proceed with the download? (Y/n): ").strip().lower()

            if decision != "y":
                print("Download cancelled.")
                return
        
        print("Downloading safetensors files from civitai...")
        download_from_civitai()
        print("*" * 100)
        print("Note: Please recheck if any files were not downloaded completely due to connection loss or anything.")
        print("If so, please rerun the command line again.")
        print("*" * 100)
    elif target == "ICE":
        print("*" * 100)
        print("Downloading all embeded files for image creating")
        print("*" * 100)
        download_embeded_citivai()
    elif target == "V":
        print("*" * 100)
        print("Downloading/Re-downloading vosk models")
        print("*" * 100)
        download_vosk_model()
    else:
        print("No cmd found, please try again")
        
def install_default_model(auto_confirm : bool = False):
    if not auto_confirm:
        decision = input(
            "This function will download all default models used by this library.\n"
            "The process can take a significant amount of time, so feel free to take a break.\n"
            "Would you like to proceed with the download? (Y/n): ").strip().lower()
            
        if decision != "y":
            print("Download cancelled.")
            return
    print("Downloading default models...")
    download_transcription()
    download_document_related()
    download_image_related()
    download_translation()
    download_vosk_model()

def _download_and_purge(cls, *args, **kwargs):
    inst = cls(*args, **kwargs)
    del inst
    gc.collect()
    
def download_transcription():
    from .audio_to_text_vn import VN_Whisper
    from .audio_to_text_whisper import OpenAIWhisper
     
    _download_and_purge(VN_Whisper)
    _download_and_purge(OpenAIWhisper)


def download_document_related():
    from .decider import DecisionMaker
    from .document_filter import AIDocumentSearcher
     
    _download_and_purge(DecisionMaker)
    _download_and_purge(AIDocumentSearcher, auto_init=False)


def download_image_related():
    from .image_to_text import ImageCaptioner
    from .text_from_image_easyocr import Text_Extractor_EasyOCR
    
    _download_and_purge(ImageCaptioner)
    _download_and_purge(Text_Extractor_EasyOCR)


def download_translation():
    from .language_detection import MBartTranslator, M2M100Translator
    
    _download_and_purge(MBartTranslator)
    _download_and_purge(M2M100Translator)

def download_LLM():
    from .localLLM import LocalLLM
    _download_and_purge(LocalLLM)

def download_image_creation_related():
    from .image_creator import SDXL_TurboImage, SD15_Image
    _download_and_purge(SDXL_TurboImage)
    _download_and_purge(SD15_Image, safety=True, embed_default = False)

def download_vosk_model():
    _download_and_extract_zip_file(url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                                   folder_name="en_us_015",
                                   download_dir=None)#for en
    _download_and_extract_zip_file(url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
                                   folder_name="en_us_022_lgraph",
                                   download_dir=None)#for en
    _download_and_extract_zip_file(url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
                                   folder_name="en_us_022_largest",
                                   download_dir=None)#for en
    _download_and_extract_zip_file(url= "https://alphacephei.com/vosk/models/vosk-model-vn-0.4.zip",
                                   folder_name="vn_04",
                                   download_dir=None) #for vn

def download_from_civitai():#download some popular models
    #https://civitai.com/models/23521/anime-pastel-dream
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/28100?type=Model&format=SafeTensor&size=full&fp=fp16",
                        model_name="anime_pastal_dream",
                        download_name="anime_pastal_dream"
                        )

    #https://civitai.com/models/11866/meinapastel
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/108289?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="meinapastel",
                        download_name="meinapastel"
                        )

    #https://civitai.com/models/81458/absolutereality
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/132760?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="reality",
                        download_name="reality"
                        )

    #https://civitai.com/models/23900?modelVersionId=304817
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/304817?type=Model&format=SafeTensor&size=pruned&fp=fp16",
                        model_name="annylora_checkpoint",
                        download_name="annylora_checkpoint"
                        )
    download_embeded_citivai()
    
def download_embeded_citivai():
    #https://civitai.com/models/7808?modelVersionId=9208
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/9208?type=Model&format=SafeTensor&size=full&fp=fp16",
                        model_name="easynegative",
                        download_name="easynegative"
                        )
    
    #https://civitai.com/models/56519/negativehand-negative-embedding
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/60938?type=Negative&format=Other",
                        model_name="negative_hand",
                        download_name="negative_hand"
                        )
    
    #https://civitai.com/models/55700/badprompt-negative-embedding
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/60095?type=Negative&format=Other",
                        model_name="bad_prompt",
                        download_name="bad_prompt"
                        )
    
    #https://civitai.com/models/58390/detail-tweaker-lora-lora
    _url_download_from_civitai(civitai_api_download_url="https://civitai.com/api/download/models/62833?type=Model&format=SafeTensor",
                        model_name="add_detail",
                        download_name="add_detail"
                        )

#only support .safetensors and .pt
def _url_download_from_civitai(civitai_api_download_url : str = "", model_name : str = None, download_name : str = None, download_dir : str = None) ->None: #only support for '.safetensors' and '.pt'
    """Download a safetensor or pt file from civitai web\n
    model_name -> this to help know what model is being downloaded\n
    downloaded_name -> this will check the name when download to own computer\n
    download_dir -> where it would be downloaded
    """
    
    if download_dir is None:
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_models")
    os.makedirs(download_dir, exist_ok=True)
    
    if download_name is None:
        raise TypeError("download_name can not be None")
    
    if model_name is None:
        model_name = download_name #use the downloaded name as the model name
    
    direct_download_url = None
    final_filename = None
    
    try:
        print(f"Fetching direct download URL for model: {model_name}...")
        response = requests.head(civitai_api_download_url, allow_redirects=False)
        response.raise_for_status()

        if response.status_code in [301, 302, 303, 307, 308]: # Check for redirect status codes
            direct_download_url = response.headers['Location']
            print(f"Found direct download URL: {direct_download_url}")

            if "Content-Disposition" in response.headers:
                cd = response.headers['Content-Disposition']
                filename_match = re.search(r'filename\*?=(?:UTF-8\'\')?([^;]+)', cd, re.IGNORECASE)
                if filename_match:
                    final_filename = filename_match.group(1).strip('\"\'')
            
            if not final_filename:
                final_filename = os.path.basename(direct_download_url.split('?')[0])
                if not final_filename.endswith(('.safetensors', '.pt')):
                    raise RuntimeError("File not end with .safetensors or .pt") #fall back if file is not in these type
                    
        else:
            print(f"Unexpected status code {response.status_code}. Not a redirect. Assuming direct download.")
            direct_download_url = civitai_api_download_url # Use the original URL if no redirect
            if "Content-Disposition" in response.headers:
                cd = response.headers['Content-Disposition']
                filename_match = re.search(r'filename\*?=(?:UTF-8\'\')?([^;]+)', cd, re.IGNORECASE)
                if filename_match:
                    final_filename = filename_match.group(1).strip('\"\'')
            if not final_filename:
                final_filename = f"{model_name}.safetensors"
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching direct download URL: {e}")
        return
        
    if not direct_download_url:
        print("Could not determine the direct download URL. Exiting.")
        return
        
    #filename for the downloaded
    filepath = os.path.join(download_dir, f"{download_name}.{final_filename.split('.')[-1]}")
    
    headers = {}
    download_start_byte = 0
    total_size_in_bytes = 0
    resume_possible = False
    
    if os.path.exists(filepath):
        download_start_byte = os.path.getsize(filepath)
        # Check existing file size matches
        try:
            head_response_for_size = requests.head(direct_download_url, allow_redirects=True)
            head_response_for_size.raise_for_status()
            expected_full_size = int(head_response_for_size.headers.get('content-length', 0))
            if expected_full_size > 0 and download_start_byte == expected_full_size:
                print(f"File {final_filename} already fully downloaded. Size: {download_start_byte} bytes.")
                while True:
                    user_choice = input(f"'{final_filename}' already exists and is complete.\nDo you want to redownload it [R], or exit? [E]  Choice(R/E): ").strip().lower()
                    if user_choice == 'r':
                        print("Initiating full re-download.")
                        os.remove(filepath) # Delete the existing file
                        download_start_byte = 0 # Reset to start new download
                        break
                    elif user_choice == 'e':
                        print("Exiting as requested.")
                        return
                    else:
                        print("Invalid choice. Please enter 'R' or 'E'.")

            if expected_full_size > download_start_byte:
                while True:
                    user_choice = input(f"Partial file '{final_filename}' found ({download_start_byte} bytes).\nDo you want to resume [R], or start [S] a new download from scratch? (R/S): ").strip().lower()
                    if user_choice == 'r':
                        headers["Range"] = f"bytes={download_start_byte}-"
                        resume_possible = True
                        print(f"Resuming download from byte {download_start_byte} for {final_filename}")
                        break
                    elif user_choice == 's':
                        print("Starting a new download from scratch.")
                        os.remove(filepath) # Delete the existing partial file
                        download_start_byte = 0 # Reset to start new download
                        break
                    else:
                        print("Invalid choice. Please enter 'R' or 'S'.")
            elif download_start_byte > 0 and expected_full_size <= download_start_byte:
                print(f"Partial file {final_filename} exists, but it's larger or equal to expected size {expected_full_size}. Possibly corrupted or full.")
                print("Starting a new download. If this is incorrect, delete the partial file manually.")
                download_start_byte = 0 # force new download
                
        except requests.exceptions.RequestException as e:
            while True:
                user_choice = input(f"Could not verify full file size from server. Partial file '{final_filename}' found ({download_start_byte} bytes).\nDo you want to resume [R], or start [S] a new download from scratch? (R/S): ").strip().lower()
                if user_choice == 'r':
                    headers["Range"] = f"bytes={download_start_byte}-"
                    resume_possible = True
                    print(f"Attempting resume from byte {download_start_byte} for {final_filename} without full size check.")
                    break
                elif user_choice == 's':
                    print("Starting a new download from scratch.")
                    if os.path.exists(filepath):
                        os.remove(filepath) # Delete the existing partial file
                    download_start_byte = 0 # Reset to start new download
                    break
                else:
                    print("Invalid choice. Please enter 'R' or 'S'.")
    else:
        print(f"Starting new download for {final_filename}.")
    
    try:
        with requests.get(direct_download_url, headers=headers, stream=True, allow_redirects=True) as r:
            r.raise_for_status() # HTTPError for bad responses 
            
            # Confirm the actual total size from the response
            if r.status_code == 206 and 'Content-Range' in r.headers:
                try:
                    range_header = r.headers['Content-Range']
                    total_size_in_bytes = int(range_header.split('/')[1])
                    print(f"Server responded with 206 Partial Content. Total file size: {total_size_in_bytes} bytes.")
                except (IndexError, ValueError):
                    total_size_in_bytes = int(r.headers.get('content-length', 0)) 
                    print("Warning: Could not parse Content-Range header. Progress bar might be inaccurate.")
            elif r.status_code == 200:
                if resume_possible:
                    print("Server did not return 206 Partial Content for resume. Starting new download from scratch.")
                    download_start_byte = 0 # Reset if server didn't resume
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                print(f"Server responded with 200 OK. Total file size: {total_size_in_bytes} bytes.")
            
            if total_size_in_bytes == 0:
                print("Warning: Could not determine total file size. Progress bar will not be accurate.")
            block_size = 1024 # 1 Kibibyte (1KB)
            
            # Open file in append-binary mode ('ab') for resuming, or write-binary ('wb') for new
            mode = 'ab' if download_start_byte > 0 and r.status_code == 206 else 'wb'
            
            print(f"Downloading to: {filepath}")
            with tqdm(
                initial=download_start_byte,
                total=total_size_in_bytes,
                unit='iB',
                unit_scale=True,
                desc=final_filename
            ) as progress_bar:
                with open(filepath, mode) as f:
                    for chunk in r.iter_content(chunk_size=block_size):
                        progress_bar.update(len(chunk))
                        f.write(chunk)
        
        print(f"Successfully downloaded {final_filename} to {download_dir}")
    
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', None)
        if status_code == 416:
            print("File already full, exiting...")
            return
        
        # Fallback for any other network/HTTP errors
        print(f"An HTTP or network error occurred during download: {e}")
        print("Please check your internet connection and the direct download URL.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def _download_and_extract_zip_file(url : str = "", folder_name : str = None, download_dir : str = None) -> None:
    zip_name : str = url.split('/')[-1]
    if download_dir is None:
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vosk_models")
    os.makedirs(download_dir, exist_ok=True)
    
    try:
        #download the ZIP file
        print(f"Downloading {zip_name}...")
        urllib.request.urlretrieve(url, zip_name)
        print("Download completed.")

        #extract
        print(f"Extracting {zip_name} to {download_dir}...")
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        print("Extraction completed.")

    finally:
        #remove ZIP file
        if os.path.exists(zip_name):
            print(f"Deleting {zip_name}...")
            os.remove(zip_name)
            print("ZIP file deleted.")

    #rename
    if folder_name is None:
        print("No new name specify, exiting..")
        return
    new_path = os.path.join(download_dir, folder_name)
    old_path = os.path.join(download_dir, zip_name.removesuffix(".zip"))
    
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"Error: The folder '{old_path}' does not exist.")
    elif os.path.exists(new_path):
        print("Found existed path, procceed to remove")
        remove_dir(new_path)
    try:
        os.rename(old_path, new_path)
        print(f"Folder '{old_path}' successfully renamed to '{new_path}'.")
    except OSError as e:
        print(f"Error renaming folder '{old_path}' to '{new_path}': {e.strerror}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def remove_dir(path : str) -> None:
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Path {path} not found")
    
    print(f"Removing folder: {path}")
    try:
        shutil.rmtree(path)
        print(f"Succesfully remove folder {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied to modify {path}. Fail to remove the folder.")
    except OSError as e:
        raise OSError(f"Error removing folder '{path}': {e.strerror}")


def install_library(package) -> None:
    """Install a library seperately from the dependencies in toml file"""
    # check before trying to install library 
    spec = importlib.util.find_spec(package)
    if spec is not None:
        return
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}.")
    except subprocess.CalledProcessError:
        print(f"Error: Can not to install {package}. Proceed to skip installing {package}")
        
def install_linux_dependencies():
    """Installs system-level dependencies for PyAutoGUI and PyAudio on Linux."""
    # This function first updates the package list, then attempts to install
    # all required packages in a single command. It will only run if the
    # operating system is Linux.

    # A list of all required apt-get packages
    apt_packages = [
        # Base audio/video dependencies
        "ffmpeg",
        "libmp3lame-dev",
        "libportaudio2",
        "libportaudiocpp0",
        "portaudio19-dev",  # Added this for PyAudio compatibility
        "espeak",
        # Dependencies for PyAutoGUI
        "python3-xlib",
        "libx11-dev",
        "libjpeg-dev",
        "libpng-dev",
        "zlib1g-dev",
        "xserver-xephyr",
        # Dependencies for PyAudio
        "libasound-dev",
        "xvfb", #for pyautogui fakescreen
    ]
    
    # Check if the operating system is Linux
    if sys.platform.startswith("linux"):
        print("Detected Linux environment. Updating package list...")
        try:
            # update the apt-get package list
            subprocess.check_call(["sudo", "apt-get", "update"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,)
            print("Package list updated. Installing dependencies...")
            
            # Now, install all the dependencies
            subprocess.check_call(["sudo", "apt-get", "install", "-y"] + apt_packages,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,)
            print("All system dependencies installed successfully.")
            if os.getenv('DISPLAY') is None:
                print("Setting up virtual display for PyAutoGUI...")
                subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24', '-ac', '+extension', 'GLX'])
                os.environ['DISPLAY'] = ':99'
                print("Virtual display is ready.")
        except subprocess.CalledProcessError as e:
            print(f"Error: An apt-get command failed.")
            print(f"Details: {e}")
            
# Additional helper function to ensure proper X11 setup before importing GUI libraries (created by AI)
def _setup_collab_environment():
    """For headless environment like google collab to not stop because of pyautogui"""
    collab_env = ('COLAB_GPU' in os.environ) or ('COLAB_TPU_ADDR' in os.environ) or ('google.colab' in sys.modules)
    if sys.platform.startswith("linux") and collab_env:
        print("Detect google collab environment...")
        # Ensure XAUTHORITY is properly set
        if "XAUTHORITY" not in os.environ:
            temp_xauth = "/tmp/.Xauth_temp"
            if os.path.exists(temp_xauth):
                os.environ["XAUTHORITY"] = temp_xauth
            else:
                # Create empty auth file
                try:
                    with open(temp_xauth, 'wb') as f:
                        pass
                    os.chmod(temp_xauth, 0o600)
                    os.environ["XAUTHORITY"] = temp_xauth
                    print(f"Created temporary X authority file: {temp_xauth}")
                except Exception as e:
                    print(f"Could not create auth file: {e}")
                    # disable auth
                    os.environ["XAUTHORITY"] = "/dev/null"

def check_for_updates(package_name) -> bool:
    try:
        installed_version = parse(version(package_name))
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest_version = parse(data["info"]["version"])
        
        if latest_version > installed_version:
            click.echo(f"\n{colorize('[notice]', '96')} A new version of {package_name} is available! ({colorize(installed_version, '31')} → {colorize(latest_version, '32')})")
            install_support = colorize(f'pip install --upgrade {package_name}', '32')
            click.echo(f"{colorize('[notice]', '96')} To update, run: {install_support}")
            return True
        return False
            
    except Exception as e:
        click.echo(f"An error occurred while checking for updates: {e}")
        return False # Return False on error
    
def colorize(text: str, color_code: str) -> str:
    """Returns a string with the specified ANSI color and a reset code."""
    return f"\033[{color_code}m{text}\033[0m"

def get_free_space_gb(path='/') -> float:
    #Defaults to the root directory ('/') which typically represents the system drive.
    try:
        disk_stats = shutil.disk_usage(path)

        # Convert bytes to gigabytes
        free_space_bytes = disk_stats.free
        free_space_gb = free_space_bytes / (1024**3)
        return free_space_gb
    except Exception as e:
        print(f"Error checking disk space: {e}")
        return None