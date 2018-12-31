# 收集整理自https://www.cnblogs.com/mengyu/p/9115832.html

import scrapy
import time
import base64
import hashlib
from urllib.parse import urlparse, parse_qs

def get_request(city_id, offset, limit=30, callback=None):
    '''
    获取房屋信息，每次10条，根据offset翻页
    '''
    url_template = 'https://wechat.lianjia.com/ershoufang/search' + "?city_id=%s&condition=&query=&order=&offset=%s&limit=%s&sign"
    url = url_template % (city_id, offset, limit)
    headers = {
        "time-stamp": str(int(time.time() * 1000)),
        "lianjia-source": "ljwxapp",
        "authorization":  get_authorization(url)
    }  # 定义header

    return scrapy.Request(url=url, headers=headers, callback=callback)

def get_authorization(url):
    """
    根据url 动态获取authorization
    :param url:
    :return:
    """

    app_id = "ljwxapp:"
    app_key = "6e8566e348447383e16fdd1b233dbb49"

    param = ""
    parse_param = parse_qs(urlparse(url).query, keep_blank_values=True)  # 解析url参数
    data = {key: value[-1] for key, value in parse_param.items()}  # 生成字典
    dict_keys = sorted(data.keys())  # 对key进行排序
    for key in dict_keys:  # 排序后拼接参数,key = value 模式
        param += str(key) + "=" + data[key]
    param = param + app_key  # 参数末尾添加app_key
    param_md5 = hashlib.md5(param.encode()).hexdigest()  # 对参数进行md5 加密
    authorization_source = app_id + param_md5  # 加密结果添加前缀app_id
    authorization = base64.b64encode(authorization_source.encode())  # 再次进行base64 编码
    return authorization.decode()