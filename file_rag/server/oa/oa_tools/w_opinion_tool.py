from langchain.tools import BaseTool
from typing import ClassVar, Dict,Any
import sys
sys.path.append('./')
import json
from file_rag.server.oa.api import w_opinion_api
class w_opinion(BaseTool):
    name = "w_opinionAndSend"
    description = """
    如果涉及到填写意见并发送的，请使用此工具。
    该工具有5个参数。分别为：令牌：token，用户id：userId，文件名称：subject，意见内容：opinion_content，接收人姓名:username
    严格遵循工具描述内容，禁止造词、造值。
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "token": {
    #             "type": "string",
    #             "description": "令牌",
    #         },
    #           "userId": {
    #             "type": "string",
    #             "description": "用户id",
    #         },
    #           "subject": {
    #             "type": "string",
    #             "description": "文件标题",
    #         },"opinion_content": {
    #             "type": "string",
    #             "description": "意见内容",
    #         },
    #         "username": {
    #             "type": "string",
    #             "description": "接收人姓名",
    #         },
    #     "required": ["token","userId","subject","opinion_content","username"]
    #     }
    # }
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': '令牌'},
            'userId': {'type': 'string', 'description': '用户id'},
            'subject': {'type': 'string', 'description': '文件名称'},
            'opinion_content': {'type': 'string', 'description': '意见内容'},
            'username': {'type': 'string', 'description': '接收人姓名'},
            'required': ['token', 'userId', 'subject','opinion_content', 'username']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, token: str, subject: str,userId: str, opinion_content: str, username: str) -> str:
        print(token)
        
        result = w_opinion_api.find_subjectId(token, subject, opinion_content, userId, username)
    
        return f'最终的发送结果为：{result}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")