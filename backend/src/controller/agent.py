from __future__ import annotations

from common.logger import get_logger
from dotenv import load_dotenv
from google.genai import types
from infrastructure.controller_service import controller_service
from service.LLM.llm import LLM

load_dotenv()

llm = LLM()
logger = get_logger("AGENT")


class Agent:
    def __init__(self):
        self.controller = controller_service.get_controller()
        self.tools = types.Tool(function_declarations=self.controller.get_tools())

    def execute(self, prompt: str):
        try:
            contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

            response = llm.function_calling(contents, tools=self.tools)
            res = []
            # Process all function calls in order
            for fc_part in response.function_calls:
                tool_name = fc_part.name
                args = fc_part.args or {}
                logger.info(f"🔧 Đang gọi tool: '{tool_name}' với args: {args}")

                try:
                    res.append(self.controller.execute_method_by_name(tool_name, args))

                except Exception as e:
                    logger.info(f"❌ Lỗi khi gọi tool '{tool_name}': {e}")
                    return "Lỗi đường truyền mạng"
            return "\n".join(res)
        except Exception as e:
            logger.info(f"❌ Lỗi trong agent loop: {e}")
            return "Error processing agent: " + str(e)
