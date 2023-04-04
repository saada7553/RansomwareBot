import webbrowser
import time
import pandas as pd
import pyautogui
import pyperclip
import spacy
import main
import testString
from thefuzz import fuzz


cleaned_data = []
nlp = spacy.load('en_core_web_sm')
dataframe = pd.read_csv("VictimAttacker Data/Ransomware Victim Tracking - Targets_Victims.csv")
pre_vs_post_data_cleaning = {}

def refang_database() -> ():
    """
    Removes the [] brackets around the links from the ransomware sheet. Removes spaces, and makes everything
    lower case for easier matching. Grabs data from 'Title Name' column and 'Victim Public URL' colum
    as everything else in the sheet is irrelevant for this purpose.
    """
    for index, row in dataframe.iterrows():
        output = ''
        for char in row['Title Name']:
            # TODO: Rewrite this to only allow a-z characters instead on only omitting spaces & square brackets
            if char != "[" and char != "]" and char != " ":
                output += char
        output = output.lower()
        if 'victim' in output:
            output = output.split('victim')[1]  # In sheet: 'x Ransomware Group Victim x'. Removes text before 'victim'
        cleaned_data.append(output)

        output = ''
        row['Victim Public URL'] = str(row['Victim Public URL'])
        for char in row['Victim Public URL']:
            if char != "[" and char != "]" and char != " ":
                output += char
        cleaned_data.append(output.lower())

falcon_hash = {}
attackers = ['Lockbit', 'BianLian', 'Endurance', 'Relic', 'Yanluowang', 'Monti', 'CL0P',
             'BlackByte', 'Abyss', 'Ice', 'KelvinSecurity', 'SunCrypt', 'Donut', 'Hive',
             'AgainstTheWest', "Abraham's", '0mega', "Karakurt", 'Cuba', 'Hades', 'Mallox',
             'MedusaLocker', 'LV', 'Snatch', 'BlackMagic', 'Radar', 'Clop', 'Bl00Dy', 'Darkbit',
             'VSOP', 'Vendetta ', 'Bl@ckT0r', 'ALPHV', 'RansomEXX', 'Nevada', 'Shao', 'AvosLocker',
             'Moses', 'Vice', 'RansomHouse', 'Royal', 'Play', 'Daixin', 'Arvin Club', 'Stormous',
             'Trigona', 'Free', 'Medusa', 'Ragnar', 'Izis', 'NB65', 'Quantum', 'Lockbit', 'Babuk',
             'Sekhmet', 'Industrial Spy', 'Nokoyawa', 'ArcLocker', 'Basta', 'Everest', 'Lorenz',
             'Red Alert', 'N4ughtySec', 'Snatch', 'UnSafe', 'Qilin', 'REvil', 'BlackBasta', 'Black Basta']
attackers = [x.lower() for x in attackers]
attackers = set(attackers)

# victims = {}
def download_falcon_tweets(num_to_scrape: int):
    scraped_data = ""
    webbrowser.open('https://twitter.com/FalconFeedsio')
    time.sleep(5)
    for i in range(int(num_to_scrape/8)):
        pyautogui.moveTo(500, 500)
        pyautogui.scroll(-2250)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.75)
        scraped_data += pyperclip.paste()
    pyautogui.hotkey('ctrl', 'w')
    return scraped_data


def clean_falcon_tweets(scraped_data: str):
    scraped_data_array = scraped_data.split('@FalconFeedsio')
    scraped_data_array = scraped_data_array[2:]
    scraped_data_array = [item.replace('#ransomware', '') for item in scraped_data_array if '#ransomware' in item]
    scraped_data_array = [item.split('#', 1)[0] for item in scraped_data_array]
    return scraped_data_array
# TODO add this
cleandata = clean_falcon_tweets(download_falcon_tweets(25))
cleandata = [x.split('\n')[3] for x in cleandata]


def process_falcon_url(word: str) -> str:
    word = word.split(',')[0]
    if '(' in word:
        tempL = word.split('(')
        word = tempL[1].split(')')[0]
    return word


def clean_falcon_tweets():
    def simplify_falcon_input(stringin: str) -> str:
        stringin = stringin.replace(' ', '')
        stringin = stringin.lower()
        return stringin

    for tweet in cleandata:
        doc = nlp(tweet)
        words = tweet.split(' ')
        falcon_victim_names = []
        attacker = 'NLP ERROR'
        for ent in doc.ents:
            if ent.label_ == 'PERSON' or ent.label_ == 'ORG' and str(ent).lower() not in attackers:
                falcon_victim_names.append(ent.text)
        for word in words:
            for item in attackers:
                if item in word.lower():
                    attacker = item
            if 'http' in word:
                pre_vs_post_data_cleaning[simplify_falcon_input(word)] = word
                word = process_falcon_url(word)
                falcon_victim_names.append(word)
        for item in falcon_victim_names:
            pre_vs_post_data_cleaning[simplify_falcon_input(item)] = item
        falcon_victim_names = [simplify_falcon_input(x) for x in falcon_victim_names]
        falcon_hash[tweet] = [attacker, falcon_victim_names]


def find_falcon_matches():
    for entry in falcon_hash:
        curr_victims = falcon_hash[entry][1]
        no_match = []
        for victim in curr_victims:
            found = False
            for item in cleaned_data:
                similarity_score = fuzz.token_set_ratio(item, victim)
                if similarity_score > 75:  # Increase threshold here to make program more strict
                    found = True
                    break
            if not found:
                no_match.append(pre_vs_post_data_cleaning[victim])
        no_match = set(no_match)
        if no_match != set([]):
            for item in no_match:
                print(f'{falcon_hash[entry][0]}: {item}')

# refang_database()
clean_falcon_tweets()
find_falcon_matches()
