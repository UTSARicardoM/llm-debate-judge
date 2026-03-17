#ui_app.py

import streamlit as st

from config_loader import load_config
from ollama_client import OllamaClient
from agents import DebaterAgent, JudgeAgent
from debate_orchestrator import DebateOrchestrator


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


st.set_page_config(page_title="LLM Debate + Judge", layout="wide")

st.title("LLM Debate + Judge Pipeline")
st.write("Enter a question and watch two agents debate before the judge makes a decision.")

question = st.text_area("Question", height=120)

if st.button("Run Debate"):
    config = load_config()
    llm_client = OllamaClient()

    debater_a_prompt = load_prompt("prompts/debater_a.txt")
    debater_b_prompt = load_prompt("prompts/debater_b.txt")
    judge_prompt = load_prompt("prompts/judge.txt")

    debater_a = DebaterAgent(
        name="Debater A",
        role="Proponent",
        model=config["models"]["debater_a"],
        prompt_template=debater_a_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_debater"],
        max_tokens=config["generation"]["max_tokens"],
    )

    debater_b = DebaterAgent(
        name="Debater B",
        role="Opponent",
        model=config["models"]["debater_b"],
        prompt_template=debater_b_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_debater"],
        max_tokens=config["generation"]["max_tokens"],
    )

    judge = JudgeAgent(
        model=config["models"]["judge"],
        prompt_template=judge_prompt,
        llm_client=llm_client,
        temperature=config["generation"]["temperature_judge"],
        max_tokens=config["generation"]["max_tokens"],
    )

    orchestrator = DebateOrchestrator(
        debater_a=debater_a,
        debater_b=debater_b,
        judge=judge,
        min_rounds=config["debate"]["min_rounds"],
        max_rounds=config["debate"]["max_rounds"],
        agreement_threshold=config["debate"]["early_stop_consecutive_agreement"],
    )

    sample = {
        "id": 0,
        "question": question,
        "answer": "N/A",
    }

    result = orchestrator.run_debate(sample)

    st.subheader("Initial Positions")
    st.text(result["initial_a"])
    st.text(result["initial_b"])

    st.subheader("Debate Rounds")
    for round_item in result["rounds"]:
        st.markdown(f"### Round {round_item['round']}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Debater A**")
            st.text(round_item["debater_a"])

        with col2:
            st.markdown("**Debater B**")
            st.text(round_item["debater_b"])

    st.subheader("Judge Verdict")
    st.text(result["judge_output"])