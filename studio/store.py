import os
from pathlib import Path

from PIL import Image

OUT_DIR = Path(os.environ.get("STUDIO_OUT_DIR", "posters")).resolve()


def save(poster_id: str, brief: str, image: Image.Image) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{poster_id}.png"
    image.save(path, format="PNG")
    (OUT_DIR / f"{poster_id}.txt").write_text(brief + "\n", encoding="utf-8")
    return path


def list_posters() -> list[dict]:
    if not OUT_DIR.exists():
        return []
    posters = []
    for path in sorted(OUT_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
        brief_path = path.with_suffix(".txt")
        brief = brief_path.read_text(encoding="utf-8").strip() if brief_path.exists() else ""
        posters.append({"id": path.stem, "brief": brief})
    return posters
