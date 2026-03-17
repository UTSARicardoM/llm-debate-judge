# src/debate_orchestrator.py
class DebateOrchestrator:
    """
    Runs the full debate pipeline:
    1. Initial independent answers
    2. Multi-round debate
    3. Judge verdict
    """

    def __init__(
        self,
        debater_a,
        debater_b,
        judge,
        min_rounds: int,
        max_rounds: int,
        agreement_threshold: int,
    ):
        self.debater_a = debater_a
        self.debater_b = debater_b
        self.judge = judge
        self.min_rounds = min_rounds
        self.max_rounds = max_rounds
        self.agreement_threshold = agreement_threshold

    @staticmethod 
    def extract_final_answer(text: str) -> str:
        """
        Extract the final answer by searching for a line that starts with
        'Final Answer:'.
        """

        # Normalize line by line 1st
        for line in text.splitlines():
            clean_line = line.strip().lower()

            # Look for any line mentioning final answer
            if "final answer" in clean_line or clean_line.startswith("answer:"):
                if "yes" in clean_line:
                    return "Yes"
                if "no" in clean_line:
                    return "No"

        # Fallback,search the full text if line arsing fails
        full_text = text.strip().lower()

        if "final answer" in full_text:
            if "yes" in full_text:
                return "Yes"
            if "no" in full_text:
                return "No"

        return "Unknown"

    def run_debate(self, sample: dict) -> dict:
        """
        Run the full debate for one question and return all intermediate results.
        """

        question = sample["question"]
        ground_truth = sample["answer"]

        transcript_parts = []
        rounds = []
        agreement_streak = 0

        # -------------------------
        # Phase 1: Initialization
        # -------------------------
        initial_a = self.debater_a.respond(
            question=question,
            transcript="No previous transcript.",
        )

        initial_b = self.debater_b.respond(
            question=question,
            transcript="No previous transcript.",
        )

        answer_a = self.extract_final_answer(initial_a)
        answer_b = self.extract_final_answer(initial_b)

        transcript_parts.append(f"Initial Position - Debater A:\n{initial_a}")
        transcript_parts.append(f"Initial Position - Debater B:\n{initial_b}")

        # If both debaters already agree, treat it as consensus.
        if answer_a.lower() == answer_b.lower() and answer_a != "Unknown":
            full_transcript = "\n\n".join(transcript_parts)

            judge_output = self.judge.judge(
                question=question,
                transcript=full_transcript,
            )

            return {
                "question_id": sample["id"],
                "question": question,
                "ground_truth": ground_truth,
                "initial_a": initial_a,
                "initial_b": initial_b,
                "rounds": [],
                "consensus_reached": True,
                "judge_output": judge_output,
                "judge_answer": self.extract_final_answer(judge_output),
                "full_transcript": full_transcript,
            }

        # -------------------------
        # Phase 2: Debate rounds
        # -------------------------
        for round_number in range(1, self.max_rounds + 1):
            prior_transcript = "\n\n".join(transcript_parts)

            response_a = self.debater_a.respond(
                question=question,
                transcript=prior_transcript,
                own_answer=answer_a,
                opponent_answer=answer_b,
            )
            answer_a = self.extract_final_answer(response_a)
            transcript_parts.append(f"Round {round_number} - Debater A:\n{response_a}")

            updated_transcript = "\n\n".join(transcript_parts)

            response_b = self.debater_b.respond(
                question=question,
                transcript=updated_transcript,
                own_answer=answer_b,
                opponent_answer=answer_a,
            )
            answer_b = self.extract_final_answer(response_b)
            transcript_parts.append(f"Round {round_number} - Debater B:\n{response_b}")

            rounds.append(
                {
                    "round": round_number,
                    "debater_a": response_a,
                    "debater_b": response_b,
                    "answer_a": answer_a,
                    "answer_b": answer_b,
                }
            )

            if answer_a.lower() == answer_b.lower() and answer_a != "Unknown":
                agreement_streak += 1
            else:
                agreement_streak = 0

            if round_number >= self.min_rounds and agreement_streak >= self.agreement_threshold:
                break

        # -------------------------
        # Phase 3: Judge
        # -------------------------
        full_transcript = "\n\n".join(transcript_parts)

        judge_output = self.judge.judge(
            question=question,
            transcript=full_transcript,
        )

        judge_answer = self.extract_final_answer(judge_output)

        return {
            "question_id": sample["id"],
            "question": question,
            "ground_truth": ground_truth,
            "initial_a": initial_a,
            "initial_b": initial_b,
            "rounds": rounds,
            "consensus_reached": False,
            "judge_output": judge_output,
            "judge_answer": judge_answer,
            "full_transcript": full_transcript,
        }