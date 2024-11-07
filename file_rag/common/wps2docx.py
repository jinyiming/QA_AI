import comtypes.client
from docx import Document

 
def wps_to_docx(wps_file, docx_file):
    # 初始化一个空的Word文档
    document = Document()
 
    # 使用comtypes加载WPS文档
    wps = comtypes.client.CreateObject('KWPS.Application')
    doc = wps.Documents.Open(wps_file)
    doc.SaveAs(docx_file, 0)  # 0 表示保存为 DOC 格式
    doc.Close()
    wps.Quit()
 
   
 
# # 使用函数转换文件
# wps_to_docx('E:\\vs-python\\AGENTS\\data\\1962300fcc0a2000\\main_doc\\关于《襄阳市网络空间综合治理平台（二期）B包》项目申请软件专业检测名额的请示.wps', 'E:\\vs-python\\AGENTS\\data\\1962300fcc0a2000\\main_doc\\关于《襄阳市网络空间综合治理平台（二期）B包》项目申请软件专业检测名额的请示.docx')