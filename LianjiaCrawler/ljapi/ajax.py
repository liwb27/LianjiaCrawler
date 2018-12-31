# 收集自https://github.com/xjkj123/Lianjia/

import scrapy
import time
import base64
import hashlib
import math
from urllib.parse import urlparse, parse_qs

def GetMD5(string_):
    m = hashlib.md5()
    m.update(string_.encode('utf-8'))
    return m.hexdigest()

def GetAuthorization(dict_):
    datastr = "vfkpbin1ix2rb88gfjebs0f60cbvhedlcity_id={city_id}group_type={group_type}max_lat={max_lat}" \
                "max_lng={max_lng}min_lat={min_lat}min_lng={min_lng}request_ts={request_ts}".format(
        city_id=dict_["city_id"],
        group_type=dict_["group_type"],
        max_lat=dict_["max_lat"],
        max_lng=dict_["max_lng"],
        min_lat=dict_["min_lat"],
        min_lng=dict_["min_lng"],
        request_ts=dict_["request_ts"])
    authorization = GetMD5(datastr)
    return authorization

city_dict = {
    '310000': {'name': '上海', 'max_lat': '31.36552', 'min_lat': '31.106158', 'max_lng': '121.600985',
            'min_lng': '121.360095'},
    '110000': {'name': '北京', 'max_lat': '40.074766', 'min_lat': '39.609408', 'max_lng': '116.796856',
            'min_lng': '115.980476'},
    '440100': {'name': '广州', 'max_lat': '23.296086', 'min_lat': '22.737277', 'max_lng': '113.773905',
            'min_lng': '113.038013'},
    '440300': {'name': '深圳', 'max_lat': '22.935891', 'min_lat': '22.375581', 'max_lng': '114.533683',
            'min_lng': '113.797791'},
    '430100': {'name': '长沙', 'max_lat': '28.368467', 'min_lat': '28.101143', 'max_lng': '113.155889',
            'min_lng': '112.735051'},
    '370600': {'name': '烟台', 'max_lat': '37.590234', 'min_lat': '37.349651', 'max_lng': '121.698469',
            'min_lng': '121.210365'},
    '350200': {'name': '厦门', 'max_lat': '24.794145', 'min_lat': '24.241819', 'max_lng': '118.533083',
            'min_lng': '117.892627'},
    '410100': {'name': '郑州', 'max_lat': '35', 'min_lat': '34', 'max_lng': '115',
            'min_lng': '112'}
}

headers = {
    'Host': 'ajax.lianjia.com',
    'Referer': 'https://sh.lianjia.com/ditu/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

url = 'https://ajax.lianjia.com/map/search/ershoufang/?callback=jQuery1111012389114747347363_1534230881479' \
        '&city_id=%s' \
        '&group_type=%s' \
        '&max_lat=%s' \
        '&min_lat=%s' \
        '&max_lng=%s' \
        '&min_lng=%s' \
        '&filters=%s' \
        '&request_ts=%d' \
        '&source=ljpc' \
        '&authorization=%s' \
        '&_=%d'
url_fang = 'https://ajax.lianjia.com/map/resblock/ershoufanglist/?callback=jQuery11110617424919783834_1541868368031' \
                '&id=%s' \
                '&order=0' \
                '&page=%d' \
                '&filters=%s' \
                '&request_ts=%d' \
                '&source=ljpc' \
                '&authorization=%s' \
                '&_=%d'

def get_district_info(city_id, callback=None):
    """
    :str city_id:
    北京:110000  上海:310000
    #获取上海的各个区域，例如浦东，长宁，徐汇
    """
    global headers, url
    time_13 = int(round(time.time() * 1000))
    authorization = GetAuthorization({
            'group_type': 'district',
            'city_id': city_id,
            'max_lat': city_dict[city_id]['max_lat'],
            'min_lat': city_dict[city_id]["min_lat"],
            'max_lng': city_dict[city_id]["max_lng"],
            'min_lng': city_dict[city_id]["min_lng"],
            'request_ts': time_13
        })
    # %7B%7D = {}
    url = url % (city_id, 'district', city_dict[city_id]['max_lat'], city_dict[city_id]["min_lat"], city_dict[city_id]["max_lng"], city_dict[city_id]["min_lng"], '%7B%7D', time_13, authorization, time_13)
    return scrapy.Request(url, headers=headers, callback=callback) #解码response方法 json.loads(response.text[43:-1])


def get_community_info(city_id, max_lat, min_lat, max_lng, min_lng, callback=None):
    """
    :str city_id:
    北京:110000  上海:310000
    : 地理范围经纬度，区域范围0.02°
    """
    global headers, url
    time_13 = int(round(time.time() * 1000))
    authorization = GetAuthorization({
        'group_type': 'community',
        'city_id': city_id,
        'max_lat': city_dict[city_id]['max_lat'],
        'min_lat': city_dict[city_id]["min_lat"],
        'max_lng': city_dict[city_id]["max_lng"],
        'min_lng': city_dict[city_id]["min_lng"],
        'request_ts': time_13
    })
    url = url % (city_id, 'community', city_dict[city_id]['max_lat'], city_dict[city_id]["min_lat"], city_dict[city_id]["max_lng"], city_dict[city_id]["min_lng"], '%7B%7D', time_13, authorization, time_13)

    return scrapy.Request(url, headers=headers, callback=callback) #解码response方法 json.loads(response.text[43:-1])

def get_house_info(community_id, community_house_count, callback=None):
    global url_fang
    for page in range(1, math.ceil(community_house_count / 10) + 1):
        time_13 = int(round(time.time() * 1000))
        authorization = GetMD5(
            "vfkpbin1ix2rb88gfjebs0f60cbvhedlid={id}order={order}page={page}request_ts={request_ts}".format(
                id=community_id, order=0, page=page, request_ts=time_13))
        # e = {id: "1111027380242", order: 0, page: 1, filters: "{}", request_ts: 1541871468249} 1b9f64bd353667b4e44ed593eca6451d
        ###############-----拼接请求url-----#################
        url = url_fang % (community_id, page, '%7B%7D', time_13, authorization, time_13)

        yield scrapy.Request(url, headers=headers, callback=callback)
