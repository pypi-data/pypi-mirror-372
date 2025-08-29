from typing import Any

from upplib import *
from upplib.common_package import *
from pymysql.connections import Connection

# 创建一个线程本地存储对象
__THREAD_LOCAL_DB_DATA_temp = threading.local().data = {}

# 创建一个线程本地存储对象
__THREAD_LOCAL_DB_DATA_temp = threading.local().data = {}


def get_doris_conn(db_config: str = None) -> Connection:
    db_config = __THREAD_LOCAL_DB_DATA_temp['get_doris_conn_db_config'] = db_config or __THREAD_LOCAL_DB_DATA_temp.get(
        'get_doris_conn_db_config', 'doris')
    return get_connect_from_config(db_config)


# 执行 sql 语句, 并且提交, 默认值提交的了
def exec_doris_sql(sql: str = '',
                   db_config: str = None,
                   database: str = None) -> None:
    db_config = __THREAD_LOCAL_DB_DATA_temp['exec_doris_sql_db_config'] = db_config or __THREAD_LOCAL_DB_DATA_temp.get(
        'exec_doris_sql_db_config', 'doris')
    database = __THREAD_LOCAL_DB_DATA_temp['exec_doris_sql_database'] = database or __THREAD_LOCAL_DB_DATA_temp.get(
        'exec_doris_sql_database', 'mx_risk')
    exec_sql(sql, db_config=db_config, database=database)


def get_data_from_doris(sql: str = '',
                        db_config: str = None) -> tuple[tuple[Any, ...], ...]:
    db_config = __THREAD_LOCAL_DB_DATA_temp[
        'get_data_from_doris_db_config'] = db_config or __THREAD_LOCAL_DB_DATA_temp.get('get_data_from_doris_db_config',
                                                                                        'doris')
    conn_doris = get_connect_from_config(db_config)
    cursor = conn_doris.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_data_from_doris_with_title(sql: str = '',
                                   db_config: str = None) -> tuple[tuple[tuple[Any, ...], ...], list[str]]:
    db_config = __THREAD_LOCAL_DB_DATA_temp[
        'get_data_from_doris_db_config'] = db_config or __THREAD_LOCAL_DB_DATA_temp.get('get_data_from_doris_db_config',
                                                                                        'doris')
    conn_doris = get_connect_from_config(db_config)
    cursor = conn_doris.cursor()
    cursor.execute(sql)
    title_list = [desc[0] for desc in cursor.description]
    return cursor.fetchall(), title_list


def get_data_line_one_from_doris(sql: str = '',
                                 db_config: str = None) -> list | None:
    db_config = __THREAD_LOCAL_DB_DATA_temp[
        'get_data_line_one_from_doris_db_config'] = db_config or __THREAD_LOCAL_DB_DATA_temp.get(
        'get_data_line_one_from_doris_db_config', 'doris')
    data_list = get_data_from_doris(sql, db_config=db_config)
    if len(data_list):
        return list(data_list[0])
    return None


def do_temp(temp=''):
    print(temp)
