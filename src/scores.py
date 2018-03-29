from bs4 import BeautifulSoup
import logging
import numpy as np
import requests
import yaml


class Scoring(object):
    """
    Gets scores of transliteration from a language to another
    """
    def __init__(self, config):
        self.language1 = config['language']
        self.language2 = config['language2']
        self.debug_url = config['debug_url']

    def get_word_score(self, spelling):
        """
        gets the score of one word from language1 transliterated to language2
        """
        try:
            url = f'{self.debug_url}/translitteration/'
            response = requests.post(url, data = {'language1': self.language1, 'language2': self.language2, 'spelling': spelling})
            data = response.text
        except Exception as e:
            logging.error("Error while fetching {0}:\n{1}".format(url, e))  
        soup = BeautifulSoup(data, "html5lib")
        score = soup.find(id="harmonic_mean").getText()
        return(int(score[:-2]))

    def get_score(self, text_file):
        """
        gets the average transliteration score of all words from a file from language1 to language2
        """
        with open(text_file) as text_file:
            all_scores = []
            not_found = 0
            for word in text_file:
                try:
                    score = self.get_word_score(word)
                    all_scores.append(score)
                except AttributeError:
                    # all_scores.append(0)
                    not_found += 1
            total_number_of_words = len(all_scores) + not_found
            return f"Total score: {round(np.mean(all_scores),2)}, total number of words: {total_number_of_words}, not found words: {not_found}" 