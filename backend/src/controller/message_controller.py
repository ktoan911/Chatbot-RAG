from __future__ import annotations

import service.LLM.PROMPT as p
from common.text import TextProcessor
from service.LLM.llm import LLM
from service.RAG import RAG


class MesageController:
    def __init__(self, num_history: int = 10):
        self.search = RAG()
        self.text_processor = TextProcessor()
        self.llm = LLM(instructions=p.model_instructions())
        self.llm_instructions = LLM(instructions=p.model_summary_chat_history_prompt())
        self.history = []
        self.num_history = num_history

    def get_message(self, query):
        is_needRAG = self.text_processor.classification_query([query])
        self.history.append({"role": "user", "content": query})
        if is_needRAG:
            query = self.text_processor.extension_query(
                self.llm_instructions, self.history[-self.num_history :]
            )
            bonus_info = self.search.get_graph_search_result(query)
            full_query = query + "\n" + bonus_info

        else:
            full_query = query

        response = self.llm.get_message(full_query)
        self.history.append({"role": "model", "content": response})

        return response

    def get_history(self):
        return self.history

    def delete_history(self):
        self.history = []
        return "History deleted successfully"
