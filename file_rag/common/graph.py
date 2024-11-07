import os
from langchain_community.graphs import Neo4jGraph
from langchain_community.llms import Ollama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from neo4j import GraphDatabase
from yfiles_jupyter_graphs import GraphWidget
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import OllamaEmbeddings
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "11111111"

def get_promptTemplate_Routing():
    # 使用llm
    # os.environ["DASHSCOPE_API_KEY"] = "sk-f60596e24761484ab0a34054c39fb334"

    # 推理生成
    template = """
    你是一个 知识图谱图的创建高手，请从给出的文档中{input}，按照一下规则 识别出相应的内容。
    文件 实体 包括：文件标题、来文单位、编号、密级、收文科室、收文时间等属性。
    多个意见 实体 包括：意见类型(拟办、领导批示、办理情况)、签署人（有可能是以部门名称落款）、签署意见、签署时间
    实体：{allowed_nodes}
    关系:{allowed_relationships}
    文件与多个意见实体之间的关系：
    1. 文件包含多个意见。
    2. 每个意见都由不同的人在不同的时间签署。
  
    """ 
    custom_rag_prompt = PromptTemplate.from_template(template)
    return custom_rag_prompt
graph = Neo4jGraph()

loader = UnstructuredMarkdownLoader(
    "./data/1930ff7e248a2000/vertor/dealForm/阅办单.md",
    mode="elements",
    strategy="fast",
)
docs = loader.load()

text = """
[{'type': '公文意见', 'content': [{'opinionContent': '同意。', 'opinionUser': '杨永旗', 'createTime': '2023-08-29 09:17:10', 'opinionCodeName': '领导批示'}, {'opinionContent': '拟同意，请永旗同志阅示。', 'opinionUser': '周富俊', 'createTime': '2023-08-29 08:35:33', 'opinionCodeName': '领导批示'}, {'opinionContent': '在市公安局主办的“襄阳护网2023”网络攻防演习中，我中心的多套业务系统因弱口令被攻破，中心领导高度重视，立即组织排查整改，现拟将该通知发送至各部室，各部室将排查整改情况于2023年9月1日前通过OA邮箱报网络安全部。\n  妥否，请领导批示。', 'opinionUser': '张涛', 'createTime': '2023-08-28 17:49:46', 'opinionCodeName': '科 室意见'}]}, {'type': '流程记录', 'content': "该文件一共经历21个环节:\n 流程记录为：\n第1个环节中 【发文拟稿】环节，【张涛】在2023-08-28 17:51:45将文件['发送']给【中心领导】的【['周富俊']】。\n第3个环节中 【发文拟稿】环节，【张涛】在2023-08-28 17:53:39将文件[' 发送']给【中心领导】的【['周富俊']】。\n第4个环节中 【中心领导】环节，【周富俊】在2023-08-29 08:36:21将文件['发送']给【大数据管理 局】的【['杨永旗']】。\n第5个环节中 【大数据管理局】环节，【杨永旗】在2023-08-29 09:17:22将文件['发送']给【拟稿人】的【['张涛']】 。\n第6个环节中 【拟稿人】环节，【张涛】在2023-08-29 10:43:14将文件['发送']给【科室意见】的【['徐涛', '朱娟', '朱雪阳', '丁伟东', '都鹏', '李松']】。\n第7个环节中 【科室意见】环节，【徐涛】在2023-09-01 08:21:57将文件['办理']给【科室意见】的【['李静乐', '唐文庆']】。\n第8个环节中 【科室意见】环节，【朱娟】在2023-08-31 14:49:24将文件['办理']给【科室意见】的【['任佳雨', '廖虹宇']】。\n第10 个环节中 【科室意见】环节，【丁伟东】在2023-08-29 10:55:48将文件['办理']给【科室意见】的【['大数据中心李莉', '李子龙', '王龙']】。\n第11个环节中 【科室意见】环节，【都鹏】在2023-09-04 14:37:19将文件['办理']给【科室意见】的【['雷一鸣', '吴慧敏']】。\n第21个环节中 【科室意见】环节，【吴慧敏】正在办理，目前处于：已读状态。\n\n 最新动态为：\n当前流程在【科室意见】环节，【吴慧敏】正在办理中。"}, {'type': '公文基本信息', 'content': [{'subject': '关于开展“弱口令”安全风险漏洞排查工作的通知', 'draftDept': '网络和安全部', 'draftDate': '2023-08-28', 'docWord': '暂无', 'secLevel': '非密', 'urgentLevel': '无', 'docSequence': '20230070'}]}, {'type': '正文 内容', 'content': ['附件2：信息系统登记表.xlsx', '附件1：密码设置指南.docx', '关于开展“弱口令”安全风险漏洞排查工作.pdf', '阅办单.html']}, {'type': '附件内容', 'content': ['附件2：信息系统登记表.xlsx', '附件1：密码设置指南.docx', '关于开展“弱口令”安全风险漏洞排查工作.pdf', '阅办单.html']}, {'type': '办理单内容', 'content': ['附件2：信息系统登记表.xlsx', '附件1：密码设置指南.docx', '关于开展“弱口令”安全风险漏洞排查工作.pdf', '阅办单.html']}]
"""
documents = [Document(page_content=text)]
# llm = Ollama(model='llama3.1:latest')

