# data_structure/project_storage.py  (or a storage/ package)
import json, re, shutil
from pathlib import Path
import sys
from PIL import Image
from first_run import DATA_DIR
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def safe_name(name):
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name).strip(" .")
    return cleaned or "item"


class ProjectStorage:
    SHARED_DIR = "shared"
    TRANSLATION_MEMORY = SHARED_DIR + "/translation_memory.db"
    CHAPTERS_DIR = "chapters"
    
    def __init__(self):
        self.project_root = None

    def set_project_root(self, root):
        self.project_root = Path(root)

    # -------- generic methods --------
    def resolve(self, relative_path):
            return self.project_root / relative_path
    
    
    def write_json(self, relative_path, data, app_data=False):
        root = self.project_root if not app_data else DATA_DIR
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def read_json(self, relative_path, app_data=False):
        root = self.project_root if not app_data else DATA_DIR
        return json.loads((root / relative_path).read_text(encoding="utf-8"))

    def store_image(self, src_path, subfolder, new_name=None):
        """Copy an image into root/subfolder unchanged. Returns the relative path."""
        src = Path(src_path)
        ext = src.suffix.lower()
        if ext not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported image type: {src.name}")

        # make sure it really is an image before copying it into the project
        try:
            with Image.open(src) as img:
                img.verify()
        except Exception:
            raise ValueError(f"Not a readable image: {src.name}")

        dest_dir = Path(self.project_root) / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)

        stem = safe_name(new_name) if new_name else "photo"
        dest = dest_dir / f"{stem}{ext}"

        if new_name is None:                       # avoid overwriting an existing file
            n = 1
            while dest.exists():
                dest = dest_dir / f"{stem}_{n}{ext}"
                n += 1

        if src.resolve() != dest.resolve():        # nothing to copy if it is already there
            tmp = dest.with_name(dest.name + ".tmp")
            shutil.copyfile(src, tmp)              # copy only, never re-encode: coordinates stay valid
            tmp.replace(dest)
        print(dest.relative_to(self.project_root).as_posix())
        return dest.relative_to(self.project_root).as_posix()

    def _find_image_path(self, images_dir, name):
        images_dir_resolved = self.resolve(images_dir)
        candidates = sorted(
                    (path for path in images_dir_resolved.glob(f"{name}.*")
                     if path.suffix.lower() in IMAGE_EXTENSIONS),
                    key=lambda path: (
                        {".png": 0, ".jpg": 1}.get(path.suffix.lower(), 2),
                        path.suffix.lower(),
                    ),
                )
        print(f"searching for {name} in {images_dir} found {candidates}")
        return candidates[0] if candidates else images_dir / f"{name}.png"


    # -----------------App-wide methods----------------------
    def get_config_data(self):
        return self.read_json("config.json", app_data=True)

    def save_config_data(self, data):
        self.write_json("config.json", data, app_data=True)
    # -----------------Project-wide methods----------------------
    def create_structure(self):
        for sub in ( self.SHARED_DIR, self.CHAPTERS_DIR):
            (self.project_root / sub).mkdir(parents=True, exist_ok=True)

    def chapter_dir(self, chapter_id):
        return f"{self.CHAPTERS_DIR}/{chapter_id}"

    def delete_old_cover(self):
        for ext in IMAGE_EXTENSIONS:
            path = self.project_root / self.SHARED_DIR / f"cover{ext}"
            if path.exists():
                path.unlink()
    def get_cover_image_path(self):
            return self._find_image_path(Path(self.SHARED_DIR), "cover")

    def add_chapter(self, path):
            # Make dir in resolve_path(path)
            (self.resolve(path)).mkdir(parents=True, exist_ok=True)
    
    # ---- Chapter-wide methods ----
    def store_chapter_images(self, chapter_id, image_paths, start_at=1):
        pages = []
        for i, src in enumerate(image_paths, start=start_at):
            rel = self.store_image(src, f"{self.chapter_dir(chapter_id)}/images",
                                   new_name=f"page_{i:03d}")
            pages.append({"file": rel, "original_name": Path(src).name})
        return pages
    
    def get_image_path(self, chapter):
        images_dir = Path(self.CHAPTERS_DIR) / chapter.path / "images"
        
        return self._find_image_path(images_dir, "page_000")

    