from bs4 import BeautifulSoup
import os
import re
import requests
import time
import logging


class Scraper(object):
    """
    A scraper for wiktionary.org using bs4 to fetch and parse pronunciations
    """
    def __init__(self, language):
        """
        A scraper instance can only ever have one language, but can read and write from different files
        :param conf:
        """
        self.language = language
        self.pronunciations = {}
        self.word_list = []

    def pronunciations_from_wiktionary_english(self, word):
        """
        Fetch pronunciation from en.wiktionary.org
        :param word:
        :return:
        """
        #word = word.lower()
        logging.info("Fetching pronunciations for: %s" % word)
        try:
            request = requests.get('https://en.wiktionary.org/wiki/%s' % word).content
        except:
            logging.error("Request failed, trying again")
            time.sleep(10)
            return self.pronunciations_from_wiktionary_english(word)
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
        found_pronunciations = [x.text for x in raw_pronunciations if not "-" in x.text]
        logging.info("Found pronunciations: ")
        for p in found_pronunciations:
            logging.info(p)

        self.pronunciations[word]=found_pronunciations

    def pronunciations_from_wiktionary_french(self, word):
        """
        Fetch pronunciation from fr.wiktionary.org
        :param word:
        :return:
        """
        #word = word.lower()
        logging.info("Fetching pronunciations for: %s\n" % word)
        soup = BeautifulSoup(requests.get('https://fr.wiktionary.org/wiki/%s' % word).content, 'lxml')

        # This is French, we don't worry about multiple pronunciations. Vive l'Académie !
        try:
            pronunciation = soup.find('span', class_="API").text
            # Difference between the two IPA syntaxes left for later
            # regex = re.compile('^[/\[\\].*[/\\\]]$')

            # Removing tags and eventual parasites (see: penis)

            # pronunciation = regex.sub(pronunciation)
            pronunciation = pronunciation.replace("[", "")
            pronunciation = pronunciation.replace("]", "")
            pronunciation = pronunciation.replace("/", "")

            pronunciation = pronunciation.replace("\\", "")

            self.pronunciations[word] = [pronunciation]
            logging.info("Found pronunciations: ")
            logging.info(pronunciation)

        except AttributeError:  # not found !
            logging.error("No pronunciation found for "+ word)




    def pronunciations_from_wiktionary_italian(self,word):
        """
        Fetches pronunciation from it.wiktionary.org
        :param word:
        :return:
        """
        #word = word.lower()
        logging.info("Fetching pronunciations for: %s\n" % word)
        soup = BeautifulSoup(requests.get('https://it.wiktionary.org/wiki/%s' % word).content, 'lxml')

        try:
            # In Italian there is only one pronunciation
            pronunciation = soup.find('span', class_="IPA").text

            # regex = re.compile('^[/\[\\].*[/\\\]]$')
            pronunciation = "/" + pronunciation.replace("\\", "") + "/"
            self.pronunciations[word] = [pronunciation]

        except AttributeError:
            logging.info("No pronunciation found for "+ word)

    pronunciations_from_wiktionary = {
        'english': pronunciations_from_wiktionary_english,
        'french': pronunciations_from_wiktionary_french,
        'italian': pronunciations_from_wiktionary_italian
    }

    def read_word_list(self, filename):
        """
        Reads a list of words from a text file (one per line)
        :param filename:
        :return:
        """
        with open(filename, 'r') as f:
            self.word_list = f.read().split("\n")

    def write_line_by_line(self, filename, overwrite=False):
        """
        Fetches and writes pronunciations from words defined in self.wordlist and writes them to file as they are found
        :param overwrite:
        :param filename:
        :return:
        """
        already_fetched = []
        if not overwrite:
            try:
                with open(filename, 'r+', encoding='utf-8') as f:
                    already_fetched = [x.split(" ")[0] for x in f.read().splitlines()]
                os.rename(filename, filename + ".previous")
            except:
                pass
        else:
            try:
                os.rename(filename, filename + ".previous")
            except:
                pass

        new_words = [x for x in self.word_list if x not in already_fetched]

        for word in new_words:
            self.pronunciations_from_wiktionary[self.language](self, word)
            with open(filename, 'a+', encoding="utf-8") as file:
                try:
                    pronunciations = self.pronunciations[word]
                    if len(pronunciations) >= 0:
                        file.write(word)
                        file.write(" ")
                        for pron in pronunciations:
                            file.write(pron + " ")
                        file.write("\n")
                except KeyError:
                    pass