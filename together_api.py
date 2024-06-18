import os
from litellm import completion

os.environ["TOGETHER_API_KEY"] = "22c9252460f6056c47ca857f02593e552a2da989b625c29da8bc54022a404af6"


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
    ):
        """Call to Together."""
        output = completion(
            messages=messages,
            model=self.model,
            together_api_key=self.together_api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        text = output['choices'][0]['message']['content']
        return text
