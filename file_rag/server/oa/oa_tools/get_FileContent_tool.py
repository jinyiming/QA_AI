from langchain.tools import BaseTool
import sys
sys.path.append('./')
from file_rag.server.oa.api import download
from typing import ClassVar, Dict,Any
import json
class get_FileContent(BaseTool):
    name = "get_FileContent"
    description = """
    主要涉及具体文件内容信息的获取。包括文件内容、正文、附件、办理单做分析、总结的，必须使用此工具。
    此工具包含三个参数：令牌（token） 与 文件标题 （subject）、用户输入(query)。
    通过上下文，找出用户输入，例如：文件内容是什么、意见内容是什么等等。
    """
    parameters = {
        "type": "object",
        "properties": {
            "token": {
                "type": "string",
                "description": "令牌",
            },
             "subject": {
                "type": "string",
                "description": "文件名称",
            },
             "query": {
                "type": "string",
                "description": "用户输入",
            },
        "required": ["token","docId",'query']
        }
    }
    # parameters: ClassVar[Dict[str, Any]] = {
    #     'type': 'object',
    #     'properties': {
    #         'token': {'type': 'string', 'description': '令牌'},
    #         'subject': {'type': 'string', 'description': '文件名称'},
    #         'query': {'type': 'string', 'description': '用户提出的问题或者是输入的问题'},
    #         'required': ['token', 'subject', 'query']
    #     },
    #     'description': "工具需要的参数"
        
    # }
    def _run(self, token: str, subject: str, query: str) -> str:
       print('文件下载')
       docs_all, filaNameList, data  = download.find_subjectId(token, subject,query)
       return f'获取的整体文件信息如下：{docs_all},文件标题为：{filaNameList},文件的大致内容为：{data}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")        