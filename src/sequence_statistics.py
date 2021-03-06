import requests
import random
import json
from scripts import *

API_URL = 'http://127.0.0.1:5001'
#API_URL = 'http://api:5000'


# -------------- Filling DB with info on preceding and following syllables ------------------------- #

def stats(language):
    """
    Here we gather all the info on previous and following syllables for a given language
    """
    bool1 = erase_stats(language)
    try:
        collection = requests.get(f'{API_URL}/{language}/').json()
    except requests.ConnectionError:
        return False
    for word in collection["result"]:
        try :
            get_statistics(language,word)
        except:
            pass
    bool2 = space(language) # we add the character " " as a syllable to deal with words' endings and beginnings
    return (bool1 and bool2)


def get_statistics(language,word):
    """
    Here, for a given word, we add for each of its syllables info of near syllables to the DB
    """
    syllables = word['syllables_ipa']
    length = len(syllables)

    i = 0 # we add info for each i-th ipa syllable of the word
    for syllable in syllables:
        # we have syllable = syllables[i]

        # we get the syllable in the database or create a new one if it does not exist
        try:
            syll = requests.get(f'{API_URL}/{language}_syllables/{syllable}').json()['result']
        except requests.ConnectionError:
            continue
        new = False
        if isinstance(syll,str):  # aka if the get return an error message
            new = True
            try :
                ortho = word['syllables'][i]
            except (KeyError,IndexError):
                ortho = ""
            syll = {
                'language': language,
                'ipa_syllable': syllable,
                'orthographical_syllable': ortho,
                'preceding_ipa_syllable': {},
                'following_ipa_syllable': {}
            }

        # we add info about the previous syllable
        if i > 0:
            previous = syllables[i-1]
        else:
            previous = " "
        try:
            syll['preceding_ipa_syllable'] = increment(syll['preceding_ipa_syllable'],previous)
        except KeyError:
            syll['preceding_ipa_syllable'] = { previous : 1 }

        # we add info about the next syllable
        if i < length - 1:
            next = syllables[i+1]
        else:
            next = " "
        try:
            syll['following_ipa_syllable'] = increment(syll['following_ipa_syllable'], next)
        except KeyError:
            syll['following_ipa_syllable'] = {next: 1}

        # we update the database
        if not new:
            requests.patch(f"{API_URL}/{language}_syllables/{syllable}", headers={'Content-Type': 'application/json'},
                           data=json.dumps(syll))
        else:
            requests.post(f"{API_URL}/{language}_syllables/", headers={'Content-Type': 'application/json'},
                          data=json.dumps(syll))

        i += 1


def erase_stats(language):
    """
    Erases all info on previous and next syllables in a whole language
    Indeed, if we use stats without it, we double every count of syllables already made
    """
    try:
        collection = requests.get(f'{API_URL}/{language}_syllables/').json()
    except requests.ConnectionError:
        return False
    for syllable in collection["result"]:
        ipa = syllable['ipa_syllable']
        syllable['following_ipa_syllable'] = {}
        syllable['preceding_ipa_syllable'] = {}
        requests.patch(f"{API_URL}/{language}_syllables/{ipa}", headers={'Content-Type': 'application/json'},
                       data=json.dumps(syllable))
    return True


def space(language):
    """
    Adds the character " " as a syllable to deal with words' ending and beginnings
    """
    begin = {}
    end = {}
    try:
        collection = requests.get(f'{API_URL}/{language}_syllables/').json()
    except requests.ConnectionError:
        return False
    for doc in collection["result"]:
        try :
            if " " in doc['preceding_ipa_syllable'].keys():
                begin[doc['ipa_syllable']] = doc['preceding_ipa_syllable'][" "]
            if " " in doc['following_ipa_syllable'].keys():
                end[doc['ipa_syllable']] = doc['following_ipa_syllable'][" "]
        except Exception:
            pass
    insert = {
        'language': language,
        'orthographical_syllable': "espace", # to retrieve the doc we need a name, may be changed in the future
        'ipa_syllable': " ",
        'preceding_ipa_syllable': end,
        'following_ipa_syllable': begin
    }
    requests.post(f"{API_URL}/{language}_syllables/", headers={'Content-Type': 'application/json'}, data=json.dumps(insert))
    return True


# -------------- Generation of random words ------------------------- #


def generate_new_down(language,length=10):
    """
    generate : Creates a pseudo-random sequence of words
    new : A word cannot appear twice
    down : we start with the first syllable, retrieve the next with "following_ipa_syllable" etc...
    :param length: number of words in the final sequence
    :return: (string of words), (pronunciation of the sequence)
    """
    space = requests.get(f'{API_URL}/{language}_syllables/espace/orthographic').json()['result']
    current = possible(space['following_ipa_syllable'])
    sentence = ""
    pronunciation = ""
    words = []
    i = 0
    while i < length:
        word = ""
        word_pronunciation = ""
        while current != " ":
            try:
                syll = requests.get(f'{API_URL}/{language}_syllables/{current}').json()['result']
                word += syll['orthographical_syllable'] + "-"
                word_pronunciation += syll['ipa_syllable']
                current = possible(syll['following_ipa_syllable'])
            except (KeyError, TypeError):
                current = " "
        if word not in words:
            # on ne vérifie l'existence d'un mot que si celui-ci est long
            if len(word_pronunciation) > 3:
                existence = requests.get(f'{API_URL}/{language}/{word_pronunciation}/phonetic').json()['result']
                if existence == []:
                    words += word
                    sentence += word + " "
                    pronunciation += word_pronunciation + " "
                    current = possible(space['following_ipa_syllable'])
                    i += 1
                else:
                    current = possible(space['following_ipa_syllable'])
            else:
                words += word
                sentence += word + " "
                pronunciation += word_pronunciation + " "
                current = possible(space['following_ipa_syllable'])
                i += 1
    return sentence.replace('-',''), pronunciation


