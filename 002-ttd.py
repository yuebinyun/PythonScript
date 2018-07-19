#!/usr/bin/env python3
#coding: utf-8

""" TiDuoDuo 小程序自动答题助手。
基于 Appium 实现
1. 自动读取题目
2. 自动点击答案选项
3. 匹配已有题库
4. 在线搜索答案，
5. 保存问题和答案到数据库 tdd-omega.db
"""

import os
from time import sleep
import requests
import sqlite3

import unittest

from appium import webdriver
from subprocess import call

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

class SimpleAndroidTests(unittest.TestCase):

    # 读取已有题库
    dict = {}

    # 首次命中
    cache = False

    # 首次命中非 A 问题
    cache_not_a = False

    def setUp(self):

        self.read_db()

        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        # desired_caps['platformVersion'] = '7.0'
        # desired_caps['deviceName'] = '19bdbe8a'
        desired_caps['platformVersion'] = '6.0.1'
        desired_caps['deviceName'] = 'aed376a9'
        desired_caps['noReset'] = 'true'
        desired_caps['appPackage'] = 'com.tencent.mm'
        desired_caps['appActivity'] =  '.ui.LauncherUI'
        desired_caps['dontStopAppOnReset'] = 'true'
        desired_caps['fullReset'] = 'false'
        desired_caps['fastReset'] = 'false'
        desired_caps['recreateChromeDriverSessions'] = ['true']
        desired_caps['chromeOptions']={'androidProcess': 'com.tencent.mm:appbrand0'}

        self.driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_caps)

    def tearDown(self):
        # end the session
        self.driver.quit()

    def play(self):

        all_handles = self.driver.window_handles
        # print(all_handles)

        # self.driver.switch_to_window(all_handles[len(all_handles)-1])
        #
        # print(self.driver.current_window_handle)

        for handle in all_handles:
            try:
                self.driver.switch_to_window(handle)
                self.driver.find_element_by_css_selector("wx-view[class='question-btm-tit a-fade-show _3f99eee']")
                break
            except Exception as e:
                continue
                # print(e)

        # question_num = self.driver.find_element_by_xpath("//wx-view[@class='question-btm-tit a-fade-show _3f99eee']").text
        # question = self.driver.find_element_by_xpath("//wx-view[@class='question-ques a-fade-show _3f99eee']").text
        # answ_list = self.driver.find_elements_by_xpath("//wx-view[@class='question-answer-tit _3f99eee']")

        question_num = self.driver.find_element_by_css_selector("wx-view[class='question-btm-tit a-fade-show _3f99eee']").text
        question = self.driver.find_element_by_css_selector("wx-view[class='question-ques a-fade-show _3f99eee']").text.strip()
        answ_list = self.driver.find_elements_by_css_selector("wx-view[class='question-answer-tit _3f99eee']")

        msg = '[{0}:{1}][A {2}][B {3}][C {4}]'.format(question_num, question, answ_list[0].text.strip(), answ_list[1].text.strip(), answ_list[2].text.strip())

        # 匹配内存中回答过的问题
        if question in type(self).dict:
            for answ in answ_list:
                if answ.text.strip() == type(self).dict[question]:

                    # if type(self).cache_not_a == False and answ.text.strip() != answ_list[0].text.strip():
                    #     type(self).cache_not_a == True
                    #     self.mac_notify("命中 " + answ.text.strip())

                    # print("命中题库...")
                    if type(self).cache == False:
                        type(self).cache = True
                        self.mac_notify("首次命中...")

                    msg = '[☕️☕️☕️]'+ msg + '[题库命中：{0}]'.format(answ.text.strip())
                    answ.click()
                    break
        else :
            # 不会就选 A
            aid = self.search_baidu(question, [answ_list[0].text.strip(), answ_list[1].text.strip(), answ_list[2].text.strip()])
            type(self).dict[question] = answ_list[aid].text.strip()
            msg += '[用户选择：{0}]'.format(answ_list[aid].text.strip())
            answ_list[aid].click()

        ## 等待若干秒，带返回答题结果

        sleep(4)

        ## 获取当前题目序号
        question_num_new = self.driver.find_element_by_xpath("//wx-view[@class='question-btm-tit a-fade-show _3f99eee']").text
        if question_num_new == question_num:

            # 这里分为两种情况
            try:
                # 情况一：答题错误，则重新答题。
                msg = "[❎❎❎]" + msg
                # 1. 根据当前页面，答案选项的颜色，找到正确的答案 <wx-view class="question-answer-tit right-syl right-syl _3f99eee" data-index="C">达芬奇</wx-view>
                # soup 解析关键字 right-syl
                # 找到答案后，将问题和正确答案保存到文件中
                source = self.driver.page_source
                source = source[source.index('<wx-view class="question-answer-tit right-syl') + len('<wx-view class="question-answer-tit right-syl right-syl _3f99eee" data-index="C">'):]
                source = source[:source.index('</')]
                type(self).dict[question] = source.strip()
                msg += '[正确答案:{0}]'.format(source.strip())

                # 2. 点击 重新开始 按钮，重新开始答题
                self.driver.find_element_by_xpath("//wx-button[@class='popup-continue-btn _79def66']").click()
                sleep(3)

            except Exception as e:
                # 情况二：答题记录创新高 继续答题
                msg += "[👍👍👍，并且创造新高!]"

                try:
                    self.driver.find_element_by_xpath("//wx-button[@class='popup-continue-btn _79def66']").click()
                    sleep(3)
                except Exception as ex:
                    sleep(10)
                    print("找不到控件, 😭")
                    self.driver.find_element_by_xpath("//wx-button[@class='popup-continue-btn _79def66']").click()
                    sleep(3)
                    return

        else :
            # 1. 保存上一题的问题和答案到配置文件中， q.json
            # 2. 回答当前新的问题
            msg = "[✅✅✅]" + msg

        self.add_record(question, type(self).dict[question])
        msg = '[题库累计数据：{0} 条] '.format(str(len(type(self).dict))) + msg

        print(msg)

    def test_find_elements(self):


        # self.driver.find_element_by_android_uiautomator('new UiSelector().text("发现")').click()
        # self.driver.find_element_by_android_uiautomator('new UiSelector().text("小程序")').click()
        self.driver.swipe(100,300,100,900)
        sleep(3)

        try:
            self.driver.find_element_by_android_uiautomator('new UiSelector().text("题多多黄金版")').click()
        except Exception as e:
            print('找不到控件 题多多黄金版')
            return

        sleep(3)
        print(self.driver.contexts)
        self.driver.switch_to.context('WEBVIEW_com.tencent.mm:appbrand0')

        sleep(3)
        all_handles = self.driver.window_handles
        # print(all_handles)

        for handle in all_handles:
            try:
