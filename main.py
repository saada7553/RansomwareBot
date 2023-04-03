import pyautogui
import time
import pyperclip
import pandas
import webbrowser
from thefuzz import fuzz

# Stores RansomwareData.csv data after strings have been processed. Basically a list of every victim we know
# from the sheet.
cleaned_data = []

# Pairs attackers & victims. Key = Victim, Value = Attacker group
victims = {}

# Pairs the original version of the Victim name with the post-processed version. When we show the output, we don't want
# the victim names to not have spaces, so we need to store the original format. Key = processed name, Victim = OG name
pre_vs_post_data_cleaning = {}

# Open the manually downloaded/new version of the victim tracking sheet
dataframe = pandas.read_csv("VictimAttacker Data/Ransomware Victim Tracking - Targets_Victims.csv")


def download_ransomware_news_tweets(num_to_scrape: int) -> ():
    """
    Opens browser, moves mouse out of the way, copies posts until enough tweets have been collected. Note that
    tweets.txt gets overwritten every time the while loop runs.
    param num_to_scrape: number of posts you want to gather.
    :return: void
    """
    webbrowser.open('https://twitter.com/RansomwareNews')
    time.sleep(5)
    while len(pre_vs_post_data_cleaning) < num_to_scrape:
        with open('VictimAttacker Data/tweets.txt', 'w', encoding='utf-8') as f:
            f.write('')  # Clears the text file from when it was used last
        pyautogui.moveTo(500, 500)
        pyautogui.scroll(-2250)  # Can be adjusted if you want to scroll further
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.75)
        with open('VictimAttacker Data/tweets.txt', 'a', encoding='utf-8') as f:
            f.write(pyperclip.paste() + '\n\n')
        process_ransomware_news_tweets()  # Process and store data before the file gets overwritten in the next loop
    pyautogui.hotkey('ctrl', 'w')  # Close browser


def remove_website_suffix(string_in: str) -> str:
    """
    Removes the suffix from a website. Not required for matching, but makes it easier.
    :param string_in:
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


def process_ransomware_news_tweets() -> ():
    """
    Uses the raw data in the tweets.txt file to find victims and attackers with string manipulation. No NLP for this
    Twitter account since the posts are always the same and NLP would run slower.
    :return:
    """
    data = open("VictimAttacker Data/tweets.txt", "r", encoding="utf8")
    link_flag = False  # This boolean has to do with a weird quirk based on how this specific Twitter Bot posts.
    group = ""

    def string_processing(inpt):
        """
        Remove prefixes and suffixes from string, remove parenthesis, removes spaces, and make everything lower case
        for ease of matching later on.
        """
        string = remove_website_suffix(inpt)
        string = remove_website_prefix(string)
        pre_vs_post_data_cleaning[string.replace(" ", "")] = string
        string = string.replace(" ", "")
        string = string.split("(", 1)[0]
        victims[string.lower()] = group

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


def find_matches() -> ():
    """
    Uses fuzzy string matching, since the name from Twitter and the name in the sheet may be a little differently
    formatted. Increase the similarity_score threshold to make the script more strict, but this may increase false
    positives (cases where the program reports that a certain victim is not present in the sheet, when in reality
    it is present)
    """
    non_matches = []
    for key, value in victims.items():
        found = False
        original_key = pre_vs_post_data_cleaning[key]
        for entry in cleaned_data:
            similarity_score = fuzz.token_set_ratio(key, entry)
            if similarity_score > 80:  # Increase threshold here to make program more strict
                found = True
                break
        if not found and key not in non_matches:
            print(f"{value}: {original_key}")
            non_matches.append(key)
    if len(non_matches) == 0:
        print('No Missing Items Discovered')


def tui_io(mode):
    """
    Handles terminal input/output to clean main loop
    """
    if mode == 'num_posts?':
        number = input("Enter minimum number of posts to collect: ")
        return number
    elif mode == 'dash_out':
        print("---------------------------------------")
    elif mode == 'header':
        tui_io('dash_out')
        print(f"Total Tweets Searched: {len(victims)}")
        print("POSSIBLE MISSING ITEMS:")
        tui_io('dash_out')
    elif mode == 'new_line':
        print("\n")
    elif mode == 'exit_prompt':
        input("Press Enter to Exit")


def main() -> ():
    num = tui_io('num_posts?')
    download_ransomware_news_tweets(int(num))
    refang_database()
    tui_io('header')
    find_matches()
    tui_io('dash_out')
    tui_io('new_line')
    tui_io('exit_prompt')


if __name__ == '__main__':
    main()
