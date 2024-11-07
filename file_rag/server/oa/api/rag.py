from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
import os
import json
import re

# 多个文件使用DirectoryLoader   
def filter_keywords(text, keywords):
    pattern = '|'.join(map(re.escape, keywords))
    return re.sub(pattern, '***', text, flags=re.IGNORECASE)

def get_splitter_doc(docPath, chunk_size, chunk_overlap):
    docs_load = DirectoryLoader(
        docPath, glob='**/*.pdf', loader_cls=PyPDFLoader, show_progress=True)
    docs_docment = docs_load.load()
    if len(docs_docment) == 0:
        return ""
#     for document in docs_docment:
#         # 对当前 document 的 page_content 属性进行替换操作\
#         keyWords = ['襄阳市','大数据中心','湖北','国务院','测试一行字的高度']
#         document.page_content = filter_keywords(document.page_content, keyWords)
#         document.page_content = document.page_content.replace('\n', '')
        # print(f'格式化之后的{docs}')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs_docment)
    print(splits)
    return splits

# 进行dashscope 接口的embedding
# embeddings = DashScopeEmbeddings(
#    model="text-embedding-v1", dashscope_api_key="sk-f60596e24761484ab0a34054c39fb334"
# )

# 进行embedding将文本转为词向量表示,并存储向量数据库中
def insert_vertorDatabase(splits, doc_type):
    # 使用本地的LLM qwen-7B进行词向量的转换
    embeddings = OllamaEmbeddings(
        model="gte-qwen:latest",
    )
    faiss_index = FAISS.from_documents(splits, embeddings)
    # 保存到向量数据库中
    faiss_index.save_local(doc_type+'.faiss')
    vertorData_name = doc_type+'.faiss'
    return vertorData_name, embeddings
  
# 将正确的结果重新写入想向量库中
def update_vertorDatabase(session_message, vetorDB_name):
     faiss_index = FAISS.from_texts(session_message, embeddings)
     FAISS.write_index(faiss_index, 'vetorDB_name')
     
     
def get_retriever(vertorData_name):
    embeddings = OllamaEmbeddings(
        model="gte-qwen:latest",
        
    )
    print(f'route to --{vertorData_name}')
    faiss_index = FAISS.load_local(
        vertorData_name, embeddings, allow_dangerous_deserialization=True)
    retriever = faiss_index.as_retriever(search_kwargs={"k": 6})
    # 搜索我们的文档数据
    docs = faiss_index.similarity_search(query="经济", k=6)
    # 打印输入
    for doc in docs:
       print(str(doc.metadata["page"]) + ":", doc.page_content[:1000])
    return retriever


# 将q与Retriever的值映射到模版中，给到llm进行推理，生成generate
def generate_by_llm(retriever, custom_rag_prompt, llm):
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )
    response = rag_chain.invoke("文件标题为住房公积金地址搬迁，目前办理人是谁")
    return response

#  推理大模型LLM


def get_llm():
    llm = Ollama(model="qwen:latest")
    return llm

# 数据集整理


def list_subfolders(directory):
    try:
        # 获取目录中的所有文件和文件夹
        items = os.listdir(directory)
        # 过滤出所有子文件夹
        subfolders = [item for item in items if os.path.isdir(
            os.path.join(directory, item))]
        return subfolders
    except Exception as e:
        return str(e)

# 获取配置文件的值


def get_chunk_properties(json_file, key):
    try:
        # 打开并读取 JSON 文件
        with open(json_file, 'r') as file:
            config = json.load(file)
        # 获取指定键的属性值
        if key in config:
            chunk_size = config[key].get('chunk_size')
            chunk_overlap = config[key].get('chunk_overlap')
            return {
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap
            }
        else:
            return f"Key '{key}' not found in the configuration."

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # 初始化数据
    data_path = './data'
    config_path = './data/config.json'
    print(list_subfolders(data_path))
    subfolder_list = list_subfolders(data_path)
    route = []
    for folder_name in subfolder_list:
        a = {}
        print(folder_name)
        config_value = get_chunk_properties(config_path, folder_name)
        print(config_value['chunk_size'])
        splits = get_splitter_doc(data_path+'/'+folder_name+'/', int(config_value['chunk_size']),
                                  int(config_value['chunk_overlap']))
        if splits != "":
            vertorData_name, embeddings = insert_vertorDatabase(
                splits, folder_name)
            a['type'] = folder_name
            a['argument'] = {
                'vertorData_name': vertorData_name,
            }
            route.append(a)
            file_path = 'route_config.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(route, f, indent=4)
#
# def get_route_config():
#    data_path = './data'
#    config_path = './data/config.json'
#    print(list_subfolders(data_path))
#    subfolder_list = list_subfolders(data_path)
#    route = []
#    for folder_name in subfolder_list:
#       a = {}
#       print(folder_name)
#       config_value = get_chunk_properties(config_path, folder_name)
#       print(config_value['chunk_size'])
#       splits = get_splitter_doc(data_path+'/'+folder_name+'/', int(config_value['chunk_size']),
#                                 int(config_value['chunk_overlap']))
#       vertorData_name, embeddings = insert_vertorDatabase(splits, folder_name)
#       a['type'] = folder_name
#       a['argument'] = {
#          'vertorData_name': vertorData_name,
#       }
#       route.append(a)
#    json_string = json.dumps(route, indent=4)
#    return route
    # 根据内容进行路由

    # prompt_template, llm = get_promptTemplate()
    # retriever = get_retriever(vertorData_name, embeddings)
    # final_output = generate_by_llm(retriever, prompt_template, llm)
    # print(final_output)
