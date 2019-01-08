from bs4 import BeautifulSoup
import requests
import pandas as pd
import xlsxwriter
import time
import sys
import argparse

#初始化所需資料項目
zhenfu_login_url = 'https://web.pcc.gov.tw/pis/main/sso/login.jsp'
zhenfu_juebiao_url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=supplier&searchType=advance'
zhenfu_after_search_url = 'https://web.pcc.gov.tw/tps/'
zhenfu_next_page_url = 'https://web.pcc.gov.tw/tps/pss/'

href_string =[]
after_search_string = ''
next_page_href = ''

Date     = [] #決標日期
Name     = [] #工程名稱
Times    = [] #招標次數
Vendor   = [] #得標廠商
Budget   = [] #工程預算
Estimate = [] #工程底價
Award    = [] #決標金額


#使用argparse讓程式可以直接透過指令產出Excel 不需要進程式改資訊
parser = argparse.ArgumentParser(description='Parse the Zhenfuxiagou_zhaobiao need below argument.')
parser.add_argument('--Name', '-n', type=str, required=True, help='Which mechanism you want to search?')
parser.add_argument('--Startdate', '-s', type=str, required=True, help='Example : 107/12/01')
parser.add_argument('--Enddate', '-e', type=str, required=True, help='Example : 107/12/19')
parser.add_argument('--Filename', '-f', type=str, required=True, help='Example : even.xlsx')

args = parser.parse_args()
print(args.Name, args.Startdate, args.Enddate, args.Filename)

def max_length(name, date, times, vendor, budget, estimate, award):
	max_length = max(len(name), len(date), len(times), len(vendor), len(budget), len(estimate), len(award))
	return max_length

def get_info(soup_find_all_href):
	#拿到每個標案的超連結
	global href_string

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
				if p.find_next_sibling('td').string is None:
					Date.append('None')
					print(Date)
				else:
					Date.append(p.find_next_sibling('td').string.strip())
					print(Date)

			if p.string == '標案名稱':
				if p.find_next_sibling('td').string is None:
					Name.append('None')
					print(Name)
				else:				
					Name.append(p.find_next_sibling('td').string.strip())
					print(Name)
			
			if p.string == '新增公告傳輸次數':
				if p.find_next_sibling('td').string is None:
					Name.append('None')
					print(Name)
				else:		
					Times.append(p.find_next_sibling('td').string.strip())
					print(Times)		
			
			if p.string == '　　得標廠商':
				if p.find_next_sibling('td').string is None:
					Vendor.append('None')
					print(Vendor)
				else:
					Vendor.append(p.find_next_sibling('td').string.strip())
					print(Vendor)

			if p.string == '預算金額':
				if p.find_next_sibling('td').string is None:
					Budget.append('None')
					print(Budget)
				else:		
					Budget.append(p.find_next_sibling('td').string.strip()[:-1])
					print(Budget)

			if p.string == '底價金額':
				if p.find_next_sibling('td').string is None:
					Estimate.append('None')
					print(Estimate)
				else:		
					Estimate.append(p.find_next_sibling('td').string.strip()[:-1])
					print(Estimate)

			if p.string == '　決標金額':
				if p.find_next_sibling('td').string is None:
					Award.append('None')
					print(Award)
				else:		
					Award.append(p.find_next_sibling('td').string.strip()[:-1])
					print(Award)		

	    #有些資料取不到，需要增加判斷式避免Pandas DataFrame出錯
		while len(Name) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):	
			Name.append('null')
			print(Name)
		while len(Date) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Date.append('null')
			print(Date)
		while len(Times) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Times.append('null')
			print(Times)
		while len(Vendor) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Vendor.append('null')
			print(Vendor)
		while len(Budget) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Budget.append('null')
			print(Budget)
		while len(Estimate) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Estimate.append('null')
			print(Estimate)
		while len(Award) < max_length(Name, Date, Times, Vendor, Budget, Estimate, Award):
			Award.append('null')
			print(Award)
		#print(max(len(Date), len(Times), len(Vendor), len(Budget), len(Estimate), len(Award)))

		#因有polling次數的關係，15秒是抓資料的極限
		time.sleep(20) 



#建立一個連線的Session
session = requests.Session()
#帶入帳密Payload
login_payload =  {'id': 'ˇ123123', 
		    	  'password': '123123'}
#進入login頁面並且帶payload進去
r = session.post(zhenfu_login_url, data=login_payload)

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
print(r.url)
#開始解析所拿到的html (在這邊是查詢到的所有工程案件)
soup = BeautifulSoup(r.text, 'lxml')
#print(soup.prettify(),soup.url)

#先拿所有的超連結資料
soup_find_all_href = soup.find_all('a')
#爬第一頁所有超連結的標案
get_info(soup_find_all_href)

#如果有下一頁 開始進下一頁爬資料
while soup.find('a', string='下一頁') is not None:
	next_page_href = soup.find('a', string='下一頁')
	next_page_href = zhenfu_next_page_url + next_page_href.get('href').strip('../')
	print(next_page_href)
	r = session.get(next_page_href, verify=False)
	soup = BeautifulSoup(r.text, 'lxml')
	soup_find_all_href = soup.find_all('a')
	get_info(soup_find_all_href)

#將所有資料排序好 
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
zhenfu_df = zhenfu_df.drop_duplicates(subset=['Name'],keep='first')
writer = pd.ExcelWriter(args.Filename, engine='xlsxwriter')
zhenfu_df.to_excel(writer, 'Sheet1')
writer.save()	

