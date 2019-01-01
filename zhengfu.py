from bs4 import BeautifulSoup
import requests
import pandas as pd
import xlsxwriter
import time
import sys
import argparse

#使用argparse讓程式可以直接透過指令產出Excel 不需要進程式改資訊
parser = argparse.ArgumentParser(description='Parse the Zhenfuxiagou_zhaobiao need below argument.')
parser.add_argument('--Name', '-n', type=str, required=True, help='Which mechanism you want to search?')
parser.add_argument('--Startdate', '-s', type=str, required=True, help='Example : 107/12/01')
parser.add_argument('--Enddate', '-e', type=str, required=True, help='Example : 107/12/19')
parser.add_argument('--Filename', '-f', type=str, required=True, help='Example : even.xlsx')

args = parser.parse_args()
print(args.Name, args.Startdate, args.Enddate, args.Filename)


zhenfu_login_url = 'https://web.pcc.gov.tw/pis/main/sso/login.jsp'
zhenfu_juebiao_url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=supplier&searchType=advance'
zhenfu_after_search_url = 'https://web.pcc.gov.tw/tps/'

#建立一個連線的Session
session = requests.Session()
#帶入帳密Payload
login_payload =  {'id': 'test', 
		    	  'password': '123123'}
#進入login頁面並且帶payload進去
r = session.post(zhenfu_login_url, data=login_payload)
#初始化所需資料項目
Date     = [] #決標日期
Name     = [] #工程名稱
Times    = [] #招標次數
Vendor   = [] #得標廠商
Budget   = [] #工程預算
Estimate = [] #工程底價
Award    = [] #決標金額

#r = session.get('https://web.pcc.gov.tw/tps/pss/tender.do?method=goSearch&searchMode=supplier&searchType=advance&searchTarget=ATM')
#print(r.text)
payload = { 'method': 'search',
			'searchMethod': 'true',
			'searchTarget': 'ATM',
			'orgName': args.Name,
			'awardAnnounceStartDate': args.Startdate,
			'awardAnnounceEndDate': args.Enddate,
			'proctrgCate':'1', # 1為工程 2為財務 3為勞務
			'radProctrgCate':'1' # 1為工程 2為財務 3為勞務
			}
#進入頁面後，輸入要查詢的相關資料並帶入
r = session.post(zhenfu_juebiao_url, data=payload)

#開始解析所拿到的html (在這邊是查詢到的所有工程案件)
soup = BeautifulSoup(r.text, 'lxml')
soup_find_all_href = soup.find_all('a')
href_string =[]
after_search_string = ''

#拿到每個標案的超連結
for l in soup_find_all_href:
	href_string.append(l.get('href'))

href_string = set(href_string) #去除重複資料
href_string = list(href_string)#回復到Python List的模式


for href_after_strip in href_string:
	href_after_strip = href_after_strip.strip('../')#因抓到的資料為../main   是抓上一頁資料所以去除
	after_search_string = zhenfu_after_search_url+href_after_strip #加上前面的網址
	print(after_search_string)

	#拿到標案的超連結session
	r = session.get(after_search_string, verify=False)
	print(r.status_code, r.url)

	#標案的html解析
	soup = BeautifulSoup(r.text, 'lxml')
	#爬出所要的資料(Tag)
	soup_find = soup.find_all(['td', 'th'], {'class':['T11b', 'newstop'], 
							   'bgcolor':['#FFCCCC', '#EFF1F1', '#ffdd83', '#ddc09e', '#DAEBED', '#FFFF99']})
	#開始拿Tag裡面的資料
	for p in soup_find:

		if p.string == '決標日期':
			Date.append(p.find_next_sibling('td').string.strip())
			print(Date)

		if p.string == '標案名稱':
			Name.append(p.find_next_sibling('td').string.strip())
			print(Name)
		
		if p.string == '新增公告傳輸次數':
			Times.append(p.find_next_sibling('td').string.strip())
			print(Times)		
		
		if p.string == '　　得標廠商':
			Vendor.append(p.find_next_sibling('td').string.strip())
			print(Vendor)

		if p.string == '預算金額':
			Budget.append(p.find_next_sibling('td').string.strip()[:-1])
			print(Budget)

		if p.string == '底價金額':
			Estimate.append(p.find_next_sibling('td').string.strip()[:-1])
			print(Estimate)

		if p.string == '　決標金額':
			Award.append(p.find_next_sibling('td').string.strip()[:-1])
			print(Award)		

    #有些資料取不到，需要增加判斷式避免Pandas DataFrame出錯
	if len(Date) != len(Name):
		Date.append('null')
	if len(Times) != len(Name):
		Times.append('null')
	if len(Vendor) != len(Name):
		Vendor.append('null')
	if len(Budget) != len(Name):
		Budget.append('null')
	if len(Estimate) != len(Name):
		Estimate.append('null')
	if len(Award) != len(Name):
		Award.append('null')

	#因有polling次數的關係，15秒是抓資料的極限
	time.sleep(15) 

zhenfu_search_dict = {"Date"     : Date,
					  "Name"     : Name,
					  "Times"    : Times,
					  "Vendor"   : Vendor,
					  "Budget"   : Budget,
					  "Estimate" : Estimate,
					  "Award"    : Award

}
#寫入pandas dataframe，每項資料長度必須相同
zhenfu_df = pd.DataFrame(zhenfu_search_dict, columns=['Date','Name','Times','Vendor','Budget','Estimate','Award'])
writer = pd.ExcelWriter(args.Filename, engine='xlsxwriter')
zhenfu_df.to_excel(writer, 'Sheet1')
writer.save()

