# coding: utf-8

from lxml import html
import requests
import re
from bs4 import BeautifulSoup
import os
import csv


def pronunciations_from_wiktionary(word):
    word = word.lower()
    print("Fetching pronunciations for: %s\n" %word)
    soup = BeautifulSoup(requests.get('https://en.wiktionary.org/wiki/%s' % word).content, 'lxml')

    try:
        first_section_break = soup.find("hr")

        # Section switches to other languages after <hr>
        pronunciations = first_section_break.find_all_previous('span', class_="IPA")

    except AttributeError:
        pronunciations = soup.find_all('span', class_="IPA")

    # Difference between the two IPA syntaxes left for later
    regex = re.compile('^[/\[].*[/\]]$')

    # Removing tags and eventual parasites (see: penis)
    pronunciations = [x.text for x in pronunciations if regex.search(x.text)]
    return pronunciations

def pronunciations_from_wiktionary_french(word):
    print("Fetching pronunciations for: %s\n" %word)
    soup = BeautifulSoup(requests.get('https://fr.wiktionary.org/wiki/%s' % word).content, 'lxml')

    # This is French, we don't worry about multiple pronunciations. Vive l'Académie !
    pronunciation = soup.find('span', class_="API").text

    # Difference between the two IPA syntaxes left for later
    # regex = re.compile('^[/\[\\].*[/\\\]]$')

    # Removing tags and eventual parasites (see: penis)

    pronunciation = "/"+pronunciation.replace("\\","")+"/"

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
            file.write(':')
            for pronunciation in dictionary[word]:
                file.write(" "+pronunciation+",")
            file.write("\n")
    file.close()




if __name__ == '__main__':
    while True:
       word = input("Enter an Italian word: \n")
       print(pronunciations_from_wiktionary_italian(word))
    # print(pronunciations_from_wiktionary_list(["cat","dog"]))
    # print(pronunciations_from_wiktionary_list(read_wordlist("wordsEn.txt")))
    # write_to_csv(pronunciations_from_wiktionary_list(read_wordlist("1000CommonWords.txt")),"1000CommonPronunciations.csv")
