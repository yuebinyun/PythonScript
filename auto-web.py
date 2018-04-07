#!/usr/bin/python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os

chromedriver = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=C:\\Users\\ban\\AppData\\Local\\Google\\Chrome\\User Data")
browser = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

url = "http://ccsct.chnl.zj.chinamobile.com/business?service=page/business&menuType=2"
browser.get(url)

for num in ['13706857722', '13626754868', '13575570202']:

    print("---------------------")
    print("获取用户信息:" + num)
    while True:
        try:
            elem = browser.find_element_by_id("custBillId")
            elem.send_keys(num)
            elem.send_keys(Keys.RETURN)
            break
        except:
            time.sleep(1)

    # time.sleep(10)

    # start = browser.page_source.find('<span class="fn-left">')
    # end = browser.page_source.find('</span> <span class="fn-right">')
    # end2 = browser.page_source.find('</span>', end + len('</span> <span class="fn-right">'))
    #
    # name = browser.page_source[ start + len('<span class="fn-left">') : end ]
    # city = browser.page_source[ end + len('</span> <span class="fn-right">') : end2 ]

    while True:
        try:
            keyword = '<i class="nameIcon"></i>姓名：'
            start = browser.page_source.find(keyword) + len(keyword)
            keyword = '</li>'
            end = browser.page_source.find(keyword, start)
            name = browser.page_source[ start : end - 5 ]
            if len(name) > 20:
                time.sleep(1)
                continue

            print("姓氏: " + name)

            keyword = '<span><i class="regionIcon"></i>地市：'
            start = browser.page_source.find(keyword) + len(keyword)
            keyword = '</span>'
            end = browser.page_source.find(keyword, start)
            city = browser.page_source[ start : end ]
            print("县市: " + city)

            base = browser.page_source.find('<span id="dataUsageInfo"><!-- 加载流量信息 -->')
            start = browser.page_source.find('<span>', base + 5) + len('<span>')
            end = browser.page_source.find('</span>', base + 5)
            print("流量套餐: " + browser.page_source[ start : end ])
            break
        except:
            time.sleep(1)


    # file = open(num +  "test2.html","w", encoding='utf-8')
    # file.write(browser.page_source)
    # file.close()

    while True:
        try:
            browser.switch_to_frame("iframe-902_1")
            break
        except:
            time.sleep(1)

    while True:
        start = browser.page_source.find('<ol><li>') + len('<ol><li>')
        end = browser.page_source.find('</li></ol>')
        msg = browser.page_source[ start : end ].replace('<li style="color:rgb(144,0,0)">', '<li>')
        if '近三个月' in msg:
            print(msg.split('</li><li>'))
            break
        else:
            time.sleep(1)

    time.sleep(5)

    browser.switch_to_default_content()
    elem = browser.find_element_by_id("logoutBtn")
    elem.click()

print("---------------------")
print("查找结束")

time.sleep(1000)

# browser.quit()
