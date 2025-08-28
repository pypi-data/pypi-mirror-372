# freeai_utils/cli.py
import sys
import click
from ._setup import install_model, remove_dir
import os
from .cleaner import Cleaner

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        sys.exit(1)

@main.command(help="Download default models for this library through hugging face ")
@click.argument("target", required=False)
@click.option("-y", "--yes", is_flag=True, help="Automatically confirm downloads without prompting")
def setup(target: str = "", yes: bool = False):
    install_model(target, yes)
    
@main.command(help="Detail guide on command line")
def help():
    print("*" * 100)
    print("HELP")
    print("*" * 100)
    print("Usage: freeai-utils setup [FLAG]\n")
    print(" Flags:")
    print("   A   Default models             →  freeai-utils setup A")
    print("   S   Speech-to-Text models      →  freeai-utils setup S")
    print("   D   Document-related models     →  freeai-utils setup D")
    print("   I   Image OCR models            →  freeai-utils setup I")
    print("   T   Translation models          →  freeai-utils setup T")
    print("   L   Default LLM models          →  freeai-utils setup L")
    print("   ICF Image generator models      →  freeai-utils setup ICF")
    print("   ICE Embeded for Image generator models      →  freeai-utils setup ICE")
    print("   V Vosk models      →  freeai-utils setup V")
    print("*" * 100)
    print("Usage: freeai-utils clean [FLAG]\n")
    print("Description: Clean up downloaded files and model through setup command")
    print(" Flags:")
    print("   A   Remove both extra downloaded safetensors and vosk models      →  freeai-utils clean A")
    print("   ICF   Remove extra safetensors file downloaded from ICF setup             →  freeai-utils clean ICF")
    print("   V   Remove Vosk models      →  freeai-utils clean V")
    print("*" * 100)
    
@main.command(help="Remove extra downloaded files")
@click.argument("target", required=False)
@click.option("-y", "--yes", is_flag=True, help="Automatically confirm delete without asking")
def clean(target : str = "", yes : bool = False):
    
    messages = {
        "V" : "Are you sure you want to remove only the Vosk model files? (Y/n): ",
        "ICF" : "Are you sure you want to remove only the safetensors files? (Y/n): ",
        "A" : "Are you sure you want to remove everything (Vosk + safetensors)? (Y/n): ",
        "" : "This will remove all downloaded files from civitai and the Vosk model.\n"
            "Use this before running pip uninstall.\n"
            "Are you sure you want to proceed? (Y/n): ",
    }
    
    key = target.strip().upper() if target is str else ""
    if key not in messages:
        print(f"Unknown target '{target}'. Valid options are: '', 'V', 'ICF', 'A'")
        return
    
    if not yes:
        decision = input(messages[key]).strip().lower()
            
        if decision != "y":
            print("Clean Up cancelled.")
            return
    
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    
    #known folder
    if key in ("A", ""):
        print("Cleaning: Vosk model and safetensors files...")
        known_folder = ["downloaded_models", "vosk_models"]
    elif key == "V":
        print("Cleaning: Vosk model files only...")
        known_folder = ["vosk_models"]
    elif key == "ICF":
        print("Cleaning: Extra safetensors files only...")
        known_folder = ["downloaded_models"]
    
    cleaner = Cleaner()
    cleaner.remove_all_files_end_with('.mp3') #for gttS audio
    
    for folder in known_folder:
        path = os.path.join(cur_dir, folder)
        try:
            remove_dir(path=path)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise Exception(e)