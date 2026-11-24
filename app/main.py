# PDF Upload + PDF loading /extracting
print("MAIN.PY LOADED")

from langchain_community.document_loaders import PyPDFLoader  #PyPDFLoader saved PDF read karke uske pages ka text extract karta hai.
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.chunking import split_text
# from app.vectorstore import create_vector_store, retrieve_chunks
from app.vectorstore import add_chunks_to_vector_store, retrieve_chunks, load_vector_store, has_documents

from pydantic import BaseModel  #we use BaseModel here to validate user's JSON request.
from app.rag import generate_answer
from app.database import SessionLocal  #It create session for performing database operation with MYSQL.
from app.models import Document , QuestionHistory#its is the SQLAlchemy model of documents table and question history table.

from typing import Annotated

import os


app = FastAPI()
# vector_store = None
vector_store=load_vector_store()

# request model
class QuestionRequest(BaseModel):
    question: str

UPLOAD_FOLDER = "uploaded_documents"  #UPLOAD_FOLDER tells us PDFs kahn save hongi.
os.makedirs(UPLOAD_FOLDER,exist_ok=True)   #It creates folder that is not already exist
@app.get("/")
def home():
    return {"message":"Banking Knowledge Assistant is running."}

# @app.post("/documents/upload")
# async def upload_pdf(file: UploadFile = File(...)):

#     return {
#         "file_name":file.filename,
#         "message":"PDF received successfully"
#     }


"""
Day1: FastAPI setup--> Upload endpoint--> PDF validation--> Save PDF--> Load PDF--> Extract/validate Text--> Error handling
Current application Flow : User--> PDF Upload -->Validation--> Save--> PyPDFLoader -->Extract Text
"""

# Now our flow id  User-->Upload PDF-->Validate PDF-->Save PDF -->
# through this function we need to call api end point again and again when we want to upload multiple pdf.
@app.post("/documents/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store
    # 1. Validate PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2.Create the location where the pdf will be saved
    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    # 3.Read uploaded PDF
    content = await file.read()

    # 4.save PDF
    with open(file_path,"wb") as f:
        f.write(content)


    try:
        #5. Load the saved pdf
        loader = PyPDFLoader(file_path)
        # Extract content from the PDF
        documents = loader.load()
        print(documents[0].page_content)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the uploaded PDF."
        )
    # Empty PDF handling
    # 6.check whether any pages were loaded
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="No content could be extracted from the PDF"
        )

    # 7.combine the extracted test only for validation or check for the readable text
    extracted_text = "\n".join(
        document.page_content.strip()
        for document in documents
    )

    # Check whether the PDF actually contains readable text.
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The Pdf does not contain readable text"

        )

    # Create chunks from loaded documents
    chunks = split_text(documents)
 
    # print first chunk for testing
    print("\nFIRST CHUNK TEXT: ")
    print(chunks[0].page_content)

    print("\nFIRST CHUNK METADATA: ")
    print(chunks[0].metadata)

    # Create embeddings and store chunks in ChromaDB
    # vector_store = create_vector_store(chunks)
    vector_store = add_chunks_to_vector_store(chunks)

    # create MYSQL session
    db=SessionLocal()  #It starts connection/session to work with Mysql.

    try:
        # To Create record
        document_record = Document(
            file_name = file.filename,
            file_path =file_path
        )

        db.add(document_record) #It tells  to SQLAlchemy session, insert this record in database.(Prepare Record)
        db.commit() #Save data to database.
        db.refresh(document_record) # Reload data from database into the Python object.

    finally:
        db.close() #it closes database session properly 


    # Temporary retrieval test
    test_question = "What is the daily ATM cash withdrawal limit?"

    relevant_chunks = retrieve_chunks(
        vector_store,
        test_question,
        k=3
    )

    print("\nUSER QUESTION:")
    print(test_question)

    print("\nRETRIEVED CHUNKS:")
    for index, chunk in enumerate(relevant_chunks,start=1):
        print(f"\n--- Chunk {index} ---")
        print(chunk.page_content)
        print("Metadata: ",chunk.metadata)


    

    # Return successful response
    return {
        "document_id": document_record.id,
        "file_name":file.filename,
        # "message":"PDF Uploaded successfully"
        # "message":"PDF Uploaded and processed successfully",
        # "message":"PDF Uploaded, processed and chunked successfully",
        "message":"PDF Uploaded, processed and stored in vector database successfully",
        "total_pages": len(documents),
        "total_chunks":len(chunks)
    }



