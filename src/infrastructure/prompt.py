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
