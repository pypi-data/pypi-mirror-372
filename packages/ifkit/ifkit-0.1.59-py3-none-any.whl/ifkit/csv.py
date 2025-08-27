import csv
from collections.abc import Iterable
from collections.abc import Iterator

# 读取 CSV 文件
def read_csv(file_name, encoding='UTF8', start_read_row_num=0):
    row_num = 0
    with open(file_name, 'r', encoding=encoding) as f: # encoding='UTF8'   encoding='GBK'
        reader = csv.DictReader(f)
        for row_data in reader:
            if row_num < start_read_row_num:
                row_num = row_num + 1
                continue

            rn = row_num
            row_num = row_num + 1
            yield (rn, row_data)

