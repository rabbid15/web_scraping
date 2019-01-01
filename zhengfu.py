from bs4 import BeautifulSoup
import requests
import ssl
import pandas as pd
import xlsxwriter
from urlmatch import urlmatch
import time
ssl._create_default_https_context = ssl._create_unverified_context
zhenfu_login_url = 'https://web.pcc.gov.tw/pis/main/sso/login.jsp'
zhenfu_juebiao_url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=supplier&searchType=advance'
zhenfu_after_search_url = 'https://web.pcc.gov.tw/tps/'
session = requests.Session()
login_payload =  {'id': '13007060', 
		    	  'password': 'ac55888'}

r = session.post(zhenfu_login_url, data=login_payload)

Date = []
Name = [] 
Times = []
Vendor = []
Budget = []
Estimate = []
Award = []

#r = session.get('https://web.pcc.gov.tw/tps/pss/tender.do?method=goSearch&searchMode=supplier&searchType=advance&searchTarget=ATM')
#print(r.text)
payload = { 'method': 'search',
			'searchMethod': 'true',
			'searchTarget': 'ATM',
			'orgName': '后里區公所',
			'awardAnnounceStartDate': '104/01/01',
			'awardAnnounceEndDate': '107/12/31',
			'proctrgCate':'1', # 1為工程 2為財務 3為勞務
			'radProctrgCate':'1' # 1為工程 2為財務 3為勞務
			}
#r = session.post(zhenfu_juebiao_url, data=payload)
#print(r.text)
r = session.post(zhenfu_juebiao_url, data=payload)
#print(r.text)

soup = BeautifulSoup(r.text, 'lxml')
soup_find_all_href = soup.find_all('a')
href_string =[]
after_search_string = ''
for l in soup_find_all_href:

	#r = session.get(l.get('href'))
	#print(r.text)
	href_string.append(l.get('href'))

href_string = set(href_string) #去除重複資料
href_string = list(href_string)#回復到Python List的模式


for href_after_strip in href_string:
	href_after_strip = href_after_strip.strip('../')#因抓到的資料為../main   是抓上一頁資料所以去除
	after_search_string = zhenfu_after_search_url+href_after_strip #加上前面的網址
	print(after_search_string)

	r = session.get(after_search_string, verify=False)

	print(r.status_code, r.url)
	match_pattern = 'http://web.pcc.gov.tw/tps/tpam/validate*'
	'''
	while urlmatch(match_pattern, r.url): #如果進入到驗證模式．開始處理
		soup = BeautifulSoup(r.text, 'lxml')
		#print(r.text)
		soup_find = soup.find_all('img', {'class':'choose'})
		id_find   = soup.find_all('input',{'name':'id'})
		poke_id=[]
		poke_url_id=[]
		validation_url=r.url
		for p in soup_find:
			poke_id.append(p['alt'])
		for p in id_find:
			poke_url_id.append(p['value'])
		#print(poke_id[0],poke_id[2])
		poke_payload =  {'choose': [poke_id[2], poke_id[3]],
						 'id' : poke_url_id[0]
				    	 }
		r = session.post(r.url, data=poke_payload)
		print(r.url, r.status_code, poke_payload)
		if r.status_code == 302:
			break
	'''
	soup = BeautifulSoup(r.text, 'lxml')
	soup_find = soup.find_all(['td', 'th'], {'class':['T11b', 'newstop'], 
							   'bgcolor':['#FFCCCC', '#EFF1F1', '#ffdd83', '#ddc09e', '#DAEBED', '#FFFF99']})


	

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

		#print(p.get_text())

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

	time.sleep(15)
zhenfu_search_dict = {"Date" : Date,
					  "Name" : Name,
					  "Times" : Times,
					  "Vendor" : Vendor,
					  "Budget" : Budget,
					  "Estimate" : Estimate,
					  "Award" : Award

}

zhenfu_df = pd.DataFrame(zhenfu_search_dict, columns=['Date','Name','Times','Vendor','Budget','Estimate','Award'])
writer = pd.ExcelWriter('Houli104-107.xlsx', engine='xlsxwriter')
zhenfu_df.to_excel(writer, 'Sheet1')
writer.save()


'''
r = session.get(href_string[0])
print(r.text)
'''
'''
	def get_link_list():
	list_req = requests.get(zhenfu_juebiao_url)
'''