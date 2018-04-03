from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
import requests
from scipy import stats

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque' #mettre le nom de la bd
app.config['MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque' #mettre le lien de la db avec username et password
app.config['JSON_AS_ASCII'] = False

API_URL = 'http://127.0.0.1:5001'

mongo = PyMongo(app)

@app.route('/', methods = ['GET']) #pour avoir tous les mots dans une langue
def default_route():
    return("Welcome to Phonetoque API !")

@app.route('/translitteration/', methods=['POST','GET'])
def translitterate():
    if request.method == 'GET':
        return dumps({'post': False, 'message':'Essayez avec une methode post !'})
    else:
        # on récupère les données de la requête
        content = request.get_json()
        print(content)
        spelling = content['spelling']
        language1 = content['language1']
        language2 = content['language2']
        if language1 == language2:
            return dumps({'post':False, 'message': u'Entrez deux langages différents pour la translittération !'})
            # on récupère la prononciation du mot
        response = json.loads(get_all_words(language1, spelling))['result']
        if response == []:
            return dumps({'post':False, 'message':u"Ce mot n'est pas répertorié !"})
        word = response[0]
        syllables_ipa1 = word['syllables_ipa']
        syllables = []
        syllables_ipa2 = []
        translitteration_score = []
        print('I saw you', syllables_ipa1)
        for syll in syllables_ipa1:
            try:
                # on cherche la correspondance de chaque syllabe dans la 2eme langue
                response = json.loads(get_all_syllables(language1, syll))['result']
                # response = requests.get(f'{API_URL}/{language1}_syllables/{syll}').json()['result']
                syll1 = response[language2]
                score = response[f'{language2}_score']
                if score < 0.5: # on traite la syllabe autrement si elle n'a pas d'équivalent, score arbitraire
                    raise KeyError
                syllables_ipa2 += [syll1]
                translitteration_score += [score]
                # syll2 = requests.get(f'{API_URL}/{language2}_syllables/{syll1}').json()['result']['orthographical_syllable']
                syll2 = json.loads(get_all_syllables(language2, syll1))['result']['orthographical_syllable']
                syllables += [syll2]
            except (KeyError, TypeError):
                syll1 = ""
                syll2 = ""
                for phonem in syll:
                    try:
                        item = json.loads(get_phonem(language1,phonem))['result']
                        equivalent = item[language2]
                        writing = json.loads(get_phonem(language2,equivalent))['result']['written']
                        syll1 += phonem
                        syll2 += writing
                    except (KeyError, TypeError):
                        continue
                syllables_ipa2 += [syll1]
                syllables += [syll2]
                translitteration_score += [0.001]
        harmonic_mean = int(100*round(stats.hmean(translitteration_score),2))
        return dumps({'post':True, 'spelling': spelling, 'syllables': syllables, 'language1' : language1, 'language2': language2, 'word_syllables':word['syllables'], 'syllables_ipa1': syllables_ipa1, 'syllables_ipa2': syllables_ipa2, 'harmonic_mean': harmonic_mean})    

@app.route('/<language>_id/<id>', methods= ['GET'])
def get_by_id(language, id):
    all_words = None
    language = language.split()[0]
    if language == 'english':
        all_words = mongo.db.english_words
    elif language == 'french':
        all_words = mongo.db.french_words
    elif language == 'italian':
        all_words = mongo.db.italian_words
    result = all_words.find_one({'_id': ObjectId(id)})
    output = ''
    if result:
        output = result
    return dumps({'result': output})

@app.route('/<language>_id/<id>', methods= ['DELETE'])
def del_by_id(language, id):
    all_words = None
    language = language.split()[0]
    if language == 'english':
        all_words = mongo.db.english_words
    elif language == 'french':
        all_words = mongo.db.french_words
    elif language == 'italian':
        all_words = mongo.db.italian_words
    #result = all_words.find_one({'_id': ObjectId(id)})
    all_words.delete_one({"_id":ObjectId(id)})
    all_words.delete_one({"_id": id})
    return f"Object {id} deleted"

@app.route('/<language>/', defaults={'word': ''}, methods = ['GET', 'POST']) #pour avoir tous les mots dans une langue
@app.route('/<language>/<path:word>', methods=['GET', 'POST']) #pour avoir les details d'un mot
@app.route('/<language>/<path:word>', methods=['PATCH']) #pour avoir les details d'un mot
def get_all_words(language, word):
    # on va selectioner la table selon la langue choisie
    all_words = None
    language = language.split()[0]
    if language == 'english':
        all_words = mongo.db.english_words
    elif language == 'french':
        all_words = mongo.db.french_words
    elif language == 'italian':
        all_words = mongo.db.italian_words
    if word == "":
        output = []
        for word in all_words.find():
            del word['_id'] #the value of this key is an ObjectId which is not JSON serializable
            output.append(word)
        return dumps({'result': output})
    elif request.method != "PATCH":
        result = all_words.find({'spelling' : word})#, {'_id': False})
        if result:
            #del result['_id'] #the value of this key is an ObjectId which is not JSON serializable
            output = result
        else:
            output = '~'
        return dumps({'result': output})
    elif request.method == "PATCH":
        data = request.get_json()
        all_words.update({"spelling": word}, {'$set': data})
        return "A new attribute {} has been added to the word {}".format(data, word)


@app.route('/<language>/<path:phonetic>/phonetic', methods=['GET']) # pour avoir les details d'un mot avec son écriture phonétique
@app.route('/<language>/<path:phonetic>/phonetic', methods=['PATCH']) # pour modifier un mot à partir de son écriture phonétique
def get_all_words_by_phonetic(language, phonetic):
    # we select the table according to the given language
    all_words = None
    language = language.split()[0]
    if language == 'english':
        all_words = mongo.db.english_words
    elif language == 'french':
        all_words = mongo.db.french_words
    elif language == 'italian':
        all_words = mongo.db.italian_words
    if phonetic == "":
        output = []
        for word in all_words.find():
            del word['_id']  # the value of this key is an ObjectId which is not JSON serializable
            output.append(word)
        return dumps({'result': output})
    elif request.method != "PATCH":
        result = all_words.find({'spelling_ipa' : phonetic})#, {'_id': False})
        if result:
            # del result['_id']  # the value of this key is an ObjectId which is not JSON serializable
            output = result
        else:
            output = 'This word is not in our database'
        return dumps({'result': output})
    elif request.method == "PATCH":
        data = request.get_json()
        all_words.update({"spelling_ipa": phonetic}, {'$set': data})
        return "A new attribute {} has been added to the phonetic word {}".format(data, phonetic)


@app.route('/<language>_words/', methods=['POST'])
def add_word(language):
    all_words = None
    if language == 'english':
        all_words = mongo.db.english_words
    elif language == 'french':
        all_words = mongo.db.french_words
    elif language == 'italian':
        all_words = mongo.db.italian_words
    data = request.get_json()
    app.logger.critical('test')
    app.logger.error(data)
    # nettoyer et transformer les donnees client
    if language == data['language']:
        pass
    else:
        raise ValueError('word entered in wrong language')
    spelling = data['spelling']
    syllables = data['syllables']
    spelling_ipa = data['spelling_ipa']
    syllables_ipa = data['syllables_ipa']
    db_insert = {'language': language, 'spelling': spelling, 'syllables':syllables, 'spelling_ipa': spelling_ipa, 'syllables_ipa': syllables_ipa}
    all_words.insert(db_insert)
    return "The word {} has been added to the {} database".format(spelling, language)


@app.route('/<language>_syllables/', defaults={'ipa_syllable': ''}, methods = ['GET']) #pour avoir toutes les syllabes dans une langue
@app.route('/<language>_syllables/<path:ipa_syllable>', methods=['GET', 'POST']) #pour avoir des details sur une syllabe
@app.route('/<language>_syllables/<path:ipa_syllable>', methods=['PATCH']) #pour rajouter des attributs en plus sur une syllabe
def get_all_syllables(language, ipa_syllable):
    # on va selectionner la table selon la langue choisie
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables
    if request.method != "PATCH":
        if ipa_syllable == "":
            output = []
            result = all_syllables.find()
            for syllable in result:
                del syllable['_id'] #the value of this key is an ObjectId which is not JSON serializable
                output.append(syllable)
            return dumps({'result': output})
        else:
            result = all_syllables.find_one({'ipa_syllable' : ipa_syllable})
            if result:
                del result['_id'] #the value of this key is an ObjectId which is not JSON serializable
                output = result
            else:
                output = 'This syllable is not in our database'
            return dumps({'result': output})
    elif request.method == "PATCH":
        data = request.get_json()
        all_syllables.update_one({"ipa_syllable": ipa_syllable}, {'$set': data})
        return "A new attribute {} has been added to the syllable {}".format(data, ipa_syllable)


@app.route('/<language>_syllables/<syllable>/orthographic', methods=['GET'])
def get_syllable_orthographic(language, syllable):
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables
    result = all_syllables.find_one({'orthographical_syllable': syllable})
    if result:
        del result['_id']  # the value of this key is an ObjectId which is not JSON serializable
        output = result
    else:
        output = 'This syllable is not in our database'
    return dumps({'result': output})


@app.route('/<language>_syllables/', methods=['POST'])
def add_syllables(language):
    """
    to add new syllables
    """
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables
    data = request.get_json()
    # nettoyer et transformer les donnees client
    # if language == data['language']:
    #     pass
    # else:
    #     raise ValueError('word entered in wrong language')
    ipa_syllable = data['ipa_syllable']
    orthographical_syllable = data['orthographical_syllable']
    try:
        preceding_ipa_syllable = data['preceding_ipa_syllable']
        following_ipa_syllable = data['following_ipa_syllable']
    except KeyError:
        preceding_ipa_syllable = ""
        following_ipa_syllable = ""
    db_insert = {'ipa_syllable': ipa_syllable, 'orthographical_syllable': orthographical_syllable, 'preceding_ipa_syllable':preceding_ipa_syllable, 'following_ipa_syllable': following_ipa_syllable}
    all_syllables.insert(db_insert)
    return "The syllable {} has been added to the {} syllable database".format(ipa_syllable, language)


@app.route('/phonems/<language>/', defaults={'phonem': ''}, methods=['GET', 'POST'])
@app.route('/phonems/<language>/<phonem>/', methods=['GET', 'POST'])
@app.route('/phonems/<language>/<phonem>/', methods=['PATCH'])
def get_phonem(language, phonem):
    # on va selectionner la table selon la langue choisie
    all_phonems = mongo.db.phonems
    if request.method != "PATCH":
        if phonem == "":
            output = []
            result = all_phonems.find({'language':language})
            for phonem in result:
                del phonem['_id'] # the value of this key is an ObjectId which is not JSON serializable
                output.append(phonem)
            return dumps({'result': output})
        else:
            result = all_phonems.find_one({'language': language,'phonem': phonem})
            if result:
                del result['_id']  # the value of this key is an ObjectId which is not JSON serializable
                output = result
            else:
                output = 'This phonem is not in our database'
            return dumps({'result': output})
    elif request.method == "PATCH":
        data = request.get_json()
        all_phonems.update_one({"language":language,"phonem": phonem}, {'$set': data})
        return "A new attribute {} has been added to the phonem {}".format(data, phonem)


@app.route('/phonems/<language>/', methods=['POST'])
def add_phonem(language):
    """
    to add new phonems
    """
    all_phonems = mongo.db.phonems.find({'language':language})
    data = request.get_json()
    phonem = data['phonem']
    written = data['written']
    db_insert = {'language': language, 'phonem': phonem, 'written': written}
    for lang in ['french', 'english', 'italian']:
        try:
            db_insert[lang] = data[lang]
        except KeyError:
            pass
    all_phonems.insert(db_insert)
    return "The phonem {} has been added in {} to the phonem database".format(phonem, language)


if __name__ == '__main__':
    #app.run(debug=True, host='127.0.0.1', port=5001)
    app.run(debug=True, host='0.0.0.0')

