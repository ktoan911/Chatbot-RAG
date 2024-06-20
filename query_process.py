import spacy
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

model = SentenceTransformer(os.environ['EMBEDDING_MODEL'])
nlp = spacy.load("en_core_web_sm")


def process_query(query):
    # Loại bỏ stop words và chuyển câu truy vấn về dạng lowercase
    doc = nlp(query.lower().strip())

    filtered_text = [token.text for token in doc if not token.is_stop]

    result_query = " ".join(filtered_text)
    if len(result_query.replace(' ', '')) == 0:
        return query, False
    return result_query, True


# Hàm lấy embedding của câu truy vấn
def get_embedding(text: str) -> list[float]:
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []

    embedding = model.encode(text.replace('###', '').replace('\n', ''))

    return embedding.tolist()


def classification_query(query, llm):
    messages = [{'role': 'system', 'content': 'You are a question categorizer, if the question is related to information about your store products then answer "1", else answer "0".'},
                {"role": "user", "content": "I want to buy a phone with a good camera."},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "I want to buy a phone with a good camera and long battery life."},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "I want to buy the newest phone, but I don't want to spend too much money."},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "what is your name."},
                {"role": "assistant", "content": '0'},
                {"role": "user", "content": "Do you think I should buy an iPhone or an Android phone?"},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "I want to know information about Samsung F13."},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "More"},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "Stop"},
                {"role": "assistant", "content": "0"},
                {"role": "user", "content": "bye"},
                {"role": "assistant", "content": "0"},
                {"role": "user", "content": "What is the newest phone in the world right now."},
                {"role": "assistant", "content": "0"},
                {'role': 'user', 'content': query}
                ]
    response = llm.call(messages, stream=False)
    if (response == "0"):
        return False  # không cần truy xuất thông tin database
    else:
        return True  # cần truy xuất thông tin database


# print(classification_query("stop",
#       llm=together_api.TogetherLLM()))
