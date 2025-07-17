from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility
)
from sentence_transformers import SentenceTransformer
import os
import json
import pickle
import numpy as np
from PyPDF2 import PdfReader
import re
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Milvus connection parameters
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "Precedence_collection"

# Export parameters
EXPORT_FOLDER = "./exported_embeddings"
EXPORT_FILENAME = f"embeddings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create export folder if it doesn't exist
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Connect to Milvus
try:
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    logger.info("Successfully connected to Milvus")
except Exception as e:
    logger.error(f"Failed to connect to Milvus: {e}")
    exit(1)

# Remove collection if it exists
if COLLECTION_NAME in utility.list_collections():
    logger.info(f"Dropping existing collection '{COLLECTION_NAME}'...")
    Collection(COLLECTION_NAME).drop()

# Define fields - Added text field to store actual content
fields = [
    FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=True
    ),
    FieldSchema(
        name="filename",
        dtype=DataType.VARCHAR,
        max_length=512
    ),
    FieldSchema(
        name="text",
        dtype=DataType.VARCHAR,
        max_length=4000  # Adjust based on your chunk size
    ),
    FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=384
    )
]

# Create collection schema
schema = CollectionSchema(fields, description="Collection for Indian legal precedents")

# Create collection
collection = Collection(name=COLLECTION_NAME, schema=schema)
logger.info(f"Created collection '{COLLECTION_NAME}'.")

# Folder containing your PDFs
PDF_FOLDER = "./case_files"

# Lists to track processing results
failed_files = []
successful_files = []

# Helper function to read PDFs with error handling
def read_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                text += page.extract_text() + "\n"
            except Exception as e:
                logger.warning(f"Error reading page {page_num + 1} of {pdf_path}: {e}")
                continue
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to read PDF {pdf_path}: {e}")
        return None

# Helper function to chunk text
def chunk_text(text, chunk_size=3000, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to end at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > start + chunk_size // 2:
                end = start + last_period + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

# Helper function to create embeddings with error handling
def create_embedding(text, model):
    try:
        embedding = model.encode([text])[0]
        return embedding
    except Exception as e:
        logger.error(f"Failed to create embedding for text chunk: {e}")
        return None

# Data structure to store embeddings for export
export_data = {
    "metadata": {
        "collection_name": COLLECTION_NAME,
        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dimension": 384,
        "created_at": datetime.now().isoformat(),
        "total_chunks": 0
    },
    "embeddings": []
}

# Iterate through PDFs and insert data
entities = []
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

logger.info(f"Found {len(pdf_files)} PDFs. Processing...")

for pdf_file in pdf_files:
    file_path = os.path.join(PDF_FOLDER, pdf_file)
    logger.info(f"Processing {pdf_file}...")
    
    # Read PDF with error handling
    text_content = read_pdf_text(file_path)
    
    if not text_content:
        logger.warning(f"No text extracted from {pdf_file}. Adding to failed files list.")
        failed_files.append({
            "filename": pdf_file,
            "error": "No text extracted or file corrupted"
        })
        continue

    try:
        # Chunk the text
        chunks = chunk_text(text_content)
        
        logger.info(f"Processing {pdf_file}: {len(chunks)} chunks")
        
        file_chunks_processed = 0
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue
            
            # Create embedding with error handling
            embedding = create_embedding(chunk, embedding_model)
            
            if embedding is None:
                logger.warning(f"Failed to create embedding for chunk {i} of {pdf_file}")
                continue
            
            # Create a unique identifier for the chunk
            chunk_id = f"{pdf_file}_chunk_{i}"
            
            # Add to entities for Milvus insertion
            entities.append([pdf_file, chunk, embedding])
            
            # Add to export data
            export_data["embeddings"].append({
                "chunk_id": chunk_id,
                "filename": pdf_file,
                "text": chunk,
                "vector": embedding.tolist()  # Convert numpy array to list for JSON serialization
            })
            
            file_chunks_processed += 1
        
        if file_chunks_processed > 0:
            successful_files.append({
                "filename": pdf_file,
                "chunks_processed": file_chunks_processed
            })
        else:
            failed_files.append({
                "filename": pdf_file,
                "error": "No valid chunks could be processed"
            })
            
    except Exception as e:
        logger.error(f"Error processing {pdf_file}: {e}")
        failed_files.append({
            "filename": pdf_file,
            "error": str(e)
        })
        continue

# Update metadata
export_data["metadata"]["total_chunks"] = len(export_data["embeddings"])
export_data["metadata"]["successful_files"] = len(successful_files)
export_data["metadata"]["failed_files"] = len(failed_files)

# Insert data into Milvus
if not entities:
    logger.warning("No valid documents found to insert.")
else:
    try:
        # Transpose entities
        filename_list = [e[0] for e in entities]
        text_list = [e[1] for e in entities]
        vector_list = [e[2] for e in entities]

        collection.insert([filename_list, text_list, vector_list])
        logger.info(f"Inserted {len(filename_list)} text chunks into collection '{COLLECTION_NAME}'.")

        # Create index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()
        logger.info(f"Collection '{COLLECTION_NAME}' is indexed and loaded.")
        
    except Exception as e:
        logger.error(f"Failed to insert data into Milvus: {e}")

# Export embeddings to different formats
try:
    # 1. Export as JSON (human-readable but large)
    json_path = os.path.join(EXPORT_FOLDER, f"{EXPORT_FILENAME}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Exported embeddings to JSON: {json_path}")
    
    # 2. Export as Pickle (efficient for Python)
    pickle_path = os.path.join(EXPORT_FOLDER, f"{EXPORT_FILENAME}.pkl")
    with open(pickle_path, 'wb') as f:
        pickle.dump(export_data, f)
    logger.info(f"Exported embeddings to Pickle: {pickle_path}")
    
    # 3. Export vectors as NumPy arrays (for ML workflows)
    vectors_only = np.array([item["vector"] for item in export_data["embeddings"]])
    numpy_path = os.path.join(EXPORT_FOLDER, f"{EXPORT_FILENAME}_vectors.npy")
    np.save(numpy_path, vectors_only)
    logger.info(f"Exported vectors to NumPy: {numpy_path}")
    
    # 4. Export metadata separately
    metadata_path = os.path.join(EXPORT_FOLDER, f"{EXPORT_FILENAME}_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": export_data["metadata"],
            "text_chunks": [{"chunk_id": item["chunk_id"], "filename": item["filename"], "text": item["text"]} 
                           for item in export_data["embeddings"]]
        }, f, indent=2, ensure_ascii=False)
    logger.info(f"Exported metadata to: {metadata_path}")
    
