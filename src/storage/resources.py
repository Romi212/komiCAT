
import os
import json, re, shutil
from pathlib import Path
import sys
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

DATA_DIR = Path(os.environ["LOCALAPPDATA"]) / "KomiCAT"
IMAGES_DIR = "resources/images"

IMG_ICON = "/icon/komi-chan.png"
IMG_PEEK = "/komi-peek.png"

APP_FONT = "Zen Kaku Gothic Antique"
def resource(rel):
        base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
        return Path(base) / rel
    
def get_image_path(rel):
        return resource(IMAGES_DIR+rel)