# everything works

import streamlit as st
import pandas as pd
import json
import os
import chromadb
from chromadb.utils import embedding_functions
from collections import Counter
import re
import random
import requests
import openai
import nltk
from nltk.corpus import stopwords

# --- Configuration and Constants ---
# Assuming the data folder is in the same directory as the script.
DATA_DIR = "data"
OCR_DIR = os.path.join(DATA_DIR, "ocr")
CHROMA_DB_PATH = "chroma_db"
# Ensure the OpenAI API key is set as a secret in Streamlit
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.error("OpenAI API key is not set. Please add it to your Streamlit secrets.")
    st.stop()
    
# Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY

# A basic tokenizer estimate for token limits
# This is a simple character-based estimate and not a true tokenization, but
# it is sufficient for preventing large requests and controlling costs.
def count_tokens(text):
    return len(text) / 4

MAX_TOKENS = 8000
MAX_RESPONSE_TOKENS = 500

# --- Helper Functions ---

def preprocess_text(text):
    """
    Performs basic text preprocessing for RAG.
    - Converts to lowercase.
    - Removes excessive whitespace and newlines.
    """
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Splits a long text into smaller chunks based on a fixed chunk size and overlap.
    This is crucial for handling large documents that exceed the embedding model's
    token limit. The overlap helps maintain context between chunks.
    """
    chunks = []
    text_len = len(text)
    start_index = 0
    while start_index < text_len:
        end_index = start_index + chunk_size
        # Ensure we don't go past the end of the text
        if end_index > text_len:
            end_index = text_len
        
        # Add the chunk to the list
        chunk = text[start_index:end_index]
        chunks.append(chunk)

        # Move the start index for the next chunk with overlap
        start_index += chunk_size - overlap
        if start_index < 0:
            start_index = 0 # Should not happen with positive overlap

    return chunks

def calculate_sentiment(text):
    """
    A simple rule-based sentiment analysis function.
    Assigns sentiment based on the presence of predefined keywords.
    """
    positive_words = ['good', 'great', 'excellent', 'striking', 'success', 'successful', 'improve', 'enhances', 'novelty', 'significant', 'robust']
    negative_words = ['challenge', 'limitations', 'error', 'difficult', 'bias', 'biased', 'sub-optimal', 'non-separable', 'unbalanced', 'unbiased']

    text_lower = text.lower()
    positive_score = sum(1 for word in positive_words if word in text_lower)
    negative_score = sum(1 for word in negative_words if word in text_lower)

    if positive_score > negative_score:
        return 'Positive'
    elif negative_score > positive_score:
        return 'Negative'
    else:
        return 'Neutral'

def load_document_data():
    """Loads and processes text from OCR JSON files, filtering for usable documents."""
    processed_docs = []
    if not os.path.exists(OCR_DIR):
        st.warning(f"OCR directory not found: {OCR_DIR}. No pre-existing documents will be loaded.")
        return pd.DataFrame(processed_docs)

    for json_file in os.listdir(OCR_DIR):
        if json_file.endswith(".json"):
            file_path = os.path.join(OCR_DIR, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check for both 'text' and 'content' keys as some OCR tools may use different keys
                    text = data.get('text') or data.get('content', '')
                    text = text.strip()
                    if text:  # Only add documents with usable text
                        processed_docs.append({
                            'fileName': os.path.splitext(json_file)[0] + '.pdf',
                            'text': text
                        })
            except (json.JSONDecodeError, FileNotFoundError) as e:
                st.warning(f"Skipping malformed or missing JSON file: {json_file}. Error: {e}")
                continue
    return pd.DataFrame(processed_docs)

def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def get_or_create_collection():
    """
    Gets or creates the ChromaDB collection with the correct embedding function.
    """
    chroma_client = get_chroma_client()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name="text-embedding-ada-002"
    )
    return chroma_client.get_or_create_collection(
        name="document_collection",
        embedding_function=openai_ef
    )

def index_all_documents(df_docs, collection):
    """
    Indexes all documents from the DataFrame into the collection,
    but only if they are not already present. This function now chunks
    large documents to avoid token limits.
    """
    if df_docs.empty:
        # No documents to index, so we return immediately.
        return

    existing_ids = set(collection.get(include=[])['ids'])
    
    texts_to_add = []
    metadatas_to_add = []
    ids_to_add = []

    st.info("Preparing to index documents...")
    
    for index, row in df_docs.iterrows():
        doc_filename = row['fileName']
        full_text = row['text']
        
        # Chunk the large document into smaller pieces
        chunks = chunk_text(full_text)

        for i, chunk in enumerate(chunks):
            doc_id = f"doc_{index}_chunk_{i}"
            if doc_id not in existing_ids:
                texts_to_add.append(chunk)
                metadatas_to_add.append({'source': doc_filename})
                ids_to_add.append(doc_id)

    if texts_to_add:
        st.info(f"Indexing {len(texts_to_add)} new document chunks. This may take a moment...")
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(texts_to_add), batch_size):
            batch_texts = texts_to_add[i:i + batch_size]
            batch_metadatas = metadatas_to_add[i:i + batch_size]
            batch_ids = ids_to_add[i:i + batch_size]
            collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        st.success("Indexing complete!")


# --- Streamlit UI ---

st.set_page_config(page_title="Document Analysis & RAG Chatbot", layout="wide")
st.title("📄 Document Analysis & RAG Chatbot")
st.markdown("This application helps you analyze a collection of documents and chat with them using a RAG system.")

# Initialize session state for the document data and chroma client
if 'df_docs' not in st.session_state:
    st.session_state.df_docs = load_document_data()
    # Pre-process text after loading
    if not st.session_state.df_docs.empty:
        st.session_state.df_docs['text'] = st.session_state.df_docs['text'].apply(preprocess_text)

if 'collection' not in st.session_state:
    try:
        st.session_state.collection = get_or_create_collection()
        index_all_documents(st.session_state.df_docs, st.session_state.collection)
    except Exception as e:
        st.error(f"Error initializing ChromaDB or indexing documents: {e}")
        st.session_state.collection = None

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["📊 Document Analysis", "🤖 RAG Chatbot"])

with tab1:
    st.header("Document Analysis Dashboard")
    
    if st.session_state.df_docs.empty:
        st.warning("No documents with usable text found. Please check your `data/ocr` directory and the content of your JSON files.")
    else:
        # --- Metrics and Visualizations ---
        st.subheader("Key Insights")

        # Download NLTK stopwords data if not already present
        try:
            nltk.data.find('corpora/stopwords')
        except IOError: # Use a more general exception for robustness
            with st.spinner("Downloading NLTK stopwords data... This only happens once."):
                nltk.download('stopwords', quiet=True)
        
        # Calculate word counts and sentiment for insights
        st.session_state.df_docs['word_count'] = st.session_state.df_docs['text'].apply(lambda x: len(x.split()))
        st.session_state.df_docs['sentiment'] = st.session_state.df_docs['text'].apply(calculate_sentiment)

        # Insight 1: Overall Sentiment
        sentiment_counts = st.session_state.df_docs['sentiment'].value_counts(normalize=True) * 100
        most_common_sentiment = sentiment_counts.idxmax()
        most_common_sentiment_percent = sentiment_counts.max()
        st.markdown(f"**Insight 1: Overall Sentiment**\n\nThe documents are predominantly **{most_common_sentiment.lower()}**, with **{most_common_sentiment_percent:.1f}%** of them showing this sentiment. This suggests a generally positive or negative tone across the collection.")
        st.markdown("---")

        # Insight 2: Document Length
        avg_word_count = st.session_state.df_docs['word_count'].mean()
        longest_doc = st.session_state.df_docs.loc[st.session_state.df_docs['word_count'].idxmax()]
        st.markdown(f"**Insight 2: Document Length**\n\nThe average document length is **{avg_word_count:.0f} words**. The longest document is **'{longest_doc['fileName']}'** with **{longest_doc['word_count']} words**, indicating a wide range in document complexity and detail.")
        st.markdown("---")
        
        # Insight 3: Top Keywords
        all_words = ' '.join(st.session_state.df_docs['text']).split()
        word_counts = Counter(all_words)
        # Exclude common stopwords and numbers
        common_words = set(stopwords.words('english') + ['the', 'and', 'in', 'of', 'to', 'a', 'is', 'for', 'with', 'as', 'by', 'an'])
        filtered_words = [word for word in all_words if word.lower() not in common_words and word.isalpha()]
        most_common_keywords = Counter(filtered_words).most_common(5)
        keywords_str = ', '.join([f"'{kw}'" for kw, count in most_common_keywords])
        st.markdown(f"**Insight 3: Top Keywords**\n\nThe most frequently mentioned keywords across all documents are **{keywords_str}**. These terms suggest the core themes of the document collection.")
        st.markdown("---")

        # --- Remaining Metrics and Visualizations ---
        st.subheader("Document Metrics")
        
        total_words = st.session_state.df_docs['word_count'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Documents", value=len(st.session_state.df_docs))
        with col2:
            st.metric(label="Total Words", value=f"{total_words:,}")

        # Sentiment Analysis
        sentiment_counts = st.session_state.df_docs['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        st.subheader("Document Sentiment Breakdown")
        st.bar_chart(sentiment_counts.set_index('Sentiment'))
        
        # Keyword Frequency
        st.subheader("Keyword Frequency")
        keywords = ['report', 'agreement', 'marketing', 'revenue', 'finance', 'meeting', 'legal', 'quarterly']
        all_words_keywords = ' '.join(st.session_state.df_docs['text'].str.lower()).split()
        word_counts_keywords = Counter(all_words_keywords)
        keyword_counts = {kw: word_counts_keywords[kw] for kw in keywords}
        
        df_keywords = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Frequency'])
        st.bar_chart(df_keywords.set_index('Keyword'))

        # --- Document Content Viewer ---
        st.subheader("Document Content Viewer")
        doc_names = st.session_state.df_docs['fileName'].tolist()
        selected_doc_name = st.selectbox("Select a document to view:", doc_names)
        
        if selected_doc_name:
            # Safely get the text for the selected document
            selected_doc_text = st.session_state.df_docs[st.session_state.df_docs['fileName'] == selected_doc_name]['text'].iloc[0]
            
            if selected_doc_text:
                st.text_area("Document Content:", value=selected_doc_text, height=500)
            else:
                st.info("This document has no usable text content.")

with tab2:
    st.header("RAG Chatbot")
    
    # Clear chat history button
    def clear_chat_history():
        st.session_state.messages = []
    
    st.button('Clear Chat History', on_click=clear_chat_history)
    
    st.info("Ask a question about the documents. The chatbot will retrieve relevant information and answer your query.")
    
    if st.session_state.collection is None or st.session_state.df_docs.empty:
        st.warning("The chatbot is currently unavailable because no documents were indexed. Please ensure your `data/ocr` directory contains JSON files with text content, then try rerunning the application.")
    else:
        # Chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        if user_query := st.chat_input("Ask a question about the documents..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.spinner("Searching for answers..."):
                try:
                    # Retrieve relevant documents
                    results = st.session_state.collection.query(
                        query_texts=[user_query],
                        n_results=3
                    )
                    
                    # Format context for the LLM
                    context = ""
                    for i, doc_text in enumerate(results['documents'][0]):
                        source = results['metadatas'][0][i]['source']
                        score = results['distances'][0][i]
                        context += f"Source: {source} (Similarity Score: {score:.2f})\n---\n{doc_text}\n\n"
                    
                    # Prepare the system and user messages for the OpenAI API
                    system_prompt = (
                        "You are a helpful assistant for answering questions based on the provided documents. "
                        "Your task is to analyze the provided documents and synthesize the information to provide a comprehensive and insightful summary in response to the user's query. "
                        "Your summary should incorporate data from all relevant sources. "
                        "If the answer is not found in the documents, state that you cannot answer. "
                        "Your response should be a single, well-structured paragraph."
                    )
                    
                    user_message = (
                        f"User question: {user_query}\n\n"
                        f"Documents:\n{context}\n"
                        "Answer:"
                    )
                    
                    # Check the number of tokens to control cost
                    if count_tokens(user_message) > MAX_TOKENS:
                        bot_response = "The query and retrieved documents are too long to process. Please try a shorter query or use fewer documents."
                    else:
                        # Make the API call to the LLM for generation
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message}
                            ],
                            max_tokens=MAX_RESPONSE_TOKENS,
                            temperature=0.7
                        )
                        
                        bot_response = response.choices[0].message.content

                    # Append the LLM response to the chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                    # Display the LLM response
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)

                    # Show sources used for the answer
                    with st.expander("Show Sources"):
                        for i, source in enumerate(results['metadatas'][0]):
                            st.markdown(f"**Document:** {source['source']} (Similarity Score: {results['distances'][0][i]:.2f})")
                            st.text(results['documents'][0][i])
                            st.markdown("---")

                except Exception as e:
                    st.error(f"An error occurred while generating the response: {e}")
