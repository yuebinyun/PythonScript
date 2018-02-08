#!/usr/bin/env python3
#coding: utf-8

import time
import os

os.system("adb shell am force-stop com.inke.trivia")

content = None
try:
	with open("accounts.txt") as fp:
		content = fp.readlines()
finally:
	fp.close()

print("the size of account is", len(content))
for line in content:
	print("get account", line.rstrip('\n'))
	print("save to file temp.txt")
	with open('temp.txt', 'w') as the_file:
			the_file.write(line)
	the_file.close()
	print("copy to mobile...")
	os.system("adb push account.txt /sdcard")

	time.sleep(10)
	print("start app...")
	os.system("adb shell am start -n com.inke.trivia/com.inke.trivia.splash.SplashActivity")

	time.sleep(30)
	print("stop app...")
	os.system("adb shell am force-stop com.inke.trivia")


	# print(line)
	# a = a + 1
