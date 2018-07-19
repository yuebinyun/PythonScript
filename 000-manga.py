#!/usr/bin/env python3
#coding: utf-8
#PYTHONIOENCODING=utf-8

import datetime
import http.client
from bs4 import BeautifulSoup
import time
import json
import os

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