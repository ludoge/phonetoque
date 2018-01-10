# coding: utf-8
import time
from lxml import html
import requests
import re
from bs4 import BeautifulSoup
import os
import csv
from Wiktionary_scraper import *

def common_words(language):
    """
    function that will give us the 1000 most common words in a language from http://1000mostcommonwords.com
    """
    url = 'http://1000mostcommonwords.com/1000-most-common-%s-words/' %language
    try:
        request = requests.get(url).content
    except:
        print("Request failed")
  
    soup = BeautifulSoup(request, 'lxml')
    section = soup.find(class_="entry-content")
    sub_sections = section.find_all('tr')
    common_words = []
    for sub_section in sub_sections:
        line = sub_section.find_all('td')
        common_word = line[1].get_text()
        common_word = common_word.lower()
        common_words.append(common_word)
    return common_words

def create_wordlist(language):
    common_words_list = common_words(language)
    language = language.title()
    filename = "1000Common%sWords.txt" %language
    write_wordlist(filename, common_words_list)



if __name__ == '__main__':
    create_wordlist('italian')
    create_wordlist('french')
    write_line_by_line(read_wordlist("1000CommonFrenchWords.txt"),"1000FrenchPron.txt", 'french')
    write_line_by_line(read_wordlist("1000CommonItalianWords.txt"),"1000ItalianPron.txt", 'italian')
    