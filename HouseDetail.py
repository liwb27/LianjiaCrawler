from bs4 import BeautifulSoup
import codecs
import re
import datetime
import sqlite3

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
    

def get_house_detail(html):
    '''
    从html文本中获取房屋详细信息
    '''
    #todo： 判断房屋时在售还是售出，现默认为在售

    house = {}
    bsObj = BeautifulSoup(html, "html.parser")
    #价格
    house["价格"] = float(bsObj.find("div", {"class":"price"}).span.text) # 房屋价格，未解析单位，默认为万

    #基本属性
    table_introContent = bsObj.find("div", {"class":"introContent"})
    table_base = table_introContent.find("div", {"class":"base"}).find("div", {"class":"content"}).ul.findAll("li")
    for item in table_base:
        item.span.decompose()
    house["房屋户型"] = parse_huxing(table_base[0].text.strip('\n'))
    house["所在楼层"] = table_base[1].text.strip('\n')
    house["建筑面积"] = parse_size(table_base[2].text.strip('\n')) #todo：解析楼高
    house["户型结构"] = table_base[3].text.strip('\n')
    house["套内面积"] = parse_size(table_base[4].text.strip('\n'))
    house["建筑类型"] = table_base[5].text.strip('\n')
    house["房屋朝向"] = table_base[6].text.strip('\n').split()
    house["建筑结构"] = table_base[7].text.strip('\n')
    house["装修情况"] = table_base[8].text.strip('\n')
    house["梯户比例"] = parse_tihu(table_base[9].text.strip('\n'))
    house["供暖方式"] = table_base[10].text.strip('\n')
    house["配备电梯"] = table_base[11].text.strip('\n')
    year = re.findall(r"\d+(?=年)", table_base[12].text.strip('\n'))
    if year != []:
        house["产权年限"] =  int(year[0])
    else:
        house["产权年限"] =  None
    #交易属性
    table_transaction = table_introContent.find("div", {"class":"transaction"}).find("div", {"class":"content"}).ul.findAll("li")
    for item in table_transaction:
        item.span.decompose()
    try:
        house["挂牌时间"] = datetime.datetime.strptime(table_transaction[0].text.strip('\n'), "%Y-%m-%d")
    except:
        house["挂牌时间"] = table_transaction[0].text.strip('\n')
    house["交易权属"] = table_transaction[1].text.strip('\n')
    try:
        house["上次交易"] = datetime.datetime.strptime(table_transaction[2].text.strip('\n'), "%Y-%m-%d")
    except:
        house["上次交易"] = table_transaction[2].text.strip('\n')
    house["房屋用途"] = table_transaction[3].text.strip('\n')
    house["抵押信息"] = table_transaction[4].text.strip('\n')
    house["房本备件"] = table_transaction[5].text.strip('\n')
    #todo:房源特色
    # table_introContent_showbasemore = bsObj.find("div", {"class":"introContent showbasemore"}).findAll("div", {"class":"content"})
    # house["核心卖点"] = table_introContent_showbasemore[0].text.strip('\n').strip()
    # house["户型介绍"] = table_introContent_showbasemore[1].text.strip('\n').strip()
    # house["交通出行"] = table_introContent_showbasemore[2].text.strip('\n').strip()
    # house["小区介绍"] = table_introContent_showbasemore[3].text.strip('\n').strip()
    
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

def test():
    f = codecs.open("webpages\\国土资源厅家属院 带车位地下室 户型方正 南北通透_郑州郑州东站建业如意家园二手房推荐(郑州链家网).html", 'r', "UTF-8")
    html = f.read()
    get_house_detail(html)

if __name__ == "__main__":
    test()