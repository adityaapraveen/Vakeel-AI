# Legal Chatbot

![Chatbot Home Page Interface](images/preview.jpeg)

## Overview

This project is a legal chatbot that provides legal advice and helps users with various legal queries. The chatbot uses a combination of advanced technologies such as Retrieval-Augmented Generation (RAG), semantic search, vector databases, and large language models (LLMs) to provide precise and relevant answers. It utilizes Milvus as a vector database for indexing legal documents, and Ollama (Llama 3.2 1B parameters) as the underlying large language model to interpret user queries.

The frontend is developed using React and Vite, while the backend is built using Flask. 

## Features

1. **IPC Section Query Assistance**: The chatbot can interpret and respond to user queries related to sections of the Indian Penal Code (IPC). It retrieves the most relevant IPC sections based on the user's query, with their brief descriptions.
2. **Legal Document Generation**: The chatbot can help in drafting various legal documents, such as contracts, agreements, and notices, by guiding the user through the necessary inputs.
3. **Precedents Search**: The chatbot can assist users in finding relevant case law precedents. It retreives key cases along with their citations and summaries, helping users understand judicial interpretations and their implications under Indian law.

## Tech Stack

- **Frontend**: React, Vite
- **Backend**: Flask
- **Semantic Search**: Retrieval-Augmented Generation (RAG) with Milvus vector database
- **LLM**: Ollama (Llama 3.2 with 1B parameters)

## How It Works

[Watch Video](images/2025-07-29 11-16-00.mkv)

1. **Query Processing**: The user enters a query through the frontend interface. The query is processed and sent to the backend Flask server.
2. **Semantic Search**: The query is run against a vectorized database of legal documents stored in Milvus, using semantic search. This search retrieves relevant legal content, such as IPC sections, case precedents, or other legal information.
3. **LLM Response Generation**: The retrieved information is passed to Ollama's LLM, which then generates a precise and coherent response to the user’s query.
4. **Frontend Display**: The response is returned to the frontend, where it is displayed to the user in an easy-to-read format.

## Requirements

- Python 3.8 or higher
- Node.js (for React and Vite)
- Milvus (for vector storage)
- Ollama LLM
- Flask

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/reethuthota/Legal_Chatbot.git
    cd Legal_Chatbot
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install backend dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Milvus Setup

1. Follow the Milvus installation guide to set up the Milvus vector database on your system using docker.
2. Run Milvus from your terminal using 
    ```bash
    bash standalone_embed.sh start
    ```
3. Run the script to make collections on the vector database.
    ```bash
    create_collections.py
    ```

### Ollama LLM Integration

1. Ensure that Ollama is properly installed and running on your machine. Refer to the Ollama documentation for installation instructions.
2. Download the Llama 3.2 with 1B parameters model
    ```bash
    ollama run llama3.2:1b
    ```

### Backend Setup (Flask)

1. Start the Flask backend:

    ```bash
    cd backend
    python app.py
    ```

   The backend server will be running on `http://localhost:8080`.

### Frontend Setup (React + Vite)

1. Install frontend dependencies:

    ```bash
    cd frontend
    npm install
    ```

2. Run the frontend development server:

    ```bash
    npm run dev
    ```

   The frontend will be available at `http://localhost:5173`.

## Usage

- **IPC Section Queries**: To inquire about a specific section of the Indian Penal Code, simply type the section number or describe your query. For example: “What is Section 302 of the IPC?” The chatbot will retrieve the relevant sections and provide concise descriptions.

- **Legal Document Creation**: To create a legal document (e.g., an affidavit, agreement, or contract), you must provide a detailed prompt that includes all the necessary information. For example, if you want to generate a **rental agreement**, your prompt should include the following details:
  - **Names of the parties** (e.g., Landlord and Tenant)
  - **Property address**
  - **Terms of the agreement** (e.g., rent amount, security deposit)
  - **Duration of the lease** (e.g., 1 year)
  - **Any special clauses or terms** (e.g., restrictions on subletting, maintenance responsibilities)

- **Precedent Search**: You can request the chatbot to search for relevant case law precedents by providing case details or describing the legal issue you're researching. The chatbot will search through past case law and return relevant cases along with citations and summaries.

## Contributing

If you'd like to contribute to the development of the Legal Chatbot, feel free to fork the repository and submit a pull request with your changes. Please ensure that your code follows the project's coding standards and is well-documented.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
