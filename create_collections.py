import fitz  # PyMuPDF for fast text extraction
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Milvus
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

# Custom class for SentenceTransformer embeddings
class SentenceTransformerEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()

# Path to your legal PDF
local_path = "/Users/shreyasr/Documents/Projects/Genesis_Hackathon/IPC.pdf"

# Extract text using PyMuPDF
print("Extracting text from PDF...")
doc = fitz.open(local_path)
text = "\n".join([page.get_text("text") for page in doc if page.get_text("text")])
print("Text extraction completed.")

# Split text into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.create_documents([text])
print(f"Split document into {len(chunks)} chunks.")

# Initialize SentenceTransformer embeddings
embedding_function = SentenceTransformerEmbeddings()
print("Generating embeddings...")

# Prepare embeddings for document chunks
embeddings = embedding_function.embed_documents([chunk.page_content for chunk in chunks])

# Milvus connection parameters (Docker instance)
MILVUS_HOST = "localhost"  # Change if running on a different server
MILVUS_PORT = "19530"  # Default port for Milvus standalone
COLLECTION_NAME = "IPC_collection"

# Store chunks into Milvus (Docker)
vector_store_saved = Milvus.from_documents(
    [Document(page_content=chunk.page_content) for chunk in chunks],
    embedding_function,
    collection_name=COLLECTION_NAME, 
    connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT},
    index_params={"index_type": "FLAT"}  # Ensure FLAT index type for accurate similarity search
)
print("Embeddings stored in Milvus (Docker). Ready for queries!")