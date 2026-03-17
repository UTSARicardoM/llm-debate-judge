# src/baselines.py

from collections import Counter


def extract_final_answer(text: str) -> str:
    """
    Extract the final answer from the model output.
    """

    for line in text.splitlines():
        if line.lower().startswith("final answer:"):
            return line.split(":", 1)[1].strip()

    return "Unknown"


def run_direct_qa(sample, llm_client, model, prompt_template, temperature, max_tokens):
    """
    Direct QA baseline:
    Ask one model to answer the question directly without debate.
    """

    prompt = prompt_template.format(question=sample["question"])

    output = llm_client.generate(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return {
        "question_id": sample["id"],
        "question": sample["question"],
        "ground_truth": sample["answer"],
        "output": output,
        "predicted_answer": extract_final_answer(output),
    }


def run_self_consistency(
    sample,
    llm_client,
    model,
    prompt_template,
    temperature,
    max_tokens,
    num_samples,
):
    """
    Self-consistency baseline:
    Sample multiple answers and take the majority vote.
    """

    outputs = []
    answers = []

    for _ in range(num_samples):
        prompt = prompt_template.format(question=sample["question"])

        output = llm_client.generate(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        outputs.append(output)
        answers.append(extract_final_answer(output))

    majority_answer = Counter(answers).most_common(1)[0][0]

    return {
        "question_id": sample["id"],
        "question": sample["question"],
        "ground_truth": sample["answer"],
        "outputs": outputs,
        "sampled_answers": answers,
        "predicted_answer": majority_answer,
    }