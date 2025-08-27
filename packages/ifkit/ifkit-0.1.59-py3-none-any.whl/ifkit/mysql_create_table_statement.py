#! /usr/bin/env python

def show_create_table(cursor, table_name):
    try:
        sql = "show create table %s"
        sql = sql % (table_name,)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        return all_data[0]['Create Table']
    except Exception as e:
        print(e)



