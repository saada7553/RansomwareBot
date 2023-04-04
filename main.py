import pyautogui
import time
import pyperclip
import pandas
import webbrowser
import spacy
from thefuzz import fuzz

# Stores RansomwareData.csv data after strings have been processed. Basically a list of every victim we know
# from the sheet.
cleaned_data = []

# Pairs attackers & victims. Key = Victim, Value = Attacker group. Used for the @RansomwareNews account only
victims = {}

# Pairs Tweets from the Falcon Feed account to a list of victims. Used for the Falcon Feed account only
falcon_hash = {}

# Pairs the original version of the Victim name with the post-processed version. When we show the output, we don't want
# the victim names to not have spaces, so we need to store the original format. Key = processed name, Victim = OG name
pre_vs_post_data_cleaning = {}

# Open the manually downloaded/new version of the victim tracking sheet
dataframe = pandas.read_csv("VictimAttacker Data/Ransomware Victim Tracking - Targets_Victims.csv")

# Pre-trained model which retrieves organization names from Tweets
nlp = spacy.load('en_core_web_sm')

# List of all known ransom groups so that they can be ignored by the nlp detection as otherwise they would be flagged
# as organizations/victims
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


def download_ransomware_news_tweets(num_to_scrape: int, acct) -> ():
    """
    Opens browser, moves mouse out of the way, copies posts until enough tweets have been collected. Note that
    tweets.txt gets overwritten every time the while loop runs. Generic function which handles downloads for both
    currently supported Twitter accounts
    param num_to_scrape: number of posts you want to gather.
    :return: void
    """
    def generic_scrape():
        """
        Handles text selection & copying for both accounts as process is similar
        """
        pyautogui.moveTo(500, 500)
        pyautogui.scroll(-2250)  # Can be adjusted if you want to scroll further
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.75)

    if acct == '@RansomwareNews':
        webbrowser.open('https://twitter.com/RansomwareNews')
        time.sleep(5)
        while len(pre_vs_post_data_cleaning) < num_to_scrape:
            with open('VictimAttacker Data/tweets.txt', 'w', encoding='utf-8') as f:
                f.write('')  # Clears the text file from when it was used last
            generic_scrape()
            with open('VictimAttacker Data/tweets.txt', 'a', encoding='utf-8') as f:
                f.write(pyperclip.paste() + '\n\n')
            process_ransomware_news_tweets(acct='@RansomwareNews')  # Process and store data before the file gets
            # overwritten in the next loop
        pyautogui.hotkey('ctrl', 'w')  # Close browser

    elif acct == 'Falcon Feed':
        scraped_data = ""
        webbrowser.open('https://twitter.com/FalconFeedsio')
        time.sleep(5)
        for i in range(int(num_to_scrape / 8)):  # Can't track # of Tweets scraped constantly for this model (too slow)
            generic_scrape()
            scraped_data += pyperclip.paste()
        pyautogui.hotkey('ctrl', 'w')
        return scraped_data


def remove_website_suffix(string_in: str) -> str:
    """
    Removes the suffix from a website. Not required for matching, but makes it easier.
    Low-key not a good idea I'll probably delete this function later on.
    :return: fixed string
    """
    suffix_list = [".au", ".in", ".br", ".it", ".ca", ".mx", ".fr", ".tw", ".il", ".uk",
                   ".com", ".co", ".edu", ".gov", ".org", ".mil", ".net", '"', "/"]  # List of common endings
    string_in = string_in.lower()
    for suffix in suffix_list:
        string_in = string_in.removesuffix(suffix)
    return string_in


def remove_website_prefix(string_in: str) -> str:
    """
    The prefix can vary from the Tweet to what we have stored in the sheet, so it's best to remove it to reduce false
    negative matches.
    """
    disregard = ["https://", "http://", "https://www.", "http://www.", "www."]
    for item in disregard:
        if item in string_in:
            string_in = string_in.replace(item, "")
    return string_in


