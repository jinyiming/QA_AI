
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

import sys
sys.path.append('./')
from file_rag.text_splitter import chinese_text_splitter
loader = UnstructuredMarkdownLoader(
    "./data/1930ff7e248a2000/vertor/main_doc/省数据局关于开展数据资源开发利用试点申报的通知.md",
    mode="elements",
    strategy="fast",
)
docs = loader.load()
# print(docs[0].page_content)
# docs = chinese_text_splitter.ChineseTextSplitter(pdf=False,sentence_size=250).split_text(docs[0].page_content)
text_splitter = chinese_text_splitter.ChineseTextSplitter(
        sentence_size=250,
        add_start_index=True
    )
splits = text_splitter.split_documents(docs)

#  将文件向量化
# import sys
# sys.path.append('./')
# from file_rag.knowledge_base.kb_service.faiss_kb_service import FaissKBService
# FaissKBService("samples").load_vector_store()
# docs = FaissKBService('samples').do_search(query='文件内容？',top_k=6)
# for doc in docs:
#     print(doc)
embeddings = OllamaEmbeddings(
        model="gte-qwen:latest",
    )
faiss_index = FAISS.from_documents(splits, embeddings)
docs = faiss_index.similarity_search(query="经济", k=6)
    # 打印输入
for doc in docs:
    print(doc.page_content)
       