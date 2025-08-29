# EDA

import streamlit as st
import pandas as pd
import json
import os
from collections import Counter

# --- 1. SET UP DIRECTORY PATHS ---
# In your real application, you would just place your folders here.
DOCS_DIR = "data/documents"
OCR_DIR = "data/ocr"

# --- 2. DATA LOADING & ANALYSIS FUNCTIONS ---
@st.cache_data
def load_and_analyze_data(docs_directory, ocr_directory):
    """Loads OCR JSON data from a directory and performs analysis."""
    processed_docs = []
    keyword_counts = Counter()
    sentiment_counts = Counter()
    
    # Simple keyword lists for analysis
    positive_words = {'strong', 'successfully', 'high', 'milestone', 'welcome', 'valued', 'inclusive', 'grow', 'positive'}
    negative_words = {'competitive', 'disputes', 'difficult', 'challenge', 'issue'}
    common_keywords = {'report', 'agreement', 'plan', 'company', 'services', 'growth', 'team', 'marketing', 'revenue'}

    # Use a dictionary to store a mapping from document name to its content for quick lookup.
    document_texts = {}
    
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
                    document_texts[doc_filename] = text
            except FileNotFoundError:
                # Handle cases where the OCR file is missing
                st.warning(f"OCR JSON file not found for {doc_filename}. Skipping analysis for this document.")
                continue
            
            # Basic analysis for each document
            word_count = len(text.split())
            
            # Simple sentiment score
            lower_text = text.lower()
            sentiment_score = sum(1 for word in positive_words if word in lower_text) - sum(1 for word in negative_words if word in negative_words)
            sentiment = 'Positive' if sentiment_score > 0 else 'Negative' if sentiment_score < 0 else 'Neutral'
            
            processed_docs.append({
                'fileName': doc_filename,
                'wordCount': word_count,
                'sentiment': sentiment,
                'text': text
            })
            
            # Count keywords across all documents
            words = lower_text.split()
            cleaned_words = [w.strip('.,;:') for w in words]
            keyword_counts.update([w for w in cleaned_words if w in common_keywords])
            
            # Count sentiment across all documents
            sentiment_counts[sentiment] += 1
            
    except FileNotFoundError:
        st.error(f"Directory not found: Please ensure you have a '{docs_directory}' and '{ocr_directory}' folder with your files.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()

    # Convert data for plotting with pandas
    df_docs = pd.DataFrame(processed_docs)
    df_keywords = pd.DataFrame(keyword_counts.items(), columns=['Keyword', 'Count'])
    df_sentiment = pd.DataFrame(sentiment_counts.items(), columns=['Sentiment', 'Count'])
    
    return df_docs, df_keywords, df_sentiment

# Load and analyze the data from your specified folders
df_docs, df_keywords, df_sentiment = load_and_analyze_data(DOCS_DIR, OCR_DIR)


# --- 3. STREAMLIT APP LAYOUT ---
st.set_page_config(
    page_title="Document EDA App",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📄 Document Explorer")
st.markdown("Discover insights from your document collection.")
st.write("") # Add some vertical space

# --- Sidebar for document selection ---
st.sidebar.header("Document Viewer")
selected_doc_name = st.sidebar.selectbox(
    "Select a document to view:",
    df_docs['fileName']
)

# Find the full text for the selected document
selected_doc_text = df_docs[df_docs['fileName'] == selected_doc_name]['text'].iloc[0]

# Display the document text in the sidebar
st.sidebar.markdown(f"**Text from {selected_doc_name}**")
st.sidebar.text_area("Document Content", selected_doc_text, height=300)

# --- Main Content Area ---
st.header("📊 Key Insights")

# Create two columns for the charts
col1, col2, col3 = st.columns(3)

# Bar chart for Document Word Counts
with col1:
    st.subheader("Document Word Counts")
    st.bar_chart(df_docs.set_index('fileName')['wordCount'])

# Bar chart for Keyword Frequency
with col2:
    st.subheader("Top Keyword Frequency")
    st.bar_chart(df_keywords.set_index('Keyword')['Count'])

# Bar chart for Sentiment
with col3:
    st.subheader("Overall Sentiment")
    st.bar_chart(df_sentiment.set_index('Sentiment')['Count'])
