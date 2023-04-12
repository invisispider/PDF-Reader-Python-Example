import pandas as pd
import json
import requests

r = json.loads(requests.get("https://experts.expcloud.com/api4/std?searchterms=Arizona&size=99999&fbclid=IwAR0KuBxx4ctu4-geQN4_TXCIWWP78wP62d9D1qsIXVz2j5HCcjUUenG5LrY").text)
json2 = r['hits']
hits = json2['hits']

rows = []

names = ['First Name', 'Last Name', 'Phone Number', 'Email Address', 'Alternative Email', 'Date Joined']
keys = ['firstName', 'lastName', 'primaryPhone', 'primaryEmail', 'secondaryEmail', 'joindate']

for person in hits:
	s = person['_source']
	row = {}
	for key in s:
		if key in keys:
			row[key] = s[key].strip()
	rows.append(row)

table = pd.DataFrame(rows)
table.to_csv('output.csv')