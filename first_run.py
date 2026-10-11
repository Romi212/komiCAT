import os
from pathlib import Path

DATA_DIR = Path(os.environ["LOCALAPPDATA"]) / "KomiCAT"
MODELS_DIR = DATA_DIR / "models"

MODELS = {
    "bubble_detector_model" : "ogkalu/comic-text-and-bubble-detector",
    "manga_ocr_model" : "kha-white/manga-ocr-base",
    "comic_panel_detection_model_leoxs" : "leoxs22/manga-panel-detector-yolo26n"
}

def missing_models():
    return [n for n in MODELS if not (MODELS_DIR / n).exists()]

def download_models(progress=print):
    from huggingface_hub import snapshot_download

    for name, repo in MODELS.items():
        if (MODELS_DIR / name).exists():
            continue
        progress(f"Downloading {name}...")
        snapshot_download(repo_id=repo, local_dir=str(MODELS_DIR / name))
