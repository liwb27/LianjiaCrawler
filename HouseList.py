import re
import os
import urllib.request
import codecs
from urllib.request import urlopen
from bs4 import BeautifulSoup

class Aera:
    subAera = []
    houseCount = 0
    aeraUrl = ""
    aeraName = ""
    def __init__(self, name, url, home_url):
        self.aeraName = name
        #   匹配/ershoufang/shangjiequ/中的shangjiequ/
        new_url = re.findall(r"(?<=/ershoufang/).*",url)
        if new_url.count != 0:
            self.aeraUrl = home_url + new_url[0]
        else:
            raise Exception("没有找到区域的url","Aera.py")

    def get_subaera_dict(self):
        subAeraDict = {}
        for subaera in self.subAera:
            subAeraDict[subaera.aeraUrl] = subaera.aeraName
        return subAeraDict

def get_house_dict(url, saveFileName = "house_list.txt"):
    '''
    从首页url开始，获取所有房源详细url
    得到区域列表->去除重复子区域
    '''
    #写入User Agent信息
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    req = urllib.request.Request(url, headers=head)

    #读取已有的房源列表
    house_dict = {}
    try:
        if os.path.exists(saveFileName):
            f = codecs.open(saveFileName, 'r', "UTF-8")
            content = f.read()
            house_dict = eval(content)
    except:
        print("读取" + saveFileName + "文件异常，未载入已有房源信息")
        house_dict = {}

    aeras = parse_aera(url)
    #去除重复子区域
    subAeraDict = {}
    for aera in aeras:
        subAeraDict.update(aera.get_subaera_dict())

    #收集每个子区域
    house_dict_new = {}
    for (sub_aera_url, sub_aera_name) in subAeraDict.items():
        print("开始收集[" + sub_aera_name + "]子区域...", end="")
        tmpDict = parse_house_url(sub_aera_url)
        oldCount = len(house_dict_new)
        house_dict_new.update(tmpDict) #合并
        newCount = len(house_dict_new)
        print("[" + sub_aera_name + "]收集完成！新收集：" + str(newCount-oldCount) + "条，重复：" + str(len(tmpDict)-newCount+oldCount) + "，共" + str(newCount) + "条")
    
    #比较两次的差值，更新字典
    house_count = len(house_dict)
    house_count_new = len(house_dict_new)
    house_dict.update(house_dict_new)
    house_count_update = len(house_dict)
    print("更新详情：获取房源" + str(house_count_new) + "条，其中新房源" + str(house_count_update - house_count) + "条，更新后总房源" + str(house_count_update) + "条")

    #保存文件
    f = codecs.open(saveFileName, 'w', "UTF-8")
    s = str(house_dict)
    f.write(s)
    f.close()

    return house_dict

def parse_aera(url):
    '''
    从url中得到区域列表和每个区域包含的子区域
    '''
    html = urlopen(url)
    bsObj = BeautifulSoup(html, "html.parser")

    totalNumber = int( bsObj.find("h2", {"class":"total fl"}).find("span").text )#房源总数
    # houseList = bsObj.find("ul", {"class":"sellListContent"})#当前页房源详细列表
    AeraList_html = bsObj.find("div", {"data-role":"ershoufang"}).findAll("a")#区域列表
    aeraList = []
    for item in AeraList_html:
        aera = Aera(item.text, item.attrs['href'], url)
        aeraList.append(aera)

    #print arealist
    for item in aeraList:
        print("发现区域：[" + item.aeraName + "]，", end="")
        (item.subAera, item.houseCount) = parse_subaera(item.aeraUrl, url)
        print("房源共：" + str(item.houseCount) + "套")

    return aeraList

def parse_subaera(url, home_url):
    '''
    获取子区域
    '''
    html = urlopen(url)
    bsObj = BeautifulSoup(html, "html.parser")

    totalNumber = int( bsObj.find("h2", {"class":"total fl"}).find("span").text )#房源总数
    if totalNumber == 0:
        return ([],0)

    # houseList = bsObj.find("ul", {"class":"sellListContent"})#当前页房源详细列表
    SubAeraList_html = bsObj.find("div", {"data-role":"ershoufang"}).findAll("div")[1].findAll("a")#区域列表
    SubAeraList = []
    for item in SubAeraList_html:
        aera = Aera(item.text, item.attrs['href'], home_url)
        SubAeraList.append(aera)
        # print("\t", aera.Name, aera.Url, aera.houseCount)
    
    return (SubAeraList, totalNumber)

def parse_house_url(url):
    '''
    从url中解析所有房源，逐页进行
    '''
    html = urlopen(url)
    bsObj = BeautifulSoup(html, "html.parser")

    totalNumber = int( bsObj.find("h2", {"class":"total fl"}).find("span").text )#房源总数
    if totalNumber > 30*99 : #链家只能查找99页，每页30个，若房源数大于99*30则无法全部抓取
        print("Warning! 房源数过多，无法全部抓取，url:", url)
    if totalNumber == 0:
        print("房源总数为0，", url)
        return {}

    #获取房源总页数
    try:
        pagebox = bsObj.find("div", {"class":"page-box house-lst-page-box"}).attrs["page-data"]
        pageMax = int(re.findall(r"(?<=\"totalPage\":)\d*", pagebox)[0])
        print("共" + str(pageMax) + "页")
    except: 
        print("Exception: 未找到页码总数，已跳过")
        return {}

    #获取每页的房源url
    # houselist = []
    # houselist.extend(GetHouseUrl(bsObj))
    houseDict = {}
    print("正在读取第1页...")
    get_house_url(bsObj, houseDict)
    for i in range(2,pageMax+1):
        print("正在读取第" + str(i) + "页...")
        html_tmp = urlopen(url + "pg" + str(i))
        bs_tmp = BeautifulSoup(html_tmp, "html.parser")
        # houselist.extend(GetHouseUrl(bs_tmp))
        get_house_url(bs_tmp, houseDict)
    return houseDict

def get_house_url(bsObj, houseDict):
    '''
    从bsObj中获取所有的房源url，存放进houseDict中
    '''
    for a in bsObj.find("ul", {"class":"sellListContent"}).findAll("a", {"class":"img"}):
        # urllist.append({'href' : a.attrs["href"], 'title' : a.img.attrs["alt"]})
        if(a.attrs["href"] not in houseDict.keys()):
            houseDict[a.attrs["href"]] = [a.img.attrs["alt"], ]
        else:
            print("发现重复：", a.attrs["href"], a.img.attrs["alt"])
