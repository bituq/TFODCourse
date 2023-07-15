import requests
from bs4 import BeautifulSoup, Tag

url = "http://www-set.win.tue.nl/~wstomv/misc/yahtzee/osyp.php"

def get_best_option(score_card,bonus=None,ybonus=None,rollIndex=None,d1=None,d2=None,d3=None,d4=None,d5=None,kd1=0,kd2=0,kd3=0,kd4=0,kd5=0):
	pat1 = score_card['Aces']
	pat2 = score_card['Twos']
	pat3 = score_card['Threes']
	pat4 = score_card['Fours']
	pat5 = score_card['Fives']
	pat6 = score_card['Sixes']
	pat7 = score_card['Three of a Kind']
	pat8 = score_card['Four of a Kind']
	pat9 = score_card['Full House']
	pat10 = score_card['Small Straight']
	pat11 = score_card['Large Straight']
	pat12 = score_card['Yahtzee']
	pat13 = score_card['Chance']
	
	payload = {
		'SID': '',
		'TurnIndex': 'Turn #%231',
		'Pat1': '' if pat1 is None else pat1,
		'Pat2': '' if pat2 is None else pat2,
		'Pat3': '' if pat3 is None else pat3,
		'Pat4': '' if pat4 is None else pat4,
		'Pat5': '' if pat5 is None else pat5,
		'Pat6': '' if pat6 is None else pat6,
		'Bonus': '' if bonus is None else bonus,
		'UTotal': f'{(pat1 or 0)+(pat2 or 0)+(pat3 or 0)+(pat4 or 0)+(pat5 or 0)+(pat6 or 0)+(bonus or 0)}',
		'PatT': '' if pat7 is None else pat7,
		'PatF': '' if pat8 is None else pat8,
		'PatH': '' if pat9 is None else pat9,
		'PatS': '' if pat10 is None else pat10,
		'PatL': '' if pat11 is None else pat11,
		'PatY': '' if pat12 is None else pat12,
		'PatC': '' if pat13 is None else pat13,
		'ExtraYz': '' if ybonus is None else ybonus,
		'Total': f'{(pat1 or 0)+(pat2 or 0)+(pat3 or 0)+(pat4 or 0)+(pat5 or 0)+(pat6 or 0)+(bonus or 0)+(pat7 or 0)+(pat8 or 0)+(pat9 or 0)+(pat10 or 0)+(pat11 or 0)+(pat12 or 0)+(pat13 or 0)+(ybonus or 0)}',
		'RollIndex': '' if rollIndex is None else rollIndex,
		'Submit': 'Submit',
		'Dice1': '' if d1 is None else d1,
		'Dice2': '' if d2 is None else d2,
		'Dice3': '' if d3 is None else d3,
		'Dice4': '' if d4 is None else d4,
		'Dice5': '' if d5 is None else d5,
		'KDice1': '' if kd1 is None else kd1,
		'KDice2': '' if kd2 is None else kd2,
		'KDice3': '' if kd3 is None else kd3,
		'KDice4': '' if kd4 is None else kd4,
		'KDice5': '' if kd5 is None else kd5,
	}
	
	print(payload)
 
	response = requests.post(url, data=payload)
	
	soup = BeautifulSoup(response.text, 'html.parser')
	
	tables = soup.find_all('table')
	
	options_table = tables[6]
	
	best_option: Tag = options_table.find('tr')
 
	return best_option.getText().strip().splitlines()[0].strip()