llm = Ollama(base_url='http://localhost:11434', model="qwen", temperature=0.1)
llm_transformer_props = LLMGraphTransformer(
    llm=llm,
    # prompt=get_promptTemplate_Routing(),
    allowed_nodes=['公文实体',"意见实体","流程实体","正文实体","附件实体","办理单实体"],
    allowed_relationships=['公文实体包括意见', "公文实体包括流程","公文实体包括正文","公文实体包括附件","公文实体包括办理单",
                           "意见实体包括意见内内容","意见实体包括签署时间","意见实体包括操作人","意见实体包括意见类型",
                           "流程实体包括流程环节名称","流程实体包括发送人","流程实体包括接收人","流程实体包括发送时间","流程实体包括接收时间",
                           "正文实体包括正文内容","正文实体包括正文标题",
                            "附件实体包括附件内容","附件实体包括附件标题",
                             "办理单实体包括办理单内容","办理单实体包括办理单标题"],
)

graph_documents_props = llm_transformer_props.convert_to_graph_documents(documents)
print(graph_documents_props)
# print(f"Nodes:{graph_documents_props[0].nodes}")
# print(f"Relationships:{graph_documents_props[0].relationships}")
# graph.add_graph_documents(graph_documents_props)
# graph.refresh_schema()

#  MATCH (n) DETACH DELETE n
# match (n) return n
graph.add_graph_documents(
  graph_documents_props, 
  baseEntityLabel=True, 
  include_source=True
)
# default_cypher = "MATCH (s)-[r:!MENTIONS]->(t) RETURN s,r,t LIMIT 50"

# # def showGraph(cypher: str = default_cypher):
# #     # create a neo4j session to run queries
# #     driver = GraphDatabase.driver(
# #         uri = os.environ["NEO4J_URI"],
# #         auth = (os.environ["NEO4J_USERNAME"],
# #                 os.environ["NEO4J_PASSWORD"]))
# #     session = driver.session()
# #     widget = GraphWidget(graph = session.run(cypher).graph())
# #     widget.node_label_mapping = 'id'
# #     #display(widget)
# #     return widget

# # showGraph()
# embeddings = OllamaEmbeddings(
#         base_url='http://localhost:11434', model="llama"
#     ),
# # vector_index = Neo4jVector.from_existing_graph(
# #     embeddings,
# #     search_type="hybrid",
# #     node_label="Document",
# #     text_node_properties=["text"],
# #     embedding_node_property="embedding"
# # )

# from langchain_core.pydantic_v1 import BaseModel, Field
# from typing import Tuple, List, Optional
# class Entities(BaseModel):
#     """识别实体相关信息。"""

#     names: List[str] = Field(
#         ...,
#         description="文本中出现的所有文件的名称",
#     )
# from langchain_core.prompts import ChatPromptTemplate
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "您正在从文本中文件、意见实体信息。",
#         ),
#         (
#             "human",
#             "请按照给定格式从以下输入中提取信息：{question}",
#         ),
#     ]
# )

# entity_chain = prompt | llm.with_structured_output(Entities)
# entity_chain.invoke({"question": "这份文件有几个处理意见？"}).names