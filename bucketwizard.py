import requests
import re
from bs4 import BeautifulSoup
from PyInquirer import prompt
from tabulate import tabulate
from teams import teams, seasons, choices

def get_table_headers(table):
    # find tr element
    header_row = table.find("tr")
    # table may have blank columns (no header or values), skip these
    headers = [th.text for th in header_row.find_all("th") if th.text.strip()]
    return headers

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
        headers = get_table_headers(table)
        headers.insert(6, "Birth Country")
        # get table data
        rows = table.find_all("tr")
        for tr in rows:
            td = tr.find_all(["td", "th"])
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
        headers = get_table_headers(table)
        # get table data
        rows = table.find_all("tr")
        for tr in rows:
            td = tr.find_all(["td", "th"])
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

def clean_game_results(headers, game_results):
    headers = headers[1:]
    headers.insert(3, "W/L")
    # remove all header rows
    game_results = [game for game in game_results if game[0] != "G"]
    # remove data that is not needed
    cleaned_game_results = []
    for game in game_results:
        cleaned_game = [value for index,value in enumerate(game) if index not in [0,3,4,8,14]]
        cleaned_game[2] = "@ " if cleaned_game[2] == "@" else "vs. "
        cleaned_game[2] = cleaned_game[2] + cleaned_game.pop(3)
        cleaned_game_results.append(cleaned_game)
    return headers, cleaned_game_results

def get_game_results(html):
    table = html.find(id="games")
    if (table):
        # get table headers
        headers = get_table_headers(table)
        # get table data
        rows = table.find_all("tr")
        game_results = []
        for tr in rows:
            td = tr.find_all(["td", "th"])
            data = [x.text for x in td]
            game_results.append(data)
        cleaned_headers, cleaned_game_results = clean_game_results(headers, game_results)
        # final print to user
        print()
        print(tabulate(cleaned_game_results, headers=cleaned_headers, tablefmt="github"))
        print()
    else:
        print ("cannot retrieve table")


def collect_data(team, year, selection):
    # build out full URL
    selected_team = teams[team]
    selected_year = year[5:]
    base_url = "https://www.basketball-reference.com/teams/{}/{}.html".format(selected_team, selected_year)
    games_url = "https://www.basketball-reference.com/teams/{}/{}_games.html".format(selected_team, selected_year)

    # print to terminal , and send out request
    print("Scraping From: {} and {}".format(base_url, games_url))

    # pull both pages
    base_page = requests.get(base_url)
    games_page = requests.get(games_url)

    if (base_page.status_code == 200 and games_page.status_code == 200):
        base_html = base_page.content.decode("utf-8")
        games_html = games_page.content.decode("utf-8")
        # use regex to remove commenting
        base_soup = BeautifulSoup(re.sub("<!--|-->", "", base_html), "html.parser")
        games_soup = BeautifulSoup(re.sub("<!--|-->", "", games_html), "html.parser")
        running = True
        while (running):
            # view salary data
            if (selection == "Player Salaries"):
                get_salary(base_soup)
            if (selection == "Team Roster"):
                get_roster(base_soup)
            if (selection == "Per Game"):
                get_per_game(base_soup)
            if (selection == "Game Results"):
                get_game_results(games_soup)

            # confirm if user wants to view more of this team's stats
            questions = [{
                "type": "confirm",
                "message": "Continue viewing {} ({}) data?".format(team, year),
                "name": "continue",
                "default": True,
            }]
            answers = prompt(questions)
            if (answers['continue'] is True):
                questions = [{
                    'type': 'list',
                    'message': 'What data would you like to view?',
                    'name': 'data_selection',
                    'choices': choices
                }]
                answers = prompt(questions)
                selection = answers['data_selection']
            else:
                # user is done looking at the data for this team/year, break
                running = False
    elif (page.status_code == 404):
        print("page not found")
        print("attempted to scrape from: {} and {}".format(base_url, games_url))


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
    collect_data(answers['team_name'], answers['team_year'], answers['data_selection'])
    # confirm if user wants to view a different team/year
    questions = [{
        'type': 'confirm',
        'message': 'View a different team/year?',
        'name': 'continue',
        'default': True,
    }]
    answers = prompt(questions)
    if (answers['continue'] is True):
        main()

if __name__ == "__main__":
    main()
