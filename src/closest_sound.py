import yaml
import requests
import json
import logging
import src.sound_distance as sd

API_URL = 'http://127.0.0.1:5001'

possible_languages = ['french', 'english']


# ______________ Operations on phonems ______________ #

def closest(sound, possible, distance):
    best = -10000
    result = None
    for item in possible:
        score = distance.sound_similarity(sound, item)
        if score > best:
            best = score
            result = item
    return result


def example_of_sound(sound, language, number=4):
    """
    A function that helps to know how to pronounce a phonem
    :param sounds: a phonem
    :return: lists of words where the phonem appears and list of ipa words
    """
    words = requests.get(f"http://127.0.0.1:5001/{language}").json()['result']
    i = 0
    writings = []
    phonetics = []
    for word in words:
        if sound in word['spelling_ipa']:
            writings.append(word['spelling'])
            phonetics.append(word['spelling_ipa'])
            i += 1
            if i >= number:
                break
    return writings, phonetics


# ________________ API interactions ________________ #

def insert_in_db(language, phonem, writing, french=None, english=None, italian=None):
    payload = {
        "language": language,
        "phonem": phonem,
        "writing": writing,
    }
    if french:
        payload['french'] = french
    if english:
        payload['english'] = english
    if italian:
        payload['italian'] = italian
    response = requests.post(f"{API_URL}/phonems/{language}", headers={'Content-Type': 'application/json'},
                             data=json.dumps(payload))
    logging.info(response.text)


def full_sounds(language):
    """
    Fills the database with all the sounds of a language, initializing their writing with "#"
    """
    # First we collect all the words of the language:
    all_words = requests.get(f"{API_URL}/{language}/").json()['result']
    all_phonetics = [word['spelling_ipa'] for word in all_words]
    sounds = []
    with open('soundbank.yml', encoding="utf-8") as file:
        soundbank = file.read().split('\n')
    for sound in soundbank:
        for phonetic in all_phonetics:
            if sound in phonetic:
                sounds.append(sound)
                break
    for sound in sounds:
        db_result = requests.get(f"{API_URL}/phonems/{language}/{sound}").json()['result']
        if isinstance(db_result, str):
            insert = {
                'language': language,
                'phonem': sound,
                'written': '#'
            }
            requests.post(f"{API_URL}/phonems/{language}/", headers={'Content-Type': 'application/json'}, data=json.dumps(insert))


def all_closest(language1,language2):
    """
    Fills the DB of phonem of language 1 with the closest equivalents in language 2
    """
    phonems1 = requests.get(f"{API_URL}/phonems/{language1}/").json()['result']
    phonems2 = requests.get(f"{API_URL}/phonems/{language2}/").json()['result']
    possible_equivalents = [phonem['phonem'] for phonem in phonems2]
    SD = sd.SoundDistance(consonant_conf='consonant_properties.yml', vowel_conf='vowel_properties.yml')
    for item in phonems1:
        phonem = item['phonem']
        best = closest(phonem,possible_equivalents,SD)
        patch = {language2: best}
        requests.patch(f"{API_URL}/phonems/{language1}/{phonem}/", headers={'Content-Type': 'application/json'}, data=json.dumps(patch))


# _______________ Main function ___________________ #

def fill_all_db(languages):
    """
    Fills the database with all you need on phonems except their writing
    The writing will be set with the debug interface
    """
    for language in languages:
        full_sounds(language)
    for language1 in languages:
        for language2 in languages:
            if language1 != language2:
                all_closest(language1,language2)


# ________________ Transliteration ________________ #

def transliterate_roughly(word,language1,language2):
    """
    Only for test, the real function is in the API
    """
    result = ""
    for phonem in word:
        try:
            item = requests.get(f"{API_URL}/phonems/{language1}/{phonem}").json()['result']
            equivalent = item[language2]
            writing = requests.get(f"{API_URL}/phonems/{language2}/{equivalent}").json()['result']['written']
            result += writing
        except ConnectionError:
            logging.info('Erreur de connection')
            continue
        except KeyError:
            logging.info(f"Phonem {phonem} mal renseigné")
        except TypeError:
            logging.info(f"Phonem {phonem} non trouvé dans la base de données")
    return result


if __name__ == '__main__':
    #print(transliterate_roughly('elephant','french','english'))
    fill_all_db(possible_languages)