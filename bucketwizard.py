import requests
import re
from teams import teams
from bs4 import BeautifulSoup
from PyInquirer import prompt

def get_abbrev(team):
	for key,value in teams.items():
		if value == team:
			return key

def get_salary(html):
	table = html.find(id="salaries2")
	salaries = []
	if (table):
		rows = table.find_all('tr')
		for tr in rows:
			td = tr.find_all('td')
			data = [x.text for x in td]
			salaries.append(data)
		salaries = salaries[1:]
		print (salaries) 
	else:
		print ("cannot retrieve table")

def collect_data(team, year, selection):
	selected_team = get_abbrev(team)
	selected_year = year[5:]
	url = "https://www.basketball-reference.com/teams/"+selected_team+"/"+selected_year+".html"
	page = requests.get(url)
	page_found = False 

	if (page.status_code == 200):
		print("page data secured ...")
		page_found = True 
		# decode so we can use regex to remove commenting
		html = page.content.decode('utf-8')
		soup = BeautifulSoup(re.sub("<!--|-->","", html), 'html.parser')

	elif (page.status_code == 404):
		print("page not found, spelling of team may be incorrect")

	if (page_found):
		# view salary data
		if (selection == 'Player Salaries'):
			get_salary(soup)


def main():
	questions = [
    	{
        'type': 'list',
        'name': 'team_name',
        'message': 'What team\'s data would you like to view?',
        'choices': teams.values()
    	},
    	{
        'type': 'list',
        'name': 'team_year',
        'message': 'Which year?',
        'choices': ['2013-2014','2014-2015','2015-2016','2016-2017','2017-2018','2018-2019']
    	},
    	{
        'type': 'list',
        'name': 'stat_selection',
        'message': 'Which data would you like to view?',
        'choices': ['Player Salaries', 'PPG', 'Rebounds']
    	}

	]
	answers = prompt(questions)
	collect_data(answers['team_name'], answers['team_year'], answers['stat_selection'])


if __name__ == "__main__":
	main()