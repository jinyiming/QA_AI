from langchain.tools import BaseTool
import sys
sys.path.append('./')   
from file_rag.server.oa.api import user
from typing import ClassVar, Dict,Any
class get_userInfo(BaseTool):
    name = "get_userInfo"
    description = """
    涉及到个人基本信息，部门、单位信息以及总结、自我介绍等有关人物的，必须使用此工具。
    此工具有两个参数：token 与用户id。
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "userId": {
    #             "type": "string",
    #             "description": "用户id,用户编号",
    #         },
    #         "token": {
    #             "type": "string",
    #             "description": "token",
    #         },
    #     "required": ["userId", "token"]
    #     }
    # }
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'userId': {'type': 'string', 'description': '用户id,用户编号'},
            'token': {'type': 'string', 'description': 'token'},
            
            'required': ['userId', 'token']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, userId: str, token: str) -> str:
       str  = user._Get_userInfo(token, userId )
       return f'获取的用户基本信息如下{str}'
   
   
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")     

       