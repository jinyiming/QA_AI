import sys
sys.path.append('./')
from file_rag.server.utils import (wrap_done, get_ChatOpenAI, get_default_llm,
                                   BaseResponse, get_prompt_template, build_logger,
                                   check_embed_model, api_address
                                   )
from file_rag.knowledge_base.kb_doc_api import search_docs
from fastapi.concurrency import run_in_threadpool
from file_rag.knowledge_base.kb_service.base import KBServiceFactory
from file_rag.knowledge_base.utils import format_reference1
import json
from fuzzywuzzy import fuzz
from pathlib import Path
import os
import requests
from typing import AsyncIterable, List, Optional, Literal
from file_rag.common import parse_pdf
from file_rag.settings import Settings
from file_rag.knowledge_base.utils import get_file_path, get_kb_path
from file_rag.server.utils import api_address
from file_rag.webui_pages.utils import ApiRequest

import asyncio

logger = build_logger()

api_base_url = api_address()
kb_api: ApiRequest = ApiRequest(api_base_url)

with open('api_config.json', 'r') as file:
    data = json.load(file)
    api = data.get('api')
    dw_path = data.get('download_path')


def _Get_docFile(token, docId, subject, kb_name, businessName):
    print('进入文件下载API')
    # 意见内容
    opinion_url = f'{
        api}/opinion/listDocOpinionByDocId?docId={docId}&_t=1724053904273'
    # 流程记录
    flow_url = f'{api}/workflow/getFlowRecordList4Page?businessDocId={
        docId}&offset=0&limit=1000&_t=1724205642655'

    # 基本信息
    if businessName == '发文':
        doc_info = f'{
            api}/doc/dispatch/getDispatchById?docId={docId}&_t=1725847692'
    elif businessName == '收文':
        doc_info = f'{
            api}/doc/receival/getReceivalById?docId={docId}&_t=1725863919760'
    # 正文
    main_url = f'{api}/attachment/listEgovAttsByDocIdAndTypes?docId={
        docId}&type%5B%5D=main_doc&type%5B%5D=main_trace&type%5B%5D=main_ofd&type%5B%5D=main_pdf&type%5B%5D=main_copy&containFile=false&moduleId=&_t=1724135953238'
    # 附件
    attach_url = f'{api}/attachment/listEgovAttsByDocIdAndTypes?docId={
        docId}&type%5B%5D=attach&containFile=false'
    # 办理单
    dealForm_url = f'{
        api}/attachment/listEgovAttByDocId?docId={docId}&type=dealForm'

    file_urls = [opinion_url, flow_url, doc_info,
                 main_url, attach_url, dealForm_url]
