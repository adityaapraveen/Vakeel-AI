from flask import Flask, request, jsonify
from flask_cors import CORS
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
import ollama

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Milvus connection parameters
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

# Function to perform search in Milvus collection
def search_milvus(collection_name, query_text, top_k=3):
    # Connect to the collection
    collection = Collection(collection_name)

    # Convert query to an embedding
    query_embedding = embedding_model.encode([query_text]).tolist()

    # Define search parameters
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    # Perform search
    results = collection.search(
        data=query_embedding,  # Query embedding
        anns_field="vector",   # The field where vectors are stored
        param=search_params,
        limit=top_k,           # Get top_k most similar results
        output_fields=["text"] # Fetch the original text field
    )

    # Format results for output
    response = []
    for hits in results:
        for hit in hits:
            response.append({
                "text": hit.entity.get("text"),
                "score": hit.distance
            })

    return response

# Endpoint to query IPC collection
@app.route("/query/ipc", methods=["POST"])
def query_ipc():
    data = request.get_json()  # Get JSON data from the request
    query_text = data.get("query")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Perform search in IPC collection
    retrieved_docs = search_milvus("IPC_collection", query_text)
    
    # If no relevant documents found, handle gracefully
    if not retrieved_docs:
        print("⚠️ No relevant legal documents found in the database.")
        context = "No legal context available."
    else:
        # Extract relevant legal content
        context = "\n\n".join([doc["text"] for doc in retrieved_docs])
        print(f"✅ Retrieved {len(retrieved_docs)} relevant legal clauses.")

    # 🔹 Use Ollama to generate a legally compliant employment contract
    response = ollama.chat(
        model="llama3.2",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': "You are an expert in Indian IPC. Your task is to give relevent Indian IPC information in the specified legal context. Ensure compliance with the Indian judicial system. Be specific and concise."
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {query_text}"
            }
        ]
    )

    return jsonify({"answer": response['message']['content']})

# Endpoint to query legal_documents collection for precedence
@app.route("/query/legal", methods=["POST"])
def query_legal_documents():
    data = request.get_json()  # Get JSON data from the request
    query_text = data.get("query")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Perform search in legal_documents collection
    retrieved_docs = search_milvus("Precedence_collection", query_text)
    
    # If no relevant documents found, handle gracefully
    if not retrieved_docs:
        print("⚠️ No relevant legal documents found in the database.")
        context = "No legal context available."
    else:
        # Extract relevant legal content
        context = "\n\n".join([doc["text"] for doc in retrieved_docs])
        print(f"✅ Retrieved {len(retrieved_docs)} relevant legal clauses.")

    # 🔹 Use Ollama to generate a legally compliant employment contract
    response = ollama.chat(
        model="llama3.2",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': "You are an expert in Indian Law. Your task is to cite relevent Indian cases and their information in the specified legal context. Ensure compliance with the Indian judicial system. Be specific and concise."
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {query_text}"
            }
        ]
    )

    return jsonify({"answer": response['message']['content']})

# Endpoint for contract drafting with Milvus and Ollama
@app.route("/generate_contract", methods=["POST"])
def generate_contract():
    data = request.get_json()  # Get JSON data from the request
    user_question = data.get("question")
    
    if not user_question:
        return jsonify({"error": "Question is required"}), 400
    
    print("\n🔍 Searching for relevant legal clauses in Milvus...")

    # Retrieve the top 3 most relevant legal documents from Milvus
    retrieved_docs = search_milvus("Document_Creation_collection", user_question, top_k=3)

    # If no relevant documents found, handle gracefully
    if not retrieved_docs:
        print("⚠️ No relevant legal documents found in the database.")
        context = "No legal context available."
    else:
        # Extract relevant legal content
        context = "\n\n".join([doc["text"] for doc in retrieved_docs])
        print(f"✅ Retrieved {len(retrieved_docs)} relevant legal clauses.")

    # 🔹 Use Ollama to generate a legally compliant employment contract
    response = ollama.chat(
        model="llama3.2",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': "You are an expert in Indian contract law. Your task is to generate a legally valid employment contract based on the given legal context and specified terms. Ensure compliance with the Indian judicial system. Be specific and concise."
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {user_question}"
            }
        ]
    )

    # Return the generated response
    return jsonify({"contract": response['message']['content']})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
