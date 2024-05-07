import requests


def check_website_availability(url):
    try:
        response = requests.get(url, timeout=5)
        # 检查响应状态码是否为 200，表示网站可访问
        return response.status_code == 200
    except Exception as e:
        return False
