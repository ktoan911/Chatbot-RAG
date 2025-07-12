from __future__ import annotations

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from common.logger import get_logger
from infrastructure.sematic_router import (
    ChitchatProdcutsSentimentRoute,
    SemanticRouter,
)


# Define prompt function directly to avoid import issues
def model_summary_chat_history_prompt():
    return """Based on the user's conversation history and their latest query that may
                                refer to context in the chat history, construct an independent query in Vietnamese that can be understood without the chat
                                history. Do not answer this query, just reconstruct it if necessary, and if there is not enough information to construct a new question,
                                keep the original question unchanged"""


# Load the environment variables from the .env file
load_dotenv()
logger = get_logger(__name__)

# load the embedding model
embedding_model = SentenceTransformer(os.environ["EMBEDDING_MODEL"])

chitchat_prodcuts_sentiment_route = ChitchatProdcutsSentimentRoute()
senmatic_router = SemanticRouter(embedding_model)

embedding_routes = chitchat_prodcuts_sentiment_route.get_json_routesEmbedding(
    path=r"E:\Python\Chatbot-RAG\src\Embedding\routesEmbedding.json",
)


class TextProcessor:
    def process_query(self, query: str) -> str:
        return query.strip()

    def _get_infomation(self, text, prompt):
        text = text.replace("\n", ".")
        if text:
            return f"{prompt} {text}.\n"
        else:
            return ""

    def transform_query(self, db_information: list) -> str:
        results = []
        for _, result in enumerate(db_information):
            title = result.get("title", "N/A")
            product_promotion = result.get("product_promotion", "N/A")
            product_specs = result.get("product_specs", "N/A")
            current_price = (
                result.get("current_price", "N/A")
                if result.get(
                    "current_price",
                    "N/A",
                )
                else "Liên hệ để trao đổi thêm"
            )
            color_options = ", ".join(result.get("color_options", "N/A"))
            search_result = ""

            search_result += self._get_infomation(title, "Tên sản phẩm:")
            search_result += self._get_infomation(
                product_promotion,
                "Ưu đãi:",
            )
            search_result += self._get_infomation(
                product_specs,
                "Chi tiết sản phẩm:",
            )
            search_result += self._get_infomation(current_price, "Giá tiền:")
            search_result += self._get_infomation(
                color_options,
                "Các màu điện thoại:",
            )
            results.append(search_result)
        return results

    # Hàm lấy embedding của câu truy vấn
    def get_embedding(self, text: str) -> list[float]:
        if not text.strip():
            logger.info("Attempted to get embedding for empty text.")
            return []

        embedding = embedding_model.encode(
            text.replace(
                "###",
                "",
            )
            .replace("\n", "")
            .replace("<br>", ""),
        )

        return embedding.tolist()

    def classification_query(self, queries):
        for query in queries:
            score, intent = senmatic_router.guide(
                query,
                embedding_routes,
            )
        if intent == "products":
            return True
        else:
            return False

    def extension_query(self, llm, history_query) -> str:
        summary_query = "###The chat history is {history_query}. ### Output: reconstruct string".format(
            history_query=history_query,
        )

        messages = [
            {
                "role": "system",
                "content": model_summary_chat_history_prompt(),
            },
            {
                "role": "user",
                "content": summary_query,
            },
        ]
        return llm.call(messages, stream=False)


