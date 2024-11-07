
import requests
import json

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def _Get_docFile(token, doctype):
    userNo = 'U004952' 
    print('进入接口11')
    
    todo_url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=running&offset=0&limit=10000'  # 示例 API 地址
    
    toreceive_url = f'{api}/exDoc/exReceiveTrack/getExReceiveTrack4Page?status=0&offset=0&limit=10000'
    
    atdo_url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=done&offset=0&limit=10000&sort=createTime'
   
    toread_url = f'{api}/workflow/getFlowWorkReadList4Page?isRead=0&handleUserNo={userNo}&offset=0&limit=15&sort=createTime'
    
    atread_url = f'{api}/workflow/getFlowWorkReadList4Page?isRead=1&handleUserNo={userNo}&offset=0&limit=15&sort=createTime'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    file_type = [todo_url, atdo_url, toread_url, atread_url]
    try:
        subject = []
        for url in file_type:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
            #   print(response.json())
                total = response.json()['total']
                list = response.json()['list']
                files = {}
                f = {}
                a = []
                name = ''
                if url == toreceive_url:
                    name = "待收公文列表如下："
                    files['doctype'] = name
                    for doc in list:
                        f['subject'] = doc['subject']
                        a.append(files)
                else:
                    if url == todo_url:
                       name = "待办公文列表如下："
                    elif url == atdo_url:
                       name = "在办公文列表如下："
                    elif url == toread_url:
                       name = "待阅公文列表如下："
                    elif url == atread_url:
                       name = "已阅公文列表如下："
                    files['doctype'] = name
                    for doc in list:
                        # subject.append(doc['businessSubject']+','+doc['businessDocId'])
                        f['subject'] = doc['businessSubject']
                        f['sendtime'] = doc['createTime']
                        f['businessName'] =  doc['businessName']
                        a.append(f'《{f['subject'] }》')
                    files['context'] =  a
                    print(f'{total}\n')
                subject.append(files)
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
                return None   
        print(subject)
        return total, subject  # 返回解析后的 JSON 数据
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    _Get_docFile('5addc2a5-0650-402f-b82f-8d9bc252b658','U004952')
