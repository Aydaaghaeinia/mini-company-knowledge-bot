import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex, StorageContext, 
    Settings, PromptTemplate
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

app = FastAPI(title="Mini Company Knowledge Bot")

# تنظیمات مدل
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small")
Settings.llm = None 

# راه‌اندازی دیتابیس
db_dir = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=db_dir)
collection = chroma_client.get_or_create_collection("company_knowledge")
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# بارگذاری یا ساخت دیتابیس
if collection.count() == 0:
    reader = SimpleDirectoryReader(input_dir="./data")
    documents = reader.load_data()
    parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes, storage_context=storage_context)
else:
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

# پرامپت تمیز برای خروجی مستقیم
STRICT_PROMPT = (
    "پاسخ را فقط بر اساس متن زیر ارائه بده. اگر پاسخ در متن نیست بگو «اطلاعات کافی ندارم».\n"
    "متن مرجع: {context_str}\n"
    "سوال: {query_str}\n"
    "پاسخ:"
)
query_engine = index.as_query_engine(
    text_qa_template=PromptTemplate(STRICT_PROMPT), 
    similarity_top_k=2
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    response = query_engine.query(request.question)
    # فقط نام فایل‌های تمیز را برمی‌گردانیم
    sources = list(set([n.metadata.get('file_name', 'Unknown') for n in response.source_nodes]))
    return {"answer": str(response).strip(), "sources": sources}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)