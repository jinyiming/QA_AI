from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine
from langchain_community.llms import Ollama
# db = SQLDatabase.from_cnosdb(url='192.168.246.117:5236',user='XYCS' ,password='Xycs#2021', database='XYCS')

db_user = "XYCS"
db_password = "Xycs#2021"
db_host = "localhost"
db_port = '5236'

llm = Ollama(model="llama:latest")
#注意要安装pymysql这个库
include_tables = ['ums_user', 'ums_user_org_relate', 'ums_org']
db = SQLDatabase.from_uri(f"dm+dmPython://{db_user}:{db_password}@{db_host}", schema='XYCS', include_tables=include_tables)
print(db._schema)
# print(f'niaho {db.dialect}')
print(print(db.get_usable_table_names()))
print(db.run('select count(*) from ums_user'))
# # # 构造连接配置
# # # engine = create_engine("dm+dmPython://XYCS:password@192.168.246.117:5236")
# # engine = create_engine('dm+dmPython://SYSDBA:SYSDBA@192.168.246.117:5236')
# # # 使用 SQLAlchemy 引擎创建 SQLDatabase
# # database = SQLDatabase(engine)
chain = create_sql_query_chain(llm, db)
chain.get_prompts()[0].pretty_print()
response = chain.invoke({"question": "统计有ums_user表有多少个用户以及ums_org中有多少个部门"})
print(response)
print(db.run(response))

