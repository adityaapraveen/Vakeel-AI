import os
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from sentence_transformers import SentenceTransformer
import pytesseract
from PIL import Image

# ====== Config ======
IMAGE_PATH = "legalform1.webp"  # <--- Replace with your image path
EMBEDDING_DIM = 768
COLLECTION_NAME = "Document_Creation_collection"

# ====== Connect to Milvus ======
connections.connect(alias="default", host="localhost", port="19530")

# ====== Define Schema ======
fields = [
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=255)
]
schema = CollectionSchema(fields=fields, description="Legal document embeddings")

# ====== Create Collection ======
if not utility.has_collection(COLLECTION_NAME):
    print("Creating collection...")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
else:
    collection = Collection(name=COLLECTION_NAME)
collection.load()

# ====== Extract Text from Image ======
image = Image.open(IMAGE_PATH)
extracted_text = pytesseract.image_to_string(image)

# Clean up extracted text
extracted_text = extracted_text.strip().replace('\n', ' ')
if not extracted_text:
    raise ValueError("No text found in the image.")

# ====== Generate Embedding ======
model = SentenceTransformer("all-MiniLM-L6-v2")  # Or your own model
embedding_vector = model.encode(extracted_text).tolist()

# ====== Prepare Data ======
data = [
    [extracted_text],         # text (PK)
    [embedding_vector],       # vector
    [os.path.basename(IMAGE_PATH)]  # filename
]

# ====== Insert Into Milvus ======
collection.insert(data)
print(f"Inserted document from {IMAGE_PATH} into Milvus.")
