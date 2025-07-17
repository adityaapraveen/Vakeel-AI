from flask import Flask, request, jsonify
from flask_cors import CORS
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
import json

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
CORS(app, resources={r"/query/*": {"origins": "http://localhost:5173"}})
# Milvus connection parameters
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBGewtHd2LeVcKVRGhlP5rtL8eSTv5OepA")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Connect to Milvus
connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)

# === Helper Functions ===

def search_milvus(collection_name, query_text, top_k=3):
    collection = Collection(collection_name)
    collection.load()

    # Fields we want to include
    preferred_fields = ["text", "filename"]

    # Only include available fields
    available_fields = {field.name for field in collection.schema.fields}
    output_fields = [field for field in preferred_fields if field in available_fields]

    # Create query embedding
    query_embedding = embedding_model.encode([query_text])[0].tolist()
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    results = collection.search(
        data=[query_embedding],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=output_fields
    )

    # Normalize distances
    distances = [hit.distance for hits in results for hit in hits]
    max_dist = max(distances) if distances else 1.0
    min_dist = min(distances) if distances else 0.0
    range_dist = max_dist - min_dist or 1.0

    # Build response
    response = []
    for hits in results:
        for hit in hits:
            text_content = hit.entity.get("text")
            if text_content:
                normalized_score = 1 - ((hit.distance - min_dist) / range_dist)
                response.append({
                    "text": text_content,
                    "filename": hit.entity.get("filename") if "filename" in output_fields else None,
                    "score": round(normalized_score, 4)
                })
    return response



def compare_llm_output_to_retrieved(llm_output, retrieved_docs):
    output_lower = llm_output.lower()
    used_docs = []
    unused_docs = []

    for doc in retrieved_docs:
        if doc["text"].lower()[:50] in output_lower:
            used_docs.append(doc)
        else:
            unused_docs.append(doc)

    return used_docs, unused_docs

def log_interaction(query_text, retrieved_docs, llm_output, used_docs, unused_docs, log_file="llm_audit_log.json"):
    entry = {
        "query": query_text,
        "llm_output": llm_output,
        "retrieved_docs": retrieved_docs[:1],
        "used_docs": used_docs[:0],
        "unused_docs": unused_docs[:0],
    }
    with open(log_file, "a") as f:
        json.dump(entry, f, indent=2)
        f.write("\n")

# === Route Handlers ===

@app.route("/query/ipc", methods=["POST"])
def query_ipc():
    data = request.get_json()
    query_text = data.get("query")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    retrieved_docs = search_milvus("IPC_collection", query_text)
    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
You are a specialized AI assistant with expertise in Indian Penal Code (IPC) and related laws. Your primary responsibility is to analyze user queries and provide accurate legal responses while clearly tracing the underlying legal logic between IPC sections.

🧠 Your answers must show a **Knowledge Graph Trace** of how key legal concepts like “intention”, “force”, or “consent” flow through IPC sections, e.g.,:

"Intent" → Section 299 (Culpable Homicide) → Section 300 (Murder) → Section 302 (Punishment)

📌 Guidelines:
- Use only Indian laws (IPC, CrPC, Evidence Act).
- Base your answer only on the provided context from legal documents.
- Do not hallucinate or make assumptions.
- Include only **valid IPC section numbers** that are traceable from the query.
- Avoid giving legal advice—provide only academic, statutory responses.

📋 Response Format:

1. **Knowledge Graph Trace**: (Legal rule flow)
- Show how one legal section leads to another.
- Example:
  "Intent" → Section 299 → Section 300 → Section 302

2. **Answer**:
- Bullet point list:
  - Section Number (e.g., 299)
  - Short Description
  - [Filename or reference if available]

✅ Example:

User Query: "IPC for murder based on intention?"

Knowledge Graph Trace:
Intent → Section 299 (Culpable Homicide) → Section 300 (Murder) → Section 302 (Punishment for Murder)

Answer:
- Section 299 IPC [IPC-299.txt] - Defines culpable homicide.
- Section 300 IPC [IPC-300.txt] - Explains when culpable homicide is murder.
- Section 302 IPC [IPC-302.txt] - Punishment for murder.

