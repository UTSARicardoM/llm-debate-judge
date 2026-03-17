# src/ollama_client.py

import ollama


class OllamaClient:
    """
    Wrapper for Ollama chat generation.
    This class centralizes all model calls so the rest of the project
    remains modular and easy to maintain.
    """

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 700,
    ) -> str:
        """
        Send a prompt to an Ollama model and return the generated text.

        Parameters
        ----------
        model : str
            The Ollama model name 'llama3.1:8b'
        prompt : str
            The full prompt text sent to the model.
        temperature : float
            Controls randomness. Higher values produce more diverse outputs.
        max_tokens : int
            Maximum number of tokens to generate.

        Returns
        -------
        str
            The model generated text response.
        """

        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            # Safely extract response text
            return response.get("message", {}).get("content", "").strip()

        except Exception as e:
            # Graceful error handling (important for long experiment runs)
            print(f"[ERROR] Ollama generation failed: {e}")
            return "ERROR: generation failed"