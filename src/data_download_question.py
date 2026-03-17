# src/data_download_questiony

import json
from urllib.request import urlopen

# Plain JSON file hosted on Hugging Face dataset repo
SOURCE_URL = "https://huggingface.co/datasets/ChilleD/StrategyQA/resolve/main/train.json"
OUTPUT_PATH = r"E:\DataScience\nlp_llm_judge\data\questions.json"
NUM_QUESTIONS = 150

with urlopen(SOURCE_URL) as response:
    raw_data = json.load(response)

converted = [
    {
        "id": i + 1,
        "question": row["question"],
        "answer": "Yes" if row["answer"] else "No",
    }
    for i, row in enumerate(raw_data[:NUM_QUESTIONS])
]

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2)

print(f"Saved {len(converted)} questions to {OUTPUT_PATH}")