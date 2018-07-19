#!/usr/bin/env python3
#coding: utf-8

""" 测试文件，每个测试都用函数的形式
"""

import sqlite3
import json
from pprint import pprint
import pickle
import requests
from subprocess import call
import os
from sys import platform

class Test:

    def __init__(self):
        self.dict = {}

    def read_db(self):
        con = sqlite3.connect('tdd-omega.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT Q,A from QA")
        re = cur.fetchall()
        for row in re:
            self.dict[row['Q'].strip()] = row['A'].strip()
        con.close()

        for key, value in self.dict.items():
            print(key, "\t", value)
        print("题库记录", len(self.dict))

    def save_db(self):
        con = sqlite3.connect('tdd-omega.db')
        sql = 'DELETE FROM QA'
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        for key, value in self.dict.items():
            sql = "INSERT INTO QA ('Q', 'A') VALUES ('%s', '%s')" % (key, value);
            print(sql)
            cur.execute(sql)

        #print("Records created successfully");
        con.commit()
        con.close()

    def load_json_file(self, file_name):
        data = json.load(open(file_name))
        pprint(data)
        for key, value in data.items():
            print(key, value)
        return data


    def save_json_file(self):
        data = {'yi':'aa', 'er':'san'}
        with open('data.p', 'w') as fp:
            json.dump(data, fp)
        fp.close()

    def add_record(self, q, a):
        self.dict[q] = a

    def modify_notify(self):
        # contents = urllib.request.urlopen("https://maker.ifttt.com/trigger/hq/with/key/bvuJsFjwnf5rZFo1Z2qErv").read()
        r = requests.post('https://maker.ifttt.com/trigger/hq/with/key/bvuJsFjwnf5rZFo1Z2qErv',  data = {'value1':'自动答题程序异常...'})
        print(r.text)
        # contents = urllib.request.urlopen('https://maker.ifttt.com/trigger/hq/with/key/bvuJsFjwnf5rZFo1Z2qErv', json.dumps({"value1":"自定义消息。"})).read()
        # print(contents)

    def mac_notify(self, msg):
        cmd = 'display notification \"{0}\" with title \"答题机器人\"'.format(msg)
        call(["osascript", "-e", cmd])

    def check_os(self):

        print(os.name)
        print(os.system("uname -a"))

        if platform == "linux" or platform == "linux2":
            print('linux')
        elif platform == "darwin":
            print('OS X')
        elif platform == "win32":
            print('Windows...')

    def delete_record(self):
        conn = sqlite3.connect('tdd-omega.db')
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
    t = Test()
    print(t.search_baidu('善于高考闻名的衡水中学位于哪个省', ['河南', '河北', '浙江']))
    print(t.search_baidu('词语“汽车”的“车”字，在象棋里，读什么',['che','ju','ce']))
    # t.delete_record()
    # t.read_db()
    # t.mac_notify('程序崩溃了')
    # t.dict = t.load_json_file('a.dict')
    # t.save_db()
    # t.read_db()
    # t.notify()
    # t.save_json_file()
    # t.add_record("q1", "a1")
    # t.save_db()
    # t.check_os()
