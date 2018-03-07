import requests
import random
import json


# API_URL = 'http://0.0.0.0:5000'
API_URL = 'http://127.0.0.1:5001'


# -------------- Fonctions pour calculer les stats sur les syllabes ------------------------- #


# Ici, pour un mot donné, on incrémente les statistiques de ses syllabes adjacentes
def get_statistics(language,word):
    i = 0
    length = len(word['syllables_ipa'])
    for syllable in word['syllables_ipa']:

        # récupération de la syllabe dans la BD ou création d'une nouvelle
        syll = requests.get(f'{API_URL}/{language}_syllables/{syllable}').json()['result']
        new = False
        if type(syll) is str:
            new = True
            try :
                ortho = word['syllables'][i]
            except (KeyError,IndexError):
                ortho = ""
            syll = {
                'language' : language,
                'ipa_syllable' : syllable,
                'orthographical_syllable' : ortho,
                'preceding_ipa_syllable' : {},
                'following_ipa_syllable' : {}
            }

        # ajout de la syllabe précédente dans les statistiques
        if i > 0:
            previous = word[i-1]
        else:
            previous = " "
        try:
            syll['preceding_ipa_syllable'][previous] += 1
        except KeyError:
            syll['preceding_ipa_syllable'][previous] = 1
        except TypeError:
            syll['preceding_ipa_syllable'] = {previous : 1}

        # ajout de la syllabe suivante dans les statistiques
        if i < length - 1:
            next = word[i+1]
        else:
            next = " "
        try:
            syll['following_ipa_syllable'][next] += 1
        except KeyError:
            syll['following_ipa_syllable'][next] = 1
        except TypeError:
            syll['following_ipa_syllable'] = {next : 1}

        # mettre à jour dans la DB
        if not new:
            requests.patch(f"{API_URL}/{language}_syllables/{syllable}", headers={'Content-Type': 'application/json'},
                           data=json.dumps(syll))
            print('syllabe modifiée : ',syll)
        else:
            requests.post(f"{API_URL}/{language}_syllables/", headers={'Content-Type': 'application/json'},
                          data=json.dumps(syll))
            print('syllabe ajoutée : ', syll)

        i += 1

    return 'Done'


# Cette fonction permet de calculer toutes les stats sur les syllabes adjacentes dans une langue donnée à l'aide
# de la fonction précédente
def stats(language):
    erase_stats(language)
    i = 0
    for word in requests.get(f'{API_URL}/{language}/').json()["result"]:
        if i == 40 :
            break
        else:
            i += 1
        try :
            get_statistics(language,word)
        except:
            print('Problème pour le mot ',word['spelling'],word['spelling_ipa'])
    space(language)
    return 'Done'


# Permet de remettre à 0 toutes les stats sur les syllabes précédentes et suivantes d'une langue
def erase_stats(language):
    for syllable in requests.get(f'{API_URL}/{language}_syllables/').json()["result"]:
        ipa = syllable['ipa_syllable']
        syllable['following_ipa_syllable'] = {}
        syllable['preceding_ipa_syllable'] = {}
        requests.patch(f"{API_URL}/{language}_syllables/{ipa}", headers={'Content-Type': 'application/json'},
                       data=json.dumps(syllable))


# permet d'ajouter l'espace " " comme une syllabe
def space(language):
    begin = {}
    end = {}
    for doc in requests.get(f'{API_URL}/{language}_syllables/').json()["result"]:
        try :
            if " " in doc['preceding_ipa_syllable'].keys():
                begin[doc['ipa_syllable']] = doc['preceding_ipa_syllable'][" "]
            if " " in doc['following_ipa_syllable'].keys():
                end[doc['ipa_syllable']] = doc['following_ipa_syllable'][" "]
        except Exception:
            print("La syllabe ",doc['orthographical_syllable']," présente un problème")
    insert = {
        'language': language,
        'orthographical_syllable': "espace",
        'ipa_syllable': " ",
        'preceding_ipa_syllable': end,
        'following_ipa_syllable': begin
    }
    requests.post(f"{API_URL}/{language}_syllables/", headers={'Content-Type': 'application/json'}, data=json.dumps(insert))


# -------------- Fonctions pour générer des mots aléatoires ------------------------- #


# permet de générer une suite pseudo-aléatoire de mots en donnant la première syllabe
# les mots déjà existants sont supprimés
def generate_new_down(language,length=10):
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
            except KeyError:
                print('Problème pour la syllabe : ', current)
                current = " "
        if word not in words:
            existence = requests.get(f'{API_URL}/{language}/{word_pronunciation}/phonetic').json()['result']
            if existence == []:
                words += word
                sentence += word + " "
                pronunciation += word_pronunciation + " "
                current = possible(space['following_ipa_syllable'])
                i += 1
            else:
                print('Mot ', existence[0]['spelling'],' (', word_pronunciation, ') retrouvé')
                current = possible(space['following_ipa_syllable'])
    print(sentence)
    print(sentence.replace('-',''))
    print(pronunciation)
    return sentence


def generate_new_up(language,length=10):
    space = requests.get(f'{API_URL}/{language}_syllables/espace/orthographic').json()['result']
    current = possible(space['preceding_ipa_syllable'])
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
                word = syll['orthographical_syllable'] + "-" + word
                word_pronunciation = syll['ipa_syllable'] + word_pronunciation
                current = possible(syll['preceding_ipa_syllable'])
            except KeyError:
                print('Problème pour la syllabe : ', current)
                current = " "
        if word not in words:
            existence = requests.get(f'{API_URL}/{language}/{word_pronunciation}/phonetic').json()['result']
            if existence == []:
                words += word
                sentence = word + " " + sentence
                pronunciation = word_pronunciation + " " + pronunciation
                current = possible(space['preceding_ipa_syllable'])
                i += 1
            else:
                print('Mot ', existence[0]['spelling'],' (', word_pronunciation, ') retrouvé')
                current = possible(space['preceding_ipa_syllable'])
    print(sentence)
    print(sentence.replace('-',''))
    print(pronunciation)
    return sentence


# Retourne une syllabe possible parmi les syllabes de following, mais omet celles de used :
# possible({'mon': 1, 'ton' : 4, 'son': 3, 'tan': 2}, ['mon','ton']) retourne 'son' avec une probabilité de 0.6 et
# 'tan' avec une probabilité de 0.4
def possible(following, used=[]):
    possibilities = []
    for key in following.keys():
        if key not in used:
            for i in range(following[key]):
                possibilities += [key]
    number = random.randint(0,len(possibilities)-1)
    return possibilities[number]


# Renvoie l'élément de  dic avec le score le plus grand dont la clé ne se trouve pas dans string
# probable({'a': 1, 'b': 2, 'c': 3}, 'cet'} retourne b
def probable(dic, string=""):
    max = 0
    result = ""
    for syllable in dic.keys():
        if (syllable not in string) and (dic[syllable] > max):
            result = syllable
    return result


if __name__ == '__main__':
    #print(requests.get(f'{API_URL}/french/ʒənu/phonetic').json()['result'])
    generate_new_up('french')
    generate_new_down('french')
