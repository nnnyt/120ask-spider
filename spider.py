# coding: utf-8
# create by Yuting Ning on 2019/11/3
# 爬取快速问医生检查库信息

import json
from bs4 import BeautifulSoup
import logging
import requests
import re
import time

HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36"
                  "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
}
LOG_LEVEL = logging.INFO
prefix = 'http://tag.120ask.com/jiancha/'
# 检查库共3442个页面
urls = [prefix + '{}'.format(i) for i in range(1, 3450)]
DEFAULT_DATADIR = "./"


def get_logger():
    """
    创建日志实例
    """
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    logger = logging.getLogger("monitor")
    logger.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def write_json(data, data_dir=DEFAULT_DATADIR, encoding='utf-8', indent=2):
    """
    将json输出到文件
    :param indent:
    :param encoding:
    :param data:
    :param data_dir:
    :return:
    """
    f = open(data_dir + 'data.json', 'w', encoding=encoding)
    json.dump(data, f, ensure_ascii=False, indent=indent)
    f.close()
    logger.info("数据已写入文件" + data_dir + 'data.json')


def get_related_disease(bs):
    """
    获取相关疾病
    :param bs:
    :return: 返回一个元组[]，里面是每个疾病对应的字典
    """
    related = bs.find("div", class_="w_cr1").find("div", class_="clears").find_all("a")
    name = []
    site = []
    for i in related:
        name.append(i.text)
        site.append(i.get("href"))
    related_disease = []
    for i in range(len(name)):
        temp = {'名称': name[i], '网址': site[i]}
        related_disease.append(temp)
    # print(related_disease)
    logger.info("完成相关疾病的获取")
    return related_disease


def get_clinical(bs):
    """
    获取临床意义: "",注意事项: "",检查过程: "",不适宜人群: "",不良反应与风险: ""
    :param bs:
    :return:
    """
    clinical = bs.find_all("div", class_="ys-clinical")
    # clinical_str = []
    clinical_str = {}
    for i in clinical:
        pos = i.text.find(":")
        if pos == -1:
            pos = i.text.find("：")
        key = i.text[pos - 2:pos]
        value = i.text[pos + 1:]
        # 不知道需不需要去掉换行符……
        # value = re.sub('[\r\n\t]', '', value)
        clinical_str[key] = value
        # # clinical_str[i.text[i.text.find("：")-2:i.text.find("：")]] = i.text[i.text.find(":") + 1:]
        # temp = i.text[i.text.find(":") + 1:]
        # # 不知道需不需要去掉换行符……
        # # temp = re.sub('[\r\n\t]', '', temp)
        # clinical_str.append(temp)
    logger.info("完成临床意义、注意事项、检查过程、不适宜人群、不良反应与风险的获取")
    return clinical_str


def get_normal(bs):
    """
    获取检查正常值
    :param bs:
    :return:
    """
    normal = bs.find("div", class_="ys-normal").text
    normal = normal[normal.find(":") + 1:]
    logger.info("完成正常值的获取")
    return normal


def get_attr(bs):
    """
    获取一个检查的属性：属性: {专科分类: "",检查分类: "",...}
    :param bs:
    :return:返回属性内容的dict格式
    """
    brief = bs.find("div", class_="ys-brief").find_all("span")
    jieguo = bs.find("div", class_="ys-brief").find_all("img")
    jieguo_str = ""
    for i in range(len(jieguo)):
        string = jieguo[i].get('data-data')
        jieguo_str = jieguo_str + string.replace('<br>', '').replace('	', '').replace('\n', '')
    attr = []
    for i in brief:
        i = re.sub('[\r\n\t<span></span>\u3000 ]', '', str(i))
        attr.append(i)
    data = {}
    for i in attr:
        pos = i.find('：')
        if pos != -1:
            name = i[:pos]
            value = i[pos + 1:]
            if name.find('分析结果') == -1:
                data[name] = value
            else:
                data['分析结果'] = jieguo_str
    logger.info("完成属性的获取")
    return data


def get_intro(bs):
    """
    获取一个检查的介绍：名称: "xx",简介: "xxx"
    :param bs:
    :return:返回名称和简介的内容(string)
    """
    name = bs.find("div", class_="ys-head").find("h1").text.replace('\t', '')
    brief_intro = bs.find("div", class_="ys-head").find("div", class_="intro").text
    logger.info("完成内容和名称的获取")
    return name, brief_intro


def get_jiancha(url):
    """
    对一个页面进行分析
    :param url:
    :return:
    """
    html = requests.get(url, timeout=30, headers=HEADERS)
    bs = BeautifulSoup(html.text, "lxml")
    # info = json.loads(json.dumps({}))
    info = {}
    info['类型'] = '检查'
    info['网址'] = url
    name, brief_intro = get_intro(bs)
    info['名称'] = name
    info['简介'] = brief_intro
    try:
        attribute = get_attr(bs)
        info['属性'] = attribute
    except:
        logger.info("无属性")
    try:
        normal = get_normal(bs)
        info['正常值'] = normal
    except:
        logger.info("无正常值")
    try:
        clinical = get_clinical(bs)
    except:
        logger.info("无临床信息")
    try:
        info['临床意义'] = clinical['意义']
    except:
        logger.info("无临床意义")
    try:
        info['注意事项'] = clinical['事项']
    except:
        logger.info("无注意事项")
    try:
        info['检查过程'] = clinical['过程']
    except:
        logger.info("无检查过程")
    try:
        info['不适宜人群'] = clinical['人群']
    except:
        logger.info("无不适宜人群")
    try:
        info['不良反应与风险'] = clinical['风险']
    except:
        logger.info("无不良反应与风险")
    try:
        related = get_related_disease(bs)
        info['相关疾病'] = related
    except:
        logger.info("无相关疾病")
    return info


def spider():
    """
    爬虫入口
    :return:
    """
    data = []
    for url in urls:
        logger.info("第 {} 页".format(urls.index(url) + 1))
        try:
            data.append(get_jiancha(url))
        except:
            logger.info("第{}页404Not Found".format(urls.index(url) + 1))
    logger.info("已获得所有数据")
    return data


if __name__ == '__main__':
    logger = get_logger()
    start = time.time()
    data = spider()
    end = time.time()
    logger.info("总时间:{}s".format(end - start))
    write_json(data)