except Exception as e:
    logger.error(f"Failed to export embeddings: {e}")

# Create processing summary
summary = {
    "total_files_found": len(pdf_files),
    "successful_files": len(successful_files),
    "failed_files": len(failed_files),
    "total_chunks_processed": len(export_data["embeddings"]),
    "successful_file_details": successful_files,
    "failed_file_details": failed_files
}

# Save processing summary
summary_path = os.path.join(EXPORT_FOLDER, f"{EXPORT_FILENAME}_summary.json")
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

# Print summary
logger.info("\n" + "="*50)
logger.info("PROCESSING SUMMARY")
logger.info("="*50)
logger.info(f"Total PDF files found: {summary['total_files_found']}")
logger.info(f"Successfully processed: {summary['successful_files']}")
logger.info(f"Failed to process: {summary['failed_files']}")
logger.info(f"Total chunks created: {summary['total_chunks_processed']}")

if failed_files:
    logger.info("\nFAILED FILES:")
    for failed in failed_files:
        logger.info(f"- {failed['filename']}: {failed['error']}")

if successful_files:
    logger.info("\nSUCCESSFUL FILES:")
    for success in successful_files:
        logger.info(f"- {success['filename']}: {success['chunks_processed']} chunks")

logger.info(f"\nAll export files saved to: {EXPORT_FOLDER}")
logger.info("="*50)

# Example function to load embeddings later
def load_embeddings(export_path):
    """
    Example function to load embeddings from exported files
    """
    if export_path.endswith('.json'):
        with open(export_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif export_path.endswith('.pkl'):
        with open(export_path, 'rb') as f:
            return pickle.load(f)
    elif export_path.endswith('.npy'):
        return np.load(export_path)
    else:
        raise ValueError("Unsupported file format")

# Print usage example
logger.info("\nTo load embeddings later, use:")
logger.info(f"data = load_embeddings('{json_path}')")
logger.info(f"vectors = load_embeddings('{numpy_path}')")