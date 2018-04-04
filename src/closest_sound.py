import yaml
import requests
import json
import logging
import src.sound_distance as sd


API_URL = 'http://127.0.0.1:5001'


# ______________ Operations on phonems ______________ #

def get_all_sounds(soundbank,data,file):
    """
    :param soundbank: List of all existing sounds (i.e. simple phonems)
    :param data: List of words, syllables or sound of the same language
    :return: List of sounds from the soundbank present in the data
    """
    with open(file, 'w') as f:
        for sound in soundbank:
            for item in data:
                if sound in item:
                    f.write(sound+'\n')
                    break


def get_closest_sounds(list1,list2,file):
    SD = sd.SoundDistance()
    with open(file, 'w') as f:
        for sound in list1:
            best = closest(sound, list2, SD)
            f.write(f'{sound} : {best}\n')


def closest(sound, possible, distance):
    best = -10000
    result = None
    for item in possible:
        score = distance.sound_similarity(sound, item)
        if score > best:
            best = score
            result = item
    return result


def print_sounds(sounds,language,number):
    """
    A function that helps to know how to pronounce phonems
    :param sounds: a list of phonems
    :return: lists of words where each phonem appears (only a print)
    """
    for sound in sounds:
        writings, phonetics = example_of_sound(sound,language,number)
        print(f"{sound} : {writings} {phonetics}")


def example_of_sound(sound,language,number=4):
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


# ________________ Transliteration ________________ #

def transliterate_roughly(word,language1,language2):
    """

    :param word:
    :param language1:
    :param language2:
    :return:
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


if __name__ == '__main__':
    print(transliterate_roughly('elephant','french','english'))
