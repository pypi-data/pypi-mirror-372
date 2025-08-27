import paramiko


def execute_remote_command(host, port, username, password, command):
    try:
        # 创建SSH客户端对象
        client = paramiko.SSHClient()

        # 自动添加主机密钥
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接到远程主机
        client.connect(hostname=host, port=port, username=username, password=password)

        # 执行命令
        stdin, stdout, stderr = client.exec_command(command)

        # 打印命令输出
        print("命令输出:")
        for line in stdout:
            print(line.strip())

        # 打印错误输出
        error = stderr.read().decode()
        if error:
            print("错误信息:")
            print(error)

        # 关闭SSH连接
        client.close()

    except Exception as e:
        print("连接远程主机并执行命令时出错:", e)

