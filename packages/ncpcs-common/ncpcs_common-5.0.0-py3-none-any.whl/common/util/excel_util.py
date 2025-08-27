import os

import pandas as pd


def read_excel(file_name, sheet_name='Sheet1'):
    df = pd.read_excel(file_name, sheet_name=sheet_name, dtype=object)
    for ele in df.values:
        yield ele


def get_excel_files(directory="."):
    """
    递归获取目录下的所有Excel文件（.xlsx, .xls）
    """
    excel_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.xlsx', '.xls')) and not file.startswith('~'):
                excel_files.append(os.path.join(root, file))
    return excel_files
