import json
import argparse
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int, default=5)
args = parser.parse_args()

stories_path = Path("stories.json")

with open(stories_path, "r", encoding="utf-8") as f:
    stories = json.load(f)

start_index = len(stories) + 1

for i in range(args.count):
    story = {
        "id": f"sos-{start_index+i:04}",
        "title": f"Generated Story {start_index+i}",
        "status": "unused",
        "characters": ["Honey Bear", "Bootsie Belle"],
        "themes": ["generated"],
        "created_at": datetime.utcnow().isoformat(),
        "panels": [
            {"panel": 1, "scene": "Opening gag setup."},
            {"panel": 2, "scene": "Situation escalates."},
            {"panel": 3, "scene": "Bootsie Belle delivers commentary."},
            {"panel": 4, "scene": "Punchline ending."}
        ]
    }

    stories.append(story)

with open(stories_path, "w", encoding="utf-8") as f:
    json.dump(stories, f, indent=2)

print(f"Added {args.count} new stories.")
