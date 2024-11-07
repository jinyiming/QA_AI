from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

from langchain.tools.retriever import create_retriever_tool
print(f"调用 retriever tool.................\n")
docs_load = DirectoryLoader(
        'data', glob='**/*.pdf', loader_cls=PyPDFLoader, show_progress=True)
docs_docment = docs_load.load()
documents = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs_docment)

embeddings = OllamaEmbeddings(
        model="gte-qwen:latest",
    )

vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()

# print(retriever.invoke('“十四五”时期我国经济社会发展瞄准六大主要目标'))


# 创建 retriever tools

retriever_tools = create_retriever_tool(
    retriever,
    '知识库搜索',
    '搜索关于国家政策、政府协同、政务服务的相关问题，都必须用此工具进行查询。'  
)   