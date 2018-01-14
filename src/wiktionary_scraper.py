from bs4 import BeautifulSoup
import os
import re
import requests
import time


def pronunciations_from_wiktionary_english(word):
    word = word.lower()
    print("Fetching pronunciations for: %s" % word)
    try:
        request = requests.get('https://en.wiktionary.org/wiki/%s' % word).content
    except:
        print("Request failed, trying again")
        time.sleep(10)
        return pronunciations_from_wiktionary_english(word)
    soup = BeautifulSoup(request, 'lxml')

    try:
        first_section_break = soup.find("hr")

        # Section switches to other languages after <hr>
        raw_pronunciations = first_section_break.find_all_previous('span', class_="IPA")

    except:
        raw_pronunciations = soup.find_all('span', class_="IPA")

    # raw_pronunciations = soup.find_all('span', class_="IPA")

    # Difference between the two IPA syntaxes left for later
    regex = re.compile('^[/\[].*[/\]]$')

    # Removing tags and eventual parasites (see: penis)
    # pronunciations = [x.text.replace("/","/").replace("[","[").replace("]","]") for x in raw_pronunciations if regex.search(x.text) and ('.' in x.text or len(x.text)<4) or (('ˌ' in x.text or 'ˈ' in x.text) and len(x.text)<14)]
    pronunciations = [x.text for x in raw_pronunciations if not "-" in x.text]
    print("Found pronunciations: ")
    for p in pronunciations: print(p)

    return pronunciations


def pronunciations_from_wiktionary_french(word):
    # print("Fetching pronunciations for: %s\n" %word)
    soup = BeautifulSoup(requests.get('https://fr.wiktionary.org/wiki/%s' % word).content, 'lxml')

    # This is French, we don't worry about multiple pronunciations. Vive l'Académie !
    pronunciation = soup.find('span', class_="API").text

    # Difference between the two IPA syntaxes left for later
    # regex = re.compile('^[/\[\\].*[/\\\]]$')

    # Removing tags and eventual parasites (see: penis)

    # pronunciation = regex.sub(pronunciation)
    pronunciation = pronunciation.replace("[", "")
    pronunciation = pronunciation.replace("]", "")
    pronunciation = pronunciation.replace("/", "")

    pronunciation = pronunciation.replace("\\", "")

    return [pronunciation]


def pronunciations_from_wiktionary_italian(word):
    print("Fetching pronunciations for: %s\n" % word)
    soup = BeautifulSoup(requests.get('https://it.wiktionary.org/wiki/%s' % word).content, 'lxml')

    try:
        # In Italian there is only one pronunciation
        pronunciation = soup.find('span', class_="IPA").text

        # regex = re.compile('^[/\[\\].*[/\\\]]$')
        pronunciation = "/" + pronunciation.replace("\\", "") + "/"
        return [pronunciation]

    except AttributeError:
        print("Can't find pronunciation for", word)


pronunciations_from_wiktionary = {
    'english': pronunciations_from_wiktionary_english,
    'french': pronunciations_from_wiktionary_french,
    'italian': pronunciations_from_wiktionary_italian
}


def read_csv(filename):
    file = open(filename, 'r')
    return file.read().split(",")


def read_word_list(filename):
    file = open(filename, 'r')
    return file.read().split("\n")


def write_line_by_line(words, filename, language):
    """
    Improved function to fetch pronunciations from a wordlist, allows to interrupt and resume scraping
    :param words:
    :param filename:
    :return:
    """
    already_fetched = []
    try:
        with open(filename, 'r+', encoding='utf-8') as file:
            already_fetched = [x.split(" ")[0] for x in file.read().splitlines()]
        os.rename(filename, filename + ".previous")
    except:
        pass

    new_words = [x for x in words if x not in already_fetched]

    for word in new_words:
        with open(filename, 'a+', encoding="utf-8") as file:
            pronunciations = pronunciations_from_wiktionary[language](word)
            if len(pronunciations) >= 0:
                file.write(word)
                file.write(" ")
                for pron in pronunciations:
                    file.write(pron + " ")
                file.write("\n")