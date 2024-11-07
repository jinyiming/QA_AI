from operator import itemgetter
# db = SQLDatabase.from_cnosdb(url='192.168.246.117:5236',user='XYCS' ,password='Xycs#2021', database='XYCS')
import dmPython


def _connDB():
    db_user = "XYCS"
    db_password = "Xycs#2021"
    db_host = "192.168.246.117"
    db_port = '5236'

    conn = dmPython.connect(user=db_user, password=db_password,
                            server=db_host, port=db_port, autoCommit=True)
#     finallySQL = "SELECT * FROM EGOV_ATT WHERE ...."
    try:
        cursor = conn.cursor()
        print('数据库连接成功！！')
    #     cursor.execute(finallySQL)
    #     resluts = cursor.fetchall()
        # print([{re for re in resluts}])
        return cursor, conn
    except ConnectionError as e:
        print(f'数据库连接异常：{e}')

    # 只是输出sql并未通过chain执行sql
    # chain = create_sql_query_chain(llm, db)
    # chain.get_prompts()[0].pretty_print()
    # response = chain.invoke({"question": "统计有ums_user表有多少个用户"})
    # print(response)
    # print(db.run(response))

    # 通过chain工具实现
