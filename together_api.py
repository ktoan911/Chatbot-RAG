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
        self.MAX_INPUT_LENGTH = os.environ["MAX_INPUT_TOKEN"]

    # def get_input_length(self, messages: list) -> int:
    #     """Calculate the total length of input message contents."""
    #     return sum(len(message['content']) for message in messages if 'content' in message)

    def call(
        self,
        messages: list,
        stream=True
    ):
        # input_length = self.get_input_length(messages)
        # while input_length > int(self.MAX_INPUT_LENGTH):
        #     if len(messages) > 3:
        #         messages = messages[:1] + messages[3:]
        #     else:
        #         raise ValueError(
        #             f"Input exceeds maximum length of {self.MAX_INPUT_LENGTH} tokens.")
        """Call to Together."""
        check_input = False

        while not check_input:
            try:
                output = completion(
                    messages=messages,
                    model=self.model,
                    together_api_key=self.together_api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=stream
                )
                check_input = True
            except:
                if len(messages) > 3:
                    messages = messages[:1] + messages[3:]
                else:
                    raise ValueError(
                        f"Input exceeds maximum length of {self.MAX_INPUT_LENGTH} tokens.")

        if stream:
            return output
        else:
            return output['choices'][0]['message']['content']
