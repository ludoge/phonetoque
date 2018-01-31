from flask import Flask, request, jsonify, make_response, render_template, Response, redirect
from flask_pymongo import PyMongo
import json
from json import *
import jinja2
from bson import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque' #mettre le nom de la bd
app.config['MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque' #mettre le lien de la db avec username et password
app.config['JSON_AS_ASCII'] = False

mongo = PyMongo(app)


# ------------------ Routes Debug ------------------------ #


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/database', methods=['GET'])
def database():
    return render_template('database.html')


@app.route('/modify_word/',methods=['POST'])
@app.route('/modify_word/<language>/<id>/', methods=['GET'])
def modify(language=None,id=None):
    if request.method == 'POST':
        # on récupère les champs entrées dans word.html
        item = json.dumps(request.form)
        insert = loads(item)
        # on met en forme
        insert['syllables'] = insert['syllables'].split('.')
        insert['syllables_ipa']=insert['syllables_ipa'].split('.')
        # on se place dans la bonne collection puis on remplace le mot
        collection = get_collection(insert['language'])
        delete_id(insert['language'],insert['id'])
        collection.insert(insert)
        url = '/all_words/'+insert['language']+'/'+insert['spelling']
        return redirect(url)
    else:
        collection = get_collection(language)
        word = collection.find_one({'_id':ObjectId(id)})
        word['id'] = str(word['_id'])
        return render_template('word.html',word=word,mod=False)


@app.route('/add_word/', methods=['GET', 'POST'])
def new_word():
    if request.method == 'GET':
        default = {'language':'english', 'spelling':'', 'spelling_ipa':'', 'syllables':[], 'syllables_ipa':[] }
        return render_template('word.html',word=default,mod=False)
    else:
        # on récupère les champs entrées dans word.html
        item = json.dumps(request.form)
        insert = loads(item)
        # on met en forme
        insert['syllables'] = insert['syllables'].split('.')
        insert['syllables_ipa'] = insert['syllables_ipa'].split('.')
        # on se place dans la bonne collection puis on insère
        collection = get_collection(insert['language'])
        collection.insert(insert)
        insert['id'] = str(collection.find_one(insert)['_id'])
        return render_template('word.html', word=insert, mod=True)


@app.route('/all_words/',methods=['POST'])
@app.route('/all_words/<language>/<spelling>/',methods=['GET'])
def all_words(language=None,spelling=None):
    if request.method == "POST":
        url = "/all_words/"+request.form['language']+"/"+request.form['spelling']
        return redirect(url)
    collection = get_collection(language).find()
    words = []
    for word in collection:
        if word['spelling'] == spelling:
            word['id'] = str(word['_id'])
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
            return render_template('translitteration.html',post=False,message='Entrez deux langages différents pour la translittération !')
            # on se place dans les bonnes collections
        coll_word_1 = get_collection(language1)
        coll_syll_1 = get_collection_syllables(language1)
        coll_syll_2 = get_collection_syllables(language2)
            # on récupère la prononciation du mot
        word = coll_word_1.find_one({'spelling':spelling})
        if word is None:
            return render_template('translitteration.html',post=False, message="Ce mot n'est pas répertorié !")
        syllables_ipa1 = word['syllables_ipa']

        syllables = []
        syllables_ipa2 = []
        for syll in syllables_ipa1:
            try:
                # on cherche la correspondance de chaque syllabe dans la 2eme langue
                syll1 = coll_syll_1.find_one({'ipa_syllable':syll})[language2] #phonetique dans la langue 2
                syllables_ipa2 += [syll1]
                syll2 = coll_syll_2.find_one({'ipa_syllable':syll1})['orthographical_syllable'] #orthographique dans la langue 2
                syllables += [syll2]
            except KeyError:
                syllables_ipa2 += ["~"]
                syllables += ["~"]
        return render_template('translitteration.html',post=True,word=spelling,result=syllables,language1=language1,language2=language2,syllables=word['syllables'],syllables_ipa=syllables_ipa1,syllables_ipa2=syllables_ipa2)


@app.route('/delete/<language>/<id>/')
def delete(language,id):
    collection = get_collection(language)
    word = collection.find_one({"_id": ObjectId(id)})["spelling"]
    delete_id(language,id)
    url = '/all_words/' + language + '/' + word
    return redirect(url)


# ------------------ Fonctions générales ------------------------ #


def get_collection(language):
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
    #return mongo.db.test_valentin


def get_collection_syllables(language):
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
    #return mongo.db.test_valentin


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
            result['id'] = str(result['_id'])
            del result['_id']  # the value of this key is an ObjectId which is not JSON serializable
            output = result
        else:
            output = 'This word is not in our database'
    return output


def delete_id(language,id):
    collection = get_collection(language)
    collection.delete_one({"_id":ObjectId(id)})


if __name__ == '__main__':
    app.run(debug=True)