'''
运行时可能会被链家重定向到别的城市，导致无法解析，多运行几次即可
'''
import os
from HouseDetail import get_houselist_detail
from HouseList import *
from Settings import *


# 读取存盘的house_list
house_list_from_file = read_list(FILE_HOUSE_LIST)
if not OFFLINE_MODE:
    # 读取区域列表
    if os.path.exists(FILE_AERA_LIST):  # 删掉该文件可以重新生成区域列表
        aeralist = read_aeralist(FILE_AERA_LIST)
    else:
        aeralist = crawl_aera(LIANJIA_URL)
        save_aeralist(aeralist, FILE_AERA_LIST)
    # 获取房源列表
    (house_list, brief_list, error_page_list) = crawl_house_list(aeralist, brief_mode=BRIEF_MODE)
    # 合并两个列表，去除重复
    house_set = set(house_list) | set(house_list_from_file)
else:  # 使用本地house_list
    house_set = set(house_list_from_file)

if not BRIEF_MODE:
    # 开始读取详细信息
    (house_list_delete, house_list_error) = get_houselist_detail(
        house_set, MONGO_CONN, update=IS_UPDATE_DB)
    # 记录完成情况
    should_done = len(house_set)
    delete = len(house_list_delete)
    err = len(house_list_error)
    print("任务结束，成功" + str(should_done - delete - err) +
          "条，消失" + str(delete) + "条，出错" + str(err) + "条。")
    print("详见" + FILE_HOUSE_DELETE_LIST + ',' + FILE_HOUSE_ERROR_LIST)
    # 存储已消失房源列表
    house_list_delete_fromfile = read_list(FILE_HOUSE_DELETE_LIST)
    save_list(list(set(house_list_delete) | set(
        house_list_delete_fromfile)), FILE_HOUSE_DELETE_LIST)
    # 存储错误列表
    save_list(house_list_error, FILE_HOUSE_ERROR_LIST)

# 存储房源列表
if BRIEF_MODE:
    house_list_success = house_set
else:
    house_list_success = house_set - set(house_list_delete)
save_list(house_list_success, FILE_HOUSE_LIST)

save_list(error_page_list, FILE_PAGE_ERROR_LIST)