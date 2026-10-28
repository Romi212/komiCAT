import lzma
import os
import tarfile
from pathlib import Path
from PyQt6.QtGui import QColor, QFontDatabase
from storage.resources import resource, APP_FONT, DATA_DIR

MODELS_DIR = DATA_DIR / "models"
JAMDICT_DIR = Path.home() / ".jamdict" / "data"
JAMDICT_DB = JAMDICT_DIR / "jamdict.db"
JAMDICT_URL = "https://drive.google.com/file/d/1QZRzOoMF4CGlkdl0FyU7ledAZLRlpoom/view?usp=sharing"
DICTS_DIR = DATA_DIR / "dictionaries"
DICT_URL = "https://drive.google.com/drive/folders/1IXzPc_56WmknVd1QfAV4EzeXR8af9Q9O?usp=sharing"
DICT_CHECK_FILE = "es_frequency_dictionary.txt"
REQUIRED_DICT_LANGS = ("es","en")
MODELS = {
    "bubble_detector_model" : "ogkalu/comic-text-and-bubble-detector",
    "manga_ocr_model" : "kha-white/manga-ocr-base",
    "comic_panel_detection_model_leoxs" : "leoxs22/manga-panel-detector-yolo26n"
}
MODEL_CHECK_FILES = {
    "bubble_detector_model": "config.json",
    "manga_ocr_model": "config.json",
    "comic_panel_detection_model_leoxs": "manga_panel_detector_fp32.pt",
}
HUNSPELL_DIR = DATA_DIR / "hunspell"
HUNSPELL_FILES = {
    "es_AR.aff": "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries/es-AR/index.aff",
    "es_AR.dic": "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries/es-AR/index.dic",
}

def load_config(config):
    config_path = DATA_DIR / "config.json"
    load_fonts()
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            import json
            json.dump(config.get_data(), f, indent=4)

def load_fonts():
    """Register the bundled font files. Must run after QApplication exists."""
    for f in resource("assets/fonts").glob("*.ttf"):
        if QFontDatabase.addApplicationFont(str(f)) == -1:
            print(f"Could not load font {f.name}")
    if APP_FONT not in QFontDatabase.families():
        print(f"{APP_FONT} not found. Registered:", QFontDatabase.families())

def missing_hunspell():
    return [n for n in HUNSPELL_FILES if not (HUNSPELL_DIR / n).exists()]

def download_hunspell(progress=print):
    import requests
    HUNSPELL_DIR.mkdir(parents=True, exist_ok=True)
    for name in missing_hunspell():
        progress(f"Downloading {name}...")
        r = requests.get(HUNSPELL_FILES[name], timeout=60)
        r.raise_for_status()
        part = HUNSPELL_DIR / (name + ".part")
        part.write_bytes(r.content)
        part.replace(HUNSPELL_DIR / name)    
def dictionary_file(lang):
    return DICTS_DIR / f"{lang}.txt"

def model_path(name):
    return str(MODELS_DIR / name)

def missing_dictionaries():
    return [l for l in REQUIRED_DICT_LANGS if not dictionary_file(l).exists()]

def missing_models():
    return [n for n, f in MODEL_CHECK_FILES.items() if not (MODELS_DIR / n / f).exists()]


def needs_setup():
    return bool(missing_models()) or not JAMDICT_DB.exists() or missing_dictionaries() or missing_hunspell()

def download_models(progress=print):
    from huggingface_hub import snapshot_download

    for name, repo in MODELS.items():
        if (MODELS_DIR / name).exists():
            continue
        progress(f"Downloading {name}...")
        snapshot_download(repo_id=repo, local_dir=str(MODELS_DIR / name))

def download_jamdict(progress=print):
    if JAMDICT_DB.exists():
        return

    import gdown

    JAMDICT_DIR.mkdir(parents=True, exist_ok=True)
    temp_download = JAMDICT_DIR / "jamdict_download.tmp"
    partial_db = JAMDICT_DIR / "jamdict.db.part"

    try:
        progress("Downloading Japanese dictionary...")
        result = gdown.download(url=JAMDICT_URL, output=str(temp_download), quiet=False)
        if result is None or not temp_download.exists():
            raise RuntimeError("Dictionary download failed (check connection or Drive link permissions).")

        with open(temp_download, "rb") as f:
            header = f.read(100).lower()
        if b"<html" in header or b"<!doctype html" in header:
            raise RuntimeError("Downloaded an HTML page instead of the database. Check Drive link permissions.")

        progress("Decompressing dictionary...")
        try:
            # raw .xz
            with lzma.open(temp_download, "rb") as f_in, open(partial_db, "wb") as f_out:
                while chunk := f_in.read(1024 * 1024):
                    f_out.write(chunk)
        except lzma.LZMAError:
            # .tar.xz archive
            with tarfile.open(temp_download, "r:xz") as tar:
                member = next((m for m in tar.getmembers() if m.name.endswith("jamdict.db")), None)
                if member is None:
                    raise RuntimeError("jamdict.db not found inside the archive.")
                with tar.extractfile(member) as f_in, open(partial_db, "wb") as f_out:
                    while chunk := f_in.read(1024 * 1024):
                        f_out.write(chunk)

        partial_db.replace(JAMDICT_DB)   # only now does the file count as installed
    finally:
        for p in (temp_download, partial_db):
            if p.exists():
                p.unlink()


def download_dictionaries(progress=print):
        for lang in missing_dictionaries():
            build_dictionary(lang, progress)
        download_hunspell()
        """if not missing_dictionaries():
            return

        import shutil
        import gdown

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temp_dir = DATA_DIR / "dictionaries.part"
        shutil.rmtree(temp_dir, ignore_errors=True)      # clear leftovers from an interrupted run

        try:
            progress("Downloading dictionaries...")
            files = gdown.download_folder(url=DICT_URL, output=str(temp_dir),
                                        quiet=False, use_cookies=False)
            if not files or not (temp_dir / DICT_CHECK_FILE).exists():
                raise RuntimeError("Dictionary download failed (check connection, Drive "
                                "sharing permissions, or the expected file name).")

            shutil.rmtree(DICTS_DIR, ignore_errors=True)
            temp_dir.replace(DICTS_DIR)                  # appears only when complete
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)"""

def build_dictionary(lang, progress=print):
    """Convert pyspellchecker's word list into SymSpell format (word count per line)."""
    from spellchecker import SpellChecker

    progress(f"Preparing {lang} dictionary...")
    freq = dict(SpellChecker(language=lang).word_frequency.dictionary)

    
    DICTS_DIR.mkdir(parents=True, exist_ok=True)
    final = dictionary_file(lang)
    partial = final.with_name(final.name + ".part")
    try:
        with open(partial, "w", encoding="utf-8") as f:
            for word, count in freq.items():
                f.write(f"{word} {count}\n")
        partial.replace(final)                    # appears only when complete
    finally:
        if partial.exists():
            partial.unlink()