# stopwords = [
#     "a lô", "a ha", "ai", "ai ai", "ai nấy", "ai đó", "alô", "amen", "anh", "anh ấy", "ba", "ba ba",
#     "ba bản", "ba cùng", "ba họ", "ba ngày", "ba ngôi", "ba tăng", "bao giờ", "bao lâu", "bao nhiêu",
#     "bao nả", "bay biến", "biết", "biết bao", "biết bao nhiêu", "biết chắc", "biết chừng nào",
#     "biết mình", "biết mấy", "biết thế", "biết trước", "biết việc", "biết đâu", "biết đâu chừng",
#     "biết đâu đấy", "biết được", "buổi", "buổi làm", "buổi mới", "buổi ngày", "buổi sớm", "bà",
#     "bà ấy", "bài", "bài bác", "bài bỏ", "bài cái", "bác", "bán", "bán cấp", "bán dạ", "bán thế",
#     "bây bẩy", "bây chừ", "bây giờ", "bây nhiêu", "bèn", "béng", "bên", "bên bị", "bên có", "bên cạnh",
#     "bông", "bước", "bước khỏi", "bước tới", "bước đi", "bạn", "bản", "bản bộ", "bản riêng", "bản thân",
#     "bản ý", "bất chợt", "bất cứ", "bất giác", "bất kì", "bất kể", "bất kỳ", "bất luận", "bất ngờ",
#     "bất nhược", "bất quá", "bất quá chỉ", "bất thình lình", "bất tử", "bất đồ", "bấy", "bấy chầy",
#     "bấy chừ", "bấy giờ", "bấy lâu", "bấy lâu nay", "bấy nay", "bấy nhiêu", "bập bà bập bõm", "bập bõm",
#     "bắt đầu", "bắt đầu từ", "bằng", "bằng cứ", "bằng không", "bằng người", "bằng nhau", "bằng như",
#     "bằng nào", "bằng nấy", "bằng vào", "bằng được", "bằng ấy", "bển", "bệt", "bị", "bị chú", "bị vì",
#     "bỏ", "bỏ bà", "bỏ cha", "bỏ cuộc", "bỏ không", "bỏ lại", "bỏ mình", "bỏ mất", "bỏ mẹ", "bỏ nhỏ",
#     "bỏ quá", "bỏ ra", "bỏ riêng", "bỏ việc", "bỏ xa", "bỗng", "bỗng chốc", "bỗng dưng", "bỗng không",
#     "bỗng nhiên", "bỗng nhưng", "bỗng thấy", "bỗng đâu", "bộ", "bộ thuộc", "bộ điều", "bội phần",
#     "bớ", "bởi", "bởi ai", "bởi chưng", "bởi nhưng", "bởi sao", "bởi thế", "bởi thế cho nên", "bởi tại",
#     "bởi vì", "bởi vậy", "bởi đâu", "bức", "cao", "cao lâu", "cao ráo", "cao răng", "cao sang", "cao số",
#     "cao thấp", "cao thế", "cao xa", "cha", "cha chả", "chao ôi", "chia sẻ", "chiếc", "cho", "cho biết",
#     "cho chắc", "cho hay", "cho nhau", "cho nên", "cho rằng", "cho rồi", "cho thấy", "cho tin", "cho tới",
#     "cho tới khi", "cho về", "cho ăn", "cho đang", "cho được", "cho đến", "cho đến khi", "cho đến nỗi",
#     "choa", "chu cha", "chui cha", "chung", "chung cho", "chung chung", "chung cuộc", "chung cục",
#     "chung nhau", "chung qui", "chung quy", "chung quy lại", "chung ái", "chuyển", "chuyển tự",
#     "chuyển đạt", "chuyện", "chuẩn bị", "chành chạnh", "chí chết", "chính", "chính bản", "chính giữa",
#     "chính là", "chính thị", "chính điểm", "chùn chùn", "chùn chũn", "chú", "chú dẫn", "chú khách",
#     "chú mày", "chú mình", "chúng", "chúng mình", "chúng ta", "chúng tôi", "chúng ông", "chăn chắn",
#     "chăng", "chăng chắc", "chăng nữa", "chơi", "chơi họ", "chưa", "chưa bao giờ", "chưa chắc", "chưa có",
#     "chưa cần", "chưa dùng", "chưa dễ", "chưa kể", "chưa tính", "chưa từng", "chầm chập", "chậc", "chắc",
#     "chắc chắn", "chắc dạ", "chắc hẳn", "chắc lòng", "chắc người", "chắc vào", "chắc ăn", "chẳng lẽ",
#     "chẳng những", "chẳng nữa", "chẳng phải", "chết nỗi", "chết thật", "chết tiệt", "chỉ", "chỉ chính",
#     "chỉ có", "chỉ là", "chỉ tên", "chỉn", "chị", "chị bộ", "chị ấy", "chịu", "chịu chưa", "chịu lời",
#     "chịu tốt", "chịu ăn", "chọn", "chọn bên", "chọn ra", "chốc chốc", "chớ", "chớ chi", "chớ gì",
#     "chớ không", "chớ kể", "chớ như", "chợt", "chợt nghe", "chợt nhìn", "chủn", "chứ", "chứ ai", "chứ còn",
#     "chứ gì", "chứ không", "chứ không phải", "chứ lại", "chứ lị", "chứ như", "chứ sao", "coi bộ",
#     "coi mòi", "con", "con con", "con dạ", "con nhà", "con tính", "cu cậu", "cuối", "cuối cùng",
#     "cuối điểm", "cuốn", "cuộc", "càng", "càng càng", "càng hay", "cá nhân", "các", "các cậu", "cách",
#     "cách bức", "cách không", "cách nhau", "cách đều", "cái", "cái gì", "cái họ", "cái đã", "cái đó",
#     "cái ấy", "câu hỏi", "cây", "cây nước", "còn", "còn như", "còn nữa", "còn thời gian", "còn về",
#     "có", "có ai", "có chuyện", "có chăng", "có chăng là", "có chứ", "có cơ", "có dễ", "có họ", "có khi",
#     "có ngày", "có người", "có nhiều", "có nhà", "có phải", "có số", "có tháng", "có thế", "có thể",
#     "có vẻ", "có ý", "có ăn", "có điều", "có điều kiện", "có đáng", "có đâu", "có được", "cóc khô",
#     "cô", "cô mình", "cô quả", "cô tăng", "cô ấy", "công nhiên", "cùng", "cùng chung", "cùng cực",
#     "cùng nhau", "cùng tuổi", "cùng tột", "cùng với", "cùng ăn", "căn", "căn cái", "căn cắt", "căn tính",
#     "cũng", "cũng như", "cũng nên", "cũng thế", "cũng vậy", "cũng vậy thôi", "cũng được", "cơ", "cơ chỉ",
#     "cơ chừng", "cơ cùng", "cơ dẫn", "cơ hồ", "cơ hội", "cơ mà", "cơ ngơi", "cơ sự", "cơ thể", "cơ thổ",
#     "cơn", "cơn cớ", "cả", "cả thể", "cả thảy", "cả tin", "cả ăn", "cấp", "cấp số", "cấp thêm", "cấn",
#     "cấn cái", "cũng tốt", "cộc", "cộc lốc", "côn đồ", "cúi đầu", "của", "của nả", "cứ", "cứ như",
#     "cứ việc", "cứ điểm", "cực lực", "do", "do vì", "do vậy", "do đó", "duy", "duy chỉ", "duy có",
#     "dài", "dài lời", "dài ra", "dành", "dành dành", "dào", "dì", "dì dì", "dù", "dù cho", "dù dì",
#     "dù gì", "dù rằng", "dù sao", "dù vậy", "dùng", "dùng cho", "dùng hết", "dùng làm", "dùng đến",
#     "dư", "dư dả", "dư sức", "dưới", "dưới nước", "dạ", "dạ bán", "dần dà", "dần dần", "dầu sao",
#     "dẫn", "dẫu", "dẫu mà", "dẫu rằng", "dẫu sao", "dễ", "dễ dùng", "dễ khiến", "dễ nghe", "dễ ngươi",
#     "dễ người", "dễ sợ", "dễ sử dụng", "dễ thường", "dễ thấy", "dễ ăn", "dở chừng", "dữ", "dữ cách",
#     "dữ tợn", "em", "em em", "em gái", "em rể", "giả", "giả dụ", "giả sử", "giảm", "giảm chính",
#     "giảm thế", "giống", "giống người", "giống như", "giờ", "giờ lâu", "giờ đây", "giờ đi", "giờ đến",
#     "giữ", "giữ lấy", "giữ ý", "giữa", "giữa lúc", "giữa nơi", "giữa trưa", "giữa tuần", "hay", "hay biết",
#     "hay hay", "hay không", "hay là", "hay làm", "hay nhỉ", "hay nói", "hay sao", "hay tin", "hay đâu",
#     "hiểu", "hiểu biết", "hoàn toàn", "hoặc", "hoặc là", "hãy", "hãy còn", "hãy cứ", "hãy nên", "hơn",
#     "hơn cả", "hơn hết", "hơn là", "hơn nữa", "hơn trước", "hết", "hết chuyện", "hết của", "hết lòng",
#     "hết nói", "hết ráo", "hết rồi", "hết ý", "họ", "họ gần", "họ xa", "hỏi", "hỏi lại", "hỏi xem",
#     "hỏi chuyện", "hỏi ra", "hỏi rằng", "hỏi tại", "hỏi thử", "hỏi đến", "hơn hết", "hệt", "họ",
#     "họ gần", "họ xa", "hỏi", "hỏi lại", "hỏi xem", "hỏi chuyện", "hỏi ra", "hỏi rằng", "hỏi tại",
#     "hỏi thử", "hỏi đến", "hệt", "họ", "họ gần", "họ xa", "hỏi", "hỏi lại", "hỏi xem", "hỏi chuyện",
#     "hỏi ra", "hỏi rằng", "hỏi tại", "hỏi thử", "hỏi đến", "hệt"
# ]
