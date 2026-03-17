# src/run_experiments.py

import json
from pathlib import Path

from tqdm import tqdm

from src.config_loader import load_config
from src.utils import ensure_directory, save_json, timestamp_string
from src.ollama_client import OllamaClient
from src.agents import DebaterAgent, JudgeAgent
from src.debate_orchestrator import DebateOrchestrator
from src.baselines import run_direct_qa, run_self_consistency
from src.evaluator import build_metrics_table

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_prompt(path: Path) -> str:
    """
    Load a prompt template from disk and return it as a string.

    Parameters
    ----------
    path : Path
        Full path to the prompt file.

    Returns
    -------
    str
        The contents of the prompt file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def main():
    """
    Main experiment pipeline.

    Steps
    -----
    1. Load configuration.
    2. Create required output directories.
    3. Load dataset and prompt templates.
    4. Initialize the Ollama client and all agents.
    5. Run debate, direct QA, and self-consistency experiments.
    6. Save debate logs and summary metrics.
    """

    # ---------------------------------------------------------
    # Load configuration from config.yaml in the project root.
    # ---------------------------------------------------------
    config_path = PROJECT_ROOT / "config.yaml"
    config = load_config(str(config_path))

    # ---------------------------------------------------------
    # Resolve important paths from the config file.
    # ---------------------------------------------------------
    logging_dir = PROJECT_ROOT / config["logging"]["save_dir"]
    results_dir = PROJECT_ROOT / "results"
    figures_dir = results_dir / "figures"
    dataset_path = PROJECT_ROOT / config["experiments"]["dataset_path"]
    metrics_path = PROJECT_ROOT / config["results"]["metrics_path"]

    # ---------------------------------------------------------
    # Ensure required directories exist.
    # ---------------------------------------------------------
    ensure_directory(str(logging_dir))
    ensure_directory(str(results_dir))
    ensure_directory(str(figures_dir))

    # ---------------------------------------------------------
    # Load dataset from JSON.
    # ---------------------------------------------------------
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    # Limit the number of samples according to config.
    dataset = dataset[: config["experiments"]["num_samples"]]

    # ---------------------------------------------------------
    # Load all prompt templates.
    # ---------------------------------------------------------
    debater_a_prompt = load_prompt(PROJECT_ROOT / "prompts" / "debater_a.txt")
    debater_b_prompt = load_prompt(PROJECT_ROOT / "prompts" / "debater_b.txt")
    judge_prompt = load_prompt(PROJECT_ROOT / "prompts" / "judge.txt")
    direct_prompt = load_prompt(PROJECT_ROOT / "prompts" / "direct_qa.txt")
    self_consistency_prompt = load_prompt(PROJECT_ROOT / "prompts" / "self_consistency.txt")

    # ---------------------------------------------------------
    # Initialize shared Ollama client.
    # ---------------------------------------------------------
    llm_client = OllamaClient()

    # ---------------------------------------------------------
    # Create Debater A.
    # ---------------------------------------------------------
    debater_a = DebaterAgent(
        name="Debater A",
        role="Proponent",
        model=config["models"]["debater_a"],
        prompt_template=debater_a_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_debater"],
        max_tokens=config["generation"]["max_tokens"],
    )

    # ---------------------------------------------------------
    # Create Debater B.
    # ---------------------------------------------------------
    debater_b = DebaterAgent(
        name="Debater B",
        role="Opponent",
        model=config["models"]["debater_b"],
        prompt_template=debater_b_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_debater"],
        max_tokens=config["generation"]["max_tokens"],
    )

    # ---------------------------------------------------------
    # Create Judge agent.
    # ---------------------------------------------------------
    judge = JudgeAgent(
        model=config["models"]["judge"],
        prompt_template=judge_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_judge"],
        max_tokens=config["generation"]["max_tokens"],
    )

    # ---------------------------------------------------------
    # Create the debate orchestrator.
    # ---------------------------------------------------------
    orchestrator = DebateOrchestrator(
        debater_a=debater_a,
        debater_b=debater_b,
        judge=judge,
        min_rounds=config["debate"]["min_rounds"],
        max_rounds=config["debate"]["max_rounds"],
        agreement_threshold=config["debate"]["early_stop_consecutive_agreement"],
    )

    # ---------------------------------------------------------
    # Lists to store outputs from each method.
    # ---------------------------------------------------------
    debate_results = []
    direct_results = []
    self_consistency_results = []

    # ---------------------------------------------------------
    # Run all experiments sample by sample.
    # ---------------------------------------------------------
    for sample in tqdm(dataset, desc="Running experiments"):
        # -------------------------
        # Debate + Judge pipeline
        # -------------------------
        debate_output = orchestrator.run_debate(sample)
        debate_results.append(debate_output)

        # Save full debate transcript and metadata as JSON.
        debate_log_path = logging_dir / f"debate_{sample['id']}_{timestamp_string()}.json"
        save_json(debate_output, str(debate_log_path))

        # -------------------------
        # Direct QA baseline
        # -------------------------
        direct_output = run_direct_qa(
            sample=sample,
            llm_client=llm_client,
            model=config["models"]["baseline"],
            prompt_template=direct_prompt,
            temperature=config["generation"]["temperature_baseline"],
            max_tokens=config["generation"]["max_tokens"],
        )
        direct_results.append(direct_output)

        # -------------------------
        # Self-consistency baseline
        # -------------------------
        self_consistency_output = run_self_consistency(
            sample=sample,
            llm_client=llm_client,
            model=config["models"]["baseline"],
            prompt_template=self_consistency_prompt,
            temperature=config["generation"]["temperature_baseline"],
            max_tokens=config["generation"]["max_tokens"],
            num_samples=config["experiments"]["self_consistency_samples"],
        )
        self_consistency_results.append(self_consistency_output)

    # ---------------------------------------------------------
    # Build metrics table comparing all methods.
    # ---------------------------------------------------------
    metrics_df = build_metrics_table(
        debate_results=debate_results,
        direct_results=direct_results,
        self_consistency_results=self_consistency_results,
    )

    # Save metrics to CSV.
    metrics_df.to_csv(metrics_path, index=False)

    # Print metrics to terminal.
    print("\nExperiment Summary:")
    print(metrics_df)


if __name__ == "__main__":
    main()