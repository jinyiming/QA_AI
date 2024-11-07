import requests
from fuzzywuzzy import fuzz
import json

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
def _Get_workflow(token, docId):
    flow_url = f'{api}/workflow/getFlowRecordList4Page?businessDocId={docId}&offset=0&limit=1000&_t=1724205642655'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    try:
        response = requests.get(flow_url, headers=headers)
        if response.status_code == 200:
            api_data_workFlow = response.json()
            a = [doc['stateName'] for doc in api_data_workFlow['list']]
            flowWork_stateName = a[len((a))-1]
            # 这是获取最后一条班里人记录
            flowWork_stateName = api_data_workFlow['list'][-1]['stateName']
            # print(flowWork_stateName)

            flowWork_assignName = api_data_workFlow['list'][-1]['assignName']

            flowWork_isRead = api_data_workFlow['list'][-1]['isRead']

            current_statue = f'当前流程在【{flowWork_stateName}】环节，【{flowWork_assignName}】正在办理中。'
            print(f'目前流程在【{flowWork_stateName}】环节，【{flowWork_assignName}】人正在办理中。')
            num = 1
            work_info = ''
            if api_data_workFlow['total'] > 0:
                for flow in api_data_workFlow['list']:
                    if flow.get('dealTraceInfo'):
                        # print(flow['dealTraceInfo'])
                        deal_trace = json.loads(flow['dealTraceInfo'])
                        for deal in deal_trace:
                            hander = deal['handler']['userName']
                            fs_stateName = flow['stateName']
                            op = deal['dealType']
                            send_time = deal['createTime']
                            # print(deal['assignArray'])
                            if len(deal['assignArray']) > 0 :
                                receiver_statename = deal['assignArray'][0]['stateName']
                                receiver = deal['assignArray'][0]['assignObject']
                                work_info += (f"第{num}个环节中 【{fs_stateName}】环节，【{hander}】在{send_time}将文件{[f'发送' if op == 'send' else '办理']}给【{receiver_statename}】的【{receiver}】。\n")
                        num = num + 1
                work_info = work_info + f"第{api_data_workFlow['total']}个环节中 【{flow['stateName']}】环节，【{flow['assignName']}】正在办理，目前处于：{f'已读' if flow['isRead'] == '1' else f'未读'}状态。\n"
                work_info = f'该文件一共经历{api_data_workFlow['total']}个环节:\n 流程记录为：\n{work_info}\n 最新动态为：\n{current_statue}'
            print(work_info)
            return work_info  # 返回解析后的 JSON 数据
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
    docs = [atdo_url, todo_url]
    # 合并 待办、在办 文件标题与docid
    file_list = []
    for url in docs:
        try:
            print(url)
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # print(response.json())
                list = response.json()['list']
                if list :
                    for l in list:
                        doc = {}
                        doc['businessSubject'] = l['businessSubject']
                        doc['businessDocId'] = l['businessDocId']
                        file_list.append(doc)
            else:
                print(f"Failed to fetch data, status code: {
                      response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    docId = find_most_similar_item(file_list, subject)
    return _Get_workflow(token, docId)

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
    find_subjectId('d633d785-faeb-4f7d-aa62-cb0dba08ab33','开展数据资源开发利用试点')