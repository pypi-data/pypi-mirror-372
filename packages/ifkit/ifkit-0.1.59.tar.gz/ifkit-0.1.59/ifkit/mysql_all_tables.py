#! /usr/bin/env python

import pymysql


def _find_all_tables(cursor, table_schema):
    sql = "SELECT * FROM information_schema.tables WHERE table_schema = '%s';"
    sql = sql % (table_schema,)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    all_tables = []
    for data in all_data:
        all_tables.append(data['TABLE_NAME'])
    return all_tables


def find_all_tables(host, port, user, passwd, db):
    conn = pymysql.connect(host=host,
                           port=port,
                           user=user,
                           passwd=passwd,
                           db=db)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    all_tables = _find_all_tables(cursor, db)

    cursor.close()
    conn.close()

    return all_tables

