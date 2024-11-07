from langchain.tools import BaseTool
import sys
sys.path.append('./')
from file_rag.server.oa.api import doc_statistic
import json

from typing import ClassVar, Dict,Any
class get_docStatistic(BaseTool):
    name = "get_docStatistic"
    description = """
    涉及公文数量统计、文件统计以及报表等功能，必须使用此工具。
    工具只有一个参数userId.
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "token": {
    #             "type": "string",
    #             "description": "令牌",
    #         },
    #          "userId": {
    #             "type": "string",
    #             "description": "用户id",
    #         },
    #     "required": ["token","userId"]
    #     }
    # }
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'userId': {'type': 'string', 'description': '用户userId'},
            'required': ['userId']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, token: str, userId: str) -> str:
       print('个人公文统计')
       data = doc_statistic._Get_docStatistic(userId)
       return data
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")        