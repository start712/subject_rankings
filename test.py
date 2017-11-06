# -*- coding:utf-8 -*-  

import pandas as pd
import re
import os

with open('urls.txt', 'r') as f:
	s = f.read()

for s0 in s.split('\n'):
	file, url0 = s0.split('|')

	if not os.path.exists(file + '.csv'):
		print u"不存在%s" %(file + '.csv')
		continue
		
	df = pd.read_csv(file + '.csv',encoding='utf_8_sig')

	df['url'] = df[u'排名'].apply(lambda s:url0 + '?page=' +str(1 + int(re.search(r'\d+', s).group())/10))

	print df#df.to_csv(file + '.csv',encoding='utf_8_sig')