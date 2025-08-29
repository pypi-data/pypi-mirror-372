# topic modeling added.
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
from nltk.corpus import words
import time
from streamlit_pdf_viewer import pdf_viewer
import fitz # PyMuPDF
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
nltk.download('words')

# --- Configuration and Constants ---
# Assuming the data folder is in the same directory as the script.
DATA_DIR = "data"
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
OCR_DIR = os.path.join(DATA_DIR, "ocr")
CHROMA_DB_PATH = "chroma_db"
# Ensure the necessary directories exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(OCR_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.error("OpenAI API key is not set. Please add it to your Streamlit secrets.")
    st.stop()

openai.api_key = OPENAI_API_KEY

def count_tokens(text):
    return len(text) / 4

MAX_TOKENS = 8000
MAX_RESPONSE_TOKENS = 500

# Download necessary NLTK data if you haven't already
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    with st.spinner("Downloading NLTK stopwords data... This only happens once."):
        nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/words')
except nltk.downloader.DownloadError:
    with st.spinner("Downloading NLTK words corpus... This only happens once."):
        nltk.download('words', quiet=True)

english_words = set(words.words())
english_stopwords = set(stopwords.words('english'))

# --- Helper Functions ---

def preprocess_text(text):
    """
    Performs robust text preprocessing to remove non-English content and stopwords.
    """
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    filtered_tokens = [word for word in tokens if word in english_words and word not in english_stopwords]
    cleaned_text = " ".join(filtered_tokens)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Splits a long text into smaller chunks.
    """
    chunks = []
    text_len = len(text)
    start_index = 0
    while start_index < text_len:
        end_index = start_index + chunk_size
        if end_index > text_len:
            end_index = text_len
        chunk = text[start_index:end_index]
        chunks.append(chunk)
        start_index += chunk_size - overlap
        if start_index < 0:
            start_index = 0
    return chunks

def calculate_readability(text):
    """
    Calculates the Flesch Reading Ease Score for a given text.
    Score: 20-30 (very difficult), 60-70 (easily understood).
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if len(s) > 0]
    num_sentences = len(sentences)
    words = re.findall(r'\b\w+\b', text)
    num_words = len(words)
    syllables = sum([len(re.findall(r'[aeiouy]+', word.lower())) for word in words])
    
    if num_words < 5 or num_sentences == 0:
        return 'N/A'
    
    score = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllables / num_words)
    return max(0, score)

def calculate_sentiment(text):
    """
    A simple rule-based sentiment analysis function.
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
    """Loads and processes text from OCR JSON files."""
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
                    text = data.get('text') or data.get('content', '')
                    text = text.strip()
                    if text:
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
    but only if they are not already present.
    """
    if df_docs.empty:
        return

    existing_ids = set(collection.get(include=[])['ids'])

    texts_to_add = []
    metadatas_to_add = []
    ids_to_add = []

    st.info("Preparing to index documents...")

    for index, row in df_docs.iterrows():
        doc_filename = row['fileName']
        full_text = row['text']

        chunks = chunk_text(full_text)

        for i, chunk in enumerate(chunks):
            doc_id = f"{doc_filename}_chunk_{i}"
            if doc_id not in existing_ids:
                texts_to_add.append(chunk)
                metadatas_to_add.append({'source': doc_filename})
                ids_to_add.append(doc_id)

    if texts_to_add:
        st.info(f"Indexing {len(texts_to_add)} new document chunks. This may take a moment...")

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
        st.rerun()

def real_ocr(file_path):
    """
    A real OCR function using PyMuPDF to extract text from a PDF.
    """
    st.info("Performing text extraction on the uploaded document...")
    extracted_text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            extracted_text += page.get_text()
        doc.close()
        st.success("Text extraction completed successfully!")
        return extracted_text
    except Exception as e:
        st.error(f"An error occurred during text extraction: {e}")
        return ""

def perform_topic_modeling(df, num_topics=5, num_top_words=10):
    """
    Performs topic modeling using Latent Dirichlet Allocation (LDA)
    and returns the top keywords for each topic.
    """
    documents = df['text'].tolist()
    if not documents:
        return None

    vectorizer = CountVectorizer(stop_words=list(english_stopwords), ngram_range=(1, 2))
    dtm = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()

    lda = LatentDirichletAllocation(
        n_components=num_topics,
        random_state=42,
        learning_method='online',
        learning_decay=0.9
    )
    lda.fit(dtm)

    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[:-num_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words)}")
    
    return topics

