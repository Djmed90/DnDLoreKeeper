# Imports
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import re

'''
Using Langchain to split story peices for easier and better searching 
FAISS: local vector database
Document: standard format LangChain uses to wrap text and metadata
and 
Using HuggingFaceEmbeddings local model to create embeddings

'''

def create_vectorstore(chunks, persist_path="vectorstore/"):
    # Wrap the chunks in a document object
    docs = [Document(page_content=c["content"], metadata={"source": c["source"]}) for c in chunks]
    # SLM to embed text into vectors
    embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    # FAISS creates a searchable index from the embedded documents
    # save_local stores the index for future use
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(persist_path)
    

# Define the chunking function
def chunk_documents(file_contents: list, chunk_size=500, chunk_overlap=50):
    # Create an empty list to hold the final chunks
    chunks = []

    # Create a CharacterTextSplitter with your chosen settings
    splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=500,
    chunk_overlap=50,
    length_function=len
    )


    # Loop over each (filename, content) in the file_contents list
    for filename, content in file_contents:
        # Use splitter to split the content into chunks
        split_chunks = splitter.split_text(content)

        # For each chunk, create a dictionary with filename + content
        for chunk in split_chunks:
            chunks.append({
                "source": filename,
                "content": chunk
            })

    # Return a list of dictionarys
    return chunks

def extract_timeline_events(chunks):
    timeline_events = []

    # Match patterns like "Year 123: Something happened"
    pattern = re.compile(r"(?:Year\s+)?(\d{3,4})[:\-–]\s+(.*)", re.IGNORECASE)

    for chunk in chunks:
        lines = chunk.page_content.splitlines()

        for line in lines:
            match = pattern.match(line.strip())
            if match:
                year = int(match.group(1))
                description = match.group(2)
                timeline_events.append((year, description))

    # Sort events by year
    timeline_events.sort(key=lambda x: x[0])
    return timeline_events
