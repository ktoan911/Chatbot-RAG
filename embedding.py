from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


# ngoc
# vvbnESrLE2gcbkmW
# mongodb+srv://ngoc:vvbnESrLE2gcbkmW@cluster0.jps061j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

def get_embedding(text: str) -> list[float]:
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []

    embedding = model.encode(text.replace('###','').replace('\n',''))

    return embedding.tolist()