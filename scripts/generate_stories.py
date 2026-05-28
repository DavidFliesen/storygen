import json
import os
import random
from pathlib import Path
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

stories_path = Path("stories.json")
captions_path = Path("captions.json")

with open(stories_path, "r", encoding="utf-8") as f:
    stories = json.load(f)

with open(captions_path, "r", encoding="utf-8") as f:
    captions = json.load(f)

with open("data/character-rules.json", "r", encoding="utf-8") as f:
    character_rules = json.load(f)

with open("data/story-rules.json", "r", encoding="utf-8") as f:
    story_rules = json.load(f)

tidbit_files = [
    "data/tidbits-south-carolina.json",
    "data/tidbits-summerville.json",
    "data/tidbits-yorkies.json",
    "data/tidbits-tuxedo-cats.json"
]

tidbits = []

for file in tidbit_files:
    if Path(file).exists():
        with open(file, "r", encoding="utf-8") as f:
            tidbits.extend(json.load(f))

recent_captions = []

for c in captions[-25:]:
    if isinstance(c, dict):
        recent_captions.append(c.get("caption", ""))

def generate_story(index):
    selected_tidbits = random.sample(tidbits, min(3, len(tidbits)))

    tidbit_text = "\n".join([
        f"- {t.get('fact', '')}" for t in selected_tidbits
    ])

    recent_text = "\n".join(recent_captions)

    prompt = f"""
Write a Sisters of Summerville comic strip.

Use:
- Southern humor
- Honey Bear and Bootsie Belle
- Summerville flavor
- 4 clear comic panels

Avoid repeating these stories:
{recent_text}

Research tidbits:
{tidbit_text}

Return ONLY valid JSON.

{{
  "title": "",
  "themes": [],
  "panels": [
    {{
      "panel": 1,
      "scene": "",
      "dialogue": []
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.9,
        messages=[
            {"role":"system","content":"You write Southern comic strips."},
            {"role":"user","content":prompt}
        ]
    )

    content = response.choices[0].message.content

    story_json = json.loads(content)

    return {
        "id": f"sos-{len(stories)+index+1:04}",
        "status": "unused",
        "created_at": datetime.utcnow().isoformat(),
        **story_json
    }

new_stories = []

for i in range(5):
    try:
        story = generate_story(i)
        stories.append(story)
        new_stories.append(story)
    except Exception as e:
        print(e)

with open(stories_path, "w", encoding="utf-8") as f:
    json.dump(stories, f, indent=2)

print(f"Generated {len(new_stories)} stories.")
