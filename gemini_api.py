import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


class Gemini_LLM:
    def __init__(self,
                 model: str = os.environ["LLM_MODEL"],
                 temperature: float = 0.7,
                 instructions: str = None,
                 save_history: bool = False):
        
        if instructions is not None:
            self.model = genai.GenerativeModel(model, system_instruction=[instructions],generation_config={"temperature": temperature})
        else:
            self.model = genai.GenerativeModel(model, generation_config={"temperature": temperature})

        print('test')

        self.save_history = save_history

        if self.save_history:
            self.chat = self.model.start_chat()
    
    def get_chat(self):
        return self.chat

    def call(
        self,
        prompt: str,
        stream: bool = False
    ):
        if self.save_history and self.chat:
            response = self.chat.send_message(prompt, stream=stream)
        else:
            response = self.model.generate_content(prompt, stream = stream)
        
        return response.text
