# LLM - OpenAI

import streamlit as st
import pandas as pd
import json
import os
import re
from openai import OpenAI
import numpy as np

# --- 1. SET UP DIRECTORY PATHS ---
DOCS_DIR = "data/documents"
OCR_DIR = "data/ocr"

# --- 2. OPENAI API KEY & MODEL SETUP ---
# IMPORTANT: You must enter your OpenAI API key here.
# You can get one from https://platform.openai.com/api-keys
# If you don't have one, you will get an API authentication error.
# api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else ""
# client = OpenAI(api_key=api_key)

api_key = "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"
client = OpenAI(api_key="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")

# We'll use this model for creating embeddings. It's affordable and effective for this task.
EMBEDDING_MODEL = "text-embedding-ada-002"

# --- 3. DATA LOADING & RETRIEVAL FUNCTIONS --
@st.cache_data
def load_and_index_documents(docs_directory, ocr_directory):
    """
    Loads OCR JSON data, organizes it, and prepares it for retrieval.
    This function chunks the documents and creates embeddings for each chunk.
    """
    all_chunks = []
    
    try:
        for doc_filename in os.listdir(docs_directory):
            base_filename = os.path.splitext(doc_filename)[0]
            ocr_filepath = os.path.join(ocr_directory, f"{base_filename}.json")
            
            try:
                with open(ocr_filepath, 'r') as f:
                    data = json.load(f)
                    text = data.get('text', '')
                    
                    # Split the document text into sentences to create smaller, more useful chunks
                    sentences = re.split(r'(?<=[.!?])\s+', text)
                    
                    # Create embeddings for each sentence. This is the core of the RAG index.
                    for sentence in sentences:
                        if len(sentence.strip()) > 0:
                            embedding = client.embeddings.create(
                                input=sentence,
                                model=EMBEDDING_MODEL
                            ).data[0].embedding
                            
                            all_chunks.append({
                                'fileName': doc_filename,
                                'text_chunk': sentence,
                                'embedding': embedding
                            })
            except FileNotFoundError:
                st.warning(f"OCR JSON file not found for {doc_filename}. Skipping this document.")
                continue
            
    except FileNotFoundError:
        st.error(f"Directory not found: Please ensure you have a '{docs_directory}' and '{ocr_directory}' folder with your files.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred during file loading: {e}")
        st.stop()
        
    return all_chunks

def retrieve_snippets_with_openai(query, chunks):
    """
    Retrieves the most relevant text snippets using cosine similarity.
    This is the "Retrieval" part of RAG using semantic search.
    """
    if not chunks:
        return []

    # Get the embedding for the user's query
    query_embedding = client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    ).data[0].embedding
    
    # Calculate cosine similarity between the query and all chunk embeddings
    scores = []
    for i, chunk in enumerate(chunks):
        chunk_embedding = np.array(chunk['embedding'])
        # A simple dot product works for embeddings normalized to unit length
        score = np.dot(query_embedding, chunk_embedding)
        scores.append({'score': score, 'index': i})
    
    # Sort by score
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Return the top 5 unique results
    retrieved_results = []
    seen_snippets = set()
    for score_item in scores:
        chunk = chunks[score_item['index']]
        if chunk['text_chunk'] not in seen_snippets:
            retrieved_results.append({
                'document_name': chunk['fileName'],
                'snippet': chunk['text_chunk'],
                'score': score_item['score']
            })
            seen_snippets.add(chunk['text_chunk'])
            if len(retrieved_results) >= 5:
                break
                
    return retrieved_results

# --- 4. STREAMLIT APP LAYOUT ---
st.set_page_config(
    page_title="Document RAG Chat",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check for API key before anything else
if not api_key:
    st.error("OpenAI API key is not set. Please add it to `st.secrets.toml` or directly in the script.")
    st.stop()

# Initialize chat history and documents in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chunks" not in st.session_state:
    with st.spinner("Indexing documents... this may take a moment."):
        st.session_state.chunks = load_and_index_documents(DOCS_DIR, OCR_DIR)

st.title("🗣️ Document Q&A Chat")
st.markdown("Ask a question, and I'll find the most relevant information in your documents.")
st.write("")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "rag_response":
            st.info("Here's what I found in your documents:")
            for item in message["content"]:
                # Use st.expander to make the response collapsible and clean
                with st.expander(f"From **{item['document_name']}** (Similarity: {item['score']:.2f})"):
                    st.write(item['snippet'])

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get a response from the "RAG system"
    with st.spinner("Searching documents..."):
        retrieved_items = retrieve_snippets_with_openai(prompt, st.session_state.chunks)

    # Display retrieved snippets in a new chat message
    with st.chat_message("assistant"):
        if retrieved_items:
            st.info("Here's what I found in your documents:")
            for item in retrieved_items:
                with st.expander(f"From **{item['document_name']}** (Similarity: {item['score']:.2f})"):
                    st.write(item['snippet'])
        else:
            st.warning("I couldn't find any relevant information for that query.")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "type": "rag_response", "content": retrieved_items})

