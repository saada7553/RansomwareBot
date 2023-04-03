import pyautogui
import time
import pyperclip
import pandas
import webbrowser


cleaned_data = []
victims = {}
pre_vs_post_data_cleaning = {}
dataframe = pandas.read_csv("RansomwareData.csv")


def download_ransomware_news_tweets(num_to_scrape: int) -> ():
    webbrowser.open('https://twitter.com/RansomwareNews')
    time.sleep(5)
    while len(pre_vs_post_data_cleaning) < num_to_scrape:
        with open('tweets.txt', 'w', encoding='utf-8') as f:
            f.write('')
        pyautogui.moveTo(500, 500)
        pyautogui.scroll(-2250)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.75)
        with open('tweets.txt', 'a', encoding='utf-8') as f:
            f.write(pyperclip.paste() + '\n\n')
        process_ransomware_news_tweets()
    pyautogui.hotkey('ctrl', 'w')


def remove_website_suffix(stringin: str) -> str:
    suffixlst = [".au", ".in", ".br", ".it", ".ca", ".mx", ".fr", ".tw", ".il", ".uk",
                 ".com", ".co", ".edu", ".gov", ".org", ".mil", ".net", '"', "/"]
    stringin = stringin.lower()
    for suffix in suffixlst:
        stringin = stringin.removesuffix(suffix)
    return stringin


def remove_website_prefix(stringin: str) -> str:
    disregard = ["https://", "http://", "https://www.", "http://www.", "www."]
    for item in disregard:
        if item in stringin:
            stringin = stringin.replace(item, "")
    return stringin


def process_ransomware_news_tweets() -> ():
    data = open("tweets.txt", "r", encoding="utf8")
    link_flag = False
    group = ""

    def string_processing(input):
        string = remove_website_suffix(input)
        string = remove_website_prefix(string)
        pre_vs_post_data_cleaning[string.replace(" ", "")] = string
        string = string.replace(" ", "")
        string = string.split("(", 1)[0]
        victims[string.lower()] = group

    for index, line in enumerate(data):
        if line[0:7] == "Group: ":
            group = line[7:len(line) - 1]
        if line[0:5] == "Title":
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

#TODO: implement partial string matching
def find_matches() -> ():
    non_matches = []
    for key, value in victims.items():
        found = False
        original_key = pre_vs_post_data_cleaning[key]
        for entry in cleaned_data:
            if key in entry:
                found = True
                break
        if not found and key not in non_matches:
            print(f"{value}: {original_key}")
            non_matches.append(key)
    if len(non_matches) == 0:
        print('No Missing Items Discovered')

def main() -> ():
    response = input("Scrape new posts from Twitter? Enter Y/N").lower()
    if response == "y":
        num = input("Enter minimum number of posts to collect: ")
        download_ransomware_news_tweets(int(num))
    else:
        process_ransomware_news_tweets()
    refang_database()
    print("---------------------------------------")
    print(f"Total Tweets Searched: {len(victims)}")
    print("POSSIBLE MISSING ITEMS:")
    print("---------------------------------------")
    find_matches()
    print("---------------------------------------")
    print("\n")
    input("Press Enter to Exit")


if __name__ == '__main__':
    main()
