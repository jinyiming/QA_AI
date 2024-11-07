from langchain.tools import BaseTool
from typing import ClassVar, Dict,Any
import json
import sys
sys.path.append('./')
from file_rag.server.oa.api import doc
class get_docList(BaseTool):
    name = "get_docList"
    description = """
        获取OA系统待办文件、在办文件、待阅文件、已阅文件列表，必须使用此工具。
        此工具包含三个参数：令牌（token）、 文件类型 （doctype）、用户id（userId）。
        待办文件为:todo,在办文件为:atdo,待收文件为:toreceive,全部文件为：all,待阅:toread
        已阅为：atread，用户id可从上下文找出。
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "token": {
    #             "type": "string",
    #             "description": "系统令牌",
    #         },
    #         "doctype": {
    #             "type": "string",
    #             "enum": ["todo", "atdo", "toreceive", "searchOpinion"],
    #             "description": "文件标识,待办文件为:todo,在办文件为:atdo,待收文件为:toreceive",
    #         },
    #         "userId": {
    #             "type": "string",
    #             "description": "用户id",
    #         },
    #     "required": ["token", "doctype","userId"]
    #     }
    # }
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': '令牌'},
            'doctype': {'type': 'string', 'description': '文件标识,待办文件为:todo,在办文件为:atdo,待收文件为:toreceive'},
            'userId': {'type': 'string', 'description': '用户userId'},
            'required': ['token', 'doctype', 'userId']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, token: str, doctype: str, userId: str) -> str:
        print(token)
        
        if doctype == 'todo' or  doctype =='toread':
            todo_total, subject = doc._Get_docFile(token, doctype, userId)
            return f'获取待办有{todo_total}文件，文件标题分别为{subject}'
        if doctype == 'atdo' or  doctype == 'atread':
            atdo_total, subject = doc._Get_docFile(token, doctype, userId)
            return f'获取在办有{atdo_total}文件，文件标题分别为{subject}'
        if doctype == 'toreceive':
            toreceive_total, subject = doc._Get_docFile(token, doctype, userId)
            return f'获取待收有{toreceive_total}文件，文件标题分别为{subject}'
        if doctype == 'all':
            toreceive_total, subject = doc._Get_docFile(token, doctype, userId)
            return f'获取的全部文件{toreceive_total}文件，文件标题分别为{subject}'
        if doctype == 'searchOpinion':
            toreceive_total, subject = doc._Get_docFile(token, doctype, userId)
            for s in subject:
                if subject in s:
                    docId = s.split(',')[1]
            return f'该文件的docId为{docId}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")