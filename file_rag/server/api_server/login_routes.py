from typing import Literal
import json,requests
from fastapi import APIRouter, Body
with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')

from file_rag.settings import Settings

login_router = APIRouter(prefix="/login", tags=["Server State"])

available_template_types = list(Settings.prompt_settings.model_fields.keys())


@login_router.post("/_userLogin_sso", summary="OA登录认证")
async def _userLogin_sso(username,password):
    # 目标 URL
    # url = f'http://192.168.244.83:2080/ssPcLogin?ignoreCaptcha=true'  # 替换为你实际的 API 端点
    url = f'{api}/login'
    # 请求的数据
    login_info ={}
    data = {
        'username': username,
        'password': password,
        'ignoreCaptcha': True
    }
    # 发送 POST 请求
    response = requests.post(url, data=data)
    if response.status_code == 200:
        cookies = response.cookies
        try:
                    response_json = response.json()
        except ValueError:
                    print("Response is not in JSON format")
        userInfo_url = f'{api}/user/umsUser/getUmsUserFullInfo?userNo={response_json['user']['username']}&_t=1725885891843'
        # x_auth_token = response_json['user']['x-auth-token']    
        headers = {
            "Accept": 'application/json, text/plain, */*',
            "Accept-Encoding": 'gzip, deflate',
            "Accept-Language": 'zh-CN,zh;q=0.9',
            # 替换为实际的 Cookie 值
            
            'Cookie': f'x-authenticated=true; x-auth-token={cookies.get('x-auth-token')}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
        }   
        try:
            response = requests.get(userInfo_url, headers=headers)
            if response.status_code == 200:
                    print(response.json())
                    user_infos = response.json()['user']
                    # org_infos = response.json()['orgs']
                    # unitName = [org['unitName'] for org in org_infos]
                    # orgName = [org['orgName'] for org in org_infos]
                    # orgNameList = [org['orgNameList'] for org in org_infos]
                    # systemNo = [org['systemNo'] for org in org_infos]
                    # str  = f'所在单位{unitName},所在部门{orgName},单位属于{orgNameList},姓名：{user_infos['userName']},手机号:{user_infos['mobile']},邮箱地址：{user_infos['email']},加入时间：{user_infos['entryDate']},最近登录时间：{user_infos['loginLastTime']},所属的OA系统id为：{systemNo},用户简称:{user_infos['shortName']},用户id:{user_infos['userNo']}'
                    # return str
                            
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        login_info['username'] = response_json['user']['username']
        login_info['x-auth-token'] = cookies.get('x-auth-token')
        login_info['systemNo'] = response_json['user']['systemNo']
        login_info['orgNo'] = response_json['user']['orgNo']
        login_info['name'] = user_infos['userName']
        login_info['status_code'] = 200
        return login_info
    else:
        login_info['status_code'] = response.status_code
        return login_info