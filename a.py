#!/usr/bin/env python3
#coding: utf-8
#PYTHONIOENCODING=utf-8

import datetime
import http.client
from bs4 import BeautifulSoup
import time
import json
import os

os.system('clear')

print("")
manga = {'海贼王':'1', '银魂':'2', '一拳超人':'53'}
for manga_name, manga_id in manga.items():

    url = "api.ishuhui.com"
    conn = http.client.HTTPConnection(url)
    conn.request("GET", "/cartoon/book_ish/ver/35744693/id/"+ manga_id + ".json")
    r1 = conn.getresponse()
    soup = BeautifulSoup(r1.read(), 'html.parser')
    conn.close()
    jsonStr = soup.getText()
    inner = json.loads(jsonStr)['data']['cartoon']['0']['posts']
    number = str(len(inner))
    laster_post = inner['n-' + str(len(inner))][0]
    post_id = laster_post['id']
    title = laster_post['title']


    url = "hhzapi.ishuhui.com"
    conn = http.client.HTTPConnection(url)
    conn.request("GET", "/cartoon/post/ver/76906890/id/"+ str(post_id) + ".json")
    r1 = conn.getresponse()
    soup = BeautifulSoup(r1.read(), 'html.parser')
    conn.close()

    jsonStr = soup.getText()
    update_time = json.loads(jsonStr)['data']['time']
    d = datetime.datetime.strptime( update_time, "%Y-%m-%d %H:%M:%S" )
    update_time_stamp = int(d.timestamp())
    offsect = int(time.time() - d.timestamp())

    if offsect < 24 * 60 * 60:
        print(manga_name + " 更新了 " + number + " " + title)
        print("http://hanhuazu.cc/cartoon/post?id=" + str(post_id))

print()

founds = ["160211", "001542", "519690", "167301", "001576", "519212", "519191", "161725", "161032", "160716", "001951"]

class Found:

    def __init__(self):
        self.found_code = ""
        self.found_name = ""
        self.gz = ""
        self.gz_zf = ""
        self.gz_sj = ""
        self.jz = ""
        self.jz_zf = ""
        self.jz_rq = ""

    @classmethod
    def printHeader(cls):
        found_header = Found()
        line = "-".ljust(len(str(found_header)), '-')
        print(line)
        found_header.buildHeader()
        print(found_header)
        print(line)

    @classmethod
    def printFooter(cls):
        found_header = Found()
        line = "-".ljust(len(str(found_header)), '-')
        print(line)

    def len_str(self, str):
        length = len(str)
        utf8_length = len(str.encode('utf-8'))
        return int((utf8_length - length)/2 + length)

    def buildHeader(self):
        self.found_name = "基金名称"
        self.gz_zf = "估值涨幅"
        self.gz_sj = "估值时间"
        self.gz = "估值"
        self.jz_zf = "净值涨幅"
        self.jz_rq = "净值日期"
        self.jz = "净值"

    def __str__(self):
        return self.found_code + "| " \
             + self.found_name.ljust(28 - (self.len_str(self.found_name) - len(self.found_name))) + "| " \
             + self.gz_zf.ljust(12 - (self.len_str(self.gz_zf) - len(self.gz_zf))) + "| " \
             + self.gz_sj.ljust(12 - (self.len_str(self.gz_sj) - len(self.gz_sj))) + "| " \
             + self.gz.ljust(10 - (self.len_str(self.gz) - len(self.gz))) + "| " \
             + self.jz_zf.ljust(10 - (self.len_str(self.jz_zf) - len(self.jz_zf))) + "| " \
             + self.jz.ljust(8 - (self.len_str(self.jz) - len(self.jz))) + "| " \
             + self.jz_rq.ljust(8 - (self.len_str(self.jz_rq) - len(self.jz_rq))) + "|"



Found.printHeader()
for code in founds:

    found_instance = Found()

    url = "fund.eastmoney.com"
    conn = http.client.HTTPConnection(url)
    conn.request("GET", "/"+ code + ".html?spm=search")
    r1 = conn.getresponse()
    soup = BeautifulSoup(r1.read(), 'html.parser')
    conn.close()

    # soup.title.string --> 国泰智能装备股票(001576)基金净值_估值_行情走势—天天基金网
    found_name = soup.title.string[:-26]
    #基金名称

    found_instance.found_name = found_name

    # 估算值
    gz = soup.find(id="gz_gsz")
    found_instance.gz = gz.text

    # 估算时间
    gz_sj = soup.find(id="gz_gztime")
    found_instance.gz_sj = gz_sj.text[4:-1]

    # 估算涨幅
    gs_zf = soup.find(id="gz_gszzl")
    found_instance.gz_zf = gs_zf.text

    # 单位净值 (2018-02-02)1.07600.56%近3月：-8.50%近3年：--
    jz_rq = soup.find_all("dl", class_="dataItem02")[0].text
    found_instance.jz_rq = jz_rq[11:16]

    jz_temp = soup.findAll("dd", class_="dataNums")[1].findAll("span")
    jz = jz_temp[0].text
    found_instance.jz = jz

    jz_zf = jz_temp[1].text
    if float(jz_zf[:-1]) > 0.0:
        jz_zf = "+" + jz_zf
    found_instance.jz_zf = jz_zf

    url = "fundgz.1234567.com.cn"
    conn = http.client.HTTPConnection(url)
    conn.request("GET", "/js/"+ code + ".js?rt=" + str(int(time.time())))
    r1 = conn.getresponse()
    soup = BeautifulSoup(r1.read(), 'html.parser')
    conn.close()
    dic = soup.getText()[8:-2]
    msg = json.loads(dic)

    found_instance.found_name = msg['name']
    gz_zf = msg['gszzl']
    if float(gz_zf) > 0.0:
        found_instance.gz_zf = "+" + gz_zf + "%"
    else:
        found_instance.gz_zf = gz_zf + "%"

    found_instance.gz_sj = msg['gztime'][5:]
    found_instance.gz = msg['gsz']

    print(found_instance)

Found.printFooter()
