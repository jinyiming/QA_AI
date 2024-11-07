import sys
sys.path.append('./')

import requests
import json
from file_rag.common.db import _connDB

def _Get_docStatistic(userId):
    # 统计个人所有文件数量
    cursor, conn = _connDB()
    atdo_sql = "SELECT COUNT(DISTINCT(BUSINESS_SUBJECT)) FROM FLOW_WORK_ATDO WHERE ASSIGN_NO = ? AND flow_status = 'done'"
    todo_sql = "SELECT COUNT(DISTINCT(BUSINESS_SUBJECT)) FROM FLOW_WORK_TODO WHERE ASSIGN_NO = ? AND flow_status = 'running'"
    
    cursor.execute(atdo_sql, (userId,))
    at_num = cursor.fetchone()[0]
    
    cursor.execute(todo_sql, (userId,))
    to_num = cursor.fetchone()[0]
    
    conn.close()
    
    return json.dumps({"在办": at_num, "待办": to_num}, ensure_ascii=False)

if __name__ == "__main__":
    print(_Get_docStatistic('U000035'))
