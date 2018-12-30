'''
房源列表相关函数
'''
import re
import os
import codecs
import pickle
from bs4 import BeautifulSoup
from GetLianjiaHtml import get_lianjian_html
import HouseDetail
import Settings
import datetime

class Aera:
    subAera = []
    houseCount = 0
    aeraUrl = ""
    aeraName = ""

    def __init__(self, name, url, home_url):
        self.aeraName = name
        # 匹配/ershoufang/shangjiequ/中的shangjiequ/
        new_url = re.findall(r"(?<=/ershoufang/).*", url)
        if new_url.count != 0:
            self.aeraUrl = home_url + new_url[0]
        else:
            raise Exception("没有找到区域的url")

    def get_subaera_dict(self):
        '''
        返回子区域，字典类型
        '''
        subAeraDict = {}
        for subaera in self.subAera:
            subAeraDict[subaera.aeraUrl] = subaera.aeraName
        return subAeraDict


def save_aeralist(aera_list, saveFileName):
    byte_list = []
    for aera in aera_list:
        byte_data = pickle.dumps(aera)
        byte_list.append(byte_data)
    save_list(byte_list, saveFileName)


def read_aeralist(saveFileName):
    byte_list = read_list(saveFileName)
    aeralist = []
    for byte_data in byte_list:
        aera = pickle.loads(byte_data)
        aeralist.append(aera)
    return aeralist


def read_list(saveFileName):
    '''
    从存盘文件中读取房源url列表
    '''
    house_from_file = []
    try:
        if os.path.exists(saveFileName):
            f = codecs.open(saveFileName, 'r', "UTF-8")
            content = f.read()
            house_from_file = eval(content)
    except:
        print("读取" + saveFileName + "文件异常，未载入已有房源信息")
        house_from_file = []

    return house_from_file


def save_list(house_list, saveFileName, mode = 'w'):
    '''
    将房源url列表存盘
    '''
    f = codecs.open(saveFileName, mode, "UTF-8")
    s = str(house_list)
    f.write(s)
    f.close()


def crawl_house_list(aeras, brief_mode=False):
    '''
    从首页url开始，获取所有房源详细url
    aeras：子区域列表
    url：起始页url
    parse_house_info：是否读取房源简要信息
    '''
    # 获取所有区域，并去除重复子区域
    subAeraDict = {}
    for aera in aeras:
        subAeraDict.update(aera.get_subaera_dict())

    # 收集每个子区域
    house_list = []
    brief_list = []
    error_page_list = []
    for (sub_aera_url, sub_aera_name) in subAeraDict.items():
        print("开始收集[" + sub_aera_name + "]子区域...", end="")
        # 解析子区域包含的所有网页
        try:
            html = get_lianjian_html(sub_aera_url)
            bsObj = BeautifulSoup(html, "html.parser")
        except:
            error_page_list.append(sub_aera_url)
            continue

        totalNumber = int(bsObj.find(
            "h2", {"class": "total fl"}).find("span").text)  # 房源总数
        if totalNumber > 30 * 99:  # 链家只能查找99页，每页30个，若房源数大于99*30则无法全部抓取
            print("Warning! 房源数过多，无法全部抓取，url:", sub_aera_url)
        if totalNumber == 0:
            print("房源总数为0，", sub_aera_url)
            continue

        # 获取房源总页数
        try:
            pagebox = bsObj.find(
                "div", {"class": "page-box house-lst-page-box"}).attrs["page-data"]
            pageMax = int(re.findall(r"(?<=\"totalPage\":)\d*", pagebox)[0])
            print("共" + str(pageMax) + "页")
        except:
            print("Exception: 未找到页码总数，已跳过")
            continue

        # 获取每页的房源url
        subaera_houselist = []
        subaera_brieflist = []
        print("正在读取第1页...")
        (urllist, brief) = parse_house_url(bsObj, sub_aera_url, brief_mode)
        subaera_houselist.extend(urllist)
        subaera_brieflist.extend(brief)
        for i in range(2, pageMax + 1):
            print("正在读取第" + str(i) + "页...")
            try:
                html_tmp = get_lianjian_html(sub_aera_url + "pg" + str(i))
            except Exception as e:
                print('page read error:' + sub_aera_url + "pg" + str(i))
                error_page_list.append(sub_aera_url + "pg" + str(i))
                html_tmp = None
            if html_tmp != None:
                try:
                    bs_tmp = BeautifulSoup(html_tmp, "html.parser")
                    (urllist, brief) = parse_house_url(bs_tmp, sub_aera_url + "pg" + str(i), brief_mode)
                    subaera_houselist.extend(urllist)
                    subaera_brieflist.extend(brief)
                except:
                    print('解析失败！', sub_aera_url + "pg" + str(i))


        # 合并子区域信息到总列表
        house_list.extend(subaera_houselist)
        brief_list.extend(subaera_brieflist)
        print("[" + sub_aera_name + "]，共" + str(len(subaera_houselist)) + "条")

    count = len(house_list)
    print("共获取房源" + str(count) + "条")
    print('错误页面列表：', error_page_list)

    return (house_list, brief_list, error_page_list)