def generate_new_up(language,length=10):
    """
    generate : Creates a pseudo-random sequence of words
    new : A word cannot appear twice
    up : we start with the last syllable, retrieve the previous with "preceding_ipa_syllable" etc...
    :param length: number of words in the final sequence
    :return: (string of words), (pronunciation of the sequence)
    """
    space = requests.get(f'{API_URL}/{language}_syllables/espace/orthographic').json()['result']
    current = possible(space['preceding_ipa_syllable'])
    sentence = ""
    pronunciation = ""
    words = [""]
    i = 0
    while i < length:
        word = ""
        word_pronunciation = ""
        while current != " ":
            try:
                syll = requests.get(f'{API_URL}/{language}_syllables/{current}').json()['result']
                word = syll['orthographical_syllable'] + "-" + word
                word_pronunciation = syll['ipa_syllable'] + word_pronunciation
                current = possible(syll['preceding_ipa_syllable'])
            except (KeyError, AttributeError):
                current = " "
        if word not in words:
            # on ne vérifie l'existence d'un mot que si celui-ci est long
            if len(word_pronunciation) > 3:
                existence = requests.get(f'{API_URL}/{language}/{word_pronunciation}/phonetic').json()['result']
                if existence == []:
                    words += word
                    sentence = word + " " + sentence
                    pronunciation = word_pronunciation + " " + pronunciation
                    current = possible(space['preceding_ipa_syllable'])
                    i += 1
                else:
                    current = possible(space['preceding_ipa_syllable'])
            else:
                words += word
                sentence = word + " " + sentence
                pronunciation = word_pronunciation + " " + pronunciation
                current = possible(space['preceding_ipa_syllable'])
                i += 1
    return sentence.replace('-',''), pronunciation


def generate_sentence(language,lengths):
    """
        Creates a sentence following the pattern of number of letters in the list "lengths"
        ex : generate_sentence('french',[8, 3, 7, 7, 3, 8, 8, 2]) : a French word of 8 letters, then 3...
        :return: string
    """
    words = generate_new_up(language, 10*len(lengths))
    possible_words = words[0].split()
    pronunciations = words[1].split()
    sentence = ""
    phonetic_sentence = ""
    for i in lengths:
        ok = False
        while not ok:
            for word in possible_words:
                if len(word) == i and word not in sentence:
                    index = possible_words.index(word)
                    sentence += word + " "
                    phonetic_sentence += pronunciations[index] + " "
                    ok = True
                    break
            if not ok:
                new_words = generate_new_up(language, 10*len(lengths))
                possible_words += new_words[0].split()
                pronunciations += new_words[1].split()
    sentence += "."
    return sentence, phonetic_sentence


# -------------- Auxiliary functions ------------------------- #

def increment(dic, key):
    """
    Adds one to the field "key" of the dictionary "dic"
    Deals with any typing problem of "dic" or "dic[key]"
    :return: dictionary
    """
    if isinstance(dic, dict):
        if key in dic.keys():
            if isinstance(dic[key], int):
                dic[key] += 1
            else:
                dic[key] = 1
        else:
            dic[key] = 1
    else:
        dic = {key: 1}
    return dic


def possible(following, used=[]):
    """
    Gives a possible syllable among the dictionary "following", without using the keys in the list "used"
    possible({'mon': 1, 'ton' : 4, 'son': 3, 'tan': 2}, ['mon','ton']) returns 'son' with a probability of 0.6 and
    'tan' with a probability of 0.4
    """
    possibilities = []
    for key in following.keys():
        if key not in used:
            for i in range(following[key]):
                possibilities += [key]
    number = random.randint(0,len(possibilities)-1)
    return possibilities[number]


def probable(dic, string=""):
    """
    Gives the element of "dic" with the biggest score whose key is not in "string"
    probable({'a': 1, 'b': 2, 'c': 3}, 'cet'} returns b
    """
    max = 0
    result = ""
    for syllable in dic.keys():
        if (syllable not in string) and (dic[syllable] > max):
            result = syllable
    return result


if __name__ == '__main__':
    #print(requests.get(f'{API_URL}/french/ʒənu/phonetic').json()['result'])
    #print(generate_new_up('french'))
    #generate_new_down('french')
    print(generate_sentence('english', [ 1, 5, 5, 8, 6, 2, 3, 6, 6]))
