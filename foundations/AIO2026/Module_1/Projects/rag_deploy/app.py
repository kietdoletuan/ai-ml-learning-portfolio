import os
import time
import tempfile
import pypdf
import chromadb
import ollama
import streamlit as st

EMBED_MODEL = "bge-m3"
LLM_MODEL = "qwen2.5:7b"

PROMPT = """You are a question-answering assistant. Use the context passages below to answer the question.
If the context does not contain the answer, say you don't know. Do not make anything up.
Answer concisely and accurately in English.

Context:
{context}

Question: {question}

Answer:"""

def chunk_text(text, size=2000, overlap=200):
    paras = [p.strip() for p in text.split('\n') if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        while len(p) > size:
            if cur:
                chunks.append(cur.strip())
                cur = ""
            chunks.append(p[:size].strip())
            p = p[size - overlap:]
        if len(p) + len(cur) + 1 <= size:
            cur += p + "\n"
        else:
            if cur:
                chunks.append(cur.strip())
            cur = cur[-overlap:] + p + "\n" if overlap else p + "\n"
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def embed(texts):
    return ollama.embed(model=EMBED_MODEL, input=texts)['embeddings']

def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        path = tmp.name

    text = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(path).pages)
    os.unlink(path)  

    chunks = chunk_text(text)
    client = chromadb.Client()

    col = client.get_or_create_collection(f"rag_{int(time.time())}")
    col.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=chunks,
        embeddings=embed(chunks)
    )
    return col, len(chunks)

def rag(question, collection, k=4):

    res = collection.query(query_embeddings=embed([question]), n_results=k)
    context = "\n\n".join(res["documents"][0])
    resp = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        options={"temperature": 0},
    )
    return resp["message"]["content"]

st.set_page_config(page_title="PDF RAG Chatbot", layout="wide", initial_sidebar_state="expanded")
st.title("PDF RAG Assistant")

if "collection" not in st.session_state:
    st.session_state.collection = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.subheader("Upload Document")
    f = st.file_uploader("Choose a PDF file", type="pdf")
    if f and st.button("Process PDF", use_container_width=True):
        with st.spinner("Processing..."):
            st.session_state.collection, n = process_pdf(f)
            st.session_state.pdf_name = f.name
            st.session_state.chat_history = []
        st.success(f"{n} chunks indexed")
    st.info(f"Loaded: {st.session_state.pdf_name}" if st.session_state.pdf_name else "No document loaded")
    if st.button("Clear chat history", use_container_width=True):
        st.session_state.chat_history = []

for m in st.session_state.chat_history:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if st.session_state.collection is None:
    st.info("Upload and process a PDF before chatting.")
    st.chat_input("Ask a question...", disabled=True)
else:
    q = st.chat_input("Ask a question about your document...")
    if q:
        st.session_state.chat_history.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ans = rag(q, st.session_state.collection)
            st.write(ans)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})