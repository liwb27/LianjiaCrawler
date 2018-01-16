"""
参数设置
"""

from pymongo import MongoClient

# 控制参数
OFFLINE_MODE = False  # 是否重新爬取房源列表，=false时会忽略QUICK_MODE
BRIEF_MODE = True  # true：不打开房源单独页面，直接从区域页面读取房源简要信息；false：打开每个房源url，速度慢；
# offline与quick_mode均为true时，不爬取数据


# 数据库
MONGO_CONN = MongoClient('localhost', 27017)  # 连接
IS_UPDATE_DB = True  # 是否更新数据库中已有条目

# 链家二手房链接首页
LIANJIA_URL = "https://zz.lianjia.com/ershoufang/"

# 存盘文件名
FILE_AERA_LIST = "aera_list.txt"
FILE_HOUSE_LIST = "house_list.txt"
FILE_HOUSE_DELETE_LIST = "house_list_delete.txt"
FILE_HOUSE_ERROR_LIST = "house_list_error"
