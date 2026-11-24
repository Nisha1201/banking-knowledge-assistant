# text/document Chunking
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No chunks were created from the document.")   #PDF load ho gyi but kisi reasin se chunks nahi bane ho to application clearly error btayenge.

    for chunk in chunks:
        source = chunk.metadata.get("source","")
        chunk.metadata["file_name"] = source.split("/")[-1]
        page =  chunk.metadata.get("page",0)
        chunk.metadata["page_number"] = page+1

    return chunks

# PDF-->Documents--> Chunking--> Chunk size--> Chunk Overlap--> Chunks--> Metadata--> File Name/Page Number
# chunking.py-->PDF ko chunks me divide karta hai