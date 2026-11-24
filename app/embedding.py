# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model():
    embedding_model=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2" #model convert text into numerical vectors.
    )

    return embedding_model



if __name__ == "__main__":
    embedding_model = get_embedding_model()   
    test_text = "What is the daily ATM cash withdrawal limit?"
    vector = embedding_model.embed_query(test_text)
    print("Vector length: ", len(vector))
    print("First 5 values: ", vector[:5])


# embedding.py-->embedding model deta  hai