def process_ransomware_news_tweets(acct: str, scraped_data='') -> ():
    """
    Uses the raw data in the tweets.txt file to find victims and attackers with string manipulation. No NLP for this
    Twitter account since the posts are always the same and NLP would run slower.
    """
    def simplify_falcon_input(stringin: str) -> str:
        """
        Just removes spaces and makes input lower case for Falcon Feed
        """
        stringin = stringin.replace(' ', '')
        stringin = stringin.lower()
        return stringin

    def process_falcon_url(url_in: str) -> str:
        url_in = url_in.split(',')[0]
        if '(' in url_in:
            temp_l = url_in.split('(')
            url_in = temp_l[1].split(')')[0]
        return url_in

    def string_processing(inpt):
        """
        Remove prefixes and suffixes from string, remove parenthesis, removes spaces, and make everything lower case
        for ease of matching later on. Used for @RansomwareNews
        """
        string = remove_website_suffix(inpt)
        string = remove_website_prefix(string)
        pre_vs_post_data_cleaning[string.replace(" ", "")] = string
        string = string.replace(" ", "")
        string = string.split("(", 1)[0]
        victims[string.lower()] = group

    if acct == 'Falcon Feed':
        scraped_data_array = scraped_data.split('@FalconFeedsio')
        scraped_data_array = scraped_data_array[2:]
        scraped_data_array = [item.replace('#ransomware', '') for item in scraped_data_array if '#ransomware' in item]
        scraped_data_array = [item.split('#', 1)[0] for item in scraped_data_array]
        cleandata = [x.split('\n')[3] for x in scraped_data_array]

        for tweet in cleandata:
            doc = nlp(tweet)
            words = tweet.split(' ')
            falcon_victim_names = []
            attacker = 'ERROR'
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
        return

    # All processing below is only for @RansomwareNews account
    data = open("VictimAttacker Data/tweets.txt", "r", encoding="utf8")
    link_flag = False  # This boolean has to do with a weird quirk based on how this specific Twitter Bot posts.
    group = ""

    # String processing specific to @RansomwareNews bot. Will not work with other Twitter accounts
    # TODO: Implement regular expression matching instead of this mess
    for index, line in enumerate(data):
        if line[0:7] == "Group: ":  # Finds the attacker
            group = line[7:len(line) - 1]
        if line[0:5] == "Title":  # Everything after the Title tag in the tweet becomes the victim
            if len(line) < 9:
                link_flag = True
            else:
                string_processing(line[7:len(line) - 1])
        elif link_flag:
            if line == "\n":
                continue
            else:
                string_processing(line[:len(line) - 1])
                link_flag = False
    data.close()


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


def find_matches(acct: str) -> ():
    """
    Uses fuzzy string matching, since the name from Twitter and the name in the sheet may be a little differently
    formatted. Increase the similarity_score threshold to make the script more strict, but this may increase false
    positives (cases where the program reports that a certain victim is not present in the sheet, when in reality
    it is present)
    """
    if acct == '@RansomwareNews':
        non_matches = []
        for key, value in victims.items():
            found = False
            original_key = pre_vs_post_data_cleaning[key]
            for entry in cleaned_data:
                similarity_score = fuzz.token_set_ratio(key, entry)
                if similarity_score > 75:  # Increase threshold here to make program more strict
                    found = True
                    break
            if not found and key not in non_matches:
                print(f"{value}: {original_key}")
                non_matches.append(key)
        if len(non_matches) == 0:
            print('No Missing Items Discovered From @RansomwareNews')

    elif acct == 'Falcon Feed':
        at_least_one_missing = False
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
                    at_least_one_missing = True
                    no_match.append(pre_vs_post_data_cleaning[victim])
            no_match = set(no_match)
            if no_match != set([]):
                for item in no_match:
                    print(f'{falcon_hash[entry][0]}: {item}')
        if not at_least_one_missing:
            print('No Missing Items Discovered From Falcon Feed')


def tui_io(mode):
    """
    Handles terminal input/output to clean main loop
    """
    if mode == 'num_posts?':
        number = input("Enter minimum number of posts to collect: ")
        return number
    elif mode == 'dash_out':
        print("---------------------------------------")
    elif mode == 'header_ransomware_news':
        tui_io('dash_out')
        print(f"Total Tweets Searched: {len(victims) * 2}")
        print("POSSIBLE MISSING ITEMS FROM @RANSOMWARENEWS:")
        tui_io('dash_out')
    elif mode == 'header_falcon':
        print("POSSIBLE MISSING ITEMS FROM FALCON FEED:")
        tui_io('dash_out')
    elif mode == 'new_line':
        print("\n")
    elif mode == 'exit_prompt':
        input("Press Enter to Exit")


def main() -> ():
    num = tui_io('num_posts?')
    download_ransomware_news_tweets(int(num), '@RansomwareNews')
    refang_database()
    tui_io('header_ransomware_news')
    find_matches('@RansomwareNews')
    tui_io('dash_out')
    tui_io('header_falcon')
    process_ransomware_news_tweets('Falcon Feed', scraped_data=download_ransomware_news_tweets(int(num), 'Falcon Feed'))
    find_matches('Falcon Feed')
    tui_io('new_line')
    tui_io('exit_prompt')


if __name__ == '__main__':
    main()
