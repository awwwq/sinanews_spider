import requests
import json
import re
import pandas
from bs4 import BeautifulSoup
from datetime import datetime

def getCommentCounts(newsurl):
	newsid = re.search(r'doc-i(.+).shtml', newsurl).group(1)
	comments = requests.get('http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=gn&newsid=comos-'+newsid+'&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20')
	js = json.loads(comments.text.strip('var data='))
	if 'count' not in js['result'].keys():
		comments = requests.get('http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=sh&newsid=comos-'+newsid+'&group=&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=20')
	js = json.loads(comments.text.strip('var data='))
	if 'count' in js['result'].keys():
		return js['result']['count']['total']
	else:return -1

def getNewsDetail(newsurl):
	result = {}
	res = requests.get(newsurl)
	res.encoding = 'utf-8'
	soup = BeautifulSoup(res.text, 'html.parser')
	timesource = soup.select('.time-source')[0].contents[0].strip()
	result['title'] = soup.select('#artibodyTitle')[0].text
	result['dt'] = datetime.strptime(timesource, '%Y年%m月%d日%H:%M')
	result['source'] = soup.select('.time-source a')[0].text
	result['article'] = '\n'.join([p.text.strip() for p in soup.select('#artibody p')[0:-1]])
	result['editor'] = soup.select('.article-editor')[0].text.strip('责任编辑：')
	result['comments'] = getCommentCounts(newsurl)
	result['url'] = newsurl
	return result

def parseListLinks(url):
	res = requests.get(url)
	res.encoding = 'utf-8'
	morenews = res.text.strip('  newsloadercallback(')
	morenews = morenews.rstrip(');')
	mnews = json.loads(morenews)
	newsDetails = []
	for ent in mnews['result']['data']:
		newsDetails.append(getNewsDetail(ent['url']))
	return newsDetails


url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callback=newsloadercallback'
news_total = []
for page in range(1, 6):
	newsurl = url.format(page)
	newsary = parseListLinks(newsurl)
	news_total.extend(newsary)
	print(len(news_total))

df = pandas.DataFrame(news_total)
print(df)
df.to_excel('foo.xlsx',sheet_name='Sheet1')


