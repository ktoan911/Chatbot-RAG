import os
from litellm import completion
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()


class TogetherLLM:
    def __init__(self,
                 model: str = "together_ai/meta-llama/Llama-3-70b-chat-hf",
                 together_api_key: str = os.environ["TOGETHER_API_KEY"],
                 temperature: float = 0.7,
                 max_tokens: int = 512):
        self.model = model
        self.together_api_key = together_api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    def call(
        self,
        messages: list,
        stream=True
    ):
        """Call to Together."""
        output = completion(
            messages=messages,
            model=self.model,
            together_api_key=self.together_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=stream
        )

        if stream:
            return output
        else:
            return output['choices'][0]['message']['content']
