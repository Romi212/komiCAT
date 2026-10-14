# data_structure/project_storage.py  (or a storage/ package)
import json, re, shutil
from pathlib import Path
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def safe_name(name):
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", name).strip(" .")
    return cleaned or "item"


class ProjectStorage:
    SHARED_DIR = "shared"
    CHAPTERS_DIR = "chapters"

    def __init__(self, root):
        self.root = Path(root)

    # ---- layout: the only place that knows these folder names ----
    def create_structure(self):
        for sub in ( self.SHARED_DIR, self.CHAPTERS_DIR):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def chapter_dir(self, chapter_id):
        return f"{self.CHAPTERS_DIR}/{chapter_id}"

    def resolve(self, relative_path):
        return self.root / relative_path

    # ---- json ----
    def write_json(self, relative_path, data):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def read_json(self, relative_path):
        return json.loads((self.root / relative_path).read_text(encoding="utf-8"))

    # ---- images ----
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

        dest_dir = Path(self.root) / subfolder
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
        print(dest.relative_to(self.root).as_posix())
        return dest.relative_to(self.root).as_posix()

    def store_chapter_images(self, chapter_id, image_paths, start_at=1):
        pages = []
        for i, src in enumerate(image_paths, start=start_at):
            rel = self.store_image(src, f"{self.chapter_dir(chapter_id)}/images",
                                   new_name=f"page_{i:03d}")
            pages.append({"file": rel, "original_name": Path(src).name})
        return pages

    def get_image_path(self, chapter):
        return Path(self.CHAPTERS_DIR) / chapter.path / "images" / "page_000.png"
    def add_chapter(self, path):
        # Make dir in resolve_path(path)
        (self.resolve(path)).mkdir(parents=True, exist_ok=True)