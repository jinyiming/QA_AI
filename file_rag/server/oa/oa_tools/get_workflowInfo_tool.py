from langchain.tools import BaseTool
from typing import ClassVar, Dict,Any
import json
import sys
sys.path.append('./')
from file_rag.server.oa.api import workflow
class get_workflowInfo(BaseTool):

    name = "get_workflowInfo"
    description = """
    如果涉及OA系统中公文（文件）的流程路线、流程信息、办理人，流程走向等请使用此工具。
    此工具有两个参数：令牌（token）和文件标题 （subject）作为参数。
    严格遵循工具描述内容，如获取不到，请在上下文找，禁止造词、造值。
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "token": {
    #             "type": "string",
    #             "description": "令牌",
    #         },
    #           "subject": {
    #             "type": "string",
    #             "description": "文件名称",
    #         },
    #     "required": ["token","docId","subject"]
    #     }
    # }
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
        
        work_info = workflow.find_subjectId(token, subject)
    
        return f'获取的意见为：{work_info}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")