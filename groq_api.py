from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key = os.environ["GROQ_API_KEY"])


class GroqLLM:
    def __init__(self,
                 model: str = os.environ["LLM_MODEL"],
                 temperature: float = 0.7,
                 max_tokens: int = 1024):
        
        self.model = model
        self.temperature = temperature  
        self.max_tokens = max_tokens
        
        
    def call(
        self,
        messages: list[dict],
        stream: bool = False
    ):
        completion = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=1,
                    stream=stream,
                    stop=None,
                )
        if not stream:
            return completion.choices[0].message.content
        else:
            return completion
            