#     download_url =f'http://192.168.244.92:2080/attachment/downloadEgovAttFile?id={id}&moduleId={moduleId}&x-auth-token={token}'
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    docs_all = []
    filaNameList = []
    # 向量数据库 kb
    oa_files = []
    for url_type in file_urls:
        try:
            response = requests.get(url_type, headers=headers)
            if response.status_code == 200:
                all = {}
                # print(response.json())
                if url_type == opinion_url:
                    type = '公文意见'
                    opinionContent = []
                    for doc in response.json():
                        opinion = {}
                        opinion['opinionContent'] = doc['opinionContent']
                        opinion['opinionUser'] = doc['opinionUser']
                        opinion['createTime'] = doc['createTime']
                        opinion['opinionCodeName'] = doc['opinionCodeName']
                        opinionContent.append(opinion)
                    all['type'] = type
                    all['content'] = opinionContent

                if url_type == flow_url:
                    type = '流程记录'
                    api_data_workFlow = response.json()
                    a = [doc['stateName'] for doc in api_data_workFlow['list']]
                    flowWork_stateName = a[len((a))-1]
                    # 这是获取最后一条班里人记录
                    flowWork_stateName = api_data_workFlow['list'][-1]['stateName']
                    # print(flowWork_stateName)

                    flowWork_assignName = api_data_workFlow['list'][-1]['assignName']

                    flowWork_isRead = api_data_workFlow['list'][-1]['isRead']

                    current_statue = f'当前流程在【{flowWork_stateName}】环节，【{
                        flowWork_assignName}】正在办理中。'
                    print(f'目前流程在【{flowWork_stateName}】环节，【{
                          flowWork_assignName}】人正在办理中。')
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
                                    if len(deal['assignArray']) > 0:
                                        receiver_statename = deal['assignArray'][0]['stateName']
                                        receiver = deal['assignArray'][0]['assignObject']
                                        work_info += (f"第{num}个环节中 【{fs_stateName}】环节，【{hander}】在{send_time}将文件{
                                                      [f'发送' if op == 'send' else '办理']}给【{receiver_statename}】的【{receiver}】。\n")
                                num = num + 1
                        work_info = work_info + f"第{api_data_workFlow['total']}个环节中 【{flow['stateName']}】环节，【{
                            flow['assignName']}】正在办理，目前处于：{f'已读' if flow['isRead'] == '1' else f'未读'}状态。\n"
                        work_info = f'该文件一共经历{api_data_workFlow['total']}个环节:\n 流程记录为：\n{
                            work_info}\n 最新动态为：\n{current_statue}'
                        all['type'] = type
                        all['content'] = work_info
                if url_type == doc_info and businessName == "发文":
                    type = '公文基本信息'
                    docInfos = []
                    docInfo = {}
                    f = response.json()
                    # 文件标题
                    docInfo['subject'] = f['subject']
                    # 拟文科室
                    docInfo['draftDept'] = f['draftDept']
                    # 拟文时间
                    docInfo['draftDate'] = f['draftDate']
                    # 编号
                    docInfo['docWord'] = f['docWord']
                    # 密级
                    docInfo['secLevel'] = f['secLevel']
                    # 紧急程度
                    docInfo['urgentLevel'] = f['urgentLevel']
                    # 流水号
                    docInfo['docSequence'] = f['docSequence']
                    # 科室承办人...,
                    docInfos.append(docInfo)
                    all['type'] = type
                    all['content'] = docInfos
                if url_type == doc_info and businessName == "收文":
                    type = '公文基本信息'
                    docInfos = []
                    docInfo = {}
                    f = response.json()
                    # 文件标题
                    docInfo['subject'] = f['subject']
                    # 来文单位
                    docInfo['sourceUnit'] = f['sourceUnit']
                    # 编号
                    docInfo['docMark'] = f['docMark']
                    # 收文科室
                    docInfo['draftUserDept'] = f['draftUserDept']
                    # 收文日期
                    docInfo['receivalDate'] = f['receivalDate']
                    # 登记人
                    docInfo['draftUser'] = f['draftUser']
                    # 紧急程度
                    docInfo['urgenLevel'] = f['urgenLevel']
                    # 密级
                    docInfo['secLevel'] = f['secLevel']
                    # 文件种类
                    docInfo['docType'] = f['docType']
                    docInfos.append(docInfo)
                    all['type'] = type
                    all['content'] = docInfos
                if url_type == main_url or url_type == attach_url or url_type == dealForm_url:
                    if url_type == main_url:
                        type = '正文内容'
                    elif url_type == attach_url:
                        type = '附件内容'
                    elif url_type == dealForm_url:
                        type = '办理单内容'
                    fs = []

                    for f in response.json():
                        id = f['id']
                        moduleId = f['moduleId']
                        print(moduleId)
                        fileName = f['fileName'] + '.' + f['fileSuffix']
                        filaNameList.append(fileName)
                        fs.append(fileName)
                    #     print(fileName)
                        url = f'{api}/attachment/downloadEgovAttFile?id={
                            id}&moduleId={moduleId}&x-auth-token={token}'
                        oa_file = download_file_with_headers(
                            url, fileName, headers, f['docId'], f['type'])
                        oa_files.append(oa_file)
                    all['type'] = type
                    all['content'] = fs
            else:
                print(f"Failed to fetch data, status code: {
                      response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        docs_all.append(all)
    print(oa_files)
    data = oa_upload_docs(oa_files, kb_name)
    print(data)
    data = oa_search_docs(kb_name, subject)
    print(data)
    return docs_all, filaNameList, data

# def wps_to_docx(wps_file, docx_file):
#     import comtypes.client
#     from docx import Document
#     # 初始化一个空的Word文档
#     document = Document()

#     # 使用comtypes加载WPS文档
#     wps = comtypes.client.CreateObject('KWPS.Application')
#     doc = wps.Documents.Open(wps_file)
#     doc.SaveAs(docx_file, 0)  # 0 表示保存为 DOC 格式
#     doc.Close()
#     wps.Quit()


def read_wps_content(file_path):
    import win32com.client
    word = win32com.client.Dispatch('Word.Application')
    doc = word.Documents.Open(file_path)
    content = doc.Content.Text
    doc.Close(False)
    word.Quit()
    return content

# def write_to_doc(file_path, wps_path):
#     import win32com.client
#     # 启动 Word 应用程序
#     word = win32com.client.Dispatch('Word.Application')
#     doc1 = word.Documents.Open(wps_path)
#     content = doc1.Content.Text
#     # 创建一个新的文档
#     doc = word.Documents.Add()

#     # 插入内容
#     doc.Content.Text = content

#     # 保存文档
#     doc.SaveAs(file_path)
#     # 关闭文档和 Word 应用程序
#     doc.Close()
#     word.Quit()


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
        path = path + 'dealForm'+'\\'
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
        # result = parse_pdf._type2md('./data/' + docId + '/')
        if local_filename.split('.')[1] == 'html':
            import pdfkit
            new_file_path = path.replace(
                '/', '\\').replace('.html', '.pdf')
            pdfkit.from_file(path.replace('/', '\\'), new_file_path)
            if os.path.exists(path):
                os.remove(path)
                print(f"文件 {path} 已被删除")
            else:
                print(f"文件 {path} 不存在")
            path = new_file_path
        if local_filename.split('.')[1] == 'wps':
            new_file_path = path.replace(
                '/', '\\').replace('.wps', '.md')
            # print(path.replace('/', '\\'))
            # print(new_file_path)
            content = read_wps_content(path.replace('/', '\\'))
            with open(new_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(content)
            if os.path.exists(path):
                os.remove(path)
                print(f"文件 {path} 已被删除")
            else:
                print(f"文件 {path} 不存在")
            path = new_file_path

        result = path
        print(result)
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
    query = "概括有关《"+subject+"》的主要内容，从处理签中的文件信息内容、意见内容以及正文、附件的内容，分类概括。不超过500字。"

    print("\n检索知识库：")
    print(query)
    data = kb_api.search_kb_docs(query=query, knowledge_base_name=kb)
    return data


def find_subjectId(token, subject, query):
    headers = {
        "Accept": 'application/json, text/plain, */*',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "cache-control": 'no-cache',
        # 替换为实际的 Cookie 值
        'Cookie': f'x-authenticated=true; x-auth-token={token}; JSESSIONID=CBB7D86FF577CFA26EEA5BDAC29F06E4'
    }
    todo_url = f'{
        api}/workflow/getActivityWorkTodoList4Page?flowStatus=running&offset=0&limit=10000'
    atdo_url = f'{
        api}/workflow/getActivityWorkTodoList4Page?flowStatus=done&offset=0&limit=10000&sort=createTime'
    docs = [todo_url, atdo_url]
    file_list = []
    for url in docs:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                #           print(response.json())
                list = response.json()['list']
                if list:
                    for l in list:
                        doc = {}
                        doc['businessSubject'] = l['businessSubject']
                        doc['businessDocId'] = l['businessDocId']
                        doc['businessName'] = l['businessName']
                        file_list.append(doc)
            else:
                print(f"Failed to fetch data, status code: {
                      response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    docId, businessName, r_subject = find_most_similar_item(file_list, subject)
    print(businessName, r_subject)
    if docId is not None or docId != '':
        # 判断知识库是否已经存在
        kb_name = 'Kb_'+docId
        if not Path(get_kb_path(kb_name)).exists():
            oa_create_kb(kb_name)
            return _Get_docFile(token, docId, r_subject, kb_name, businessName)
        else:
            print('知识库已存在，只进行检索即可')
            kb = KBServiceFactory.get_service_by_name(kb_name)
            ok, msg = kb.check_embed_model()
            if not ok:
                raise ValueError(msg)
            # docs = run_in_threadpool(search_docs,
            #                          query=query,
            #                          knowledge_base_name=kb_name,
            #                          top_k=3,
            #                          score_threshold='2.0',
            #                          file_name="",
            #                          metadata={})
            docs = search_docs(query=query, knowledge_base_name=kb_name, top_k=3,score_threshold=2.0,file_name="",metadata={})
            source_documents = format_reference1(
                kb_name, docs, api_address(is_public=True))
            a = ''
            b =''
            print(f'------------{source_documents}')
            return a, b , source_documents

def find_most_similar_item(json_data, string_a):
    # 将 JSON 字符串解析为 Python
    max_similarity = 0
    most_similar_item = None
    # businessName
    most_similar_businessDocId = ''
    most_similar_businessName = ''
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
            most_similar_businessName = most_similar_item.get(
                'businessName', '')
    most_similar_businessDocId = most_similar_businessDocId
    most_similar_businessSubject = most_similar_businessSubject
    max_similarity = max_similarity
    print(f'相似度最高的是：{most_similar_businessSubject}:{
          max_similarity}:{most_similar_businessName}')
    return most_similar_businessDocId, most_similar_businessName, most_similar_businessSubject


if __name__ == "__main__":
    find_subjectId('1f4d361d-a4ca-4f34-b2aa-48445faf145e',
                   '弱口令', '弱口令的主要内容是什么')
