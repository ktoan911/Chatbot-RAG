from text_process import process_query
import model
import VectorSearch
import torch

messages = [
    {"role": "system", "content": "You are a phone sales representative in a mobile phone store. Your task is to help customers find the best phone that suits their needs."}
    # {"role": "user", "content": "Hello, I'm looking for a phone with a great camera. Can you suggest a few models?"},
    # {"role": "assistant", "content": "Hello! For great camera quality, I would recommend the following models: iPhone 14 Pro, Samsung Galaxy S23 Ultra, and Google Pixel 7 Pro. These phones all have high-quality cameras and advanced photography features. Do you have any other specific requirements, such as battery life or storage capacity?"}
]
