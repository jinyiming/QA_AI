import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.document_loaders import PyPDFLoader
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import httpx
from fastapi.responses import StreamingResponse
import json
from fastapi import Form, File, UploadFile
# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# class MaxSizeLimitMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, max_upload_size: int):
#         super().__init__(app)
#         self.max_upload_size = max_upload_size

#     async def dispatch(self, request: Request, call_next):
#         # 获取请求体大小
#         request_size = int(request.headers.get('content-length', 0))
#         if request_size > self.max_upload_size:
#             return JSONResponse(content={"detail": "File too large"}, status_code=413)
#         return await call_next(request)

# # 设置最大上传文件大小为50MB（字节）
# app.add_middleware(MaxSizeLimitMiddleware, max_upload_size=50 * 1024 * 1024)
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，实际应用中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from langchain.prompts import PromptTemplate

def get_promptTemplate_doc():
    template = """
    使用中文简要概括文件内容、总结文件要点并请以结构化的方式呈现信息。
    
    问题: {question}
    
    上下文: {context}
    
    回答:
    """
    return PromptTemplate(template=template, input_variables=["question", "context"])

# 创建一个临时存储向量数据的变量
temp_vectorstore = None

class Query(BaseModel):
    question: str

# 添加新的模型用于接收聊天请求
class ChatRequest(BaseModel):
    question: str

# 添加新的路由处理AI聊天请求
@app.post("/ai_chat")
async def ai_chat(question: str = Form(...), file: UploadFile = File(None)):
    global temp_vectorstore

    if file:
        # 处理文件上传
        UPLOAD_DIR = "uploaded_files"
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        file_location = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_location, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            loader = PyPDFLoader(file_location)
            pages = loader.load_and_split()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(pages)
            
            embeddings = OllamaEmbeddings(model="qwen2:latest")
            temp_vectorstore = FAISS.from_documents(chunks, embeddings)
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if os.path.exists(file_location):
                os.remove(file_location)
        qa_chain = RetrievalQA.from_chain_type(
            llm=Ollama(model="qwen2:latest"),
            chain_type="stuff",
            retriever=temp_vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": get_promptTemplate_doc()}  # 传递提示词字符串
        )
        summary = qa_chain({"query": question})
        
    if temp_vectorstore is None:
        raise HTTPException(status_code=400, detail="请先上传文件")

    payload = {
        "model": "qwen2:latest",
        "messages": [{"role": "user", "content": summary}],
        "prompt": "使用中文简要概括、总结文件要点",
        "stream": True
    }

    async def generate():
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending request to Ollama service: {payload}")
                async with client.stream('POST', 'http://localhost:11434/api/chat', json=payload, timeout=60.0) as response:
                    if response.status_code != 200:
                        logger.error(f"Ollama服务返回非200状态码: {response.status_code}")
                        yield json.dumps({"error": f"AI服务返回错误状态码: {response.status_code}"}) + '\n'
                        return
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                logger.debug(f"Received line from Ollama: {line}")
                                yield json.dumps(json.loads(line)) + '\n'
                            except json.JSONDecodeError:
                                logger.warning(f"Unable to parse line: {line}")
        except httpx.ConnectError as e:
            logger.error(f"无法连接到Ollama服务: {e}")
            yield json.dumps({"error": "无法连接到AI服务，请确保Ollama服务正在运行"}) + '\n'
        except httpx.ReadTimeout as e:
            logger.error(f"从Ollama服务读取超时: {e}")
            yield json.dumps({"error": "AI服务响应超时，请稍后再试"}) + '\n'
        except Exception as e:
            logger.error(f"处理AI聊天请求时发生错误: {str(e)}", exc_info=True)
            yield json.dumps({"error": f"处理AI聊天请求时发生错误: {str(e)}"}) + '\n'

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global temp_vectorstore
    # 定义上传目录
    UPLOAD_DIR = "uploaded_files"

    # 如果目录不存在，创建目录
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    logger.info(f"Received file: {file.filename}")
    
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 使用 LangChain 的 PyPDFLoader 读取 PDF 文件内容
        loader = PyPDFLoader(file_location)
        pages = loader.load_and_split()
        logger.info(f"Successfully read PDF file content")
        
        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(pages)
        logger.info(chunks)
        # 使用 Ollama 进行向量化
        embeddings = OllamaEmbeddings(model="qwen2:latest")
        temp_vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # 创建检索链并生成摘要
        qa_chain = RetrievalQA.from_chain_type(
            llm=Ollama(model="qwen2:latest"),
            chain_type="stuff",
            retriever=temp_vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": get_promptTemplate_doc()}  # 传递提示词字符串
        )
        summary = qa_chain({"query": "分类概述文件的主要内容。"})
        logger.info(summary)
        return {"summary": summary["result"]}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 确保临时文件被删除
        if os.path.exists(file_location):
            os.remove(file_location)
            logger.info(f"Temporary file deleted: {file_location}")

@app.post("/query")
async def query(query: Query):
    global temp_vectorstore
    
    if temp_vectorstore is None:
        return {"error": "请先上传文件"}

    qa_chain = RetrievalQA.from_chain_type(
        llm=Ollama(model="qwen2:latest"),
        chain_type="stuff",
        retriever=temp_vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": get_promptTemplate_doc()}
    )

    result = qa_chain({"query": query.question})

    return {"answer": result["result"]}

@app.post("/test")
async def test(test):
    return {"message": "Backend is working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)