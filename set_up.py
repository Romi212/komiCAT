# download_models.py
import os
import subprocess
import sys

def install_dependencies():
    try:
        # sys.executable ensures it installs to the correct virtual environment if active
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "./requirements.txt"])
        print("Dependencies installed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies. {e}")
        sys.exit(1)



def setup_local_models():
    from huggingface_hub import snapshot_download

    base_path = "./src/models/"
    # 1. Download the Comic Text and Bubble Detector Model
    print(" -> Downloading bubble detector model to "+base_path+"bubble_detector_model...")
    snapshot_download(
        repo_id="ogkalu/comic-text-and-bubble-detector",
        local_dir=base_path + "bubble_detector_model"
    )

    # 2. Download the Manga OCR Text Recognition Model
    print(" -> Downloading Manga OCR model to "+base_path+"manga_ocr_model...")
    snapshot_download(
        repo_id="kha-white/manga-ocr-base",
        local_dir=base_path + "manga_ocr_model"
    )

    print(" -> Downloading best comic panel detection model to "+base_path+"comic_panel_detection_model...")
    snapshot_download(
        repo_id="mosesb/best-comic-panel-detection",
        local_dir=base_path + "comic_panel_detection_model"
    )
    print(" -> Downloading leoxs22 comic panel detection model to "+base_path+"comic_panel_detection_model_leoxs...")
    snapshot_download(
        repo_id="leoxs22/manga-panel-detector-yolo26n",
        local_dir=base_path + "comic_panel_detection_model_leoxs"
    )

if __name__ == "__main__":
    print("Set up Started :3")

    print("Downloading required libraries...")
    install_dependencies()
    print("Setting up local models...")
    setup_local_models()