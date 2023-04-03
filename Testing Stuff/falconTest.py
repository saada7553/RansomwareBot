import pandas as pd
import spacy
import testString
import main


cleaned_data = []
dataframe = pd.read_csv("../VictimAttacker Data/RansomwareData.csv")
def refang_database() -> ():
    for index, row in dataframe.iterrows():
        output = ""
        for char in row['Title Name']:
            if char != "[" and char != "]" and char != " ":
                output += char
        cleaned_data.append(output.lower())
        row['Victim Public URL'] = str(row['Victim Public URL'])
        for char in row['Victim Public URL']:
            if char != "[" and char != "]" and char != " ":
                output += char
        cleaned_data.append(output.lower())
refang_database()

falcon_hash = {}
attackers = ['Lockbit', 'BianLian', 'Endurance', 'Relic', 'Yanluowang', 'Monti', 'CL0P',
             'BlackByte', 'Abyss', 'Ice', 'KelvinSecurity', 'SunCrypt', 'Donut', 'Hive',
             'AgainstTheWest', "Abraham's", '0mega', "Karakurt", 'Cuba', 'Hades', 'Mallox',
             'MedusaLocker', 'LV', 'Snatch', 'BlackMagic', 'Radar', 'Clop', 'Bl00Dy', 'Darkbit',
             'VSOP', 'Vendetta ', 'Bl@ckT0r', 'ALPHV', 'RansomEXX', 'Nevada', 'Shao', 'AvosLocker',
             'Moses', 'Vice', 'RansomHouse', 'Royal', 'Play', 'Daixin', 'Arvin Club', 'Stormous',
             'Trigona', 'Free', 'Medusa', 'Ragnar', 'Izis', 'NB65', 'Quantum', 'Lockbit', 'Babuk',
             'Sekhmet', 'Industrial Spy', 'Nokoyawa', 'ArcLocker', 'Basta', 'Everest', 'Lorenz',
             'Red Alert', 'N4ughtySec', 'Snatch', 'UnSafe', 'Qilin', 'REvil']
attackers = [x.lower() for x in attackers]
attackers = set(attackers)

victims = {}
def download_falcon_tweets(num_to_scrape: int):
    scraped_data = ""
    scraped_data = testString.testString
    '''
    webbrowser.open('https://twitter.com/FalconFeedsio')
    time.sleep(5)
    for i in range(10):
    # while len(victims) < num_to_scrape:
        pyautogui.moveTo(500, 500)
        pyautogui.scroll(-2250)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.75)
        scraped_data += pyperclip.paste()
    pyautogui.hotkey('ctrl', 'w')
    '''
    return scraped_data


def clean_falcon_tweets(scraped_data: str):
    scraped_data_array = scraped_data.split('@FalconFeedsio')
    scraped_data_array = scraped_data_array[2:]
    scraped_data_array = [item.replace('#ransomware', '') for item in scraped_data_array if '#ransomware' in item]
    scraped_data_array = [item.split('#', 1)[0] for item in scraped_data_array]
    return scraped_data_array
cleandata = clean_falcon_tweets(download_falcon_tweets(25))


def process_falcon_url(word: str) -> str:
    word = word.split(',')[0]
    if '(' in word:
        tempL = word.split('(')
        word = tempL[1].split(')')[0]
    word = main.remove_website_suffix(word)
    word = main.remove_website_prefix(word)
    falcon_victim_names.append(word)
    return word


def simplify_falcon_input(stringin: str) -> str:
    stringin = stringin.replace(' ', '')
    stringin = stringin.lower()
    return stringin


nlp = spacy.load('en_core_web_sm')
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
            word = process_falcon_url(word)
    falcon_victim_names = [simplify_falcon_input(x) for x in falcon_victim_names]
    #print(f'Attacker: {attacker} \nVictims: {falcon_victim_names}')
    falcon_hash[tweet] = [attacker, falcon_victim_names]
    #print("---------------------------------------")


def find_falcon_matches():
    for entry in falcon_hash:
        curr_victims = falcon_hash[entry][1]
        no_match = []
        for victim in curr_victims:
            for item in cleaned_data:
                if victim not in item:
                    no_match.append(victim)

        no_match = set(no_match)
        if no_match != []:
            pass
            print(f'Attacker: {falcon_hash[entry][0]} \nVictims: {no_match}')

find_falcon_matches()
print(cleaned_data)