# --- Streamlit UI ---

st.set_page_config(page_title="Document Analysis & RAG Chatbot", layout="wide")
st.title("📄 Document Analysis & RAG Chatbot")
st.markdown("This application helps you analyze a collection of documents and chat with them using a RAG system.")

# Initialize session state for the document data and chroma client
if 'df_docs' not in st.session_state:
    st.session_state.df_docs = load_document_data()
    if not st.session_state.df_docs.empty:
        st.session_state.df_docs['text'] = st.session_state.df_docs['text'].apply(preprocess_text)

if 'collection' not in st.session_state:
    try:
        st.session_state.collection = get_or_create_collection()
        index_all_documents(st.session_state.df_docs, st.session_state.collection)
    except Exception as e:
        st.error(f"Error initializing ChromaDB or indexing documents: {e}")
        st.session_state.collection = None

tab1, tab2 = st.tabs([" Document Analysis", "RAG Chatbot"])

with tab1:
    st.header("Document Analysis Dashboard")

    st.subheader("Upload New Document (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF file to upload", type="pdf")
    if uploaded_file:
        with st.spinner("Processing uploaded file..."):
            pdf_file_path = os.path.join(DOCUMENTS_DIR, uploaded_file.name)
            file_name_no_ext = os.path.splitext(uploaded_file.name)[0]
            output_json_path = os.path.join(OCR_DIR, f"{file_name_no_ext}.json")

            if not os.path.exists(output_json_path):
                with open(pdf_file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Original PDF saved to: {pdf_file_path}")

                extracted_text = real_ocr(pdf_file_path)
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump({"text": extracted_text}, f, ensure_ascii=False, indent=4)
                st.success(f"Document '{uploaded_file.name}' processed and saved.")

                new_doc = pd.DataFrame([{'fileName': uploaded_file.name, 'text': preprocess_text(extracted_text)}])
                st.session_state.df_docs = pd.concat([st.session_state.df_docs, new_doc], ignore_index=True)
                index_all_documents(st.session_state.df_docs, st.session_state.collection)
            else:
                st.warning("This document has already been processed and is in the database.")
    st.markdown("---")

    if st.session_state.df_docs.empty:
        st.warning("No documents with usable text found. Please upload a PDF file to begin.")
    else:
        st.subheader("Key Insights")
        
        st.session_state.df_docs['word_count'] = st.session_state.df_docs['text'].apply(lambda x: len(x.split()))
        st.session_state.df_docs['sentiment'] = st.session_state.df_docs['text'].apply(calculate_sentiment)
        st.session_state.df_docs['readability_score'] = st.session_state.df_docs['text'].apply(calculate_readability)

        sentiment_counts = st.session_state.df_docs['sentiment'].value_counts(normalize=True) * 100
        most_common_sentiment = sentiment_counts.idxmax()
        most_common_sentiment_percent = sentiment_counts.max()

        avg_word_count = st.session_state.df_docs['word_count'].mean()
        longest_doc = st.session_state.df_docs.loc[st.session_state.df_docs['word_count'].idxmax()]

        topic_results = perform_topic_modeling(st.session_state.df_docs)
        topics_str = '; '.join(topic_results) if topic_results else "No topics found in documents."

        st.markdown(f"""
        - **Overall Sentiment:** The documents are predominantly **{most_common_sentiment.lower()}**, with **{most_common_sentiment_percent:.1f}%** showing this sentiment.
        - **Document Length:** The average document is **{avg_word_count:.0f} words** long. The longest document is **'{longest_doc['fileName']}'** with **{longest_doc['word_count']} words**.
        - **Identified Topics:** The main themes found are: **{topics_str}**.
        """)
        st.markdown("---")

        st.subheader("Document Metrics")
        total_words = st.session_state.df_docs['word_count'].sum()
        
        valid_scores = [score for score in st.session_state.df_docs['readability_score'] if isinstance(score, (int, float))]
        avg_readability = sum(valid_scores) / len(valid_scores) if valid_scores else 'N/A'

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Documents", value=len(st.session_state.df_docs))
        with col2:
            st.metric(label="Total Words", value=f"{total_words:,}")
        with col3:
            st.metric(label="Readability Score", value=f"{avg_readability:.2f}" if isinstance(avg_readability, (int, float)) else "N/A")

        st.markdown("---")
        
        st.subheader("Document Sentiment Breakdown")
        sentiment_counts = st.session_state.df_docs['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        st.bar_chart(sentiment_counts.set_index('Sentiment'))

        st.subheader("Document Topics")
        if topic_results:
            for topic in topic_results:
                st.write(topic)
        else:
            st.info("Not enough data to generate topics.")
            
        st.subheader("Document Content Viewer")
        doc_names = st.session_state.df_docs['fileName'].tolist()
        
        selected_doc_name = ''
        if doc_names:
            with st.popover("Select a document to view"):
                selected_doc_name = st.selectbox("Choose a document:", doc_names)
        else:
            st.info("No documents to display. Please upload a PDF.")

        if selected_doc_name:
            selected_doc_text = st.session_state.df_docs[st.session_state.df_docs['fileName'] == selected_doc_name]['text'].iloc[0]
            pdf_file_path = os.path.join(DOCUMENTS_DIR, selected_doc_name) 
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"Content for: **{selected_doc_name}**")
                if selected_doc_text:
                    st.text_area("Document Content:", value=selected_doc_text, height=800, key=f"doc_viewer_{selected_doc_name}")
                else:
                    st.info("This document has no usable text content.")

            with col2:
                st.subheader("Original PDF Viewer")
                if os.path.exists(pdf_file_path):
                    binary_content = open(pdf_file_path, 'rb').read()
                    pdf_viewer(input=binary_content, key=f"pdf_viewer_{selected_doc_name}")
                else:
                    st.warning(f"PDF file '{selected_doc_name}' not found.")
                    st.info("Please ensure the original PDF is in the same directory as the script to view it.")

with tab2:
    st.header("RAG Chatbot")

    def clear_chat_history():
        st.session_state.messages = []
    
    st.button('Clear Chat History', on_click=clear_chat_history)
    st.info("Ask a question about the documents. The chatbot will retrieve relevant information and answer your query.")

    if st.session_state.collection is None or st.session_state.df_docs.empty:
        st.warning("The chatbot is currently unavailable because no documents were indexed. Please ensure your `data/ocr` and `data/documents` directories contain files with text content, then try rerunning the application.")
    else:
        doc_names = st.session_state.df_docs['fileName'].tolist()
        doc_options = ["All Documents"] + sorted(doc_names)
        
        selected_paper = st.selectbox("Search within a specific paper?", options=doc_options, index=0)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_query := st.chat_input("Ask a question about the documents..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.spinner("Searching for answers..."):
                try:
                    doc_filter = {}
                    if selected_paper != "All Documents":
                        doc_filter = {"source": selected_paper}

                    results = st.session_state.collection.query(
                        query_texts=[user_query],
                        n_results=3,
                        where=doc_filter if doc_filter else None
                    )
                    
                    if not results['documents'][0]:
                        bot_response = "I'm sorry, I could not find any relevant information in the documents to answer your question."
                        st.session_state.messages.append({"role": "assistant", "content": bot_response})
                        with st.chat_message("assistant"):
                            st.markdown(bot_response)
                        st.stop()

                    unique_sources = {}
                    for i, doc_text in enumerate(results['documents'][0]):
                        source = results['metadatas'][0][i]['source']
                        if source not in unique_sources:
                            unique_sources[source] = []
                        unique_sources[source].append({
                            'text': doc_text,
                            'score': results['distances'][0][i]
                        })

                    context = ""
                    for source, chunks in unique_sources.items():
                        context += f"Source: {source}\n---\n"
                        for chunk in chunks:
                            context += f"{chunk['text']}\n"
                        context += "\n"
                    
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
                    
                    if count_tokens(user_message) > MAX_TOKENS:
                        bot_response = "The query and retrieved documents are too long to process. Please try a shorter query or use fewer documents."
                    else:
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

                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)

                    with st.expander("Show Sources"):
                        for source, chunks in unique_sources.items():
                            st.markdown(f"**Document:** {source}")
                            for chunk in chunks:
                                st.markdown(f"_(Similarity Score: {chunk['score']:.2f})_")
                                st.text(chunk['text'])
                            st.markdown("---")
                except Exception as e:
                    st.error(f"An error occurred while generating the response: {e}")