# # New implementation of upload_pdf function here we upload multiple pdf in one request:
# @app.post("/documents/upload")
# async def upload_pdf(files: Annotated[list[UploadFile], File()]):
#     global vector_store
#     processed_files = []
#     for file in files:
#         #1. Validate PDF
#         if not file.filename.lower().endswith(".pdf"):
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"{file.filename} is not PDF file."
#             )


#         #2.Create file path:
#         file_path = os.path.join(UPLOAD_FOLDER, file.filename)

#         #3.Read uploaded PDF
#         content = await file.read()

#         #4.Save PDF
#         with open(file_path,"wb") as f:
#             f.write(content)

#         #5.Load PDF
#         try:
#             loader = PyPDFLoader(file_path)
#             documents = loader.load()

#         except Exception:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Unable to read {file.filename}"
#             )

#         #6.Check pages
#         if not documents:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"No content found in {file.filename}"
#             )

#         #7.Check readable text
#         extracted_text = "\n".join(document.page_content.strip() for document in documents)

#         if not extracted_text.strip():
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"No readable text found in {file.filename}"
#             )


#         #8.Check chunks
#         chunks = split_text(documents)

#         #9.Add chunks to ChromaDB
#         vector_store = add_chunks_to_vector_store(chunks)

#         #10.Store processing information
#         processed_files.append(
#             {
#             "file_name":file.filename,
#             "total_pages":len(documents),
#             "total_chunks":len(chunks)
#             }
#         )

#     return {
#         "message":"PDFs added to the banking knowledge base successfully.",
#         "total_files": len(processed_files),
#         "files":processed_files
#     }


@app.post("/questions/ask")
def ask_question(request: QuestionRequest):
    print("\n----- ASK API HIT -----")

    print("Vector Store:", vector_store)

    if vector_store  is not  None:
        try:
            print("Document Count:",vector_store._collection.count())
        except Exception as e:
            print("Count Error:",e)

    print("Question Received:",request.question)


    if vector_store is None or not has_documents(vector_store):
        raise HTTPException(
            status_code=400,
            detail="Knowledge base is empty . Please upload a PDF."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        # answer = generate_answer(
        #     vector_store,
        #     question
        # )

        result = generate_answer(
                vector_store,
                question
            )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate answer:{str(error)}"
        )

    # return {
    #     "question":question,
    #     "answer":answer

    # }

    source_file = None
    source_page = None

    if result["sources"]:

        source_file = result["sources"][0]["file_name"]
        source_page = result["sources"][0]["page_number"]

    # Open MySQL session:
    db = SessionLocal()

    try:
        history_record = QuestionHistory(
            question=question,
            answer=result["answer"],
            source_file=source_file,
            source_page=source_page
        )

        db.add(history_record)
        db.commit()
        db.refresh(history_record)

    finally:
        db.close()


    return {
            "history_id":history_record.id,
            "question":question,
            "answer":result["answer"],
            "sources": result["sources"]
    
        }


@app.get("/questions/history")
def get_question_history():

    db = SessionLocal()
    try:
        records = (
            db.query(QuestionHistory)
            .order_by(QuestionHistory.created_at.desc()) #It shows latest question first.
            .all() #retrieve all matching records
        )

        history = []

        for record in records:
            history.append(
                {
                "id":record.id,
                "question":record.question,
                "answer":record.answer,
                "source_file":record.source_file,
                "source_page":record.source_page,
                "created_at" : record.created_at
            }
            )

        return {
            "total_records":len(history),
            "history":history
        }
    finally:
        db.close()

# Flow of Get/questions/history  FastAPI->SessionLocal->MYSQL->question_history table-> Previous Questions & Answers ->JSON Response

# main.py-->API requests handle karta hai