def crawl_aera(url):
    '''
    从url中得到区域列表和每个区域包含的子区域
    '''
    html = get_lianjian_html(url)
    bsObj = BeautifulSoup(html, "html.parser")

    AeraList_html = bsObj.find(
        "div", {"data-role": "ershoufang"}).findAll("a")  # 区域列表
    aeraList = []
    for item in AeraList_html:
        aera = Aera(item.text, item.attrs['href'], url)
        aeraList.append(aera)

    # 子区域处理
    for item in aeraList:
        print("发现区域：[" + item.aeraName + "]，", end="")
        bsObj = BeautifulSoup(get_lianjian_html(
            item.aeraUrl), "html.parser")  # 打开每个区域的页面查找其子区域
        totalNumber = int(bsObj.find(
            "h2", {"class": "total fl"}).find("span").text)  # 区域房源总数
        if totalNumber != 0:
            SubAeraList_html = bsObj.find(
                "div", {"data-role": "ershoufang"}).findAll("div")[1].findAll("a")  # 子区域列表
            SubAeraList = []
            for subaera_html in SubAeraList_html:
                subaera = Aera(subaera_html.text,
                               subaera_html.attrs['href'], url)
                SubAeraList.append(subaera)
            item.subAera = SubAeraList
            item.houseCount = totalNumber
        print("房源共：" + str(totalNumber) + "套")

    return aeraList


# def crawl_houselist_from_url(url):
#     '''
#     从url中解析所有房源，逐页进行，返回所有房源列表
#     '''
#     html = get_lianjian_html(url)
#     bsObj = BeautifulSoup(html, "html.parser")

#     totalNumber = int(bsObj.find(
#         "h2", {"class": "total fl"}).find("span").text)  # 房源总数
#     if totalNumber > 30 * 99:  # 链家只能查找99页，每页30个，若房源数大于99*30则无法全部抓取
#         print("Warning! 房源数过多，无法全部抓取，url:", url)
#     if totalNumber == 0:
#         print("房源总数为0，", url)
#         return []

#     # 获取房源总页数
#     try:
#         pagebox = bsObj.find(
#             "div", {"class": "page-box house-lst-page-box"}).attrs["page-data"]
#         pageMax = int(re.findall(r"(?<=\"totalPage\":)\d*", pagebox)[0])
#         print("共" + str(pageMax) + "页")
#     except:
#         print("Exception: 未找到页码总数，已跳过")
#         return []

#     # 获取每页的房源url
#     houselist = []
#     print("正在读取第1页...")
#     houselist.extend(parse_house_url(bsObj))
#     for i in range(2, pageMax + 1):
#         print("正在读取第" + str(i) + "页...")
#         html_tmp = get_lianjian_html(url + "pg" + str(i))
#         bs_tmp = BeautifulSoup(html_tmp, "html.parser")
#         houselist.extend(parse_house_url(bs_tmp))
#     return houselist  # 返回list,未去除重复url


