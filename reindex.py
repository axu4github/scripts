# coding: utf-8

import csv

file = 'kf_kf01_20170220_1.index'
new_file = 'kf_kf01_20170220_1.index.new'

rows = []
with open(file, 'rb') as f:        # 采用b的方式处理可以省去很多问题
    reader = csv.reader(f)
    for row in reader:
        tmp = row
        tmp[7] = tmp[6]
        rows.append(tmp)

print len(rows)

with open(new_file, 'wb') as f:      # 采用b的方式处理可以省去很多问题
    writer = csv.writer(f)
    writer.writerows(rows)
