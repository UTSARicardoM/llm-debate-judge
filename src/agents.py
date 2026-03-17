# src/agents.py
class DebaterAgent:
    """
    A debater agent that generates responses using a prompt template and model.
    """

    def __init__(
        self,
        name: str,
        role: str,
        model: str,
        prompt_template: str,
        llm_client,
        temperature: float,
        max_tokens: int,
    ):
        self.name = name
        self.role = role
        self.model = model
        self.prompt_template = prompt_template
        self.llm_client = llm_client
        self.temperature = temperature
        self.max_tokens = max_tokens

    def respond(
        self,
        question: str,
        transcript: str,
        own_answer: str = "",
        opponent_answer: str = "",
    ) -> str:
        """
        Fill the prompt template and ask the model for a response.
        """

        prompt = self.prompt_template.format(
            question=question,
            transcript=transcript,
            own_answer=own_answer,
            opponent_answer=opponent_answer,
        )

        return self.llm_client.generate(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )


class JudgeAgent:
    """
    A judge agent that reviews the debate transcript and produces a verdict.
    """

    def __init__(
        self,
        model: str,
        prompt_template: str,
        llm_client,
        temperature: float,
        max_tokens: int,
    ):
        self.model = model
        self.prompt_template = prompt_template
        self.llm_client = llm_client
        self.temperature = temperature
        self.max_tokens = max_tokens

    def judge(self, question: str, transcript: str) -> str:
        """
        Fill the judge prompt and generate the verdict.
        """

        prompt = self.prompt_template.format(
            question=question,
            transcript=transcript,
        )

        return self.llm_client.generate(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )