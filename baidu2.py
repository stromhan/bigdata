﻿#coding: utf-8
import requests
import json
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

"""
	查询关键字：
"""
FileKey = 'preclass'
KeyWord = u"金融$房地产"

"""
	关注区域的左下角和右上角百度地图坐标(经纬度）
	118.118991,31.253479
	119.092682,32.552191
"""
BigRect = {
	'left': {
		'x': 118.495777,
		'y': 31.694008,
	},
	'right': {
		'x': 119.045612,
		'y': 32.45548
	}
}

"""
	定义细分窗口的数量，横向X * 纵向Y
"""
WindowSize = {
	'xNum': 30.0,
	'yNum': 30.0
}


def getBaiduApiAk():
	"""
	获取配置文件中百度apikey:
	 { "baiduak":"xx"}
	:return: str
	"""
	with open("./config.json", "r") as f:
		config = json.load(f)
		return config["baiduak"]

def getSmallRect(bigRect, windowSize, windowIndex):
	"""
	获取小矩形的左上角和右下角坐标字符串（百度坐标系） 
	:param bigRect: 关注区域坐标信息
	:param windowSize:  细分窗口数量信息
	:param windowIndex:  Z型扫描的小矩形索引号
	:return: lat,lng,lat,lng
	"""
	offset_x = (bigRect['right']['x'] - bigRect['left']['x'])/windowSize['xNum']
	offset_y = (bigRect['right']['y'] - bigRect['left']['y'])/windowSize['yNum']
	left_x = bigRect['left']['x'] + offset_x * (windowIndex % windowSize['xNum'])
	left_y = bigRect['left']['y'] + offset_y * (windowIndex // windowSize['yNum'])
	right_x = (left_x + offset_x)
	right_y = (left_y + offset_y)
	#print "offset_x,offset_y=",windowIndex % windowSize['xNum'],windowIndex // windowSize['yNum']
	return str(left_y) + ',' + str(left_x) + ',' + str(right_y) + ',' + str(right_x)


def requestBaiduApi(keyWords, smallRect, baiduAk, index, fileKey):
	today = time.strftime("%Y-%m-%d")
	pageNum = 0
	logfile = open("./log/" + fileKey + "-" + KeyWord + "-" + today + ".log", 'a+')
	file = open("./result/" + fileKey + "-" + KeyWord + "-" + today + ".txt", 'a+')
	# print('-------------')
	# print(index)
	while True:
		try:
			URL = "http://api.map.baidu.com/place/v2/search?query=" + keyWords + \
				"&bounds=" + smallRect + \
				"&output=json" +  \
				"&ak=" + baiduAk + \
				"&scope=2" + \
				"&page_size=20" + \
				"&page_num=" + str(pageNum)
			# print(pageNum)
			# print(URL)
			resp = requests.get(URL)
			res = json.loads(resp.text)
			# print(resp.text.strip())
			if len(res['results']) == 0:
				logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " stop " + str(index) + " " + smallRect + " " + str(pageNum) + ",pagesize=" + str(len(res['results'])) + '\n')
				break
			else:
				logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " stop " + str(index) + " " + smallRect + " " + str(pageNum) + ",pagesize=" + str(len(res['results'])) + '\n')
				for r in res['results']:
					print>>file,r
					# print(r)
					#file.writelines(str(r).strip() + '\n')
			if len(res['results']) >= 20:
				pageNum += 1
				time.sleep(1)
			else:
				break
		except Exception,e:
			print("except")
			logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " except " + str(e) + ";"  + str(index) + " " + smallRect + " " + str(pageNum) + '\n')
			break

def requestBaiduApiKeywords(keyWords, baiduAk):
	today = time.strftime("%Y-%m-%d")
	logfile = open("./log/" + today + ".log", 'a+')
	file = open("./result/" + today + ".txt", 'a+')
	try:
		URL = "http://api.map.baidu.com/place/v2/search?query=" + keyWords +"&region=南京&output=json&ak=" + baiduAk
		resp = requests.get(URL)
		res = json.loads(resp.text)
		if len(res['results']) == 0:
			logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " :keyWords= "+ keyWords +",pagesize=" + str(len(res['results'])) + '\n')
		else:
			logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " :keyWords= "+ keyWords +",pagesize=" + str(len(res['results'])) + '\n')
			for r in res['results']:
				print>>file,r
	except Exception,e:
		print("except")
		logfile.writelines(time.strftime("%Y%m%d%H%M%S") + " except " + str(e) + ";"  + " :keyWords= "+ keyWords + '\n')

def main():
	baiduAk = getBaiduApiAk()
	for index in range(int(WindowSize['xNum'] * WindowSize['yNum'])):
		smallRect = getSmallRect(BigRect, WindowSize, index)
		requestBaiduApi(keyWords=KeyWord, smallRect=smallRect, baiduAk=baiduAk, index=index, fileKey=FileKey)
		time.sleep(1)


if __name__ == '__main__':
	baiduAk = getBaiduApiAk()
	for line in open("./all_enterprise.txt","r"):
		requestBaiduApiKeywords(line.strip(), baiduAk)
