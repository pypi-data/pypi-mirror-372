import requests

def post_url(url, data):
    # 发送POST请求，json参数会自动将字典转换为JSON格式的字符串
    response = requests.post(url, json=data)

    # 检查请求是否成功
    if response.status_code == 200:
        print('请求成功！')
    else:
        print('请求失败，状态码：', response.status_code)

    return response.json()

