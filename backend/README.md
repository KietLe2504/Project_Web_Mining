## Quick Start

1. Extract the KKBox `.7z` archives into `data/` at the repository root.
2. `pip install -r ../requirements.txt`
3. `python -m mining.train`
4. `python -m scripts.seed_db --kkbox ../data`
5. `uvicorn app.main:app --reload`
6. Start the frontend as before:
   ```bash
   cd frontend
   npm install
   npm run dev
