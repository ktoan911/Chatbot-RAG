from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig, Part

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from common.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class LLM:
    def __init__(
        self,
        model: str = os.environ["LLM_MODEL"],
        temperature: float = 0.7,
        top_p: float = 0.5,
        top_k: int = 20,
        instructions: str = None,
        history: list[dict] = None,
    ):
        self.keys = os.environ["API_KEY"].split(",")
        self.api_key_index = 0

        self.client = genai.Client(api_key=self.keys[0])
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.instructions = instructions
        self.num_try = 3

    def get_chat(self):
        return self.chat

    def convert_openai_style_messages(self, messages):
        return [Part(text=msg["content"]) for msg in messages]

    def get_message(
        self,
        prompt: str,
        stream: bool = False,
    ) -> str | None:
        while self.num_try > 0:
            try:
                if not stream:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=GenerateContentConfig(
                            temperature=self.temperature,
                            system_instruction=self.instructions,
                            candidate_count=1,
                            top_p=self.top_p,
                            top_k=self.top_k,
                            seed=42,
                            max_output_tokens=2048,
                        ),
                    )
                    return response.text
                else:
                    for chunk in self.client.models.generate_content_stream(
                        model=self.model,
                        contents=prompt,
                        config=GenerateContentConfig(
                            temperature=self.temperature,
                            system_instruction=self.instructions,
                            candidate_count=1,
                            top_p=self.top_p,
                            top_k=self.top_k,
                            seed=42,
                            max_output_tokens=2048,
                        ),
                    ):
                        print(chunk.text)
                    return
            except Exception as e:
                logger.info(
                    f"API key {self.keys[self.api_key_index]} with error {e} failed. Trying next key."
                )
                self.api_key_index += 1
                if self.api_key_index >= len(self.keys):
                    self.api_key_index = 0
                    self.num_try -= 1
                self.client = genai.Client(api_key=self.keys[self.api_key_index])

        return "Internet error. Please check your connection."

    def function_calling(self):
        pass
