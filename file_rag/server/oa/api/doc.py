
import requests
import json

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def _Get_docFile(token, doctype, userId):
    
    print('进入接口')
    if doctype == 'todo' or doctype == 'searchOpinion':
        url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=running&offset=0&limit=20'  # 示例 API 地址
    if doctype == 'toreceive' or doctype == 'searchOpinion':
        url = f'{api}exDoc/exReceiveTrack/getExReceiveTrack4Page?status=0&offset=0&limit=10'
    if doctype == 'atdo' or doctype == 'searchOpinion':
        url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=done&offset=0&limit=10&sort=createTime'
    if doctype == 'toread':
        url = f'{api}/workflow/getFlowWorkReadList4Page?isRead=0&handleUserNo={userId}&offset=0&limit=15&sort=createTime'
    if doctype == 'atread':
        url = f'{api}/workflow/getFlowWorkReadList4Page?isRead=1&handleUserNo={userId}&offset=0&limit=15&sort=createTime'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "connection": "keep-alive",
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            #           print(response.json())
            total = response.json()['total']
            list = response.json()['list']
            subject = []
            if doctype == 'toreceive':
                for doc in list:
                    subject.append(doc['subject']+','+doc['docId'])
            # 待办、在办文件列表
            elif doctype == 'todo':
                for doc in list:
                    #   文件id: {doc["businessDocId"]},\
                    subject.append(f'文件标题：【{doc["businessSubject"]},\
                                     公文类别：{doc["businessName"]},\
                                     办理环节: {doc["stateHandleInfo"].split(':')[0].split('{')[1]}环节, \
                                     发送人：{doc["stateHandleInfo"].split(':')[1].split('}')[0]}, \
                                     接收时间: {doc["createTime"]},\
                                     公文类别：{doc["businessName"]} \
                                     workid: {doc["id"]}'
                                   )
                print(f'{total}\n {subject}')   
                
            elif doctype == 'atdo':
                for doc in list:
                    subject.append(f'文件标题：【{doc["businessSubject"]}】,公文类别：{doc["businessName"]},文件id: {doc["businessDocId"]},办理环节: {doc["stateHandleInfo"].split(':')[0].split('{')[1]}环节,办理人：{doc["stateHandleInfo"].split(':')[1].split('}')[0]},接收时间:{doc["createTime"]},公文类别：{doc["businessName"]},workid: {doc["id"]} \n' 
                                   )
                print(f'{total}\n {subject}')
            return total, subject  # 返回解析后的 JSON 数据
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    _Get_docFile('60ceb353-e4d0-4f86-836a-b2a7c4b64ca1','atdo', 'U006072')
