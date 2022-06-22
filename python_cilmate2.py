#!/usr/bin/env
# -*- coding: utf-8 -*-

"""
資料來源:
https://selenium-python-zh.readthedocs.io/en/latest/getting-started.html
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

import os
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# 引用私密金鑰
# path/to/serviceAccount.json 請用自己存放的路徑
cred = credentials.Certificate('serviceAccount.json')


# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)

# 初始化firestore
db = firestore.client()


print(os.name)
if(os.name=="posix"):   # mac 作業系統的處理方法
    chromedriver='/Users/powenko/Desktop/chromedriver'
    chromedriver = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(chromedriver)

else:                   # Windows OS
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome('chromedriver.exe', options=option)
driver.get("https://www.accuweather.com/")


wait = WebDriverWait(driver, 5)  # 等待10秒

citys = ["臺北市","新北市","桃園市","臺中市","臺南市","高雄市","基隆市","新竹市","嘉義市","宜蘭縣","新竹縣","苗栗縣","彰化縣","南投縣","雲林縣","嘉義縣","屏東縣","花蓮縣","臺東縣","澎湖縣"]
data = []
for city in citys:
    print(city)
    # 搜尋欄

    # <input name="query" class="search-input" type="text" placeholder="搜尋" autocomplete="off">
    elem = driver.find_element(by=By.NAME, value="query")
    elem.clear()
    elem.send_keys(city)

    # 搜尋按鈕

    # <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path transform="translate(3 3)" d="M7.186 13.554c-3.462 0-6.303-2.869-6.303-6.359C.883 3.681 3.724.837 7.186.837c3.437 0 6.278 2.844 6.278 6.358 0 3.49-2.865 6.359-6.278 6.359zm5.323-1.602a7.176 7.176 0 0 0 1.815-4.757c0-3.968-3.2-7.195-7.138-7.195C3.223 0 0 3.227 0 7.195c0 3.944 3.223 7.171 7.186 7.171a7.058 7.058 0 0 0 4.75-1.84L17.427 18l.573-.55-5.49-5.498z"></path></svg>
    try:
        elem = driver.find_element(by=By.CLASS_NAME, value="search-icon")
    except:
        elem = driver.find_element(by=By.CLASS_NAME, value="icon-search")
    elem.click()

    # 等待搜尋結果
    time.sleep(2)               # 等1sec

    try:
        # 選擇搜尋結果
        text = city + ", " + city + ", TW"
        elem = driver.find_element(by=By.LINK_TEXT, value=text)
        elem.click()
        print("需選擇")
        # 等待搜尋結果
        time.sleep(2)  # 等1sec
    except:
        print("不需選擇")

    try:
        # 關掉廣告
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(elem, 0, 0)
        action.click()
        action.perform()
        print("有廣告")
        # 等待搜尋結果
        time.sleep(3)  # 等1sec
    except:
        print("沒有廣告")

    # 每小時按鈕
    try:
        # <a class="subnav-item " href="/zh/tw/taichung-city/315040/hourly-weather-forecast/315040" data-qa="hourly" data-gaid="hourly">
        elem = driver.find_element(by=By.LINK_TEXT, value="每小時")
        elem.click()
        print("未選擇每小時")

        # 等待網頁載入
        time.sleep(2)  # 1sec
    except:
        elem = driver.find_element(by=By.CSS_SELECTOR, value=".subnav-item.active")
        # elem.click()
        print("已選擇每小時")


    ## BS4 爬蟲
    str1=driver.page_source
    soup=BeautifulSoup(str1, "html.parser")

    #<div class="hourly-wrapper content-module">
    # class="hourly-wrapper content-module"
    # list1 = soup.select('.hourly-wrapper')   # . 找class

    #<div id="hourlyCard0" data-qa="hourlyCard0" class="accordion-item hourly-card-nfl hour non-ad" data-shared="false" data-collapsed="false">...</div>
    # id="hourlyCard0"
    soup1 = soup.select('#hourlyCard0')    # # 找id

    dataTitle = ["城市","現在時間","天氣","溫度","體感溫度","降雨機率","紫外線指數","風","強風","濕度","空氣品質","露點","雲量","能見度","雲冪"]

    # 現在時間
    soup2 = soup1[0].select('.date')[0].string
    # 天氣
    soup3 = soup1[0].select('.phrase')[0].string
    # 溫度
    soup4 = soup1[0].select('.metric')[0].string
    # 體感溫度
    soup5 = soup1[0].select('.real-feel-shade__text')[0].string
    ## 整理資料
    soup5 = soup5.replace('\n\t\t\t\t\t','')
    soup5 = soup5.replace('\n\t\t\t\t','')
    # 降雨機率
    soup6 = soup1[0].select('.precip')[0].text
    soup6 = soup6.replace('\n\n\t\t\t','')
    soup6 = soup6.replace('\n\t\t\t','')
    try:
        # 紫外線指數
        soup7 = soup1[0].select('.panel')[2].select('.value')[0].string
        # 風
        soup8 = soup1[0].select('.panel')[2].select('.value')[1].string
        # 強風
        soup9 = soup1[0].select('.panel')[2].select('.value')[2].string
        # 濕度
        soup10 = soup1[0].select('.panel')[2].select('.value')[3].string
        # 空氣品質
        soup11 = soup1[0].select('.panel')[2].select('.value')[4].string
        print("有紫外線指數")
    except:
        # 紫外線指數
        soup7 = []
        # 風
        soup8 = soup1[0].select('.panel')[2].select('.value')[0].string
        # 強風
        soup9 = soup1[0].select('.panel')[2].select('.value')[1].string
        # 濕度
        soup10 = soup1[0].select('.panel')[2].select('.value')[2].string
        # 空氣品質
        soup11 = soup1[0].select('.panel')[2].select('.value')[3].string
        print("沒有紫外線指數")
    # 露點
    soup12 = soup1[0].select('.panel')[3].select('.value')[0].string
    # 雲量
    soup13 = soup1[0].select('.panel')[3].select('.value')[1].string
    # 能見度
    soup14 = soup1[0].select('.panel')[3].select('.value')[2].string
    # 雲冪
    soup15 = soup1[0].select('.panel')[3].select('.value')[3].string
    list = [city,soup2,soup3,soup4,soup5,soup6,soup7,soup8,soup9,soup10,soup11,soup12,soup13,soup14,soup15]
    data.append(list)

    time.sleep(1)  # 5sec
               
    doc ={
          'time':soup2,
          'cilmate':soup3,
          'temperature':soup4,
          'temperature_body':soup5,
          'rain':soup6
          }
          # 建立文件 必須給定 集合名稱 文件id
          # 即使 集合一開始不存在 都可以直接使用

          # 語法
          # doc_ref = db.collection("集合名稱").document("文件id")
    doc_ref = db.collection("exam2").document(city)
          # doc_ref提供一個set的方法，input必須是dictionary
    doc_ref.set(doc)
    

driver.close()              # 視窗關閉
