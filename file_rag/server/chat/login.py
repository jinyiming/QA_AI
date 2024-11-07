import requests
import json
from fastapi import HTTPException, Query

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')

def _userLogin(username,password):
    # 目标 URL
    # url = f'http://192.168.244.83:2080/ssPcLogin?ignoreCaptcha=true'  # 替换为你实际的 API 端点
    url = f'{api}/login'
    # 请求的数据
    data = {
        'username': username,
        'password': password,
        'ignoreCaptcha': True
    }
    # 发送 POST 请求
    response = requests.post(url, data=data)
    cookies = response.cookies
    # print(response.text)
    # print(cookies.get('x-auth-token'))
    # 打印响应状态码
    # print(f"Status Code: {response.status_code}")

    # 打印响应文本
    # print("Response Text:")
    # print(response.text)
    
    # 如果响应是 JSON 格式，可以用 response.json() 解析并打印
    try:
                response_json = response.json()
                # print("Response JSON:")
                print(response_json['user']['systemNo'])
    except ValueError:
                print("Response is not in JSON format")
    return response_json['user']['username'],cookies.get('x-auth-token')

async def _userLogin_sso(username: str = Query(...), password: str = Query(...)):
    print(f"Received login request: username={username}, password={password}")
    # 实现您的登录逻辑
    if username == "测试" and password == "12345678":  # 示例验证
        return {"token": "sample_token"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

if __name__ == "__main__":
      print( _userLogin('任佳雨','87654321'))
