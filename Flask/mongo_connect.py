from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'phonetoque' #mettre le nom de la bd
app.config['MONGO_URI'] = 'mongodb://joseph:password@ds135866.mlab.com:35866/phonetoque' #mettre le lien de la db avec username et password

mongo = PyMongo(app)

@app.route('/english_words', methods = ['GET']) #pour avoir tous les mots
def get_all_words():
    all_words = mongo.db.english_words 
    output = []
    for word in all_words.find():
        del word['_id'] #the value of this key is an ObjectId which is not JSON serializable
        output.append(word)
    return jsonify({'result': output})

@app.route('/english_words/<word>', methods=['GET']) #pour avoir les details d'un mot
def get_one_word(word):
    all_words = mongo.db.english_words
    result = all_words.find_one({'spelling' : word}) #pour avoir les valeurs quon veut
    if result:
        del result['_id'] #the value of this key is an ObjectId which is not JSON serializable
        output = result
    else:
        output = 'This word is not in our database'    
    return jsonify({'result': output})


@app.route('/post', methods=['POST'])
def add_word():
    words = mongo.db.english_words
    data = request.get_json()
    # nettoyer et transformer les donnees client
    language = data['language']
    spelling = data['spelling']
    syllables = data['syllables']
    spelling_ipa = data['spelling_ipa']
    syllables_ipa = data['syllables_ipa']

    db_insert = {'language': language, 'spelling': spelling, 'syllables':syllables, 'spelling_ipa': spelling_ipa, 'syllables_ipa': syllables_ipa}
    words.insert(db_insert)
    return "The word {} has been added".format(spelling)

if __name__ == '__main__':
    app.run(debug=True)



