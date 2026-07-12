import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.embeddings import get_embedding_model
from utils.vector_store import create_vector_store
from utils.text_splitter import split_text
from dotenv import load_dotenv
from utils.retriever import get_retriever
from utils.chatbot import get_answer, rewrite_question
import time
from utils.renderer import render_markdown

load_dotenv()

MAX_PREVIEW = 350
STREAM_DELAY = 0.03

if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(
    page_title="AI PDF Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_vector_store(uploaded_files):

    documents, total_pages = extract_text_from_pdf(uploaded_files)

    chunks = split_text(documents)

    embeddings = get_embedding_model()

    vector_store = create_vector_store(
        chunks,
        embeddings,
    )

    return (vector_store, total_pages, len(chunks))


def show_sources(sources):

    shown = set()

    for doc in sources:

        source = (doc.metadata["source"], doc.metadata["page"])

        if source in shown:
            continue

        with st.expander(
            f"📄 {source[0]} • Page {source[1]}",
            expanded=False,
        ):

            st.caption("Retrieved Context")

            preview = (
                doc.page_content[:400] + "..."
                if len(doc.page_content) > 400
                else doc.page_content
            )

            st.write(preview)

            if len(doc.page_content) > 400:

                st.markdown("### Full Context")

                st.code(
                    doc.page_content,
                    language="text",
                )

        shown.add(source)


CUSTOM_CSS = """
<style>

.hero{

padding:35px;

border-radius:20px;

background:linear-gradient(
90deg,
#0f172a,
#1e3a8a
);

color:white;

margin-bottom:25px;

box-shadow:0px 8px 20px rgba(0,0,0,0.3);

}

.hero h1{

margin-bottom:10px;

font-size:45px;

}

.hero p{

font-size:18px;

opacity:0.9;

}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
<div class="hero">

<h1>🤖 AI PDF Chatbot</h1>

<p>
Ask questions across multiple PDFs using
<b>Gemini</b>,
<b>LangChain</b>,
<b>FAISS</b>,
and
<b>RAG</b>.
</p>

</div>
""",
    unsafe_allow_html=True,
)


uploaded_files = st.file_uploader(
    "Upload PDF Files", type="pdf", accept_multiple_files=True
)
if not uploaded_files:

    st.info("""
### 👋 Welcome!

Upload one or more PDF documents to begin.

Once uploaded, you can:

- 📄 Ask questions about your PDFs
- 🔍 Search across multiple documents
- 💬 Ask follow-up questions naturally
- 📚 View the exact source pages used for answers
""")

    st.stop()

with st.sidebar:

    st.header("📂 Workspace")

    st.divider()

    st.subheader("📄 Uploaded PDFs")

    if uploaded_files is not None:

        for pdf in uploaded_files:
            st.success(pdf.name)

    else:
        st.info("No PDFs uploaded.")

    st.divider()

    st.subheader("📊 Project Stats")

    pdf_count = len(uploaded_files) if uploaded_files else 0

    chat_count = len(st.session_state.messages)

    question_count = sum(
        1 for message in st.session_state.messages if message["role"] == "user"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("PDFs", pdf_count)

    with col2:
        st.metric("Messages", chat_count)

    st.metric("AI Model", "Gemini 2.5")

    st.metric("Questions Asked", question_count)

    st.divider()

    st.subheader("⚙️ Tech Stack")

    st.markdown("""
                🧠 **LLM:** Gemini 2.5 Flash
                
                📚 **Embeddings:** Gemini Embedding 2
                
                🔎 **Vector Store:** FAISS
                
                ⚙️ **Framework:** LangChain
                
                📄 **PDF Parser:** PyMuPDF
            """)

    st.divider()

    st.subheader("ℹ️ About")

    st.info("""
### RAG Pipeline

📄 PDF Upload

⬇

✂ Text Chunking

⬇

🧠 Gemini Embeddings

⬇

🔎 FAISS Similarity Search

⬇

🤖 Gemini 2.5 Flash

⬇

💬 Final Answer
""")

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption("""
🚀 **AI PDF Chatbot v1.0**

Built by **Vansh Garg**

Powered by Gemini • LangChain • FAISS
""")


if uploaded_files:

    vector_store, total_pages, total_chunks = load_vector_store(uploaded_files)

    st.success(f"✅ {len(uploaded_files)} PDF(s) ready for querying.")

    st.subheader("📊 Document Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📄 PDFs", len(uploaded_files))

    with col2:
        st.metric("📃 Pages", total_pages)

    with col3:
        st.metric("✂️ Text Chunks", total_chunks)

    with col4:
        st.metric("🧠 Model", "Gemini")

    retriever = get_retriever(vector_store)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_markdown(message["content"])
            else:
                st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                st.divider()
                st.subheader("📚 Sources Used")
                show_sources(message["sources"])

    question = st.chat_input("Ask a question about your uploaded documents...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.write(question)

        start = time.time()

        with st.spinner("🔍 Searching your PDFs..."):
            user_history = [
                message["content"]
                for message in st.session_state.messages
                if message["role"] == "user"
            ]

            history = "\n".join(user_history[:-1][-3:])

            followup_words = [
                "it",
                "this",
                "that",
                "these",
                "those",
                "more",
                "another",
                "another example",
                "example",
                "examples",
                "syntax",
                "code",
                "sample",
                "explain",
                "detail",
                "detailed",
                "why",
                "how",
                "when",
                "where",
            ]
            if history.strip() and any(
                word in question.lower() for word in followup_words
            ):
                rewritten_question = rewrite_question(question, history)
            else:
                rewritten_question = question

            docs = retriever.invoke(rewritten_question)
            if not docs:
                answer = "I couldn't find relevant information in the uploaded PDFs."
                sources = []
            else:
                try:
                    answer, sources = get_answer(rewritten_question, docs)
                except Exception:
                    st.error("""
                        ⚠️ Unable to generate an answer.
                        Possible reasons:
                        • Gemini API temporarily unavailable
                        • API quota exceeded
                        • Internet connection issue
                        Please try again in a few moments.
                        """)
                    st.stop()

            elapsed = time.time() - start

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )

        with st.chat_message("assistant"):

            st.markdown("### 💡 AI Answer")

            render_markdown(answer)

            st.caption(f"⏱ Response generated in {elapsed:.2f} seconds")
            st.divider()
            st.subheader("📚 Sources Used")
            show_sources(sources)
