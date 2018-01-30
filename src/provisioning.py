import json
import logging
import pyphen
import requests
import collections


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
        self.all_words_route = self.url + "/" + self.language
        self.all_syllables_ipa = {}
        self.max_syllables = {}

    def prepare_data(self):
        """
        Syllabifies words and pronunciations
        :return:
        """
        self.pronunciations = {self.hyphenation_dict.inserted("  "+k+"  ").strip():
                                   [self.ipa_hyphenation_dict.inserted("  "+x+"  ").strip() for x in v]
                               for k, v in self.pronunciations.items()}

    def post_word_to_db(self, word):
        spelling = word.replace("-", "").lower()
        syllables = [x for x in word.split("-") if x != '']
        for pronunciation in self.pronunciations[word]:
            spelling_ipa = pronunciation.replace("-","")
            syllables_ipa = [x for x in pronunciation.split("-") if x!= '']

            if self.language == 'french':
                if spelling[-1] == 'e' and len(syllables) == len(syllables_ipa)+1 and len(syllables) >= 2:
                    syllables = syllables[:-2]+[syllables[-2]+syllables[-1]]

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

    def post_all_words(self):
        for word in self.pronunciations:
            self.post_word_to_db(word)
        
    def get_all_syllables(self):
        """
        Args:
            self
        Return:
            Dictionary of all the phonetical syllables found in the word collection
            of a specific language. The values are a dictionary of orthographical 
            syllabes as keys and occurences as values. 
        """
        try:
            r = requests.get(self.all_words_route)
        except requests.exceptions.RequestException as e:
            print("Error with the request:")
            print(e)
        dico = json.loads(r.content)
        result = dico['result']
        all_syllables_ipa = collections.defaultdict(lambda: collections.defaultdict(int))
        counter = 0
        else_counter = 0
        else_words = {}
        for word in result:
            word_syllables_ipa = word['syllables_ipa']
            word_syllables = word['syllables']
            if len(word_syllables) != len(word_syllables_ipa):
                else_counter += 1
                # spelling = word['spelling']
                # else_words[spelling] = word
                # to get the words for which the number of syllables and syllables_ipa is different 
            else:    
                for i in range(len(word_syllables)):
                    syllable_ipa = word_syllables_ipa[i]
                    syllable = word_syllables[i]
                    all_syllables_ipa[syllable_ipa][syllable] += 1
                counter +=1
        print("Words with different number of phonetical and orhtographical syllables (not processed): {}".format(else_counter))
        print("Words with same number of phonetical and orhtographical syllables (processed): {}".format(counter))
        self.all_syllables_ipa = all_syllables_ipa

    def get_max_syllables(self):
        """
        Args:
            Self
            all_syllables_ipa : output of get_all_syllables()
        Returns:
            Dictionary of all the phonetical syllables found in the word collection
            of a specific language. The values are the orthographical 
            syllabe with maximum occurences for each phonetical syllable.
        """
        self.max_syllables = self.all_syllables_ipa
        for ipa_syllable in self.max_syllables:
            orth_syllables = self.max_syllables[ipa_syllable]
            max_orth_syllable = max(orth_syllables, key=orth_syllables.get)
            self.all_syllables_ipa[ipa_syllable] = max_orth_syllable

    def post_syllable_to_db(self, ipa_syllable):
        """
        Function to post one syllable to the collection of syllables for one specific language
        Args:
            ipa_syllable (str): the phonetical writing of the syllable
        """
        orthographical_syllable = self.max_syllables[ipa_syllable]
        preceding_syllable = "" #to do: similar to get_max_syllables()
        following_sylable = "" #to do: similar to get_max_syllables()
        payload = {
            "ipa_syllable": ipa_syllable,
            "orthographical_syllable": orthographical_syllable,
            "preceding_syllable": preceding_syllable,
            "following_syllable": following_sylable
            }
        response = requests.post(f"{self.url}/{self.language}_syllables/", headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        logging.info(response.text)

    def post_all_syllables(self):
        """
        Function that posts all the processed syllables to the collection of syllables for a specific language
        Args:
            Self
            syllables_to_post: Dictionary of the syllables that we want to post to our collection
            usually the output of get_all_syllables()
        """
        for ipa_syllable in self.all_syllables_ipa:
            # the 2 latters are empty for the moment
            print("sending the syllable: {}".format(ipa_syllable))
            self.post_syllable_to_db(ipa_syllable)