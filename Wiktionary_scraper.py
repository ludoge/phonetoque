# coding: utf-8
import time
from lxml import html
import requests
import re
from bs4 import BeautifulSoup
import os
import csv


def pronunciations_from_wiktionary(word):
    word = word.lower()
    print("Fetching pronunciations for: %s" %word)
    try:
        request = requests.get('https://en.wiktionary.org/wiki/%s' % word).content
    except:
        print("Request failed, trying again")
        time.sleep(10)
        return pronunciations_from_wiktionary(word)
    soup = BeautifulSoup(request, 'lxml')

    try:
        first_section_break = soup.find("hr")

        # Section switches to other languages after <hr>
        raw_pronunciations = first_section_break.find_all_previous('span', class_="IPA")

    except:
        raw_pronunciations = soup.find_all('span', class_="IPA")


    #raw_pronunciations = soup.find_all('span', class_="IPA")

    # Difference between the two IPA syntaxes left for later
    regex = re.compile('^[/\[].*[/\]]$')

    # Removing tags and eventual parasites (see: penis)
    #pronunciations = [x.text.replace("/","/").replace("[","[").replace("]","]") for x in raw_pronunciations if regex.search(x.text) and ('.' in x.text or len(x.text)<4) or (('ˌ' in x.text or 'ˈ' in x.text) and len(x.text)<14)]
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
    pronunciation = pronunciation.replace("[","")
    pronunciation = pronunciation.replace("]","")
    pronunciation = pronunciation.replace("/","")

    pronunciation = pronunciation.replace("\\","")

    return [pronunciation]

def pronunciations_from_wiktionary_italian(word):
    print("Fetching pronunciations for: %s\n" %word)
    soup = BeautifulSoup(requests.get('https://it.wiktionary.org/wiki/%s' % word).content, 'lxml')

    try:
        # In Italian there is only one pronunciation
        pronunciation = soup.find('span', class_="IPA").text
        
         # regex = re.compile('^[/\[\\].*[/\\\]]$')
        pronunciation = "/"+pronunciation.replace("\\","")+"/"
        return [pronunciation]

    except AttributeError:
        print("Can't find pronunciation for", word)



def pronunciations_from_wiktionary_list(words):
    pronunciations_dictionary = {word: pronunciations_from_wiktionary(word) for word in words}
    return pronunciations_dictionary


def read_csv(filename):
    file = open(filename, 'r')
    return file.read().split(",")


def read_wordlist(filename):
    file = open(filename, 'r')
    return file.read().split("\n")


def write_to_csv(dictionary, filename):
    try:
        os.rename(filename, filename+".previous")
    except:
        pass
    file = open(filename, 'w+', encoding="utf-8")
    for word in dictionary:
        if len(dictionary[word])>0:
            file.write(word)
            file.write(" ")
            #file.write(':')
            for pronunciation in dictionary[word]:
                file.write(pronunciation+"\n")
            #file.write("\n")
    file.close()

def write_line_by_line(words, filename):
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
        os.rename(filename, filename+".previous")
    except:
        pass

    #print(already_fetched)
    new_words = [x for x in words if x not in already_fetched]
    #print(new_words)
    if new_words == []:
        with open(filename, "a+", encoding="utf-8") as file:
            file.write(". ˈ ˌ -")

    for word in new_words:
        with open(filename, 'a+', encoding="utf-8") as file:
            prons = pronunciations_from_wiktionary(word)
            if len(prons)>=0:
                file.write(word)
                file.write(" ")
                for pron in prons:
                    file.write(pron+" ")
                file.write("\n")


if __name__ == '__main__':
    # while True:
    #   word = input("Enter an English word: \n")
    #   print(pronunciations_from_wiktionary(word))
    # print(pronunciations_from_wiktionary_list(["cat","dog"]))
    # print(pronunciations_from_wiktionary_list(read_wordlist("wordsEn.txt")))
    # write_to_csv(pronunciations_from_wiktionary_list(read_wordlist("google10k.txt")),"10kpron.txt")
    # pronunciations_from_wiktionary_list(read_wordlist("10Words.txt"))
    write_line_by_line(read_wordlist("1000CommonWords.txt"),"1000Pron.txt")