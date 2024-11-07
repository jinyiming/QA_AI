import requests
import json
from fuzzywuzzy import fuzz

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def _Get_docOpinion(token, docId):
    print('进入接口')
    url = f'{api}/opinion/listDocOpinionByDocId?docId={docId}&_t=1724053904273'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response.json())
            opinionContent = []
            for doc in response.json():
                opinion = {}
                opinion['opinionContent']=doc['opinionContent']
                opinion['opinionUser']=doc['opinionUser']
                opinion['createTime']=doc['createTime']
                opinion['opinionCodeName']=doc['opinionCodeName']
                opinionContent.append(opinion)
            print(opinionContent)
            return opinionContent  # 返回解析后的 JSON 数据
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def find_subjectId(token, subject):
     print(f'文件标题为：{subject}')
     headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
     todo_url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=running&offset=0&limit=10000'  
     atdo_url = f'{api}/workflow/getActivityWorkTodoList4Page?flowStatus=done&offset=0&limit=10000&sort=createTime'
     docs = [todo_url, atdo_url]
     # 合并 待办、在办 文件标题与docid
     file_list = []
     for url in docs:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
            #           print(response.json())
                list = response.json()['list']
                if list :
                    for l in list:
                        doc = {}
                        doc['businessSubject'] = l['businessSubject']
                        doc['businessDocId'] = l['businessDocId']
                        file_list.append(doc)          
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
     docId = find_most_similar_item(file_list, subject)
     return _Get_docOpinion(token, docId)
def find_most_similar_item(json_data, string_a):
    # 将 JSON 字符串解析为 Python

    max_similarity = 0
    most_similar_item = None
    most_similar_businessDocId = ''
    most_similar_businessSubject = ''
    # print(json_data)
    for item in json_data:
        # 获取当前项目的 'b' 值
        b_value = item.get('businessSubject', '')
        
        # 计算相似度
        similarity = fuzz.ratio(string_a, b_value) / 100
        print(b_value,similarity)
        # 如果找到更高的相似度，更新最大相似度和对应的项目
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_item = item
            most_similar_businessDocId = most_similar_item.get('businessDocId', '')
            most_similar_businessSubject = most_similar_item.get('businessSubject', '')
    most_similar_businessDocId = most_similar_businessDocId
    most_similar_businessSubject = most_similar_businessSubject
    max_similarity = max_similarity
    print(f'相似度最高的是：{most_similar_businessSubject}:{max_similarity}')
    return most_similar_businessDocId


if __name__ == "__main__":
    find_subjectId('50be4061-1821-481c-889c-cada43f5ccbc','体制改革的方针')



