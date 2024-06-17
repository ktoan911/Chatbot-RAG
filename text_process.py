import spacy
nlp = spacy.load("en_core_web_sm")


def process_query(query: str) -> str:
    doc = nlp(query.lower().strip())

    filtered_text = [token.text for token in doc if not token.is_stop]

    result_query = " ".join(filtered_text)
    if len(result_query.replace(' ', '')) == 0:
        return query
    return result_query


query = "How much"
print(process_query(query))
