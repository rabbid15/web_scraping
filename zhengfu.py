from bs4 import BeautifulSoup
import requests
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
zhenfu_login_url = 'https://web.pcc.gov.tw/pis/main/sso/login.jsp'
zhenfu_juebiao_url = 'https://web.pcc.gov.tw/tps/pss/tender.do?searchMode=supplier&searchType=advance'
zhenfu_after_search_url = 'https://web.pcc.gov.tw/tps/'
session = requests.Session()
login_payload =  {'id': 'test', 
		    	  'password': '123'}

r = session.post(zhenfu_login_url, data=login_payload)

print(r.cookies.get_dict())

#r = session.get('https://web.pcc.gov.tw/tps/pss/tender.do?method=goSearch&searchMode=supplier&searchType=advance&searchTarget=ATM')
#print(r.text)
payload = { 'method': 'search',
			'searchMethod': 'true',
			'searchTarget': 'ATM',
			'orgName': '后里區公所',
			'awardAnnounceStartDate': '107/10/30',
			'awardAnnounceEndDate': '107/12/26',
			'proctrgCate':'1', # 1為工程 2為財務 3為勞務
			'radProctrgCate':'1' # 1為工程 2為財務 3為勞務
			}
#r = session.post(zhenfu_juebiao_url, data=payload)
#print(r.text)
r = session.post(zhenfu_juebiao_url, data=payload)
#print(r.text)

soup = BeautifulSoup(r.text, 'html.parser')
soup_find_all_href = soup.find_all('a',limit=2)
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

r = session.get(after_search_string)
soup = BeautifulSoup(r.text, 'html.parser')
#soup_find = soup.find_all(['th', {'class':'T11b'}, 'td', {'class':'newstop'}])
soup_find = soup.find_all('td')
for p in soup_find:
	print(p.get_text())
#print(list(s[0]) #index從0開始


'''
r = session.get(href_string[0])
print(r.text)
'''
'''
	def get_link_list():
	list_req = requests.get(zhenfu_juebiao_url)
'''