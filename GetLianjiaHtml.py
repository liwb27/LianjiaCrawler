'''
获取html源码
'''
import requests

def get_lianjian_html(url):
    try:
        html =session.get(url, headers=headers)
        if html.status_code == 301:#重定向
            raise Exception
        if html.status_code == 404:#页面未找到
            return None
    except Exception as e:
        print(e)
        return None
    return html.content

session = requests.Session()

headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
