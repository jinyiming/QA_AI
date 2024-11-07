import requests
import json
from fuzzywuzzy import fuzz

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def do_flowCancle(token, docId, workId, doctype,re, cur_stateName, most_similar_cur_statePerson):
    print('进入接口')
    
    if doctype == '发文':
        doctype ='disptch'
    elif doctype == '收文':
        doctype = 'receival'
    # 撤办接口
    flowCancle_url = f'{api}/doc/{doctype}/workflow/flowCancle?docId={docId}&workTodoId={workId}&_t=1726132519607'
    print(flowCancle_url)
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    try:
        response = requests.get(flowCancle_url, headers=headers)
        if response.status_code == 200:
            print(response.text)
            if response.text:
                return f'已成功从【{cur_stateName}】环节的办理人【{most_similar_cur_statePerson}】撤办，但是【{most_similar_cur_statePerson}】已看过文件,最好通过其他方式告知。'  # 返回解析后的 JSON 数据
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def do_flowCancle_bysubject(token, subject,sure):
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
                        # print(l)
                        doc = {}
                        doc['businessSubject'] = l['businessSubject']
                        doc['businessDocId'] = l['businessDocId']
                        doc['id'] =  l['id']
                        doc['businessName'] = l['businessName']
                        doc['isRead'] = l['isRead']
                        doc['cur_stateName'] = {l["stateHandleInfo"].split(':')[0].split('{')[1]}
                        doc['cur_statePerson'] = {l["stateHandleInfo"].split(':')[1].split('}')[0]}
                        file_list.append(doc)          
            else:
                print(f"Failed to fetch data, status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            
     print(file_list)
     
     docId, workId, doctype, isRead, cur_stateName,most_similar_cur_statePerson = find_most_similar_item(file_list, subject)
     re = '未读'
     if isRead == '1':
            re ='已读'
     print(f'isRead--{isRead},cur_stateName--{cur_stateName},most_similar_cur_statePerson-->{most_similar_cur_statePerson} ')
     if sure =='否' or sure is None:
        return f' 结束thought，将以下情况作为结果回答问题。目前该文件在【{cur_stateName}】环节，办理人为：【{most_similar_cur_statePerson}】，处于{re}状态。'
     else:
        return do_flowCancle(token, docId, workId, doctype,re,cur_stateName,most_similar_cur_statePerson)
 
 
def find_most_similar_item(json_data, string_a):
    # 将 JSON 字符串解析为 Python
    max_similarity = 0
    most_similar_businessDocId = ''
    most_similar_businessSubject = ''
    most_similar_workId = ''
    most_similar_businessName = ''
    most_similar_isRead = ''
    most_similar_cur_stateName= ''
    most_similar_cur_statePerson=''
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
            most_similar_businessDocId = item.get('businessDocId', '')
            most_similar_workId = item.get('id', '')
            most_similar_businessSubject = item.get('businessSubject', '')
            most_similar_businessName = item.get('businessName', '')
            most_similar_isRead = item.get('isRead', '')
            most_similar_cur_stateName = item.get('cur_stateName', '')
            most_similar_cur_statePerson = item.get('cur_statePerson', '')
    print(f'相似度最高的是：{most_similar_businessSubject}:{max_similarity}:{most_similar_businessName}')
    return most_similar_businessDocId,most_similar_workId, most_similar_businessName, most_similar_isRead,most_similar_cur_stateName, most_similar_cur_statePerson


if __name__ == "__main__":
    do_flowCancle_bysubject('3db5077b-2803-4a1f-98d0-2e71ad71c4de','火热太热特瑞特瑞特热热他')



