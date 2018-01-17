import csv
import logging
import os
import time
import requests
import re
import Wiktionary_scraper as ws

from lxml import html
from bs4 import BeautifulSoup

def common_words(language):
    """
    function that will give us the 1000 most common words in a language from http://1000mostcommonwords.com
    """
    url = 'http://1000mostcommonwords.com/1000-most-common-{}-words/'.format(language)
    try:
        request = requests.get(url).content
    except Exception as e:
        logging.error("Error while fetching {0}:\n{1}".format(url, e))
        
    soup = BeautifulSoup(request, 'lxml')
    section = soup.find(class_="entry-content")
    sub_sections = section.find_all('tr')
    common_words = []
    for sub_section in sub_sections:
        line = sub_section.find_all('td')
        if len(line) == 2:
            common_words.append(line[1].get_text().lower())
        else:
            pass
    return common_words

def create_wordlist(language):
    common_words_list = common_words(language)
    language = language.title()
    filename = "1000Common{}Words.txt".format(language)
    ws.write_wordlist(filename, common_words_list)



if __name__ == '__main__':
    create_wordlist('italian')
    create_wordlist('french')
    ws.write_line_by_line(ws.read_wordlist("1000CommonFrenchWords.txt"),"1000FrenchPron.txt", 'french')
    ws.write_line_by_line(ws.read_wordlist("1000CommonItalianWords.txt"),"1000ItalianPron.txt", 'italian')
    