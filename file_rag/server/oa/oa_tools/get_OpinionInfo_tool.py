from langchain.tools import BaseTool
import sys
sys.path.append('./')
from typing import ClassVar, Dict,Any
import json
from file_rag.server.oa.api import opinion
class get_OpinionInfo(BaseTool):

    name = "get_OpinionInfo"
    description = """
    如果关于公文（文件）的意见内容、意见查询、意见填写，请使用此工具。
    此工具包含两个参数：令牌（token） 与文件标题（subject）。
    严格遵循工具描述内容，如获取不到，请在上下文找，禁止造词、造值。
    """
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': '令牌'},
            'subject': {'type': 'string', 'description': '文件名称'},
            
            'required': ['token', 'subject']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, token: str, subject: str) -> str:
        print(token)
        
        opinionContent = opinion.find_subjectId(token, subject)
    
        return f'获取的意见为：{opinionContent}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")