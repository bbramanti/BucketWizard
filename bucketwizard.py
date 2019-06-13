import requests
from teams import teams
from bs4 import BeautifulSoup
from PyInquirer import prompt
from pprint import pprint

def get_abbrev(team):
	for key,value in teams.items():
		if value == team:
			return key

def collect_data(team, year):
	selected_team = get_abbrev(team)
	selected_year = year[5:]
	url = "https://www.basketball-reference.com/teams/"+selected_team+"/"+selected_year+".html"
	page = requests.get(url)
	page_found = False 

	if (page.status_code == 200):
		print("page data secured ...")
		page_found = True 
		soup = BeautifulSoup(page.content, 'html.parser')

	elif (page.status_code == 404):
		print("page not found, spelling of team may be incorrect")

	if (page_found):
		## use soup to access html content
		print ("continue with soup object here")

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
    	}

	]
	answers = prompt(questions)
	pprint(answers)
	collect_data(answers['team_name'], answers['team_year'])


if __name__ == "__main__":
	main()