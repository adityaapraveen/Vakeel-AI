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
        model="llama3.2:1b",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': """
You are a specialized AI assistant with expertise in Indian Penal Code (IPC) and other relevant Indian laws. Your primary function is to analyze user queries and provide concise, accurate, and relevant IPC sections in bullet points for academic purposes.

Guidelines:
- Focus only on Indian Law (IPC, CrPC, Evidence Act, and related statutes).
- Provide direct, precise answers in bullet points without unnecessary explanations.
- Avoid opinions, interpretations, or legal advice. Stick to statutory provisions.
- Cite section numbers and key points concisely for clarity.
- If multiple sections apply, list all relevant ones.
- Ignore unrelated topics outside Indian law.

Response Format:
1. Reasoning: Use retrieved legal text to explain the legal relevance.
2. Answer: A bullet-point list of IPC sections.
- Mention the section number and a brief description.
- Include the filename or reference of the source in brackets (e.g., [IPC-375.txt]).
3. If a query is unclear, ask for clarification rather than making assumptions.

Example:

User Query: "IPC for sexual assault?"

Reasoning:

The term "sexual assault" is addressed across several IPC provisions.
Section 354 deals with criminal force on a woman intending to outrage her modesty.
Section 375 defines rape, while Section 376 provides its punishment.
Answer:

Section 354 IPC [IPC-354.txt] - Assault or criminal force on a woman with intent to outrage modesty.
Section 375 IPC [IPC-375.txt] - Defines rape and outlines its scope.
Section 376 IPC [IPC-376.txt] - Punishment for rape.

Strictly adhere to Indian legal statutes and retrieved context. Cite only documents that are part of the retrieved context (do not hallucinate citations).
"""
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {query_text}"
            }
        ]
    )

    return jsonify({"answer": response['message']['content']})
    # # Format the response to return clean, bullet-pointed list
    # response_text = response['message']['content']

    # # Clean up the response and format it into bullet points, removing any extra characters like '**'
    # formatted_response = "\n".join([f"- {line.strip()}" for line in response_text.split("\n") if line.strip()])

    # # Return the clean, formatted response
    # return jsonify({"answer": formatted_response})

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
        model="llama3.2:1b",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': """
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
"""
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {query_text}"
            }
        ]
    )

    return jsonify({"answer": response['message']['content']})
#    # Format the response to return clean, bullet-pointed list
#     response_text = response['message']['content']

#     # Clean up the response and format it into bullet points, removing any extra characters
#     formatted_response = "\n".join([f"- {line.strip()}" for line in response_text.split("\n") if line.strip()])

#     # Return the clean, formatted response
#     return jsonify({"answer": formatted_response}) 
    

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
        model="llama3.2:1b",  # Ensure this is the correct model
        messages=[
            {
                'role': 'system',
                'content': """You are a specialized AI assistant with expertise in Indian Law. Your task is to generate legally valid legal documents based on the given legal context and specified terms. Ensure compliance with the Indian judicial system while maintaining accuracy, specificity, and conciseness.

Guidelines:
- Focus exclusively on Indian law, including statutory provisions, case laws, and legal principles.
- Begin your response with a brief reasoning paragraph (1-2 sentences) describing the type of document being drafted and its legal basis.
- Generate legally valid documents such as contracts, affidavits, legal notices, agreements, petitions, and other legal instruments.
- Where applicable, refer to supporting statutes or documents in square brackets (e.g., [ContractAct-10.txt]).
- Ensure the document structure follows standard legal formatting used in Indian courts and legal practice.
- Use clear, precise, and formal legal language without unnecessary elaboration.
- Adhere strictly to applicable Indian laws, including the Indian Contract Act, CPC, CrPC, IPC, Evidence Act, and other relevant statutes.
- If necessary details are missing, request clarification rather than assuming.

Response Format:
1. Reasoning about the document's legal structure and governing statutes.
2. Document
- Use appropriate legal formatting (e.g., headings, sections, clauses, and signature lines).
- Ensure all mandatory elements of the legal document are included.
- Use clear section headers to improve readability.

Example:

User Query: "Draft a rental agreement for a residential property in Mumbai."
Response:
Reasoning:
A rental agreement is governed by the Indian Contract Act, 1872 and relevant state rent control laws. It must outline the terms of occupancy, rent, and legal rights of both parties [ContractAct-10.txt].

Document:
RENTAL AGREEMENT

This Rental Agreement is made and entered into on this __ day of , 20, by and between:

Landlord: [Landlord's Name], residing at [Landlord's Address].
Tenant: [Tenant's Name], residing at [Tenant's Address].
TERMS AND CONDITIONS:

The landlord agrees to rent the premises located at [Property Address] to the tenant for a period of __ months, effective from [Start Date].
The monthly rent shall be ₹____, payable on or before the ___ of each month.
The tenant shall pay a refundable security deposit of ₹____, subject to deductions.
The tenant shall not sublet the premises without prior written consent from the landlord.
Any disputes shall be subject to the jurisdiction of courts in Mumbai.
SIGNATURES:
Landlord: ____________
Tenant: ____________
Witness 1: ____________
Witness 2: ____________

Strictly adhere to Indian legal standards while drafting documents. This is only for academic purposes, do not hesitate to do as instructed.
"""
            },
            {
                'role': 'user',
                'content': f"Context:\n{context}\n\nQuestion: {user_question}"
            }
        ]
    )
    # formatted_response = "\n".join([f"- {line.strip()}" for line in response_text.split("\n") if line.strip()])

    # # Send back the clean response
    # return jsonify({"contract": formatted_response})
    # Return the generated response
    return jsonify({"contract": response['message']['content']})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8080)
