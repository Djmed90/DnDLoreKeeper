import os
import streamlit as st
from dotenv import load_dotenv
from textSplitter import chunk_documents, create_vectorstore, extract_timeline_events
from vault_config import load_markdown_files
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# All my api keys are loaded from my .env file so hip hip hurray no problemos
# Set page config FIRST
st.set_page_config(page_title="Lorekeeper AI", layout="wide")

# Load env variables
load_dotenv()
st.title("D&D LoreKeeper")

# Config 
# Only change rebuild to true if I add anything to the vault
REBUILD_VECTORSTORE = False
VAULT_PATH = r"C:\D&D Vault\Obsidian Vault"
VECTORSTORE_DIR = "vectorstore/"

# Initialize embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# If rebuilding is enabled, read files, chunk them, and save a new index
# Otherwise, just load the saved one
if REBUILD_VECTORSTORE:
    st.info("Rebuilding vectorstore...")
    files = load_markdown_files(VAULT_PATH)
    chunks = chunk_documents(files)
    create_vectorstore(chunks)

    # ✅ Load it right after saving
    vectorstore = FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings=embedding,
        allow_dangerous_deserialization=True
    )

    st.success("Vectorstore rebuilt and loaded.")

else:
    try:
        st.info("Loading existing vectorstore from disk...")
        vectorstore = FAISS.load_local(
            VECTORSTORE_DIR,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
        st.success("Vectorstore loaded successfully.")
    except Exception as e:
        st.error(f"Vectorstore not found or failed to load: {e}")
        st.stop()


    # Search and answer part
    # Uses GPT to answer
    # Uses local FAISS database to provide lore context


qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
    retriever=vectorstore.as_retriever()
)

# creates the ui tabs
tab1, tab2, tab3 = st.tabs(["Questions", "Wold builder", "Story Timeline"])

# tab 1 lore questions
with tab1:
    st.subheader("Ask question")
    user_question = st.text_input("Put question here:")
    if user_question:
        with st.spinner("Searching the lore..."):
            answer = qa_chain.run(user_question)
        st.markdown("**Answer:**")
        st.write(answer)

# === Tab 2: World Builder ===
with tab2:
    st.subheader("Im lazy :) ")

    password = st.text_input("No noobs allowed:", type="password")
 
    if password == os.getenv("BUILDER_PASSWORD"):
        st.success("Access granted.")
        creative_prompt = st.text_area("What would you like to generate?", height=150)

        if st.button("Generate Story"):
            with st.spinner("Summoning story magic..."):
                context = "Use the following lore to guide your writing.\n"
                story = ChatOpenAI(model_name="gpt-3.5-turbo")(
                    context + creative_prompt
                ).content

            st.markdown("**Generated Story:**")
            st.write(story)

            if st.button("Save to Vault"):
                output_path = os.path.join("generated", "generated_scene.md")
                os.makedirs("generated", exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(story)
                st.success(f"Saved to {output_path}")

    elif password:
        st.error("Incorrect password.")

with tab3:
    st.subheader("Timeline of Events")
    events = extract_timeline_events(vectorstore.docstore._dict.values())

    if not events:
        st.info("I NEED TO ADD EVENTS SORRY!")
    else:
        for year, desc in events:
            st.markdown(f"**{year}** – {desc}")