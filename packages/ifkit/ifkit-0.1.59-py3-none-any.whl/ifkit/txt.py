
# 读取 txt 文件
def read_txt(file_name, encoding='GBK', start_read_row_num=0):
    row_num = 0
    with open(file_name, 'r', encoding=encoding) as f:
        for row_data in f.readlines():
            if row_num < start_read_row_num:
                row_num = row_num + 1
                continue

            rn = row_num
            row_num = row_num + 1
            yield (rn, row_data)