from __future__ import annotations

INSTRUCTIONS = """Bạn là một nhân viên bán hàng điện thoại trong cửa
                hàng điện thoại di động Hedspi. Nhiệm vụ của bạn là giúp
                khách hàng tìm chiếc điện thoại tốt nhất phù hợp với nhu cầu của họ."""


SUMMARY_CHAT_HISTORY_PROMPT = """Based on the user's conversation history and their latest query that may
                                refer to context in the chat history, construct an independent query in Vietnamese that can be understood without the chat
                                history. Do not answer this query, just reconstruct it if necessary, and if there is not enough information to construct a new question,
                                keep the original question unchanged"""


def model_instructions() -> str:
    return INSTRUCTIONS


def model_summary_chat_history_prompt() -> str:
    return SUMMARY_CHAT_HISTORY_PROMPT



def extract_entity_relationship_prompt(text: str) -> str:
    return (
        "Extract entities (nodes) and their relationships (edges) from the text below."
        "Entities and relationships MUST be in Vietnamese\n"
        # f"Only use RelationshipType 'giảm giá' for both 'giảm giá' and 'giảm giá qua' "
        # f"Entities only in ['Công ty tài chính']"
        "Follow this format:\n\n"
        "Entities:\n"
        "- {{Entity}}: {{Type}}\n\n"
        "Relationships:\n"
        "- ({{Entity1}}, {{RelationshipType}}, {{Entity2}})\n\n"
        f'Text:\n"{text}"\n\n'
        "Output:\nEntities:\n- {{Entity}}: {{Type}}\n...\n\n"
        "Relationships:\n- ({{Entity1}}, {{RelationshipType}}, {{Entity2}})\n"
    ).format(text=text)
