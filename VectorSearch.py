import pymongo
from text_process import get_embedding

mongo_uri = "mongodb+srv://ktoan911:ci12ZbPRMJSNjRoB@cluster0.ogeezq3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


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


client = get_mongo_client(mongo_uri)


class VectorSearch:
    def __init__(self, db_name='Phone', collection_name='Phone_Type'):
        if not mongo_uri:
            raise ValueError("MongoDB URI is missing")
        self.client = client
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_mongo_client(self, mongo_uri):
        """Establish connection to the MongoDB."""
        try:
            client = pymongo.MongoClient(
                mongo_uri, appname="devrel.content.python")
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None

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
                "_id": 0,  # Loại bỏ trường _id
                "Phone": 1,  # Trả về trường Phone
                "Features": 1,  # Trả về trường Features
                "Description": 1,  # Trả về trường Description
                'specs': 1,  # Trả về trường specs
                'price': 1,  # Trả về trường price
                "score": {
                    # Trả về điểm số của các vector gần nhất.
                    "$meta": "vectorSearchScore"
                }
            }
        }

        # Xây dựng pipeline
        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Thực thi pipeline
        results = collection.aggregate(pipeline)
        return list(results)

    def get_search_result(self, query, num_candidates=100, k=2, combine_query=True):
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

        # Lấy vector database từ vector search
        db_information = self.vector_search(
            query, self.collection, num_candidates, k)

        search_result = ""

        # Duyệt qua kết quả trả về từ vector search và thêm vào search_result
        for result in db_information:
            phone = result.get('Phone', 'N/A')
            features = result.get(
                'Features', 'N/A').replace('\n', ' ').replace('|', ',').replace('\t', ' ')
            description = result.get('Description', 'N/A').replace('\n', ' ')
            price = result.get('price', 'N/A')
            search_result += f"Phone: {phone},Description: {description}, Features: {features}, Price: {price} VND\n"

        if not combine_query:
            return search_result
        else:
            prompt_query = query + ". " + "Answer with information below:"
            return f"Query: {prompt_query} \n {search_result}."
