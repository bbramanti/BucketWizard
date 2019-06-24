import requests
import re
from teams import teams
from bs4 import BeautifulSoup
from PyInquirer import prompt
from tabulate import tabulate


def get_abbrev(team):
    for key, value in teams.items():
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
        # remove empty header row
        salaries = salaries[1:]
        # final print to user
        print()
        print(tabulate(
            salaries, headers=["Player", "Salary"], tablefmt="github"))
        print()
    else:
        print ("cannot retrieve table")


def collect_data(team, year, selection):
    selected_team = get_abbrev(team)
    # if 2015-2016, grab 2016
    selected_year = year[5:]
    url = "https://www.basketball-reference.com/teams/"
    url += selected_team+"/"+selected_year+".html"
    page = requests.get(url)

    if (page.status_code == 200):
        # decode so we can use regex to remove commenting
        html = page.content.decode('utf-8')
        soup = BeautifulSoup(re.sub("<!--|-->", "", html), 'html.parser')
        running = True
        while (running):
            # view salary data
            if (selection == 'Player Salaries'):
                get_salary(soup)

            # confirm if user wants to view more of this team's stats
            questions = [{
                'type': 'confirm',
                'message': 'Continue viewing ' + team + ' stats?',
                'name': 'continue',
                'default': True,
            }]
            answers = prompt(questions)
            if (answers['continue'] is False):
                # exit
                running = False
                # else: user makes stat selection again

        print ("bucketwizard shutting down ...")
        # option here to allow user to cycle back to main()

    elif (page.status_code == 404):
        print("page not found, spelling of team may be incorrect")


def main():
    questions = [{
        'type': 'list',
        'name': 'team_name',
        'message': 'What team\'s data would you like to view?',
        'choices': teams.values()
        },
        {
        'type': 'list',
        'name': 'team_year',
        'message': 'Which year?',
        'choices': ['2013-2014', '2014-2015', '2015-2016', '2016-2017',
                    '2017-2018', '2018-2019']
        },
        {
        'type': 'list',
        'name': 'stat_selection',
        'message': 'Which data would you like to view?',
        'choices': ['Player Salaries', 'PPG', 'Rebounds']
        }]
    answers = prompt(questions)
    collect_data(
        answers['team_name'], answers['team_year'], answers['stat_selection'])


if __name__ == "__main__":
    main()
