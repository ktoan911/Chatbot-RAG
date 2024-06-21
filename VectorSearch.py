import pymongo
import os
from query_process import get_embedding
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()


def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB."""
    try:
        # Kết nối tới MongoDB sử dụng URI
        client = pymongo.MongoClient(
            mongo_uri, appname="devrel.content.python")
        print("Connection to MongoDB successful")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None


client = get_mongo_client(os.environ["MONGO_URI"])


class VectorSearch:
    def __init__(self, db_name='Phone', collection_name='Phone_ViType'):
        if not os.environ["MONGO_URI"]:
            raise ValueError("MongoDB URI is missing")
        self.client = client
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_document(self, df):
        """
            Đưa dữ liệu từ DataFrame vào collection trong MongoDB.
        """
        try:
            documents = df.to_dict("records")
            self.collection.insert_many(documents)
            print("Data ingestion into MongoDB completed")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_collection(self):
        """Delete the collection."""
        try:
            self.collection.delete_many({})
            print("Collection deleted")
        except Exception as e:
            print(f"An error occurred: {e}")

    def vector_search(self, user_query, collection, num_candidates=100, k=2):
        """
        Lấy ra các vector gần nhất với vector của user_query từ collection.
        Args:
            user_query (str): Câu truy vấn của người dùng.
            collection (pymongo.collection.Collection): Collection trong MongoDB.
            num_candidates (int): Số lượng vector ứng viên.
            k (int): Số lượng vector gần nhất cần lấy ra.
        Returns:
            list: Danh sách các vector gần nhất với vector của user_query.
        """

        # Generate embedding for the user query
        query_embedding = get_embedding(user_query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed."

        # Định nghĩa các stage trong pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": num_candidates,  # Số lượng vector ứng viên.
                "limit": k  # Trả về k vector gần nhất.
            }
        }

        unset_stage = {
            # Loại bỏ trường embedding khỏi kết quả trả về.
            "$unset": "embedding"
        }

        project_stage = {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "url": 1,  # Include the Phone url
                "title": 1,  # Include the Phone field
                "product_promotion": 1,  # Include the Description field
                'product_specs': 1,  # Include the specs field
                'current_price': 1,
                'color_options': 1,
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }

        # Xây dựng pipeline
        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Thực thi pipeline
        results = collection.aggregate(pipeline)
        return list(results)

    def get_search_result(self, query, num_candidates=100, k=4, combine_query=True):
        '''
        Lấy kết quả tìm kiếm từ vector search và trả về dưới dạng chuỗi.
        Args:
            query (str): Câu truy vấn của người dùng.
            num_candidates (int): Số lượng vector ứng viên.
            k (int): Số lượng vector gần nhất cần lấy ra.
            combine_query (bool): Kết hợp câu truy vấn với kết quả tìm kiếm hay không.
        Returns:
            str: Kết quả tìm kiếm dưới dạng chuỗi.
        '''

        def get_infomation(text, prompt):
            text = text.replace('\n', '.')
            if text:
                return f"{prompt} {text}.\n"
            else:
                return ""

        # Lấy vector database từ vector search
        db_information = self.vector_search(
            query, self.collection, num_candidates, k)

        search_result = ""

        # Duyệt qua kết quả trả về từ vector search và thêm vào search_result
        for i, result in enumerate(db_information):
            url = result.get('url', 'N/A')
            title = result.get('title', 'N/A')
            product_promotion = result.get('product_promotion', 'N/A')
            product_specs = result.get('product_specs', 'N/A')
            current_price = result.get('current_price', 'N/A') if result.get(
                'current_price', 'N/A') else 'Liên hệ để trao đổi thêm'
            color_options = ", ".join(result.get('color_options', 'N/A'))

            search_result += f"Sản phẩm thứ {i+1}: \n"

            search_result += get_infomation(url, "Link sản phẩm:")
            search_result += get_infomation(title, "Tên sản phẩm:")
            search_result += get_infomation(product_promotion,
                                            "Ưu đãi:")
            search_result += get_infomation(product_specs,
                                            "Chi tiết sản phẩm:")
            search_result += get_infomation(current_price, "Giá tiền:")
            search_result += get_infomation(color_options,
                                            "Các màu điện thoại:")

        if not combine_query:
            return search_result
        else:
            prompt_query = query + ". " + "Cửa hàng có những sản phẩm sau:"
            return f"Query: {prompt_query} \n {search_result}.".replace('<br>', '')
