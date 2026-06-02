import os
import warnings
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

warnings.filterwarnings('ignore')

DATA_FOLDER = "data"

# ۱. بارگذاری اسناد
def load_pdfs_and_mds(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' does not exist!")
        return documents
        
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if filename.endswith('.pdf'):
            try:
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
                print(f"✅ Loaded PDF: {filename}")
            except Exception as e:
                print(f"❌ Error in PDF {filename}: {e}")
                
        elif filename.endswith('.md'):
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
                print(f"✅ Loaded MD: {filename}")
            except Exception as e:
                print(f"❌ Error in MD {filename}: {e}")
    
    return documents

print("📂 Loading PDF & MD files from 'data' folder...")
docs = load_pdfs_and_mds(DATA_FOLDER)

if not docs:
    print("⚠️ No PDF or MD files found! Exiting...")
    exit()

# ۲. خرد کردن و ایجاد بردارهای متنی
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=150,
    separators=["\n\n", "\n", "。", "،", " ", ""]
)
chunks = text_splitter.split_documents(docs)

print("🔍 Creating embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    encode_kwargs={'normalize_embeddings': True} 
)
vectorstore = FAISS.from_documents(chunks, embeddings)
print("✅ Vectorstore Ready!\n")

# ۳. بارگذاری مدل هوش مصنوعی
print("🧠 Loading Small AI Model (Qwen 0.5B)...")
model_id = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|im_end|>")
]

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=400,
    temperature=0.01,
    repetition_penalty=1.1,
    do_sample=False,
    return_full_text=False,
    eos_token_id=terminators,
    pad_token_id=tokenizer.pad_token_id
)
llm = HuggingFacePipeline(pipeline=pipe)

def format_prompt(question, context):
    return f"""<|im_start|>system
تو یک دستیار تحلیلگر و دقیق هستی. وظیفه تو استخراج اطلاعات و پاسخگویی جامع است.
قوانین اکید تو:
۱. اگر پاسخ سوال در "متن موجود" بود: یک جواب کامل، روان و با تمام جزئیاتی که در متن هست ارائه بده. تا جایی که متن اجازه می‌دهد توضیحات را بسط بده و هیچ نکته مرتبطی را جا نینداز.
۲. اگر پاسخ در متن نبود: تحت هیچ شرایطی حدس نزن، از دانش قبلی‌ات استفاده نکن و فقط و فقط بنویس: "نمی‌دانم، در فایل‌های موجود پاسخی برای این سوال نیست."<|im_end|>
<|im_start|>user
متن موجود:
{context}

سوال: {question}<|im_end|>
<|im_start|>assistant
"""

# ۴. راه‌اندازی سرور FastAPI
app = FastAPI(title="RAG API Server")

# ساختار دریافت درخواست
class QueryRequest(BaseModel):
    question: str

DISTANCE_THRESHOLD = 0.35 

@app.post("/ask")
async def ask_question(request: QueryRequest):
    question = request.question.strip()
    
    if not question:
        return {"answer": "لطفا یک سوال معتبر بپرسید.", "sources": []}
        
    try:
        results = vectorstore.similarity_search_with_score(question, k=3)
        retrieved_docs = [doc for doc, score in results if score < DISTANCE_THRESHOLD]
        
        if not retrieved_docs:
            return {"answer": "نمی‌دانم، در فایل‌های موجود پاسخی برای این سوال نیست.", "sources": []}
            
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        final_prompt = format_prompt(question, context)
        
        response = llm.invoke(final_prompt) if hasattr(llm, 'invoke') else llm(final_prompt)
        answer = response.strip()
        
        sources = list(set([os.path.basename(doc.metadata.get('source', 'unknown')) for doc in retrieved_docs]))
        
        return {"answer": answer, "sources": sources}
        
    except Exception as e:
        return {"answer": f"خطا در پردازش سرور: {e}", "sources": []}

# برای اجرای محلی
if __name__ == "__main__":
    print("🚀 Starting API Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)