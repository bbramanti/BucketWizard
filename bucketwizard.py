import requests
import re
from teams import teams, seasons, choices
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

def clean_per_game(headers, stats):
    # replace the first "Rk" or Rank header with "Name
    headers[0] = "Name"
    # remove first row of stats, it restates the headers
    stats = stats[1:]
    # remove first stat for each player (has no value)
    stats = [player[1:] for player in stats]
    return headers, stats

def get_per_game(html):
    table = html.find(id="per_game")
    per_game_stats = []
    if (table):
        # get table headers
        header = table.find('thead')
        header_row = header.find('tr')
        headers = []
        for th in header_row.find_all('th'):
            # check for &nbsp using strip()
            if (th.text.strip()):
                headers.append(th.text)
        # get table data
        rows = table.find_all('tr')
        for tr in rows:
            td = tr.find_all(['td', 'th'])
            data = [x.text for x in td]
            per_game_stats.append(data)
        # clean up data in both headers, and per_game_stats
        cleaned_headers, cleaned_per_game_stats = clean_per_game(headers, per_game_stats)
        # final print to user
        print()
        print(tabulate(cleaned_per_game_stats, headers=cleaned_headers, tablefmt="github"))
        print()
    else:
        print ("cannot retrieve table")


def collect_data(team, year, selection):
    # build out full URL
    selected_team = teams[team]
    selected_year = year[5:]
    url = "https://www.basketball-reference.com/teams/"
    url += selected_team+"/"+selected_year+".html"

    # print to terminal , and send out request
    print("Scraping From: " + url)
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
            if (selection == 'Per Game'):
                get_per_game(soup)

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
                    'choices': ['Team Roster', 'Player Salaries', 'Per Game']
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
        'message': 'Select Team: ',
        'choices': sorted(teams.keys())
        },
        {
        'type': 'list',
        'name': 'team_year',
        'message': 'Select Year: ',
        'choices': seasons
        },
        {
        'type': 'list',
        'name': 'data_selection',
        'message': 'What data would you like to view?',
        'choices': choices
        }]
    answers = prompt(questions)
    collect_data(
        answers['team_name'], answers['team_year'], answers['data_selection'])


if __name__ == "__main__":
    main()
