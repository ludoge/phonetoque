# coding: utf-8

from flask import Flask, request, render_template, redirect
import requests
import json
from json import *
from scipy import stats

app = Flask(__name__)

# API_URL = 'http://api:5000'
API_URL = 'http://127.0.0.1:5001'

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
            syllables = response['syllables']
            language1 = response['language1']
            language2 = response['language2']
            syllables_ipa1 = response['syllables_ipa1']
            syllables_ipa2 = response['syllables_ipa2']
            harmonic_mean = response['harmonic_mean']
            return render_template('translitteration.html',post=post,word=word,result=syllables,language1=language1,language2=language2,syllables=syllables,syllables_ipa=syllables_ipa1,syllables_ipa2=syllables_ipa2, harmonic_mean=harmonic_mean)


@app.route('/delete/<language>/<id>/')
def delete(language, id):
    word = requests.get(f"{API_URL}/{language}_id/{id}").json()['result']['spelling']
    delete = requests.delete(f"{API_URL}/{language}_id/{id}")
    url = '/all_words/' + language + '/' + word
    return redirect(url)

if __name__ == '__main__':
    #print(get_word('french','test'))
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=True, port=5000)