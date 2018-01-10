import urllib.request
import requests
import random
import time
def get_lianjian_html(url):
    # req = urllib.request.Request(url, headers=headers)
    # html = urllib.request.urlopen(req)
    try:
        # headers['User-Agent'] = random.choice(user_agent_list)
        html =session.get(url, headers=headers)
        # html =requests.get(url, headers=headers, allow_redirects=False)
        if html.status_code == 301:
            raise Exception
        if html.status_code == 404:
            return None
    except Exception as e:
        print(e)
        return None
    # time.sleep(1)
    return html.content

session = requests.Session()
headers = {
            # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding':'gzip, deflate, br',
            # 'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
            # 'Cache-Control':'max-age=0',
            # 'Connection':'keep-alive',
            # 'Cookie':'lianjia_uuid=85eb4f3c-95cc-4ed2-b86a-07b85e59bc0a; _smt_uid=5a2ff374.4d47b148; UM_distinctid=1604b4efe86291-0c688d7f1f7f73-5a442916-144000-1604b4efe8732b; _ga=GA1.2.1759480769.1513091958; all-lj=eae2e4b99b3cdec6662e8d55df89179a; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1513091956,1513664131,1514519393; _gid=GA1.2.252895151.1515504359; Qs_lvt_200116=1515510036; Qs_pv_200116=3704611047163635700%2C2273924954399624000%2C2186455080714128600%2C100849714713553780%2C1475417949497755100; select_city=410100; CNZZDATA1255849631=430196579-1513658896-https%253A%252F%252Fxa.lianjia.com%252F%7C1515512038; CNZZDATA1255633284=392581843-1513662805-https%253A%252F%252Fxa.lianjia.com%252F%7C1515509930; CNZZDATA1255604082=1765875631-1513660000-https%253A%252F%252Fxa.lianjia.com%252F%7C1515511363; CNZZDATA1254525948=1575827639-1513659362-https%253A%252F%252Fxa.lianjia.com%252F%7C1515512636; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1515513571',
            # 'DNT':'1',
            # 'Host':'zz.lianjia.com',
            # 'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        ]