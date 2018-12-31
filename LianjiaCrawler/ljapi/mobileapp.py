# 收集自https://github.com/CaoZ/Fast-LianJia-Crawler

import scrapy
import time
import base64
import hashlib
from urllib.parse import urlparse, parse_qs


lian_jia = {
    'ua': 'HomeLink7.7.6; Android 7.0',
    'app_id': '20161001_android',
    'app_secret': '7df91ff794c67caee14c3dacd5549b35'
}

def get_token(url):
    parse_param = parse_qs(urlparse(url).query, keep_blank_values=True)  # 解析url参数
    data = {key: value[-1] for key, value in parse_param.items()}

    data = list(data.items())
    data.sort()

    token = lian_jia['app_secret']

    for entry in data:
        token += '{}={}'.format(*entry)

    token = hashlib.sha1(token.encode()).hexdigest()
    token = '{}:{}'.format(lian_jia['app_id'], token)
    token = base64.b64encode(token.encode()).decode()

    return token



def get_city_info(city_id, callback=None):
    '''
    获得城市详情：区域、商圈、地铁。。。
    '''
    url = 'http://app.api.lianjia.com/config/config/initData?params={"city_id":%s, "mobile_type": "android", "version": "8.0.1"}&fields={"city_info": "", "city_config_all": ""}&request_ts=%s'
    url = url % (city_id, int(time.time()))
    # url = url % (city_id, 1546230132)
    headers = {
        'User-Agent': lian_jia['ua'],
        'Authorization': get_token(url)
    }

    return scrapy.Request(url=url, headers=headers, callback=callback)
    
def get_communities_by_biz_circle(city_id, biz_circle_id, offset=0, limit=30, callback=None):
    """
    按商圈获得小区信息
    """
    url = 'http://app.api.lianjia.com/house/community/search?bizcircle_id=%s&group_type=community&limit_offset=%s&city_id=%s&limit_count=%s&request_ts=%s'
    url = url % (biz_circle_id, offset, city_id, limit, int(time.time()))
    headers = {
        'User-Agent': lian_jia['ua'],
        'Authorization': get_token(url)
    }
    return scrapy.Request(url=url, headers=headers, callback=callback)
    

if __name__ == '__main__':
    get_city_info('410100')
    get_communities_by_biz_circle('410100', 1100001416)
