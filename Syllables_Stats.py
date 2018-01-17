import requests
import json

api_url = 'http://127.0.0.1:5000'

class Syllables:
    def __init__(self, language):
        self.language = language
        self.all_words_route = api_url + "/" + self.language

    def get_all_syllables(self):
        r = requests.get(self.all_words_route)
        dico = json.loads(r.content)
        result = dico['result']
        all_syllables_ipa = {}
        counter = 0
        else_counter = 0
        else_words = {}
        for word in result:
            word_syllables_ipa = word['syllables_ipa']
            word_syllables = word['syllables']
            if len(word_syllables) == len(word_syllables_ipa):
                for i in range(0, len(word_syllables)-1):
                    syllable_ipa = word_syllables_ipa[i]
                    syllable = word_syllables[i]
                    try:
                        all_syllables_ipa[syllable_ipa]
                    except KeyError:
                        all_syllables_ipa[syllable_ipa] = {}
                    try:
                        all_syllables_ipa[syllable_ipa][syllable] += 1
                    except KeyError:
                        all_syllables_ipa[syllable_ipa][syllable] = 1
                counter +=1
            else:
                else_counter += 1
                # spelling = word['spelling']
                # else_words[spelling] = word
                # to get the words for which the number of syllables and syllables_ipa is different 
        return all_syllables_ipa

    def get_max_syllables(self):
        all_syllables_ipa = self.get_all_syllables()
        for ipa_syllable in all_syllables_ipa:
            orth_syllables = all_syllables_ipa[ipa_syllable]
            max_orth_syllable = max(orth_syllables, key=orth_syllables.get)
            all_syllables_ipa[ipa_syllable] = max_orth_syllable
        return all_syllables_ipa

    def post_syllable(self, ipa_syllable, orth_syllable, preceding_syllable = "", following_sylable = ""):
        payload = {
                "ipa_syllable": ipa_syllable,
                "orthographical_syllable": orth_syllable,
                "preceding_syllable": preceding_syllable,
                "following_syllable": following_sylable
            }
        response = requests.post(f"{api_url}/{self.language}_syllables/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(payload))
        print(response.text)

    def post_all_syllables(self):
        all_syllables_ipa = self.get_max_syllables()
        for syllable in all_syllables_ipa:
            ipa_syllable = syllable
            orth_syllable = all_syllables_ipa[ipa_syllable]
            preceding_syllable = ""
            following_syllable = ""
            # the 2 latters are empty for the moment
            print("sending the syllable: {}".format(ipa_syllable))
            self.post_syllable(ipa_syllable, orth_syllable, preceding_syllable, following_syllable)


b = Syllables('english')
b.post_all_syllables()

    

    