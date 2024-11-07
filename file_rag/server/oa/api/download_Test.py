import requests
import os
from pathlib import Path
from fuzzywuzzy import fuzz
import json
import sys
sys.path.append('./')
from common import parse_pdf
from file_rag.settings import Settings
from file_rag.knowledge_base.utils import get_file_path, get_kb_path
from file_rag.server.utils import api_address
from file_rag.webui_pages.utils import ApiRequest

api_base_url = api_address()
kb_api: ApiRequest = ApiRequest(api_base_url)

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
    dw_path = data.get('download_path')
def _Get_docFile(token, docId,subject, kb_name):
    print('进入文件下载API')
    # 意见内容
    opinion_url = f'{api}/opinion/listDocOpinionByDocId?docId={docId}&_t=1724053904273'
    # 流程记录
    flow_url = f'{api}/workflow/getFlowRecordList4Page?businessDocId={docId}&offset=0&limit=1000&_t=1724205642655'
    # 基本信息
    doc_info = f'{api}/doc/dispatch/getDispatchById?docId={docId}&_t=1725847692'
    # 正文
    main_url = f'{api}/attachment/listEgovAttsByDocIdAndTypes?docId={
        docId}&type%5B%5D=main_doc&type%5B%5D=main_trace&type%5B%5D=main_ofd&type%5B%5D=main_pdf&type%5B%5D=main_copy&containFile=false&moduleId=&_t=1724135953238'
    # 附件
    attach_url = f'{api}/attachment/listEgovAttsByDocIdAndTypes?docId={
        docId}&type%5B%5D=attach&containFile=false'
    # 办理单
    dealForm_url = f'{api}/attachment/listEgovAttByDocId?docId={
        docId}&type=dealForm'
    
    file_urls = [main_url, attach_url, dealForm_url]
#     download_url =f'http://192.168.244.92:2080/attachment/downloadEgovAttFile?id={id}&moduleId={moduleId}&x-auth-token={token}'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    
    filaNameList = []
    # 向量数据库 kb
    for url_type in file_urls:
        try:
            response = requests.get(url_type, headers=headers)
            if response.status_code == 200:
                # print(response.json())
                for f in response.json():
                    id = f['id']
                    moduleId = f['moduleId']
                    fileName = f['fileName'] + '.' + f['fileSuffix']
                    filaNameList.append(fileName)
                #     print(fileName)
                    url = f'{api}/attachment/downloadEgovAttFile?id={
                        id}&moduleId={moduleId}&x-auth-token={token}'
                    oa_files = download_file_with_headers(
                        url, fileName, headers, f['docId'], f['type'])    
            else:
                print(f"Failed to fetch data, status code: {
                      response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    print(oa_files)
    data = oa_upload_docs(oa_files,kb_name)
    print(data)
    data = oa_search_docs(kb_name, subject)
    print(data)
    return filaNameList, data



def download_file_with_headers(url, local_filename, headers, docId, url_type):
    path = dw_path + docId+'\\'
#     print(url_type)
    if not os.path.exists(path):
        os.makedirs(path)
    if url_type == 'main_doc':
        path = path + 'main_doc'+'\\'
    if url_type == 'attach':
        path = path + 'attach'+'\\'
    if url_type == 'dealForm':
        path = path + 'dealForm'+'\\dealForm'
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + local_filename
    # 检查请求是否成功
    # 发送 GET 请求以下载文件，包含请求头
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        # 打开本地文件以写入内容
        with open(path, 'wb') as file:
            # 逐块写入文件内容，以处理大型文件
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'文件已保存为 {local_filename}')
        # 将pdf、docx、doc、ppt、xlsx、wps等格式转换为MD
        result = parse_pdf._type2md('./data/' + docId + '/')
        return result
    else:
        print(f'下载失败，状态码: {response.status_code}')
        return 'FAIL'


# 创建知识库
def oa_create_kb(kb: str):
    # print(f"\n尝试用空名称创建知识库：")
    # data = api.create_knowledge_base(" ")
    # pprint(data)
    # assert data["code"] == 404
    # assert data["msg"] == "知识库名称不能为空，请重新填写知识库名称"
    test_delete_kb_before(kb)
    print(f"\n创建新知识库： {kb}")
    data = kb_api.create_knowledge_base(kb)
    return data 

# 删除知识库
def test_delete_kb_before(kb):
    if not Path(get_kb_path(kb)).exists():
        return
    data = kb_api.delete_knowledge_base(kb)
    assert data["code"] == 200

# 将文件上传至知识库
def oa_upload_docs(oa_files, kb):
    files = list(set(oa_files))
    print(files)
    print(f"\n上传知识文件")
    data = {"knowledge_base_name": kb, "override": True}
    data = kb_api.upload_kb_docs(files, **data)
    assert data["code"] == 200
    assert len(data["data"]["failed_files"]) == 0
    return data

def oa_search_docs(kb, subject):
    query = "概括有关《"+subject+"》的主要内容，大约200字"
    
    print("\n检索知识库：")
    print(query)
    data = kb_api.search_kb_docs(query=query, knowledge_base_name=kb)
    return data

   
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
     if docId is not None or docId != '':
        kb_name = 'Kb_'+docId
        oa_create_kb(kb_name)
        return _Get_docFile(token, docId,subject,kb_name)

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
    find_subjectId('34636446-81e8-4842-b9e1-40733b1e2ccf', '薪休假并入境香港旅游')
