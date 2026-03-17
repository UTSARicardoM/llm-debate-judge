# src/data_conversion.py

import json
from datasets import load_dataset

# Load StrategyQA from Hugging Face
dataset = load_dataset("wics/strategy-qa", split="train")

# Convert to your required format
converted = [
    {
        "id": i + 1,
        "question": row["question"],
        "answer": "Yes" if row["answer"] else "No",
    }
    for i, row in enumerate(dataset)
]

# Limit to 150 questions for the assignment
converted = converted[:150]

# Save to your project data folder
with open(r"E:\DataScience\nlp_llm_judge\data\questions.json", "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2)

print(f"Saved {len(converted)} questions")