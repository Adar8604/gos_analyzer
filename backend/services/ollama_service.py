import json
import requests


class OllamaClient:

    def __init__(
        self,
        model="qwen3:4b-q4_K_M",
        url="http://localhost:11434/api/generate",
        keep_alive="30m"
    ):
        self.model = model
        self.url = url
        self.keep_alive = keep_alive

        # Reuse the same HTTP connection
        self.session = requests.Session()

    def generate(
        self,
        prompt,
        temperature=0,
        think=False
    ):

        try:

            response = self.session.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": True,
                    "think": think,
                    "keep_alive": self.keep_alive
                },
                stream=True,
                timeout=300
            )

            response.raise_for_status()

            for line in response.iter_lines():

                if not line:
                    continue

                try:

                    data = json.loads(
                        line.decode("utf-8")
                    )

                    if "response" in data:
                        yield data["response"]

                except json.JSONDecodeError:
                    continue

        except requests.exceptions.RequestException as e:

            yield f"❌ Ollama Error: {str(e)}"