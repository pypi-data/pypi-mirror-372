# RAG

import streamlit as st
import pandas as pd
import json
import os
import re

# --- 1. SET UP DIRECTORY PATHS ---
# In your real application, you would just place your folders here.
DOCS_DIR = "data/documents"
OCR_DIR = "data/ocr"

# --- 2. DATA LOADING & RETRIEVAL FUNCTIONS ---
@st.cache_data
def load_and_index_documents(docs_directory, ocr_directory):
    """
    Loads OCR JSON data, organizes it, and prepares it for retrieval.
    This function will be the 'database' for our RAG system.
    """
    all_documents = []
    
    # Iterate through all files in the documents directory to get the list of documents
    try:
        for doc_filename in os.listdir(docs_directory):
            # Assume PDF documents, but we only care about the base name
            base_filename = os.path.splitext(doc_filename)[0]
            
            # Construct the path to the corresponding OCR JSON file
            ocr_filepath = os.path.join(ocr_directory, f"{base_filename}.json")
            
            # Try to load the OCR JSON data
            try:
                with open(ocr_filepath, 'r') as f:
                    data = json.load(f)
                    text = data.get('text', '')
                    
                    # Store the document data
                    all_documents.append({
                        'fileName': doc_filename,
                        'text': text
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
        
    return all_documents

def retrieve_snippets(query, documents):
    """
    Retrieves the most relevant text snippets from the documents based on a user query.
    This is the "Retrieval" part of RAG.
    """
    query_words = set(query.lower().split())
    retrieved_results = []
    
    # Simple, keyword-based search
    for doc in documents:
        document_text = doc['text'].lower()
        sentences = re.split(r'(?<=[.!?])\s+', document_text)
        
        for sentence in sentences:
            sentence_words = set(sentence.split())
            
            # Calculate a simple score based on matching keywords
            score = len(query_words.intersection(sentence_words))
            
            if score > 0:
                retrieved_results.append({
                    'score': score,
                    'document_name': doc['fileName'],
                    'snippet': sentence.capitalize()
                })
                
    # Sort results by relevance score (highest score first)
    retrieved_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top 5 unique results to avoid redundancy
    unique_results = []
    seen_snippets = set()
    for result in retrieved_results:
        if result['snippet'] not in seen_snippets:
            unique_results.append(result)
            seen_snippets.add(result['snippet'])
            if len(unique_results) >= 5:
                break
                
    return unique_results

# --- 3. STREAMLIT APP LAYOUT ---
st.set_page_config(
    page_title="Document RAG Chat",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize chat history and documents in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = load_and_index_documents(DOCS_DIR, OCR_DIR)

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
                with st.expander(f"From **{item['document_name']}** (Relevance: {item['score']})"):
                    st.write(item['snippet'])
            

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get a response from the "RAG system"
    retrieved_items = retrieve_snippets(prompt, st.session_state.documents)

    # Display retrieved snippets in a new chat message
    with st.chat_message("assistant"):
        if retrieved_items:
            st.info("Here's what I found in your documents:")
            for item in retrieved_items:
                with st.expander(f"From **{item['document_name']}** (Relevance: {item['score']})"):
                    st.write(item['snippet'])
        else:
            st.warning("I couldn't find any relevant information for that query.")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "type": "rag_response", "content": retrieved_items})
