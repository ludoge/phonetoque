# coding: utf-8

from lxml import html
import requests
import re
from bs4 import BeautifulSoup
import os
import csv


def pronunciation_from_rhouse(word):
    word = word.lower()
    print("Fetching pronunciations for: %s\n" %word)
    try:
        soup = BeautifulSoup(requests.get("https://www.thefreedictionary.com/%s" % word).content, "lxml")
        # soup = BeautifulSoup(requests.get('https://en.wiktionary.org/wiki/%s' % word).content, 'lxml')

        '''
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
        '''

        section = soup.find("section", attrs={"data-src": "rHouse"})

        syllabified_word = section.find("h2").text

        pronunciation = section.find("span", class_="pron").text

        return [syllabified_word, pronunciation]

    except:
        print ("No data found for: "+word)



def pronunciations_from_rhouse_list(words):
    pronunciations_dictionary = {word: pronunciation_from_rhouse(word) for word in words}
    return pronunciations_dictionary


def read_csv(filename):
    file = open(filename, 'r')
    return file.read().split(",")


def read_wordlist(filename):
    file = open(filename, 'r')
    return file.read().split("\n")


def write_to_file(dictionary, filename):
    try:
        os.rename(filename, filename+".previous")
    except:
        pass
    file = open(filename, 'w+', encoding="utf-8")
    for word in dictionary:
        try:
            file.write(dictionary[word][0])
            file.write(':')
            for pronunciation in dictionary[word][1:]:
                file.write(" "+pronunciation+",")
            file.write("\n")
        except:
            pass
    file.close()




if __name__ == '__main__':
    #while True:
    #   word = input("Enter an English word: \n")
    #   print(pronunciation_from_rhouse(word))
    # print(pronunciations_from_wiktionary_list(["cat","dog"]))
    # print(pronunciations_from_wiktionary_list(read_wordlist("wordsEn.txt")))
    write_to_file(pronunciations_from_rhouse_list(read_wordlist("1000CommonWords.txt")),"rhtest1000.txt")

