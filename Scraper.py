# coding: utf-8

# In[45]:


from lxml import html
import requests
import re
from bs4 import BeautifulSoup


def pronunciations_from_wiktionary(word):
    soup = BeautifulSoup(requests.get('https://en.wiktionary.org/wiki/%s' % word).content, 'lxml')

    first_section_break = soup.find("hr")

    pronunciations = first_section_break.find_all_previous('span', class_="IPA")

    regex = re.compile('^[/\[].*[/\]]$')

    pronunciations = [x.text for x in pronunciations if regex.search(x.text)]

    return pronunciations


if __name__ == '__main__':
    while True:
        word = input("Enter an English word: \n")
        print(pronunciations_from_wiktionary(word))
