from langchain.tools import BaseTool
import sys
sys.path.append('./')
from file_rag.server.oa.api import login
import json


class LoginTool(BaseTool):
    name = "user_login"
    description = """
        如果涉及到系统登录，请使用此工具。默认用户名为：U000035，密码为：12345678
    """
    parameters = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "账号、用户名",
            },
            "password": {
                "type": "string",
                "description": "密码",
            },
        "required": ["username", "password"]
        }
    }
    # description = """
    #     如果是涉及到用户登录的，请使用它
    #     请从问题中提取用户名、密码两个参数传给工具，格式为:
    #     username:用户名,password:密码
    #     请把不能直接提取到的参数置为null, 请不要制造参数。
    # """

    def _run(self, username: str, password: str) -> str:
        # login_info = json.loads(query)
        # return Login._userLogin(login_info['username'], login_info['password'])
        userid, tocken =  login._userLogin(username, password)
        if tocken != '':
            return f'用户id为:{username}', f'令牌token为:{tocken}' 
        else:
            return '登录失败，用户名、密码错误。'
        # return Login._userLogin(query)
        # print(query['username'])
        #  return Login._userLogin(username,password)
#         params = extract_json(query)
#         if params is None:
#             params = extract_re(query)
#         if params is None:
#             params = extract_split(query)
#         if params is None:
#             return "参数不合法，未找到员工信息!"

#         print('final params: ', params)

#         info = query_employee(params)
#         if (len(info) > 0) :
#             return info
#         else:
#             return "未找到员工信息!"
        # return '登录失败'
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")
