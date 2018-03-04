from Flask.debug import *
import random

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque'  # mettre le nom de la bd
app.config[
    'MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque'  # mettre le lien de la db avec username et password
app.config['JSON_AS_ASCII'] = False

mongo = PyMongo(app)

# Ici, pour un mot donné, on incrémente les statistiques de ses syllabes adjacentes
# ex : get_statistics('english',["dɑ","kjə","mɛn","təɹ","i"])
def get_statistics(language,word):
    syll_coll = get_collection_syllables(language)
    i = 0
    for syllable in word:

        # récupération de la syllabe dans la BD ou création d'une nouvelle
        syll = syll_coll.find_one({'ipa_syllable':syllable})
        new = False
        if syll is None:
            new = True
            syll = {
                'language' : language,
                'ipa_syllable' : syllable
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
        if i < len(word) - 1:
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
            syll_coll.replace_one({'ipa_syllable':syllable},syll)
        else:
            syll_coll.insert(syll)

        i += 1
    return 'Done'


@app.route('/stats/<language>/')
# Cette fonction permet de calculer toutes les stats sur les syllabes adjacentes dans une langue donnée à l'aide
# de la fonction précédente
def stats(language):
    collection = get_collection(language)
    for word in collection.find():
        try :
            get_statistics(language,word['syllables_ipa'])
        except:
            print('Problème pour le mot ',word['spelling'],word['spelling_ipa'])
    space(language)
    return 'Done'


# inutile ?
def generate(language,spelling):
    collection = get_collection_syllables(language)
    spelling = collection.find_one({'orthographical_syllable':spelling})['ipa_syllable']
    sentence = ""
    pronunciation = ""
    for i in range(10):
        try:
            syll = collection.find_one({'ipa_syllable':spelling})
            sentence += syll['orthographical_syllable'] + "-"
            pronunciation += syll['ipa_syllable']
        except:
            if spelling != " ":
                print('Problème pour la syllabe : ', spelling)
            break
        try:
            spelling = probable(syll['following_ipa_syllable'],pronunciation)
        except:
            break
    return sentence, pronunciation


# Renvoi l'élément de  dic avec le score le plus grand dont la clé ne se trouve pas dans string
# probable({'a': 1, 'b': 2, 'c': 3}, 'cet'} retourne b
def probable(dic, string):
    max = 0
    result = ""
    for syllable in dic.keys():
        if (syllable not in string) and (dic[syllable] > max):
            result = syllable
    return result


# Permet de remettre à 0 toutes les stats sur les syllabes précédentes et suivantes d'une langue
@app.route('/erase_stats/<language>')
def erase_stats(language):
    collection = get_collection_syllables(language)
    for syllable in collection.find():
        syllable['following_ipa_syllable'] = {}
        syllable['preceding_ipa_syllable'] = {}
        collection.replace_one({'_id':syllable['_id']},syllable)


# permet d'ajouter l'espace " " comme une syllabe
def space(language):
    collection = get_collection_syllables(language)
    begin = {}
    end = {}
    for doc in collection.find():
        try :
            if " " in doc['preceding_ipa_syllable'].keys():
                begin[doc['ipa_syllable']] = doc['preceding_ipa_syllable'][" "]
            if " " in doc['following_ipa_syllable'].keys():
                end[doc['ipa_syllable']] = doc['following_ipa_syllable'][" "]
        except Exception:
            print("La syllabe ",doc['orthographical_syllable']," présente un problème")
    collection.insert({
        'language' : language,
        'orthographical_syllable': " ",
        'ipa_syllable': " ",
        'preceding_ipa_syllable': end,
        'following_ipa_syllable': begin
    })


# permet de générer une suite pseudo-aléatoire de mots en donnant la première syllabe
# ici une même syllabe ne peut pas être utilisée 2 fois
@app.route('/generate_sentence/<language>/<first>')
def generate_all_different_down(language,first):
    collection = get_collection_syllables(language)
    current = collection.find_one({'orthographical_syllable': first})['ipa_syllable']
    sentence = ""
    pronunciation = ""
    used = []
    for i in range(30):
        try:
            syll = collection.find_one({'ipa_syllable': current})
            sentence += syll['orthographical_syllable'] + "-"
            pronunciation += syll['ipa_syllable']
        except:
            if current != " ":
                print('Problème pour la syllabe : ', current)
            break
        try:
            current = possible(syll['following_ipa_syllable'], used)
            if current != " ":
                used += [current]
        except:
            break
    print(sentence)
    print(sentence.replace('-',''))
    print(pronunciation)
    print(used)
    return sentence


# Retourne une syllabe possible parmi les syllabes de following, mais omet celles de used :
# possible({'mon': 1, 'ton' : 4, 'son': 3, 'tan': 2}, ['mon','ton']) retourne 'son' avec une probabilité de 0.6 et
# 'tan' avec une probabilité de 0.4
def possible(following, used):
    possibilities = []
    for key in following.keys():
        if key not in used:
            for i in range(following[key]):
                possibilities += [key]
    number = random.randint(0,len(possibilities)-1)
    return possibilities[number]


if __name__ == '__main__':
    app.run(debug=True)
