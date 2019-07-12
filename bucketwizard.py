import requests
import re
from teams import teams
from bs4 import BeautifulSoup
from PyInquirer import prompt
from tabulate import tabulate


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


def get_roster(html):
    table = html.find(id="roster")
    roster = []
    if (table):
        # get table headers
        header = table.find('thead')
        header_row = header.find('tr')
        headers = []
        for th in header_row.find_all('th'):
            # check for &nbsp using strip()
            if (th.text.strip()):
                headers.append(th.text)
            else:
                # instead of &nbsp
                headers.append("Birth Country")
        # get table data
        rows = table.find_all('tr')
        for tr in rows:
            td = tr.find_all(['td', 'th'])
            data = [x.text for x in td]
            roster.append(data)
        # remove empty header row
        roster = roster[1:]
        # final print to user
        print()
        print(tabulate(
            roster, headers=headers, tablefmt="github"))
        print()
    else:
        print ("cannot retrieve table")


def collect_data(team, year, selection):
    selected_team = teams[team]
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
            if (selection == 'Team Roster'):
                get_roster(soup)

            # confirm if user wants to view more of this team's stats
            questions = [{
                'type': 'confirm',
                'message': 'Continue viewing ' + team + ' data?',
                'name': 'continue',
                'default': True,
            }]
            answers = prompt(questions)
            if (answers['continue'] is False):
                # exit
                running = False
            else:
                # let user select new piece of data
                questions = [{
                    'type': 'list',
                    'message': 'What data would you like to view?',
                    'name': 'data_selection',
                    'choices': ['Team Roster', 'Player Salaries']
                }]
                answers = prompt(questions)
                selection = answers['data_selection']

        print ("bucketwizard shutting down ...")

    elif (page.status_code == 404):
        print("page not found, spelling of team may be incorrect")


def main():
    questions = [{
        'type': 'list',
        'name': 'team_name',
        'message': 'Select a Team: ',
        'choices': sorted(teams.keys())
        },
        {
        'type': 'list',
        'name': 'team_year',
        'message': 'Select a Year: ',
        'choices': ['2013-2014', '2014-2015', '2015-2016', '2016-2017',
                    '2017-2018', '2018-2019']
        },
        {
        'type': 'list',
        'name': 'data_selection',
        'message': 'What data would you like to view?',
        'choices': ['Team Roster', 'Player Salaries']
        }]
    answers = prompt(questions)
    collect_data(
        answers['team_name'], answers['team_year'], answers['data_selection'])


if __name__ == "__main__":
    main()
