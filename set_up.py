# download_models.py
import os
import subprocess
import sys
import lzma
import tarfile

def install_dependencies():
    try:
        # sys.executable ensures it installs to the correct virtual environment if active
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "./requirements.txt"])
        print("Dependencies installed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies. {e}")
        sys.exit(1)

def install_jamdict_db():

    import gdown
    drive_url_or_id = "https://drive.google.com/file/d/1QZRzOoMF4CGlkdl0FyU7ledAZLRlpoom/view?usp=sharing"
    # Extract file ID from Drive link if a full URL is provided
    drive_url = "https://drive.google.com/file/d/1QZRzOoMF4CGlkdl0FyU7ledAZLRlpoom/view?usp=sharing"
    
    target_dir = os.path.expanduser("~\\.jamdict\\data")
    os.makedirs(target_dir, exist_ok=True)
    
    temp_download = os.path.join(target_dir, "jamdict_download.tmp")
    db_path = os.path.join(target_dir, "jamdict.db")

    print("Downloading database from Google Drive...")
    gdown.download(url=drive_url, output=temp_download, quiet=False)

    # 1. Verify the download isn't an HTML error page
    with open(temp_download, "rb") as f:
        header = f.read(100)
        if b"<html" in header.lower() or b"<!doctype html" in header.lower():
            raise RuntimeError("Downloaded file is an HTML page instead of the database archive. Check Drive link permissions.")

    print("Decompressing database...")

    # 2. Try raw .xz decompression first (using built-in lzma)
    decompressed = False
    try:
        with lzma.open(temp_download, "rb") as f_in, open(db_path, "wb") as f_out:
            f_out.write(f_in.read())
        print(f"Successfully decompressed raw .xz file to {db_path}")
        decompressed = True
    except Exception:
        pass

    # 3. Fallback to .tar.xz archive extraction if raw .xz failed
    if not decompressed:
        try:
            with tarfile.open(temp_download, "r:xz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("jamdict.db"):
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=target_dir)
                        break
            print(f"Successfully extracted .tar.xz archive to {db_path}")
        except Exception as e:
            if os.path.exists(temp_download):
                os.remove(temp_download)
            raise RuntimeError(f"Could not extract or decompress archive: {e}")

    # Clean up temporary download file
    if os.path.exists(temp_download):
        os.remove(temp_download)

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
    print("Downloading jmdict database")
    install_jamdict_db()
    print("Setting up local models...")
    setup_local_models()