def parse_house_url(bsObj, url, brief_mode=False):
    '''
    从bsObj中获取所有的房源url
    仅在crawl_houselist_from_url中调用
    '''
    urllist = []
    brief = {}
    db = Settings.MONGO_CONN.lianjia
    myset = db.house_detail

    for li in bsObj.find("ul", {"class": "sellListContent"}).findAll("li", {"class": "clear"}):
        houseurl = li.a.attrs["href"]
        urllist.append(houseurl)
        if brief_mode:  # 读取brief，写入数据库
            try:
                brief = {}
                brief['_id'] = int(re.findall(r"[0-9]+", houseurl)[0])
                brief['title'] = li.find('div', {'class': 'title'}).text
                attrs = li.find('div', {'class': 'address'}).text.split('|')
                brief['小区名称'] = attrs[0].strip()
                brief['房屋户型'] = HouseDetail.house_detail_switcher(
                    '房屋户型')(attrs[1].strip())
                brief['建筑面积'] = float(re.findall(r"[0-9.]+", attrs[2].strip())[0])
                brief['房屋朝向'] = HouseDetail.house_detail_switcher(
                    '房屋朝向')(attrs[3].strip())
                if len(attrs) >= 5:
                    brief['装修情况'] = attrs[4].strip()
                # floor
                brief['所在区域'] = li.find('div', {'class': 'positionInfo'}).a.extract().text
                floor_text = li.find('div', {'class': 'positionInfo'}).text.split()[0].split('(')
                brief['所在楼层'] = {}
                brief['所在楼层']['所在楼层'] = floor_text[0]
                if len(floor_text) > 1:
                    brief['所在楼层']['总楼层'] = floor_text[1].split(')')[0]
                    brief['所在楼层']['结构'] = floor_text[1].split(')')[1]
                # followinfo
                followinfo_text = li.find('div', {'class': 'followInfo'}).text
                followinfo_text_split = followinfo_text.split('/')
                if len(followinfo_text_split) > 2:
                    brief['发布时间'] = followinfo_text.split('/')[2]
                brief['关注人数'] = int(re.findall(r"[0-9.]+", followinfo_text)[0])
                brief['带看次数'] = int(re.findall(r"[0-9.]+", followinfo_text)[1])
                # tag
                brief['tag'] = []
                for child in li.find('div', {'class': 'tag'}).select('span'):
                    brief['tag'].append(child.text)
                price = {}
                div_price = li.find('div', {'class': 'priceInfo'})
                price['价格'] = {
                    'date': datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d'),
                    '价格': float(re.findall(r"[0-9.]+", div_price.find('div', {'class': 'totalPrice'}).text)[0])
                }
                price['单价'] = {
                    'date': datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d'),
                    '单价': float(re.findall(r"[0-9.]+", div_price.find('div', {'class': 'unitPrice'}).text)[0])
                }
                old_house = myset.find_one({"_id": brief['_id']})
                if not old_house:
                    brief['价格'] = []
                    brief['价格'].append(price['价格'])
                    brief['单价'] = []
                    brief['单价'].append(price['单价'])
                    myset.insert(brief)
                    # print("新增数据库条目成功!")
                else:
                    old_house.update(brief)
                    isTodayFlag = False
                    for item in old_house["价格"]:
                        if item['date'] == datetime.datetime.strptime(str(datetime.date.today()),'%Y-%m-%d'):
                            isTodayFlag = True
                            break
                    if not isTodayFlag:
                        old_house["价格"].append(price["价格"])
                        old_house["单价"].append(price["单价"])
                    myset.save(old_house)
                    # print("更新数据库条目成功!")
            except Exception as e:
                print('house_id:' + url)
                print(e)
                save_list(url,'brief_error.txt','a')

    return (urllist, brief)


def test():
    # crawl_aera("https://zz.lianjia.com/ershoufang/")
    sub_aera_url = 'https://zz.lianjia.com/ershoufang/zhongyuan/pg/3'
    html_tmp = get_lianjian_html(sub_aera_url)
    bs_tmp = BeautifulSoup(html_tmp, "html.parser")
    (urllist, brief) = parse_house_url(bs_tmp, sub_aera_url, True)

if __name__ == "__main__":
    test()
