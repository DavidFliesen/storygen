import argparse
import json
import os
import random
from datetime import datetime
from pathlib import Path
from openai import OpenAI

from common import read_json, write_json, story_to_text, make_slug
from similarity_check import find_similar_story

client = OpenAI()

def load_tidbits():
    tidbits = []
    for file in [
        "data/tidbits-south-carolina.json",
        "data/tidbits-summerville.json",
        "data/tidbits-yorkies.json",
        "data/tidbits-tuxedo-cats.json",
    ]:
        items = read_json(file, [])
        for item in items:
            item["source_file"] = file
            tidbits.append(item)
    return tidbits

def load_context():
    return {
        "character_rules": read_json("data/character-rules.json", {}),
        "story_rules": read_json("data/story-rules.json", {}),
        "topic_pools": read_json("data/topic-pools.json", {}),
        "seasonal_topics": read_json("data/seasonal-topics.json", {})
    }

def existing_title_set(stories):
    return {s.get("title", "").strip().lower() for s in stories if s.get("title")}

def select_inspiration(tidbits, context):
    selected_tidbits = random.sample(tidbits, min(5, len(tidbits)))
    local = random.sample(context["topic_pools"].get("local_flavor", []), 2)
    pet = random.sample(context["topic_pools"].get("pet_behavior", []), 2)
    engine = random.sample(context["topic_pools"].get("comic_engines", []), 2)
    return selected_tidbits, local, pet, engine

def coerce_story(story):
    story.setdefault("title", "Untitled SoS Story")
    story.setdefault("themes", [])
    story.setdefault("characters", ["Honey Bear", "Bootsie Belle"])
    story.setdefault("panels", [])
    fixed_panels = []
    for i in range(1, 5):
        panel = story["panels"][i-1] if i-1 < len(story["panels"]) else {}
        fixed_panels.append({
            "panel": i,
            "scene": panel.get("scene", f"Panel {i} scene."),
            "dialogue": panel.get("dialogue", [])
        })
    story["panels"] = fixed_panels
    story["characters"] = ["Honey Bear", "Bootsie Belle"]
    return story

def generate_candidate(context, tidbits, existing_titles):
    selected_tidbits, local, pet, engine = select_inspiration(tidbits, context)

    prompt = f"""
You are the story editor for the Sisters of Summerville comic strip.

SERIES CANON:
{json.dumps(context["character_rules"], indent=2)}

STORY RULES:
{json.dumps(context["story_rules"], indent=2)}

RANDOMIZED INSPIRATION:
Local flavor: {local}
Pet behavior: {pet}
Comic engines: {engine}

RESEARCH TIDBITS:
{json.dumps(selected_tidbits, indent=2)}

EXISTING TITLES TO AVOID:
{sorted(list(existing_titles))[-80:]}

Write ONE original, fully developed 4-panel comic idea.

Hard requirements:
- Central characters must be Honey Bear and Bootsie Belle.
- Do not introduce generic substitute pets.
- Do not use the title Sweet Tea Showdown.
- Do not make the whole story about sweet tea unless the inspiration clearly demands it.
- Must be visual and funny, not just polite conversation.
- Each panel needs a scene description and short dialogue.
- Keep dialogue bubble-friendly, no long speeches.
- No ellipses.
- Return only valid JSON.

JSON shape:
{{
  "title": "",
  "themes": [],
  "characters": ["Honey Bear", "Bootsie Belle"],
  "inspiration_notes": [],
  "panels": [
    {{
      "panel": 1,
      "scene": "",
      "dialogue": [
        {{"character": "Honey Bear", "line": ""}},
        {{"character": "Bootsie Belle", "line": ""}}
      ]
    }},
    {{
      "panel": 2,
      "scene": "",
      "dialogue": []
    }},
    {{
      "panel": 3,
      "scene": "",
      "dialogue": []
    }},
    {{
      "panel": 4,
      "scene": "",
      "dialogue": []
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_STORY_MODEL", "gpt-4.1-mini"),
        temperature=0.95,
        messages=[
            {"role": "system", "content": "You write visual Southern comic-strip scripts with strong continuity discipline."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip()
    story = json.loads(content)
    return coerce_story(story)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--max-attempts", type=int, default=30)
    parser.add_argument("--similarity-threshold", type=float, default=0.80)
    args = parser.parse_args()

    stories = read_json("stories.json", [])
    context = load_context()
    tidbits = load_tidbits()
    titles = existing_title_set(stories)

    approved = []
    rejected = []

    attempts = 0

    while len(approved) < args.count and attempts < args.max_attempts:
        attempts += 1

        try:
            candidate = generate_candidate(context, tidbits, titles)
        except Exception as e:
            rejected.append({"reason": f"generation_error: {e}"})
            continue

        title = candidate.get("title", "").strip()
        title_key = title.lower()

        if not title or title_key in titles or title_key == "sweet tea showdown":
            rejected.append({"title": title, "reason": "duplicate_or_banned_title"})
            continue

        sim = find_similar_story(candidate, threshold=args.similarity_threshold)

        if sim["is_duplicate"]:
            rejected.append({
                "title": title,
                "reason": "too_similar",
                "similarity_score": sim["score"],
                "matches": sim["matches"][:3]
            })
            continue

        story_id = f"sos-{len(stories) + len(approved) + 1:04}"
        candidate["id"] = story_id
        candidate["slug"] = make_slug(title)
        candidate["status"] = "unused"
        candidate["created_at"] = datetime.utcnow().isoformat()
        candidate["similarity_check"] = {
            "score": sim["score"],
            "nearest_matches": sim["matches"][:3]
        }

        approved.append(candidate)
        titles.add(title_key)

    stories.extend(approved)
    write_json("stories.json", stories)
    write_json("data/last-generation-report.json", {
        "created_at": datetime.utcnow().isoformat(),
        "requested_count": args.count,
        "approved_count": len(approved),
        "attempts": attempts,
        "rejected": rejected[-20:]
    })

    print(f"Approved {len(approved)} stories after {attempts} attempts.")
    if len(approved) < args.count:
        print("Warning: fewer stories approved than requested. Check data/last-generation-report.json.")

if __name__ == "__main__":
    main()
