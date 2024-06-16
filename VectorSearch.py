import pymongo
import embedding

mongo_uri = "mongodb+srv://ktoan911:ci12ZbPRMJSNjRoB@cluster0.ogeezq3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB."""
    try:
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
        """Insert a document into the collection."""
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

    def vector_search(self, user_query, collection, num_candidates=100, k=5):
        """
        Perform a vector search in the MongoDB collection based on the user query.

        Args:
        user_query (str): The user's query string.
        collection (MongoCollection): The MongoDB collection to search.

        Returns:
        list: A list of matching documents.
        """

        # Generate embedding for the user query
        query_embedding = embedding.get_embedding(user_query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed."

        # Define the vector search pipeline
        vector_search_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": num_candidates,  # Number of candidate matches to consider
                "limit": k  # Return top 4 matches
            }
        }

        unset_stage = {
            "$unset": "embedding"  # Exclude the 'embedding' field from the results
        }

        project_stage = {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "Phone": 1,  # Include the Phone field
                "Features": 1,  # Include the Features field
                "Description": 1,  # Include the Description field
                'specs': 1,  # Include the specs field
                'price': 1,
                "score": {
                    "$meta": "vectorSearchScore"  # Include the search score
                }
            }
        }

        pipeline = [vector_search_stage, unset_stage, project_stage]

        # Execute the search
        results = collection.aggregate(pipeline)
        return list(results)

    def get_search_result(self, query, num_candidates=100, k=5, combine_query=True):

        db_information = self.vector_search(
            query, self.collection, num_candidates, k)

        search_result = ""
        for result in db_information:
            search_result += f"Phone: {result.get('Phone', 'N/A')}, Features: {result.get('Features', 'N/A')}, Description: {result.get('Description', 'N/A')}, specs: {result.get('specs', 'N/A')}, price: {result.get('price', 'N/A')}\n"
        if not combine_query:
            return search_result
        else:
            prompt_query = query + ". " + "Choose one of them:"
            return f"Query: {prompt_query} \n {search_result}."
