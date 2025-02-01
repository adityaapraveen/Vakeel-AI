import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from together import Together
# from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

# from secret_key import openapi_key
# os.environ['OPENAI_API_KEY'] = openapi_key

client = Together(api_key="")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Custom embedding class for SentenceTransformer
class SentenceTransformerEmbeddings:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        # Embed the documents and return the embeddings
        return self.model.encode(texts, show_progress_bar=True).tolist()

    def embed_query(self, text):
        # Embed a single query (text)
        return self.model.encode([text])[0].tolist()

def main():
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    
    st.title("Multi-PDF Chatbot 💬")
    
    pdf_docs = st.file_uploader("Upload your PDFs here", type="pdf", accept_multiple_files=True)
   #if st.button("Process"):
   
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
            
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len)
    chunks = text_splitter.split_text(text)
    
    if chunks:
        embeddings = SentenceTransformerEmbeddings(model=model)
        # knowledge_base = Chroma.from_texts(chunks, embeddings)
        knowledge_base = Chroma.from_texts(chunks, embeddings, persist_directory="./chroma_db")

    
    
        user_question = st.text_input("Ask a question about your PDF:")
        if user_question:
            docs = knowledge_base.similarity_search(user_question)
            
            collection = knowledge_base.get()
            print(f"Total documents stored: {len(collection['documents'])}")
            
            # llm = OpenAI()
            # chain = load_qa_chain(llm, chain_type="stuff")
            # response = chain.run(input_documents=docs, question=user_question)
            
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[{
                    "role": "user",
                    "content": f"Based on the following text, answer the question:\n\n{docs}\n\n{user_question}"
                }]
            )
            print(response)
            # st.write(response['choices'][0]['message']['content'])
            content = response.choices[0].message.content
            print(content)
            st.write(content)

            
if __name__ == '__main__':
    main()