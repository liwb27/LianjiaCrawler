'''
房源详细信息相关函数
'''
import codecs
import re
import datetime
from bs4 import BeautifulSoup
from GetLianjiaHtml import get_lianjian_html

def house_detail_switcher(label):
    def parse_huxing(text):
        ting = re.findall(r"\d(?=室)",text)
        if ting != []:
            ting = int(ting[0])
        else:
            ting = 0
        shi = re.findall(r"\d(?=厅)",text)
        if shi != []:
            shi = int(shi[0])
        else:
            shi = 0
        chu = re.findall(r"\d(?=厨)",text)
        if chu != []:
            chu = int(chu[0])
        else:
            chu = 0
        wei = re.findall(r"\d(?=卫)",text)
        if wei != []:
            wei = int(wei[0])
        else:
            wei = 0
        return {
            "室":ting,
            "厅":shi,
            "厨":chu,
            "卫":wei,
        }

    def parse_tihu(text):
        chs_arabic_map = {u"零":0, u"一":1, u"二":2, u"三":3, u"四":4, u"五":5, u"六":6, u"七":7, u"八":8, u"九":9, u"两":2, 
                        u"十":10, u"十一":11, u"十二":12, u"十三":13, u"十四":14, u"十五":15, u"十六":16, u"十七":17, u"十八":18, u"十九":19}
        ti = re.findall(r".(?=梯)",text)
        if ti != []:
            ti = chs_arabic_map[ti[0]]
        else:
            ti = 0
        hu = re.findall(r".(?=户)",text)
        if hu != []:
            hu = chs_arabic_map[hu[0]]
        else:
            hu = 0

        return {
            "梯":ti,
            "户":hu,
        }

    def parse_size(text):
        size = re.findall(r"[0-9.]+(?=㎡)", text)
        if size != []:
            return float(size[0])
        else:
            return None

    def parse_year(text):
        year = re.findall(r"\d+(?=年)", text)#
        if year != []:
            return int(year[0])
        else:
            return None

    def parse_date(text):
        try:
            return datetime.datetime.strptime(text, "%Y-%m-%d")
        except:
            return text

    #属性解析器
    switcher = {
        "房屋户型": parse_huxing,
        "建筑面积": parse_size,
        "套内面积": parse_size,
        "房屋朝向": lambda text:text.split(),
        "梯户比例": parse_tihu,
        "产权年限": parse_year,
        "挂牌时间": parse_date,
        "上次交易": parse_date
    }

    return switcher.get(label, lambda text: text)


def get_house_detail(html):
    '''
    从html文本中获取房屋详细信息
    '''
    #todo： 判断房屋时在售还是售出，现默认为在售
    if html == None:
        return {}
    house = {}
    bsObj = BeautifulSoup(html, "html.parser")

    #价格
    house["价格"] = {str(datetime.date.today()) : float(bsObj.find("div", {"class":"price"}).span.text)} # 房屋价格，未解析单位，默认为万
    house["单价"] = {str(datetime.date.today()) : float(re.findall("[0-9.]+", bsObj.find("div", {"class":"unitPrice"}).span.text)[0])} #元/平米
    #基本属性
    table_introContent = bsObj.find("div", {"class":"introContent"})
    table_base = table_introContent.find("div", {"class":"base"}).find("div", {"class":"content"}).ul.findAll("li")
    for item in table_base:
        label = item.span.extract().text
        house[label] =house_detail_switcher(label)(item.text.strip('\n'))

    #交易属性
    table_transaction = table_introContent.find("div", {"class":"transaction"}).find("div", {"class":"content"}).ul.findAll("li")
    for item in table_transaction:
        label = item.span.extract().text
        house[label] =house_detail_switcher(label)(item.text.strip('\n'))

    #房源特色
    table_name = bsObj.find("div", {"class":"introContent showbasemore"}).findAll("div", {"class":"name"})
    table_content = bsObj.find("div", {"class":"introContent showbasemore"}).findAll("div", {"class":"content"})
    if len(table_name) == len(table_content):
        for i in range(0, len(table_name)):
            name = table_name[i].text
            content = table_content[i].text.strip()
            house[name] =house_detail_switcher(label)(content)
    
    #小区名称，所在区域
    table_aroundInfo = bsObj.find("div", {"class":"aroundInfo"})
    house["小区名称"] = table_aroundInfo.find("div", {"class":"communityName"}).a.text
    house["所在区域"] = []
    for aera in table_aroundInfo.find("div", {"class":"areaName"}).findAll("a", {"target":"_blank"}):
        house["所在区域"].append(aera.text)
    house["_id"] = int(table_aroundInfo.find("div", {"class":"houseRecord"}).find("span", {"class":"info"}).next)
    #todo：经纪人带看情况

    #返回值
    return house

def get_houselist_detail(house_list, conn, update = True):
    '''
    分析house_list中所有的房源数据，结果存入数据库中
    '''
    #数据库表设置
    db = conn.lianjia
    myset = db.house_detail
    #记录完成信息
    house_list_delete = []
    # house_list_finished = []
    house_list_error = []
    count = len(house_list)
    num = 1
    for key in house_list:
        id =  int(re.findall(r"[0-9]+", key)[0])
        print("开始读取"+str(num)+"/"+str(count),key,end="  ")
        num = num + 1
        try:
            html = get_lianjian_html(key)
            if html == None:
                house_list_delete.append(key)
            else:
                house = get_house_detail(html)
                old_house = myset.find_one({"_id":id})
                # myset.update({"_id":id}, house, upsert=True)
                if not old_house:
                    myset.insert(house)
                    print("新增数据库条目成功!")
                else:
                    if update:
                        old_house["价格"].update(house["价格"])
                        house["价格"] = old_house["价格"]
                        old_house["单价"].update(house["单价"])
                        house["单价"] = old_house["单价"]
                        myset.save(house)
                        print("更新数据库条目成功!")
                    else:
                        print("跳过已存在条目！")
        except Exception as e:
            house_list_error.append(key)
            print(e)
    return (house_list_delete, house_list_error)

def test():


    f = codecs.open("house_list.txt", 'r', "UTF-8")
    urllist = eval(f.read())
    for url in urllist:
        html = get_lianjian_html(url)
        house = get_house_detail(html)
        print(house)
    print("done")

if __name__ == "__main__":
    test()