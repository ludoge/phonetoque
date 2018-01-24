from collections import defaultdict
import json
import logging
import requests


api_url = 'http://127.0.0.1:5000'

class Syllables(object):
    """
    This class is used to calculate the correspondance between 
    the phonetical syllables and the orthographical syllables
    in a specific language according to the word database that
    we have for this language.

    TODO:
    Take into account the preceding and following syllables
    """
    def __init__(self, language):
        self.language = language
        self.all_words_route = api_url + "/" + self.language

    def get_all_syllables(self):
        """
        Args:
            self
        Return:
            Dictionary of all the phonetical syllables found in the word collection
            of a specific language. The values are a dictionary of orthographical 
            syllabes as keys and occurences as values. 
        """
        # try:
        r = requests.get(self.all_words_route)
        # except requests.exceptions.RequestException as e:
        #     logging.info("Error with the request:")
        #     logging.info(e)
        dico = json.loads(r.content)
        result = dico['result']
        all_syllables_ipa = defaultdict(lambda: defaultdict(int))
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
        logging.info("Words with different number of phonetical and orhtographical syllables (not processed): {}".format(else_counter))
        logging.info("Words with same number of phonetical and orhtographical syllables (processed): {}".format(counter))
        return all_syllables_ipa

    def get_max_syllables(self):
        """
        Args:
            Self
        Returns:
            Dictionary of all the phonetical syllables found in the word collection
            of a specific language. The values are the orthographical 
            syllabe with maximum occurences for each phonetical syllable.
        """
        all_syllables_ipa = self.get_all_syllables()
        for ipa_syllable in all_syllables_ipa:
            orth_syllables = all_syllables_ipa[ipa_syllable]
            max_orth_syllable = max(orth_syllables, key=orth_syllables.get)
            all_syllables_ipa[ipa_syllable] = max_orth_syllable
        return all_syllables_ipa

    def post_syllable(self, ipa_syllable, orthographical_syllable, preceding_syllable = "", following_sylable = ""):
        """
        Function to post one syllable to the collection of syllables for one specific language
        Args:
            ipa_syllable (str): the phonetical writing of the syllable
            orthographical_syllable (str): the orthographical writing with the most occurences for the phonetical syllable
            preceding_syllable (str): the phonetical syllable that mostly precedes this phonetical syllable
            following_syllable (str): the phonetical syllable that mostly follows this phonetical syllable
        """
        payload = {
                "ipa_syllable": ipa_syllable,
                "orthographical_syllable": orthographical_syllable,
                "preceding_syllable": preceding_syllable,
                "following_syllable": following_sylable
            }
        response = requests.post(f"{api_url}/{self.language}_syllables/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(payload))
        logging.info(response.text)

    def post_all_syllables(self):
        """
        Function that posts all the processed syllables to the collection of syllables for a specific language
        Args:
            Self
        """
        all_syllables_ipa = self.get_max_syllables()
        for syllable in all_syllables_ipa:
            ipa_syllable = syllable
            orth_syllable = all_syllables_ipa[ipa_syllable]
            preceding_syllable = ""
            following_syllable = ""
            # the 2 latters are empty for the moment
            print("sending the syllable: {}".format(ipa_syllable))
            self.post_syllable(ipa_syllable, orth_syllable, preceding_syllable, following_syllable)
    

    