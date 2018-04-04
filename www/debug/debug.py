# coding: utf-8

import json
from json import *

import requests
from flask import Flask, request, render_template, redirect

from src.closest_sound import example_of_sound
from src.sequence_statistics import generate_sentence

app = Flask(__name__)

API_URL = 'http://api:5000'
# API_URL = 'http://127.0.0.1:5001'

app.config['JSON_AS_ASCII'] = False

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
        # on PATCH
        language = insert['language']
        word = insert['spelling']
        requests.patch(f"{API_URL}/{language}/{word}", headers={'Content-Type': 'application/json'}, data=json.dumps(insert))
        url = '/all_words/'+insert['language']+'/'+insert['spelling']
        return redirect(url)
    else:
        word = requests.get(f"{API_URL}/{language}_id/{str(id)}").json()['result']
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
        # on POST
        language=insert['language']
        requests.post(f"{API_URL}/{language}_words/", headers={'Content-Type': 'application/json'}, data=json.dumps(insert))
        return render_template('word.html', word=insert, mod=True)


@app.route('/all_words/',methods=['POST'])
@app.route('/all_words/<language>/<spelling>/',methods=['GET'])
def all_words(language=None,spelling=None):
    if request.method == "POST":
        url = "/all_words/"+request.form['language']+"/"+request.form['spelling']
        return redirect(url)
    words = requests.get(f"{API_URL}/{language}/{spelling}").json()['result']
    for word in words:
        word['_id'] = word['_id']['$oid']
    if not words:
        words = []
    return render_template('all_words.html',all_words=words)


@app.route('/translitteration/',methods=['POST','GET'])
def translitterate():
    if request.method == 'GET':
        default = {'language':'english', 'spelling':'', 'spelling_ipa':'', 'syllables':[], 'syllables_ipa':[] }
        return render_template('translitteration.html',post= False)
    elif request.method == 'POST':
        payload = {'spelling':request.form['spelling'], 'language1':request.form['language1'], 'language2':request.form['language2']}
        response = requests.post(f'{API_URL}/translitteration/', headers={'Content-Type': 'application/json'}, data = json.dumps(payload)).json()
        post = response['post']
        if post is False:
            message = response['message']
            return render_template('translitteration.html',post=post, message = message)
        else:
            word = response['spelling']
            syllables1 = response['syllables1']
            syllables2 = response['syllables2']
            language1 = response['language1']
            language2 = response['language2']
            syllables_ipa1 = response['syllables_ipa1']
            syllables_ipa2 = response['syllables_ipa2']
            harmonic_mean = response['harmonic_mean']
            return render_template('translitteration.html',post=post,word=word,result=syllables2,language1=language1,language2=language2,syllables=syllables1,syllables_ipa=syllables_ipa1,syllables_ipa2=syllables_ipa2, harmonic_mean=harmonic_mean)


@app.route('/delete/<language>/<id>/')
def delete(language, id):
    word = requests.get(f"{API_URL}/{language}_id/{id}").json()['result']['spelling']
    delete = requests.delete(f"{API_URL}/{language}_id/{id}")
    url = '/all_words/' + language + '/' + word
    return redirect(url)


@app.route('/generate_words/')
@app.route('/generate_words/<language>/')
def generate_words(language='french'):
    try:
        words, phonems = generate_sentence(language,[3,8,7,6,2,9,4,3,5])
        return render_template('generate_words.html',words=words, phonems=phonems, language=language)
    except:
        return f'<a href="/generate_words/{language}"> Réessayer </a>'


@app.route('/phonems/', defaults={'language': 'english'}, methods=['GET', 'POST'])
@app.route('/phonems/<language>/', methods=['GET'])
def phonems(language):
    if request.method == 'POST':
        language = request.form['language']
    all_phonems = requests.get(f"{API_URL}/phonems/{language}").json()['result']
    return render_template('phonems.html',language=language,all_phonems=all_phonems)


@app.route('/phonem/<language>/<phonem>/', methods=['GET', 'POST'])
def phonem(language,phonem):
    if request.method == 'GET':
        item = requests.get(f"{API_URL}/phonems/{language}/{phonem}/").json()['result']
        number_of_examples = 4
        words, phonetics = example_of_sound(phonem, language, number_of_examples)
        return render_template('phonem.html',phonem=item,words=words,phonetics=phonetics, number_of_examples=number_of_examples)
    else:
        patch = {'written': request.form['written']}
        requests.patch(f"{API_URL}/phonems/{language}/{phonem}/", headers={'Content-Type': 'application/json'}, data=json.dumps(patch))
    return redirect(f'/phonems/{language}')


if __name__ == '__main__':
    #print(get_word('french','test'))
    app.run(debug=True, host='0.0.0.0')
    # app.run(debug=True, port=5000)