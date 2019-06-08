import requests
from bs4 import BeautifulSoup
from teams import teams

def main():
	print("BucketWizard at attention ...\n")
	print("Which team's stats would you like to view?\n")

	user_input = input()
	selected_team = ""
	for key,value in teams.items():
		if (user_input in value):
			selected_team = key

	url = "https://www.basketball-reference.com/teams/"+selected_team+"/2019.html"
	page = requests.get(url)
	page_found = False 

	if (page.status_code == 200):
		print("page data secured ...")
		page_found = True 
		soup = BeautifulSoup(page.content, 'html.parser')
	elif (page.status_code == 404):
		print("page not found, spelling of team may be incorrect")

	if (page_found):
		print ("which stat in specific?")




if __name__ == "__main__":
	main()