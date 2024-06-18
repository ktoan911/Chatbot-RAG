import spacy
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
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
