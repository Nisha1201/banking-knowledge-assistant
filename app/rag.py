from langchain_core.prompts import PromptTemplate  #PromptTemplate-->Context+question ko proper prompt me convert karega
from langchain_ollama import ChatOllama  #ChatOllama->Local LLM ko call karega

from app.vectorstore import retrieve_chunks #ChromaDB se relevant chunks retrieve karega

def generate_answer(vector_store, question):
    relevant_chunks = retrieve_chunks(
        vector_store,
        question,
        k=3
    ) 

    if not relevant_chunks:
        return {
            "answer": "I could not find this information in the uploaded document.",
            "sources": []
        }


    context = "\n\n".join(
        chunk.page_content
        for chunk in relevant_chunks
    )

    prompt = PromptTemplate.from_template(
        """
        You are a Banking Policy Knowledge Assistant.

        Answer the user's question using only the provides context.

        If the answer is not available in the context, say:
        "I could not find this information from the uploaded document."
        
        Do not make up banking policies , limits, fees, or rules.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
    )

    llm = ChatOllama(
        model = "llama3.2",
        temperature=0
    )

    chain = prompt | llm
#Why we use try except here? normal flow : Question-> Retriever->Prompt->Ollama->Answer 
# If Ollama has a problem: Question->Ollama unavailable->clear error message instead of showing a long technical exception.


    try:
        response = chain.invoke(
            {
                "context":context,
                "question":question
            }
        )
    except Exception as error:
        raise RuntimeError(
            "Unable to connect to the LLM.",
            "Please make sure Ollama is running.",
            "and the llama3.2 model is available."
        ) from error
    # return response.content

# when we want to return answer+source PDF+ Page number
    # sources = []
    # for chunk in relevant_chunks:
    #     sources.append({
    #         "file_name": chunk.metadata.get("file_name","Unknown"),
    #         "page_number": chunk.metadata.get("page_number","Unknown")
    #     })


# Here we do implement where we remove duplicate sources. i.e if there is top-3 retrieved chunks are present in the same PDF/page through we don't show same same source again and again to user. 
    sources = []
    seen_sources= set()

    for chunk in relevant_chunks:
        file_name = chunk.metadata.get(
            "file_name",
            "Unknown"
        )

        page_number = chunk.metadata.get(
            "page_number",
            "Unknown"
        )

        source_key = (
            file_name,
            page_number
        )

        if source_key not in seen_sources:
            sources.append({
                "file_name":file_name ,
                "page_number":page_number
            })

            seen_sources.add(source_key)

    return {
        "answer": response.content,
        "sources": sources
    }




if __name__ == "__main__":
    print("RAG module loaded successfully")

# Complete Flow: Question--> Retriever--> Relevant chunks--> Context--> Prompt--> LLM-->Answer
# rag.py-->retrieval information ko LLM se connect karke final answer answer banata hai.