import json
import os
from pathlib import Path
from openai import OpenAI
from common import read_json, write_json

client = OpenAI()

RESEARCH_TASKS = {
    "data/tidbits-south-carolina.json": "South Carolina history, culture, Lowcountry life, foodways, weather, landscapes, and family-friendly comic story hooks.",
    "data/tidbits-summerville.json": "Summerville South Carolina history, culture, Flowertown identity, porch life, azaleas, sweet tea, local flavor, and family-friendly comic story hooks.",
    "data/tidbits-yorkies.json": "Yorkshire Terrier traits, behavior, vocal habits, protective instincts, food behavior, and family-friendly comic story hooks.",
    "data/tidbits-tuxedo-cats.json": "Black and white tuxedo cat traits, common cat behaviors, independence, cleverness, dignity, and family-friendly comic story hooks."
}

def generate_tidbits(topic_prompt, existing):
    prompt = f"""
Create 20 evergreen research tidbits for Sisters of Summerville story generation.

Topic:
{topic_prompt}

Existing tidbits:
{json.dumps(existing, indent=2)}

Rules:
- Keep facts evergreen and broadly useful.
- Do not claim niche facts unless widely accepted.
- Include a story_angle that can inspire a 4-panel comic.
- Avoid political content.
- Return only valid JSON list.
- Each item must include id, topic, fact, story_angle.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.6,
        messages=[
            {"role": "system", "content": "You create reliable evergreen research notes for a comic story engine."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)

def main():
    for path, prompt in RESEARCH_TASKS.items():
        existing = read_json(path, [])
        generated = generate_tidbits(prompt, existing)
        write_json(path, generated)
        print(f"Wrote {len(generated)} tidbits to {path}")

if __name__ == "__main__":
    main()
