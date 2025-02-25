import requests
import json
from fuzzywuzzy import fuzz

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')


def get_post_headers(token):
    post_headers = {
        "Accept": 'application/json, text/plain, */*',
        "content-type": 'application/json;charset=UTF-8',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    return post_headers


def get_headers(token):
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    return headers


def _write_docOpinion(token, docId, content, userId, username):
    print('进入接口')
    #     获取文件信息
    doc_info = f'{
        api}/doc/receival/workflow/getProcessPermission?docId={docId}&_t=1726205601228'

#   填写意见的接口
    w_opinion_url = f'{api}/opinion/insertDocOpinion'
    #     url = f'{api}/opinion/listDocOpinionByDocId?docId={docId}&_t=1724053904273'


#     发送人选择
    flowVersion = ''
    flowLabel = ''
    sendStateLabel = ''
#    当前环节名称
    stateName = ''
    workTodoId = ''
#
    try:
        response = requests.get(doc_info, headers=get_headers(token))
        if response.status_code == 200:
            print(response.json())
            opc = {}
            opc['createTime'] = ''
            opc['docId'] = response.json()['docId']
            opc['flowSlab'] = response.json()['stateBase']['stateLabel']
            sendStateLabel = response.json()['stateBase']['stateLabel']
            stateName = response.json()['stateBase']['stateName']
            opc['id'] = ''
            flowLabel = response.json()['flowInfo']['label']
            flowVersion = response.json()['flowInfo']['version']
#           是否有填写意见按钮
            for a in response.json()['stateBusiness']['businessHandle']:
                if a['handleName'] == '填写意见':
                    for opinion in response.json()['stateBusiness']['businessOpinion']:
                        if opinion['auto'] == 1:
                            opc['opinionCode'] = opinion['opinionNo']
                            opc['opinionCodeName'] = opinion['opinionName']
            opc['opinionContent'] = content
            opc['opinionDeptNo'] = ''
            opc['opinionUserNo'] = userId
            workTodoId = response.json()['workTodoId']
            print(opc)
            # 发送 POST 请求，指定请求头和数据
            response = requests.post(
                w_opinion_url, json=opc, headers=get_post_headers(token))
            if response.status_code == 200:
                print(response.text)
                print('意见已保存。等待发送------')
#             return response.text  # 返回解析后的 JSON 数据
#             print(f'流程信息--flowVersion--{flowVersion},sendStateLabel---{sendStateLabel}.--{flowLabel},---{flowVersion}')
#             selectUser_url = f'{api}/workflow/getAiAssignedUsers?sendUserNo={userId}&flowVersion={flowVersion}&flowLabel={flowLabel}&sendStateLabel={sendStateLabel}&_t=1726'
            users, stats = select_user(
                token, userId, flowVersion, flowLabel, sendStateLabel, username)
            result = ''
            if users !='' and stats !='':
                result = toSend(token, docId, users, stats, workTodoId) 
            else:
                result = '意见已保存，无法获取发送人，发送失败。'
            print(f'文件最终结果---{result}')
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def find_subjectId(token, subject, content, userId, username):

    print(f'文件标题为：{subject}')
    todo_url = f'{
        api}/workflow/getActivityWorkTodoList4Page?flowStatus=running&offset=0&limit=10000'
    atdo_url = f'{
        api}/workflow/getActivityWorkTodoList4Page?flowStatus=done&offset=0&limit=10000&sort=createTime'
    docs = [todo_url, atdo_url]
    # 合并 待办、在办 文件标题与docid
    file_list = []
    for url in docs:
        try:
            response = requests.get(url, headers=get_headers(token))
            if response.status_code == 200:
                #           print(response.json())
                list = response.json()['list']
                if list:
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
    return _write_docOpinion(token, docId, content, userId, username)


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
        print(b_value, similarity)
        # 如果找到更高的相似度，更新最大相似度和对应的项目
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_item = item
            most_similar_businessDocId = most_similar_item.get(
                'businessDocId', '')
            most_similar_businessSubject = most_similar_item.get(
                'businessSubject', '')
    most_similar_businessDocId = most_similar_businessDocId
    most_similar_businessSubject = most_similar_businessSubject
    max_similarity = max_similarity
    print(f'相似度最高的是：{most_similar_businessSubject}:{max_similarity}')
    return most_similar_businessDocId


def select_user(token, userId, flowVersion, flowLabel, sendStateLabel, username):
    selectUser_url = f'{api}/workflow/getAiAssignedUsers?sendUserNo={userId}&flowVersion={
        flowVersion}&flowLabel={flowLabel}&sendStateLabel={sendStateLabel}&_t=1726' 
    try:
        response = requests.get(selectUser_url, headers=get_headers(token))
        if response.status_code == 200:
            print(response.json())
            for stats in response.json():
                for users in stats['listUsers']:
                    print(users['userName'])
                    if username in  users['userName'] :
                        return users, stats
            return '',''
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def toSend(token, docId, users, stats, workTodoId):
    send_url = f'{api}/doc/receival/workflow/flowSend'
    content = {}
    content['docId'] = docId
    content['workTodoId'] = workTodoId
    msg ={}
    msg['content'] = ''
    msg['outType'] = ['msg']
    msg['sendMsg'] = True
    content['messageCustomization'] = msg
    a = {}
    a['selGroups'] = []
    a['selOrgs'] = []
    a['stateLabel'] = stats['stateLabel']
    a['stateName'] = stats['stateName']
    a['transitionLabel'] = stats['transitionLabel']
    user = {}
    user['userNo'] = users['userNo']
    user['userName'] = users['userName']
    user['orgNo'] = users['orgNo']
    user['orgNameChain'] = users['orgNameChain']
    a['selUsers'] = [user]
    content['submitStates'] = [a]
    print(content)
    try:
        response = requests.post(
            send_url, json=content, headers=get_post_headers(token))
        if response.status_code == 200:
            return f'该文件已成功发给{user['userName']}'
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


if __name__ == "__main__":
    find_subjectId('b5316ebc-af00-4d51-92a7-057f6e4ac9b3',
                   '关于请假的通知报告', '测试', 'U006072', '方波')