If context is not sufficient or query is unclear, ask for clarification.
""" # Use same IPC system prompt as before
    user_prompt = f"Context:\n{context}\n\nQuestion: {query_text}"

    try:
        response = gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        llm_output = response.text
        used_docs, unused_docs = compare_llm_output_to_retrieved(llm_output, retrieved_docs)
        log_interaction(query_text, retrieved_docs, llm_output, used_docs, unused_docs)
        return jsonify({
            "answer": llm_output,
            "retrieved_docs": retrieved_docs,
            "used_docs": used_docs,
            "unused_docs": unused_docs
        })

    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500


@app.route("/query/legal", methods=["POST"])
def query_legal_documents():
    data = request.get_json()
    query_text = data.get("query")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    retrieved_docs = search_milvus("Precedence_collection", query_text)
    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """
    You are a specialized AI assistant with expertise in Indian Law. Your task is to cite relevant Indian case laws and provide their key details based on the specified legal context. Ensure compliance with the Indian judicial system while maintaining accuracy, specificity, and relevance.

Guidelines:
- Focus exclusively on Indian case laws, including Supreme Court, High Court, and other relevant tribunal decisions.
- Begin with a brief reasoning paragraph (1-3 sentences) based on the retrieved case summaries.
- Provide precise case citations, including case name, year, court, and key legal principles established.
- Ensure the cited cases are legally valid and recognized within the Indian legal framework.
- Avoid interpretations, personal opinions, or speculative reasoning—cite only established judicial precedents.
- If multiple cases are relevant, list them concisely with a brief summary of each.
- If necessary case details are missing, request clarification rather than assuming.

Response Format:
1. Reasoning based on the retrieved case law.
2. Answer: Bullet-pointed list of cited cases.
- Include case name, citation, year, and short summary of legal significance.
- Use [filename] tags (e.g., [Case-Puttaswamy.txt]) if available.
- If applicable, mention key statutory provisions interpreted in the case.

Example:
Reasoning: The Right to Privacy was recognized as a fundamental right by the Indian Supreme Court in 2017. Earlier decisions also laid the groundwork by interpreting Article 21 of the Constitution in related contexts.
Answer:
K.S. Puttaswamy v. Union of India (2017) 10 SCC 1 [Case-Puttaswamy.txt] - Supreme Court recognized the Right to Privacy as a fundamental right under Article 21.
Govind v. State of Madhya Pradesh (1975) 2 SCC 148 [Case-Govind.txt] - Held that the right to privacy is protected but subject to reasonable restrictions.
PUCL v. Union of India (1997) 1 SCC 301 [Case-PUCL.txt] - Established safeguards around telephone tapping and privacy under constitutional principles.

Strictly adhere to Indian judicial precedents while citing cases. If a query lacks specificity, seek clarification rather than making assumptions.  

    """  # Use same case law prompt as before
    user_prompt = f"Context:\n{context}\n\nQuestion: {query_text}"

    try:
        response = gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        llm_output = response.text
        used_docs, unused_docs = compare_llm_output_to_retrieved(llm_output, retrieved_docs)
        log_interaction(query_text, retrieved_docs, llm_output, used_docs, unused_docs)
        return jsonify({
            "answer": llm_output,
            "retrieved_docs": retrieved_docs,
            "used_docs": used_docs,
            "unused_docs": unused_docs
        })

    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500


@app.route("/generate_contract", methods=["POST"])
def generate_contract():
    data = request.get_json()
    user_question = data.get("question")

    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    retrieved_docs = search_milvus("Document_Creation_collection", user_question, top_k=3)
    context = "\n\n".join([doc["text"] for doc in retrieved_docs]) or "No legal context available."

    system_prompt = """..."""  # Use same contract prompt as before
    user_prompt = f"Context:\n{context}\n\nQuestion: {user_question}"

    try:
        response = gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        llm_output = response.text
        used_docs, unused_docs = compare_llm_output_to_retrieved(llm_output, retrieved_docs)
        log_interaction(user_question, retrieved_docs, llm_output, used_docs, unused_docs)
        return jsonify({"contract": llm_output})
    except Exception as e:
        return jsonify({"error": f"Error generating contract: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
