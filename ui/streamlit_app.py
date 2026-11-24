import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Banking Policy Knowledge Assistant",
    page_icon="🏦"
)

st.title("🏦 Banking Policy Knowledge Assistant")

st.write(
    "Upload a banking policy PDF and ask Questions"
    "based on the document."
)

# PDF Uploader
uploaded_file = st.file_uploader(
    "Upload Banking Policy PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    if st.button("Process PDF"):
        files = {
            "file":(
                uploaded_file.name, 
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/documents/upload",
                files=files,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                st.success(
                    "PDF processed successfully."
                )

                st.write("File:",result["file_name"])
                st.write("Pages:",result["total_pages"])
                st.write("Chunks:",result["total_chunks"])
            else:
                st.error(
                    response.json().get(
                        "detail",
                        "Unable to process PDF."
                    )
                )
        except requests.RequestException:
            st.error("Unable to connect to the FastAPI backend.")


st.divider()
st.subheader("Ask a Question")
question = st.text_input(
    "Enter your question"
)
if st.button("Ask Question"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.post(f"{API_BASE_URL}/questions/ask", json={"question":question}, timeout=120)

            if response.status_code == 200:
                result = response.json()
                st.subheader("Answer")
                st.write(result["answer"])

                if result["sources"]:
                    st.subheader("sources")
                    for source in result["sources"]:
                        st.write(
                            f"{source["file_name"]}"
                            f"-page{source["page_number"]}"
                        )

            else:
                st.error(
                    response.json().get(
                        "detail",
                        "Unable to generate answer."
                    )
                )

        except requests.RequestException:
            st.error("Unable to connect to the FastAPI backend.")


# Architecture: User-> Streamlit UI ->FasAPI ->RAG Pipeline ->ChromaDB ->Ollama ->Answer+Source  + MYSQL ->Documents Q&A History