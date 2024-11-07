# 获取个人信息
import requests
import json

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def _Get_userInfo(token, userId):
    
    print('进入接口')
    userInfo_url = f'{api}/user/umsUser/getUmsUserFullInfo?userNo={userId}&_t=1725885891843'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    try:
        response = requests.get(userInfo_url, headers=headers)
        if response.status_code == 200:
                print(response.json())
                user_infos = response.json()['user']
                org_infos = response.json()['orgs']
                unitName = [org['unitName'] for org in org_infos]
                orgName = [org['orgName'] for org in org_infos]
                orgNameList = [org['orgNameList'] for org in org_infos]
                systemNo = [org['systemNo'] for org in org_infos]
                str  = f'所在单位{unitName},所在部门{orgName},单位属于{orgNameList},姓名：{user_infos['userName']},手机号:{user_infos['mobile']},邮箱地址：{user_infos['email']},加入时间：{user_infos['entryDate']},最近登录时间：{user_infos['loginLastTime']},所属的OA系统id为：{systemNo},用户简称:{user_infos['shortName']},用户id:{user_infos['userNo']}'
                return str
                         
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    _Get_userInfo('946ccb6e-7444-44e1-b0b0-cf2ac2dec4a4','U004952')
