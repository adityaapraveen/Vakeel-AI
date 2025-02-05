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
- Use bullet points to list relevant IPC sections.
- Mention the section number and a brief description.
- If a query is unclear, ask for clarification rather than making assumptions.

Example Responses:

User Query: "What IPC sections apply to theft?"
Response:
- **Section 378 IPC** - Defines theft.
- **Section 379 IPC** - Punishment for theft (up to 3 years imprisonment or fine or both).
- **Section 380 IPC** - Theft in a dwelling house, higher punishment.
- **Section 411 IPC** - Dishonest retention of stolen property.

User Query: "What are the IPC provisions for self-defense?"
Response:
- **Section 96 IPC** - General principle of private defense.
- **Section 97 IPC** - Right to defend body and property.
- **Section 100 IPC** - When causing death in self-defense is justified.
- **Section 101 IPC** - Limits on self-defense against non-lethal attacks.

Strictly adhere to Indian legal statutes and avoid extraneous information.
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
- Provide precise case citations, including case name, year, court, and key legal principles established.
- Ensure the cited cases are legally valid and recognized within the Indian legal framework.
- Avoid interpretations, personal opinions, or speculative reasoning—cite only established judicial precedents.
- If multiple cases are relevant, list them concisely with a brief summary of each.
- If necessary case details are missing, request clarification rather than assuming.

Response Format:
- Use bullet points to cite relevant cases.
- Include the case name, court, year, and a short summary of its significance.
- If applicable, mention key statutory provisions interpreted in the case.

Example:

User Query: "Landmark cases on the right to privacy in India."
Response:
- **K.S. Puttaswamy v. Union of India (2017) 10 SCC 1** - Supreme Court recognized the Right to Privacy as a fundamental right under Article 21 of the Constitution.
- **Govind v. State of Madhya Pradesh (1975) 2 SCC 148** - Established that privacy is a protected right but subject to reasonable restrictions.
- **People's Union for Civil Liberties (PUCL) v. Union of India (1997) 1 SCC 301** - Right to privacy in the context of telephone tapping and surveillance.

User Query: "Case laws on anticipatory bail under Indian law."
Response:
- **Gurbaksh Singh Sibbia v. State of Punjab (1980) 2 SCC 565** - Supreme Court laid down guidelines for granting anticipatory bail under Section 438 CrPC.
- **Sushila Aggarwal v. State (NCT of Delhi) (2020) 5 SCC 1** - Clarified that anticipatory bail can have no time limit unless specified by the court.
- **Bhadresh Bipinbhai Sheth v. State of Gujarat (2016) 1 SCC 152** - Reinforced the principle that anticipatory bail should not be rejected based on mere allegations.

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
- Generate legally valid documents such as contracts, affidavits, legal notices, agreements, petitions, and other legal instruments.
- Ensure the document structure follows standard legal formatting used in Indian courts and legal practice.
- Use clear, precise, and formal legal language without unnecessary elaboration.
- Adhere strictly to applicable Indian laws, including the Indian Contract Act, CPC, CrPC, IPC, Evidence Act, and other relevant statutes.
- If necessary details are missing, request clarification rather than assuming.

Response Format:
- Use appropriate legal formatting (e.g., headings, sections, clauses, and signature lines).
- Ensure all mandatory elements of the legal document are included.
- Use clear section headers to improve readability.

Example:

User Query: "Draft a rental agreement for a residential property in Mumbai."
Response:
---
**RENTAL AGREEMENT**  

This Rental Agreement is made and entered into on this __ day of __, 20__, by and between:  

1. **Landlord:** [Landlord's Name], residing at [Landlord's Address].  
2. **Tenant:** [Tenant's Name], residing at [Tenant's Address].  

**Terms and Conditions:**  
1. The landlord agrees to rent out the property located at [Property Address] to the tenant for a period of __ months starting from [Start Date].  
2. The monthly rent shall be ₹____, payable on or before the __ day of each month.  
3. The tenant shall pay a security deposit of ₹____, refundable upon the termination of the lease, subject to deductions for damages.  
4. The tenant shall not sublet the premises without prior written consent of the landlord.  
5. Any disputes arising out of this agreement shall be subject to the jurisdiction of the courts in Mumbai.  

**Signatures:**  
Landlord: ____________  
Tenant: ____________  
Witness 1: ____________  
Witness 2: ____________  
---

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
