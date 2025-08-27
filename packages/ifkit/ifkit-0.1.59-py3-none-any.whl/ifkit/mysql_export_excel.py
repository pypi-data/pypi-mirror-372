#! /usr/bin/env python

import decimal
import re

import pymysql


def export_excel(host, port, user, passwd, db, query_sql, charset='utf8', file_name=None):
    conn = pymysql.connect(host=host,
                           port=port,
                           user=user,
                           passwd=passwd,
                           db=db,
                           charset=charset)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    from .excel import WriteXlsxUtil
    write_book = WriteXlsxUtil(file_name)

    cursor.execute(query_sql)
    alias_field = alias(cursor.description)
    write_book.write(tuple(alias_field))

    all_data = cursor.fetchall()
    for data in all_data:
        data_list = []
        for field in alias_field:
            value = data[field]
            data_list.append(replace(value))
        write_book.write(tuple(data_list))

    # 保存文件
    write_book.save()

    # 关闭数据库连接
    cursor.close()
    conn.close()


def alias(description):
    alias_field = []
    for i in range(len(description)):
        alias_field.append(description[i][0])
    return alias_field

def replace(data):
    if data:
        if isinstance(data, decimal.Decimal):
            if data == 0:
                return 0
            else:
                return replace(str(data))
        elif isinstance(data, str):
            # 70.10 -> 70.1
            data = re.sub(r'^(.*\.\d+?)0+$', r'\1', data)
            # 70.00 -> 70
            data = re.sub(r'^(.*)\.0+$', r'\1', data)

            return data
        else:
            return replace(str(data))
    else:
        return ''
