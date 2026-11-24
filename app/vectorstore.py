# vector store
from pathlib import Path
import hashlib #it created unique_ID for every chunk.Means if same chunk uploaded twice or repeatedy then same ID will be generated for that.
from langchain_chroma import Chroma
from app.embedding import get_embedding_model

"""
PROJECT_ROOT,CHROMA_PATH we added these to create absolute project path for CHROMADB because 
i was facing issue where chunks are not stored properly before and after PDF uploading.
"""


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT/"chroma_db"

# Duplicate chunk handling
def create_chunk_id(chunk):
    file_name = chunk.metadata.get(
        "file_name",
        "unknown"
    )

    page_number = chunk.metadata.get(
        "page_number",
        0
    )

    text = chunk.page_content
    unique_text = f"{file_name}-{page_number}-{text}"

    return hashlib.sha256(    #hashlib.sha256->it create uniqueID.
        unique_text.encode("utf-8")
    ).hexdigest()


# def create_vector_store(chunks):
#     embedding_model = get_embedding_model()

#     vector_store=Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         collection_name="banking_policies",
#         persist_directory="chroma_db"
#     )

#     # new implementation
#     chunk_id = [
#         create_chunk_id(chunk) for chunk in chunks
#     ]

#     vector_store.add_documents(documents=chunks, ids=chunk_id)

#     return vector_store



def add_chunks_to_vector_store(chunks):

    embedding_model = get_embedding_model()

    vector_store = Chroma(
        collection_name="banking_policies",
        embedding_function=embedding_model,
        # persist_directory="chroma_db"
        persist_directory=str(CHROMA_PATH)
    )

    chunk_ids = [create_chunk_id(chunk) for chunk in chunks]

    vector_store.add_documents(documents=chunks, ids=chunk_ids)
    print("Documents after upload:",vector_store._collection.count())
    print(type(chunk_ids))
    print(chunk_ids[:5])

    return vector_store

def retrieve_chunks(vector_store, question, k=3):
    retriever = vector_store.as_retriever(
        search_kwargs={"k":k}
    )

    relevant_chunks = retriever.invoke(question)

    return relevant_chunks


# # Using score_threshold
# def retrieve_chunks(vector_score, question, k=3, score_threshold=0.5):
#     retriever = vector_score.as_retriever(
#         search_type = "similarity_score_threshold",  #it means return only sufficiently relevant chunks .
#         search_kwargs = {
#                 "k":k,
#                 "score_threshold" : score_threshold
#         }
#     )

#     relevant_chunks = retriever.invoke(question)
#     return relevant_chunks



# Persistent Vector store Cleanup-->Abhi kya hai when we ask question we got "please upload at least one PDF first"even through chromaDB disk par already available hai.
def load_vector_store():
    embedding_model=get_embedding_model()

    vector_store=Chroma(
        collection_name="banking_policies",
        embedding_function=embedding_model,
        # persist_directory="chroma_db"
        persist_directory=str(CHROMA_PATH)
    )

    count = vector_store._collection.count()
    print("chromaDB path:",CHROMA_PATH)
    print("Documents available in ChromaDB:", count)
    return vector_store


# Error handling improve karna.
def has_documents(vector_store):
    try:
        count=vector_store._collection.count()
        return count>0

    except Exception:
        return False
# vectorstore.py --> chunks store aur retrieve karta hai