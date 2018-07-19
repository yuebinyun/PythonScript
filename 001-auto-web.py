#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" 
移动业务数据自动批量读取
基于 selenium 实现
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
import csv
import time
from pathlib import Path
import os
import sys


chromedriver = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("user-data-dir=C:\\Users\\ban\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--silent")

url = "http://ccsct.chnl.zj.chinamobile.com/business?service=page/business&menuType=2"
browser = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
browser.get(url)

def parse(browser, users, interval, hxkeyword):

    try:
        alert = browser.switch_to.alert
        alert.accept()

        print("需要重新登录...")
        browser.switch_to_default_content()
        browser.switch_to_frame(0)
        time.sleep(10)

        # 输入用户名
        elem = browser.find_element_by_id("loginName")
        elem.clear()
        elem.send_keys("")
        print("输入用户名成功...")

        try:
            elem = browser.find_element_by_id("passwd_input_placeholder")
            elem.send_keys("")
        except:
            pass

        # 输入密码
        elem = browser.find_element_by_id("loginPassword")
        elem.clear()
        elem.send_keys("")
        print("输入密码成功...")

        elem = browser.find_element_by_id("login_btn")
        elem.click()

        print("点击登录成功")

        sys.stdout.write('\a')
        smkey = input("请输入短信验证码: ")

        elem = browser.find_element_by_id("smKey")
        elem.clear()
        elem.send_keys(smkey)

        elem = browser.find_element_by_id("login_btn")
        elem.click()
        print("登录成功")

        browser.switch_to_default_content()

    except Exception as e:
        print("无需重新登录...")

    history = ''

    file_name = "output.csv"
    file = Path(file_name)
    if file.is_file():
        print("输出内容添加到 output.csv 文件中...")
        with open(file_name, 'r') as myfile:
            history = myfile.read()
    else:
        print("输出内容保存到 output.csv 文件中...")
        u = []
        u.append('手机号码')
        u.append('姓氏')
        u.append('实名')
        u.append('县市')

        u.append('流量套餐')
        u.append('客户画像')
        u.append('推荐业务')
        u.append('国内数据流量')

        with open(file_name, "a", newline='') as fp:
            wr = csv.writer(fp, dialect='excel')
            wr.writerow(u)

    # for num in []:
    for num in users:

        num = num.strip()

        if num == '':
            continue

        if num in history:
            continue

        xingshi = ''
        shiming = ''
        liuliang = ''
        xianshi = ''
        huaxiang = ''
        yewu = ''
        shuju = ''

        print("\n*** 分析用户：", num, " ***")

        browser.switch_to_default_content()

        # 如果有流量信息弹出窗口，先关闭弹出窗口
        try:
            elem = browser.find_element_by_class_name("aui_close")
            elem.click()
            time.sleep(5)
        except:
            pass

        # 如果有注销按钮且可用，先点击注销
        try:
            elem = browser.find_element_by_id("logoutBtn")
            elem.click()
            time.sleep(5)
            browser.execute_script("window.stop();")
        except:
            pass

        # 输入用户手机号码
        elem = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.ID, "custBillId"))
        )
        elem.clear()
        elem.send_keys(num)
        elem.send_keys(Keys.RETURN)

        try:
            elem = WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ui-tiptext-error"))
            )
            print('未找到该用户身份信息：', num)
            u = []
            u.append(num)
            u.append("空号")
            u.append("空号")
            u.append("空号")

            u.append("空号")
            u.append("空号")
            u.append("空号")
            u.append("空号")

            saveCsv(u)
            continue
        except Exception as e:
            pass

        try:
            elem = WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "aui_outer"))
            )
            print('该用户欠费停机了：', num)
            u = []
            u.append(num)
            u.append("停机")
            u.append("停机")
            u.append("停机")

            u.append("停机")
            u.append("停机")
            u.append("停机")
            u.append("停机")
            saveCsv(u)
            continue
        except Exception as e:
            pass

        # 姓氏
        elem = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "userInfo_head"))
        )
        elem = elem.find_elements_by_tag_name("li")
        xingshi = elem[0].text[3:4]
        print("姓氏:", xingshi)

        # 实名
        elem = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "userInfo_body"))
        )
        elem = elem.find_elements_by_tag_name("li")
        shiming = elem[3].text[3:]
        print("实名:", shiming)

        loop = 0
        while loop < 10:
            try:
                elem = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "userInfo_foot"))
                )
                elem = elem.find_elements_by_tag_name("li")
                liuliang = elem[2].text[3:] + "[" + elem[3].text[:-2] + "]"
                xianshi =  elem[7].text[3:]
                if len(elem[2].text[3:]) > 5 and len(xianshi) > 1:
                    print("流量:", liuliang)
                    print("县市:", xianshi)
                    break
                else:
                    loop += 1
                    time.sleep(3)
            except Exception as e:
                # print(e)
                loop += 1
                time.sleep(3)

        WebDriverWait(browser, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "iframe-902_1"))
        )
        # browser.switch_to_frame(elem)

        loop = 0
        while loop < 10:
            try:
                elem = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located((By.ID, "server-label-box"))
                )
                elem = elem.find_elements_by_tag_name("li")
                if len(elem) < 1:
                    # print("客户画像 size:", len(elem))
                    time.sleep(3)
                    continue

                print("客户画像：")
                huaxiang = ''

                for e in elem:
                    if hxkeyword == '':
                        print("       ", e.text)
                        huaxiang = huaxiang + "|" + e.text
                    elif hxkeyword in e.text:
                        print("       ", e.text)
                        huaxiang = huaxiang + "|" + e.text

                print("推荐业务：")
                elem = browser.find_element_by_id("business-box")
                elem = elem.find_elements_by_tag_name("h4")

                yewu = ""
                if len(elem) < 1:
                    print("       ", '无')
                    yewu = '无'
                for e in elem:
                    print("       ", e.text)
                    yewu = yewu + " | " +  e.text

                break
            except Exception as e:
                # print(e)
                loop += 1
                time.sleep(3)

        browser.switch_to_default_content()

        # 查询字段 【国内数据流量】
        elem = browser.find_element_by_class_name("custOffersSpan")
        elem.click()

        WebDriverWait(browser, 30).until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "OpendataUsageInfo"))
        )

        loop = 0
        while loop < 10:
            try:
                elem = browser.find_element_by_id("JS_CustOffers1")
                tds = elem.find_elements_by_tag_name("td")
                if len(tds) < 10:
                    # print("td size", len(tds))
                    time.sleep(1)
                    loop += 1
                    continue

                for i in range(0, len(tds)):
                    if tds[i].text == '国内数据流量':
                        shuju = tds[i+1].text
                        print('国内数据流量: ', shuju)

                break

            except Exception as e:
                # print(e)
                loop += 1
                time.sleep(3)

        browser.switch_to_default_content()

        elem = browser.find_element_by_class_name("aui_close")
        elem.click()

        loop = 0
        while loop < 10:
            try:
                elem = WebDriverWait(browser, 30).until(
                    EC.visibility_of_element_located((By.ID, "logoutBtn"))
                )
                elem.click()
                time.sleep(5)
                browser.execute_script("window.stop();")
                break

            except Exception as e:
                # print(e)
                loop += 1
                time.sleep(3)


        # u.display()
        print("\n---------------------\n")

        u = []
        u.append(num)
        u.append(xingshi)
        u.append(shiming)
        u.append(xianshi)

        u.append(liuliang.replace("..", ""))
        u.append(huaxiang)
        u.append(yewu)
        u.append(shuju)

        saveCsv(u)

        time.sleep(int(interval))

    print("\n---------------------")
    print("所有用户查找结束")
    time.sleep(10)
    print("---------------------\n")
    exit()

def saveCsv(u):
    with open("output.csv", "a", newline='') as fp:
        wr = csv.writer(fp, dialect='excel')
        wr.writerow(u)


# 第一步，读取用户列表
users_file_name = "users.txt"
my_file = Path(users_file_name)
users = []

if my_file.is_file():
    with open(users_file_name) as f:
        users = f.readlines()
else:
    print('用户列表文件不存在:', users_file_name)
    print('程序退出....')
    exit()


# 第二步，读取过滤关键字
### 查询每个用户之间的时间间隔 单位 秒
interval = 40

### 过滤客户画像的关键字，如果关键字为空，则不过滤
hxkeyword = '三个月'



if len(users) >= 1:
    print('-------------------------------------')
    print('用户数量', len(users))
    print("时间间隔", interval)
    print("画像过滤关键字", hxkeyword)
    print('-------------------------------------')


while True:
    try:
        parse(browser, users, interval, hxkeyword)
        exit()
    except Exception as e:
        sys.stdout.write('\a')
        print('【Error】', e)
        print('请将页面恢复到初始界面。请确认该用户是否欠费停机。')
        time.sleep(100000)
        browser.get(url)
