import csv


# 输出数据到data.csv文件
def write_csv(csvheader, results, fileName):
    with open(fileName, 'w', encoding='utf-8-sig') as f:
        # f.write(codecs.BOM_UTF8)
        writer = csv.DictWriter(f, csvheader)
        writer.writeheader()
        for row in results:
            writer.writerow(row)