#                print(self.driver.page_source)
                self.driver.switch_to_window(handle)
                self.driver.find_element_by_css_selector("wx-button[class='menu-item menu-item-long start _cc26306']")
                # print('定位成功')
                break
            except Exception as e:
                # print(e)
                pass


        # print(self.driver.window_handles)
        self.driver.find_element_by_css_selector("wx-button[class='menu-item menu-item-long start _cc26306']").click()

        # 开始答题了
        sleep(3)

        while True:
            try:
                self.play()
            except Exception as e:
                print(e)
                break

        # 发送崩溃消息到手机
        self.mac_notify("自动答题程序异常...")

        # sleep(5)

    def read_db(self):
        con = sqlite3.connect('tdd-omega.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT Q,A from QA")
        re = cur.fetchall()
        for row in re:
            # print(row['Q'], row['A'])
            type(self).dict[row['Q'].strip()] = row['A'].strip()
        con.close()
        print("题库已有数据：", len(type(self).dict))

    def add_record(self, q, a):
        con = sqlite3.connect('tdd-omega.db')
        cur = con.cursor()
        sql = "INSERT INTO QA ('Q', 'A') VALUES ('%s', '%s')" % (q, a);
        cur.execute(sql)
        con.commit()
        con.close()

    def notify(self, msg):
        requests.post('https://maker.ifttt.com/trigger/hq/with/key/bvuJsFjwnf5rZFo1Z2qErv',  data = {'value1': msg})
        # print(r.text)

    def mac_notify(self, msg):
        cmd = 'display notification \"{0}\" with title \"答题机器人\"'.format(msg)
        call(["osascript", "-e", cmd])

    def delete_record(self):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("DELETE from QA where Q='';")
        conn.commit()
        print("Total number of rows deleted :", conn.total_changes)
        conn.close()

    def search_baidu(self, keyword, ops):
        try:
            r = requests.get('http://www.baidu.com/s?wd={0}&cl=3 '.format(keyword)).text
            c0 = r.count(ops[0])
            c1 = r.count(ops[1])
            c2 = r.count(ops[2])
            if c0 >= c1:
                if c0 >= c2:
                    return 0
                else:
                    return 2
            else:
                if c1 >= c2:
                    return 1
                else:
                    return 2
        except Exception as e:
            print(e)
            return 0

if __name__ == '__main__':

    while True:
        suite = unittest.TestLoader().loadTestsFromTestCase(SimpleAndroidTests)
        unittest.TextTestRunner(verbosity=2).run(suite)
        print("程序退出了...")


        os.system('adb shell am force-stop com.tecent.mm')

        sleep(10)
        os.system('adb shell am start -n com.tencent.mm/.ui.LauncherUI')

        sleep(5)
