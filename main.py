import pyautogui
import time
import pyperclip
import pandas
import webbrowser


cleaned_data = []
interest = {}
originals = {}

def build_database() -> ():
    df = pandas.read_csv("RansomwareData.csv")
    with open("items.txt", "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(df["Title Name"]))
        for index, row in df.iterrows():
            currURL = str(row["Victim Public URL"])
            f_out.write(currURL)
            f_out.write("\n")


def scrape(num_to_scrape: int) -> ():
    webbrowser.open('https://twitter.com/RansomwareNews')
    time.sleep(5)
    while len(originals) < num_to_scrape:
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
        clean_tweets()
    pyautogui.hotkey('ctrl', 'w')


def remove_suffix(stringin: str) -> str:
    suffixlst = [".au", ".in", ".br", ".it", ".ca", ".mx", ".fr", ".tw", ".il", ".uk",
                 ".com", ".co", ".edu", ".gov", ".org", ".mil", ".net", '"', "/"]
    stringin = stringin.lower()
    for suffix in suffixlst:
        stringin = stringin.removesuffix(suffix)
    return stringin


def clean_tweets() -> ():
    data = open("tweets.txt", "r", encoding="utf8")
    disregard = ["https://", "http://", "https://www.", "http://www.", "www."]
    link_flag = False
    group = ""

    def string_processing(input):
        string = remove_suffix(input)
        for item in disregard:
            if item in string:
                string = string.replace(item, "")
        originals[string.replace(" ", "")] = string
        string = string.replace(" ", "")
        interest[string.lower()] = group

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


def clean_data() -> ():
    items_file = open("items.txt", "r", encoding="utf8")
    entries = items_file.readlines()
    items_file.close()
    for entry in entries:
        output = ""
        for char in entry:
            if char != "[" and char != "]" and char != " ":
                output += char
        cleaned_data.append(output.lower())


def find_matches() -> ():
    non_matches = []
    for key, value in interest.items():
        found = False
        original_key = originals[key]
        for entry in cleaned_data:
            if key in entry:
                found = True
                break
        if not found and key not in non_matches:
            print(f"{value}: {original_key}")
            non_matches.append(key)

def main() -> ():
    build_database()
    response = input("Scrape new posts from Twitter? Enter Y/N").lower()
    if response == "y":
        num = input("Enter minimum number of posts to collect: ")
        scrape(int(num))
    else:
        clean_tweets()
    clean_data()
    print("---------------------------------------")
    print(f"Total Tweets Searched: {len(interest)}")
    print("POSSIBLE MISSING ITEMS:")
    print("---------------------------------------")
    find_matches()
    print("---------------------------------------")
    print("\n")
    input("Press Enter to Exit")


if __name__ == '__main__':
    main()
