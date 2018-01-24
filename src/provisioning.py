import json
import logging
import pyphen
import requests


class PhonetoqueRequest(object):
    """
    Prepares and posts pronunciation data to the REST API defined in configuration
    """
    def __init__(self, config):
        self.language = config['language']
        self.hyphenation_dict = pyphen.Pyphen(lang=config['hyphenation_dict'])
        self.ipa_hyphenation_dict = pyphen.Pyphen(lang=config['ipa_hyphenation_dict'])
        self.url = config['server_url']
        self.pronunciations = {}

    def prepare_data(self):
        """
        Syllabifies words and pronunciations
        :return:
        """
        self.pronunciations = {self.hyphenation_dict.inserted(k): [self.ipa_hyphenation_dict.inserted(x) for x in v]
                               for k, v in self.pronunciations.items()}

    def post_to_db(self, word):
        spelling = word.replace("-","")
        syllables = word.split("-")
        for pronunciation in self.pronunciations[word]:
            spelling_ipa = pronunciation.replace("-","")
            syllables_ipa = pronunciation.split("-")

            payload = {
                "language": self.language,
                "spelling": spelling,
                "spelling_ipa": spelling_ipa,
                "syllables": syllables,
                "syllables_ipa": syllables_ipa
            }
            response = requests.post(f"{self.url}/{self.language}_words/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(payload))
            logging.info(response.text)

    def post_all(self):
        for word in self.pronunciations:
            self.post_to_db(word)