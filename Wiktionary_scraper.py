# coding: utf-8

from lxml import html
import requests
import re
from bs4 import BeautifulSoup


def pronunciations_from_wiktionary(word):
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


if __name__ == '__main__':
    while True:
        word = input("Enter an English word: \n")
        print(pronunciations_from_wiktionary(word))
