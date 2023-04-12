import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date

base = 'https://www.realtor.com/realestateagents/'
spreadsheet = pd.read_csv('AZZipcodes.csv').values
# zipcode_list = []
# omg = (value for value in spreadsheet.values)
# for value in omg:
# 	for v in value:
# 		zipcode_list.append(v)

zipcode_list = {[[v for v in value] for value in omg] for omg in spreadsheet}
print(zipcode_list)
exit()
agents = []

def getAgentInfo(agent_card):
	name = agent_card.find(class_="agent-name")
	name = lambda agent_card : agent_card.find(class_="agent_name")
	name = name.text if name else ''
	phone = agent_card.find(class_="agent-phone")
	phone = phone.text if phone else ''
	experience = agent_card.select_one("#agentExperience span")
	experience = experience.text if experience else ''
	experience = int(experience[0]+experience[1].strip()) if experience else 0
	joindate = date.today().year - experience
	agent_dict = {'name': name, 'phone': phone, 'joindate': joindate}
	return agent_dict

def getSoups(zipcode, i, base=base):
	pg = '/pg-'+str(i)
	page_url = base+zipcode+pg
	r = requests.get(page_url)
	soup = BeautifulSoup(r.text, features="html.parser")
	agent_cards = soup.find_all(class_="agent-list-card")
	return agent_cards

def controller(zipcode, i=1, agents=agents):
	print("Zipcode: "+zipcode)
	while True:
		agent_cards = getSoups(zipcode, i)
		if len(agent_cards)==1:
			return agents
		i += 1
		for agent_card in agent_cards:
			incoming_dict = getAgentInfo(agent_card)
			if incoming_dict not in agents:
				agents.append(incoming_dict)

for zipcode in zipcode_list:
	agents.append(controller(str(zipcode)))
	agents.pop()

df = pd.DataFrame(agents)
df.to_csv('output_2nd_quest.csv')