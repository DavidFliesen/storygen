import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(".")
DATA_DIR = ROOT / "data"
VECTOR_DIR = ROOT / "vector_store"

def read_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False)

def story_to_text(story: Dict[str, Any]) -> str:
    parts = [
        story.get("title", ""),
        " ".join(story.get("themes", [])) if isinstance(story.get("themes"), list) else clean_text(story.get("themes", "")),
    ]
    for panel in story.get("panels", []):
        parts.append(clean_text(panel.get("scene", "")))
        dialogue = panel.get("dialogue", [])
        if isinstance(dialogue, list):
            for d in dialogue:
                if isinstance(d, dict):
                    parts.append(clean_text(d.get("character", "")))
                    parts.append(clean_text(d.get("line", "")))
                else:
                    parts.append(clean_text(d))
        else:
            parts.append(clean_text(dialogue))
    return " ".join([p for p in parts if p]).strip()

def caption_to_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return " ".join([
            clean_text(item.get("title", "")),
            clean_text(item.get("caption", "")),
            clean_text(item.get("description", "")),
            clean_text(item.get("text", "")),
        ]).strip()
    return clean_text(item)

def make_slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or "story"
