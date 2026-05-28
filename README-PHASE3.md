# SoS Story Forge Phase 3

This package upgrades the project from simple prompt generation to a more structured story engine.

## What this adds

- Three manual GitHub Actions:
  - Build or Refresh SoS Research Tidbits
  - Rebuild SoS FAISS Story Memory
  - Generate SoS Story Ideas
- FAISS vector memory for duplicate detection
- OpenAI embeddings for captions and used stories
- Stronger character canon
- Topic diversity pools
- Better story generation rules
- Last generation report

## Upload instructions

Add these files on top of your existing repo.

Keep your existing:
- index.html
- app.js
- style.css
- stories.json
- captions.json

Replace or add:
- requirements.txt
- scripts/
- data/
- .github/workflows/

## Run order

1. Run: Build or Refresh SoS Research Tidbits
   - You only need this rarely.

2. Run: Rebuild SoS FAISS Story Memory
   - Run after updating captions.json or marking stories as used.

3. Run: Generate SoS Story Ideas
   - Run whenever you want new unused story scripts.

## Required GitHub secret

Add:
OPENAI_API_KEY

Repository Settings → Secrets and variables → Actions → New repository secret

## Note

The vector store files are committed into:
vector_store/stories.faiss
vector_store/metadata.json

That lets generation use memory without rebuilding it every time.
