from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque' #mettre le nom de la bd
app.config['MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque' #mettre le lien de la db avec username et password
app.config['JSON_AS_ASCII'] = False

mongo = PyMongo(app)

@app.route('/', methods = ['GET']) #pour avoir tous les mots dans une langue
def default_route():
    return("Welcome to Phonetoque API !")

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
    result = all_words.find_one({'_id': ObjectId(id)})
    all_words.delete_one({"_id":ObjectId(id)})
    return f"Object {id} deleted"

@app.route('/<language>/', defaults={'word': ''}, methods = ['GET']) #pour avoir tous les mots dans une langue
@app.route('/<language>/<path:word>', methods=['GET']) #pour avoir les details d'un mot
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
            output = 'This word is not in our database'
        return dumps({'result': output})
    elif request.method == "PATCH":
        data = request.get_json()
        all_words.update({"spelling": word}, {'$set': data})
        return "A new attribute {} has been added to the syllable {}".format(data, word)

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
@app.route('/<language>_syllables/<path:ipa_syllable>', methods=['GET']) #pour avoir des details sur une syllabe
@app.route('/<language>_syllables/<path:ipa_syllable>', methods=['PATCH']) #pour rajouter des attributs en plus sur une syllabe
def get_all_syllables(language, ipa_syllable):
    # on va selectionner la table selon la langue choisie
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables
    if request.method == "GET":
        if ipa_syllable == "":
            output = []
            result = all_syllables.find()
            for syllable in result:
                del syllable['_id'] #the value of this key is an ObjectId which is not JSON serializable
                output.append(syllable)
            return jsonify({'result': output})
        else:
            result = all_syllables.find_one({'ipa_syllable' : ipa_syllable})
            if result:
                del result['_id'] #the value of this key is an ObjectId which is not JSON serializable
                output = result
            else:
                output = 'This syllable is not in our database'
            return jsonify({'result': output})
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
    return jsonify({'result': output})


@app.route('/<language>_syllables/', methods=['POST'])
def add_syllables(language):
    """
    to add new sylables
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
    preceding_ipa_syllable = data['preceding_syllable']
    following_ipa_syllable = data['following_syllable']
    db_insert = {'ipa_syllable': ipa_syllable, 'orthographical_syllable': orthographical_syllable, 'preceding_ipa_syllable':preceding_ipa_syllable, 'following_ipa_syllable': following_ipa_syllable}
    all_syllables.insert(db_insert)
    return "The syllable {} has been added to the {} syllable database".format(ipa_syllable, language)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
    #app.run(debug=True, host='0.0.0.0')
