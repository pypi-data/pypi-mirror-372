import os
import zipfile
import rarfile


def unzip_files(directory):
    fail_list = []
    # 遍历目录中的所有文件和子目录
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        # 判断文件是否为RAR或ZIP格式
        if filename.endswith(".rar") or filename.endswith(".zip"):
            print(filename + "开始解压")
            # 创建解压缩目录
            extract_path = os.path.splitext(filepath)[0]
            os.makedirs(extract_path, exist_ok=True)
            # 解压缩文件
            if filename.endswith(".zip"):
                try:
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                except Exception:
                    fail_list.append(filename)
            if filename.endswith(".rar"):
                try:
                    with rarfile.RarFile(filepath, 'r') as rar_ref:
                        rar_ref.extractall(extract_path)
                except Exception:
                    fail_list.append(filename)
            # 删除压缩文件
            print(filename + "解压成功")
        elif os.path.isdir(filepath):
            # 递归遍历子目录
            unzip_files(filepath)
    return fail_list

