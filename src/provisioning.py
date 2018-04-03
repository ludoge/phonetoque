import json
import logging
import pyphen
import requests
import collections
from src.sound_distance import SoundDistance


class PhonetoqueRequest(object):
    """
    Prepares and posts pronunciation data to the REST API defined in configuration
    """

    def __init__(self, config):
        self.language = config['language']
        self.other_languages = [language for language in config['scraper_languages'] if language != self.language]
        self.hyphenation_dict = pyphen.Pyphen(lang=config['hyphenation_dict'])
        # self.ipa_hyphenation_dict = pyphen.Pyphen(lang=config['ipa_hyphenation_dict'])
        self.url = config['server_url']
        self.pronunciations = {}
        self.all_words_route = self.url + "/" + self.language
        self.all_syllables_route = self.url + "/" + self.language + "_syllables"
        self.all_syllables_ipa = {}
        self.sound_distance = SoundDistance()

    def prepare_data(self):
        """
        Syllabifies words and pronunciations
        :return:
        """
        self.pronunciations = {self.hyphenation_dict.inserted(k.replace(' ', '-')).strip():
                               # [self.ipa_hyphenation_dict.inserted(x).strip() for x in v]
                                   v
                               for k, v in self.pronunciations.items()}

    def get_ipa_syllabification(self, word):
        """
        Obsolete
        """
        # syllabed_word = self.ipa_hyphenation_dict.inserted(word)
        return word

    def post_word_to_db(self, word):
        """
        Also contains pre-treatment to get number of phonetic and orthographic syllables
        :param word:
        :return:
        """
        for pronunciation in self.pronunciations[word]:
            spelling = word.replace("-", "").lower()
            syllables = [x.lower() for x in word.split("-") if x != '']
            spelling_ipa = pronunciation.replace("-", "")
            syllables_ipa = [x for x in pronunciation.split("-") if x != '']

            if len(spelling) > 2 and (
                            len(syllables[0]) > 2 or len(syllables) < len(
                        syllables_ipa)) and len(syllables_ipa[0])==1:  # initial vowel is often a syllable by itself
                if len(syllables[0]) > len(syllables_ipa[0]):
                    if spelling[0] in 'aeiou' and spelling[1] in 'aeiouy' and len(syllables) <= len(syllables_ipa):
                        syllables = [syllables[0][:2], syllables[0][2:]] + syllables[2:]
                    elif spelling[0] in 'aeiou' and len(syllables) <= len(syllables_ipa):
                        syllables = [syllables[0][0], syllables[0][1:]] + syllables[1:]

            if 'e' in spelling and self.language == 'french' and len(syllables) > len(syllables_ipa) and len(
                    syllables) >= 2:
                syll = []
                for i in range(len(syllables)):
                    if syllables[i][-1] == 'e' and i >= 1:
                        previous_syll = syll[-1]
                        syll = syll[:-1]
                        syll.append(previous_syll + syllables[i])
                    else:
                        syll.append(syllables[i])
                syllables = syll

            # if the specific fixes above fail, map phonetic syllabification onto orthographical one
            if (len(spelling) == len(spelling_ipa) or len(spelling) == len(spelling_ipa) + 1) and len(syllables) != len(
                    syllables_ipa):
                lengths = [len(x) for x in syllables_ipa]
                sts = spelling[:]
                syllables = []
                while lengths:
                    syllables += [sts[:lengths[0]]]
                    sts = sts[lengths[0]:]
                    lengths = lengths[1:]

            if '' in syllables:
                syllables.remove('')

            # removes double consonants from syllable ends, except for Italian, and handling "cc" exceptions

            if self.language not in ['italian', 'finnish']:
                for i in range(len(syllables) - 1):
                    if ((syllables[i][-1] == syllables[i + 1][0]) or (
                            syllables[i][-1] == 'c' and syllables[i + 1][0] == 'q')) and len(syllables[i]) > 0:
                        if len(syllables_ipa) > i: #sanity check
                            if not (syllables_ipa[i][-1] == 'k' and syllables_ipa[i + 1][0] == 's'):  # cc
                                if not syllables[i][-1] in 'aeiou': # Aaron !
                                    syllables[i] = syllables[i][:-1]

            if '' in syllables:
                syllables.remove('')

            print(syllables_ipa)
            print(syllables)

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
        """
        Self-explanatory
        :return:
        """
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
                counter += 1
        print("Words with different number of phonetical and orhtographical syllables (not processed): {}".format(
            else_counter))
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
        max_syllables = self.all_syllables_ipa
        for ipa_syllable in max_syllables:
            orth_syllables = max_syllables[ipa_syllable]
            max_orth_syllable = max(orth_syllables, key=orth_syllables.get)
            self.all_syllables_ipa[ipa_syllable] = max_orth_syllable

    def get_similar_syllables(self):
        """
        /!\ this also patches, not just gets
        :return:
        """
        req = requests.get(self.all_syllables_route)
        dico = json.loads(req.content)
        language_syllables = dico['result']
        for language in self.other_languages:
            other_language_syllables_routes = self.url + "/" + language + "_syllables/"
            try:
                r = requests.get(other_language_syllables_routes)
                dico = json.loads(r.content)
                other_language_syllables = dico['result']
            except requests.exceptions.RequestException as e:
                print("Error with the request:")
                print(e)
                other_language_syllables = []
            for syllable in language_syllables:
                score = 0
                payload = {}
                for other_syllable in other_language_syllables:
                    new_score = self.sound_distance.syllable_similarity(syllable['ipa_syllable'],
                                                                        other_syllable['ipa_syllable'])
                    # print(new_score)
                    if new_score > score and new_score > 0:
                        score = round(new_score, 3)
                        payload = {language: other_syllable['ipa_syllable'], f"{language}_score": score}
                if score > 0:
                    response = requests.patch(f"{self.url}/{self.language}_syllables/{syllable['ipa_syllable']}",
                                              headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                print(syllable['ipa_syllable'], payload)

    def post_syllable_to_db(self, ipa_syllable):
        """
        Function to post one syllable to the collection of syllables for one specific language
        Args:
            ipa_syllable (str): the phonetical writing of the syllable
        """
        orthographical_syllable = self.all_syllables_ipa[ipa_syllable]
        preceding_syllable = ""  # to do: similar to get_max_syllables()
        following_sylable = ""  # to do: similar to get_max_syllables()
        payload = {
            "ipa_syllable": ipa_syllable,
            "orthographical_syllable": orthographical_syllable,
            "preceding_syllable": preceding_syllable,
            "following_syllable": following_sylable
        }
        response = requests.post(f"{self.url}/{self.language}_syllables/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(payload))
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
