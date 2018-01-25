from flask import Flask, request, jsonify, make_response, render_template, Response, redirect
from flask_pymongo import PyMongo
from Words import *
import json
from json import *
import jinja2

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque' #mettre le nom de la bd
app.config['MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque' #mettre le lien de la db avec username et password
app.config['JSON_AS_ASCII'] = False

mongo = PyMongo(app)


# ------------------ Routes Debug ------------------------ #


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/database', methods=['GET', 'POST'])
def database():
    if request.method == 'POST':
        try:
            result = get_word(request.form['language'],request.form['word'])
            JSON = json.dumps(result)
            word = loads(JSON)
            return render_template('word.html', word=word, mod=False)
        except jinja2.exceptions.UndefinedError:
            render_template('error.html',message="Ce mot n'existe pas dans la base")
    return render_template('database.html')


@app.route('/modify_word', methods=['GET', 'POST'])
def modify():
    if request.method == 'POST':
        # on récupère les champs entrées dans word.html
        item = json.dumps(request.form)
        insert = loads(item)
        # on met en forme
        insert['syllables'] = insert['syllables'].split('.')
        insert['syllables_ipa']=insert['syllables_ipa'].split('.')
        # on se place dans la bonne collection puis on insère
        collection = get_collection(insert['language'])
        collection.insert(insert)
        return render_template('word.html',word=insert,mod=True)
    else:
        return render_template('error.html',message="Impossible d'accéder à cette page"), 404


@app.route('/add_word', methods=['GET', 'POST'])
def new_word():
    if request.method == 'POST':
        item = json.dumps(request.form)
        insert = loads(item)
        # on met en forme
        insert['syllables'] = insert['syllables'].split('.')
        insert['syllables_ipa'] = insert['syllables_ipa'].split('.')
        # on se place dans la bonne collection puis on insère
        collection = get_collection(insert['language'])
        collection.insert(insert)
        return render_template('word.html', word=insert, mod=True)
    else:
        default = {'language':'english', 'spelling':'', 'spelling_ipa':'', 'syllables':[], 'syllables_ipa':[] }
        return render_template('word.html',word=default,mod=False)

@app.route('/all_words/',methods=['POST'])
@app.route('/all_words/<language>/<spelling>/',methods=['GET'])
def all_words(language=None,spelling=None):
    if request.method == "POST":
        url = "/all_words/"+request.form['language']+"/"+request.form['spelling']
        print(url)
        return redirect(url)
    collection = get_collection(language).find()
    words = []
    for word in collection:
        if word['spelling'] == spelling:
            words += [word]
    return render_template('all_words.html',all_words=words)


@app.route('/translitteration/',methods=['POST','GET'])
def translitterate():
    if request.method == 'GET':
        return render_template('translitteration.html',post=False)
    else:
            # on récupère les données de la requête
        spelling = request.form['spelling']
        language1 = request.form['language1']
        language2 = request.form['language2']
        if language1 == language2:
            return render_template('error.html',message='Entrez deux langages différents pour la translittération !')
            # on se place dans les bonnes collections
        coll_word_1 = get_collection(language1)
        coll_syll_1 = get_collection_syllables(language1)
        coll_syll_2 = get_collection_syllables(language2)
            # on récupère la prononciation du mot
        word = coll_word_1.find_one({'spelling':spelling})
        if word is None:
            return render_template('error.html', message="Ce mot n'est pas répertorié !")
        syllables_ipa1 = word['syllables_ipa']

        syllables = []
        syllables_ipa2 = []
        for syll in syllables_ipa1:
            # on cherche la correspondance de chaque syllabe dans la 2eme langue
            syll1 = coll_syll_1.find_one({'spelling_ipa':syll})[language2] #phonetique dans la langue 2
            syllables_ipa2 += [syll1]
            syll2 = coll_syll_2.find_one({'spelling_ipa':syll1, 'language':language2})['spelling'] #orthographique dans la langue 2
            syllables += [syll2]

        return render_template('translitteration.html',post=True,word=spelling,result=syllables,language1=language1,language2=language2,syllables=word['syllables'],syllables_ipa=syllables_ipa1,syllables_ipa2=syllables_ipa2)


# ------------------ Fonctions générales ------------------------ #


def get_collection(language):
    """""
    # on se place dans la collection correspondant à la langue choisie
    if language == 'english':
        collection = mongo.db.english_words
    elif language == 'french':
        collection = mongo.db.french_words
    elif language == 'italian':
        collection = mongo.db.italian_words
    else:
        collection = None
    return collection
    """
    return mongo.db.test_valentin


def get_collection_syllables(language):
    """"
     # on se place dans la collection de syllabes correspondant à la langue choisie
    if language == 'english':
        collection = mongo.db.english_syllables
    elif language == 'french':
        collection = mongo.db.french_syllables
    elif language == 'italian':
        collection = mongo.db.italian_syllables
    else:
        collection = None
    return collection
    """
    return mongo.db.test_valentin


def get_word(language,word):
    # on va selectioner la table selon la langue choisie
    all_words = get_collection(language)
    if word == "":
        output = []
        for word in all_words.find():
            del word['_id']  # the value of this key is an ObjectId which is not JSON serializable
            output.append(word)
    else:
        result = all_words.find_one({'spelling': word})
        if result:
            del result['_id']  # the value of this key is an ObjectId which is not JSON serializable
            output = result
        else:
            output = 'This word is not in our database'
    return output


def delete(language,id):
    return None


# ------------------ Routes API ------------------------ #

"""""
@app.route('/<language>/', defaults={'word': ''}, methods = ['GET']) #pour avoir tous les mots dans une langue
@app.route('/<language>/<path:word>', methods=['GET']) #pour avoir les details d'un mot
def get_all_words(language, word):
    output = get_word(language,word)
    response = jsonify({'result': output})
    return response

@app.route('/<language>_words/', methods=['POST'])
def add_word(language):
    all_words = get_collection(language)
    data = request.get_json()
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
def get_all_syllables(language, ipa_syllable):
    # on va selectionner la table selon la langue choisie
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables

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

@app.route('/<language>_syllables/', methods=['POST'])
def add_syllables(language):
    #to add new sylables
    if language == 'english':
        all_syllables = mongo.db.english_syllables
    elif language == 'french':
        all_syllables = mongo.db.french_syllables
    elif language == 'italian':
        all_syllables = mongo.db.italian_syllables
    data = request.get_json()
    # nettoyer et transformer les donnees client
    if language == data['language']:
        pass
    else:
        raise ValueError('word entered in wrong language')
    ipa_syllable = data['ipa_syllable']
    orthographical_syllable = data['orthographical_syllable']
    preceding_ipa_syllable = data['preceding_syllable']
    following_ipa_syllable = data['following_syllable']
    db_insert = {'ipa_syllable': ipa_syllable, 'orthographical_syllable': orthographical_syllable, 'preceding_ipa_syllable':preceding_ipa_syllable, 'following_ipa_syllable': following_ipa_syllable}
    all_syllables.insert(db_insert)
    return "The syllable {} has been added to the {} syllable database".format(ipa_syllable, language)
"""


if __name__ == '__main__':
    app.run(debug=True)