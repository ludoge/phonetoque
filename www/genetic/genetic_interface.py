# coding: utf-8

from flask import Flask, render_template, request, redirect
from www.genetic.sounds.sound_distance_for_genetic import SoundDistance
import random
import json
from math import sqrt, exp

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

with open("all_syllables_en.yml", encoding="utf-8") as f_en:
    syllables_en = f_en.read().split()
with open("all_syllables_fr.yml", encoding="utf-8") as f_fr:
    syllables_fr = f_fr.read().split()
with open("all_syllables_it.yml", encoding="utf-8") as f_it:
    syllables_it = f_it.read().split()

"""
First convergence : manner : 9,26		place : 7,54	other : 3,42
	                closedness : 20,42	frontness : 2,65	roundedness : 16,70
Second convergence : manner : 9,82		place : 8,23	other : 8,18
	                closedness : 17,56	frontness : 3,37	roundedness : 12,88
Third convergence : manner: 11,25		place : 11,47	other : 10,22
                    closedness: 10,68	frontness : 13,56	roundedness : 2,81
"""

parameters_to_train = ['manner', 'place', 'other', 'closedness', 'frontness', 'roundedness', 'balance']
default_parameters = {}
# we can use this to reinput the already calculated result from choice
# in case we restart the program


# ------------------ Routes for the interface ------------------ #
@app.route('/')
def index():
    return '<a href="/closest/given/4"> Get started </a>'


@app.route('/closest/given/',methods=['POST','GET'])
@app.route('/closest/given/<int:number>',methods=['POST','GET'])
def closest_given(number=3, parameters=default_parameters):

    # we get the parameters from the request and create a set of parameters from it
    #if request.method == 'POST':
    #    parameters = request.form
    if parameters:
        list_of_parameters = genetic_parameters(number, parameters)
    else:
        list_of_parameters = []
        for i in range(number):
            list_of_parameters.append(random_parameters())

    # we get syllables that have different equivalents with a different set of parameters
    sample_en_fr, list_of_closest_en_fr, list_of_scores_en_fr = get_useful_sample(5,syllables_en,syllables_fr,list_of_parameters)
    sample_fr_en, list_of_closest_fr_en, list_of_scores_fr_en = get_useful_sample(5,syllables_fr,syllables_en,list_of_parameters)
    sample_en_it, list_of_closest_en_it, list_of_scores_en_it = get_useful_sample(5,syllables_en,syllables_it,list_of_parameters)
    sample_fr_it, list_of_closest_fr_it, list_of_scores_fr_it = get_useful_sample(5,syllables_fr,syllables_it,list_of_parameters)
    sample_it_fr, list_of_closest_it_fr, list_of_scores_it_fr = get_useful_sample(5,syllables_it,syllables_fr,list_of_parameters)
    sample_it_en, list_of_closest_it_en, list_of_scores_it_en = get_useful_sample(5,syllables_it,syllables_en,list_of_parameters)

    return render_template('compare_useful.html',
                           sample=sample_en_fr + sample_fr_en + sample_en_it + sample_fr_it + sample_it_en + sample_it_fr,
                           list_of_closest=list_of_closest_en_fr + list_of_closest_fr_en + list_of_closest_en_it + list_of_closest_fr_it + list_of_closest_it_en + list_of_closest_it_fr,
                           list_of_scores=list_of_scores_en_fr + list_of_scores_fr_en + list_of_scores_en_it + list_of_scores_fr_it + list_of_scores_it_en + list_of_scores_it_fr,
                           list_of_parameters=list_of_parameters,
                           n_sample=len(sample_en_fr + sample_fr_en + sample_en_it + sample_fr_it + sample_it_en + sample_it_fr),
                           n_parameters=len(list_of_parameters)
                           )


@app.route('/choice/',methods=['POST','GET'])
def choice():
    if request.method == 'GET':
        return redirect('/closest/random/')

    data = request.form
    n_sample = int(data['n_sample'])
    n_parameters = int(data['n_parameters'])
    list_of_parameters = json.loads(data['list_of_parameters'].replace("'", '"'))

    ratings = []
    for i in range(int(n_sample)):
        try:
            ratings.append(int(data['syllable' + str(i)]))
        except:
            ratings.append(-1) # -1 means no set of parameter was chosen by the user

    best, score, variance = get_best_set(ratings)

    result = {}
    for parameter in parameters_to_train:
        value = list_of_parameters[best][parameter]
        deviation = 1+10*variance/score
        result[parameter] = [value, deviation]

    record(result)
    return closest_given(n_parameters,result)


# ------------------         Genetics         ------------------ #
def get_best_set(ratings):
    """
    :param ratings: a list of indexes : [0,1,0,,2,4,2,0,0,,0]
    :return: the index present the most (0), its number of occurrences (5), the number of others (4)
    """
    n = max(ratings)+1
    scores = [0 for i in range(n)]
    for i in range(len(ratings)):
        if ratings[i] > -1: # we check if a parameter has been chosen for this instance
            scores[ratings[i]] += 1
    best = None
    score = -1
    var = 0
    for i in range(n):
        if scores[i] > score:
            score = scores[i]
            best = i
        var += scores[i]
    return best, score, var-score


def genetic_parameters(number, data):
    """
    :param number: number of child given the genetic parent data
    :param data: {parameters : [mean, standard deviation])
    :return: list of {parameter : value}
    """
    result = []
    for i in range(number):
        set = {}
        for parameter in data.keys():
            value = random.gauss(data[parameter][0], data[parameter][1])
            if value > 0:
                set[parameter] = value
            else:
                set[parameter] = data[parameter][0]
        result.append(set)
    return result


def converged(parameters):
    # returns the percentage of convergence for the result of choice
    deviations = 0
    for key in parameters.keys():
        deviations += parameters[key][1]
    return round(100*exp(-deviations/12),2)


# ------------------     Data generation      ------------------ #
def random_parameters():
    """
    Returns a random set of parameters (between 0 and 50)
    """
    return {parameter: 50*random.random() for parameter in parameters_to_train}


def get_useful_sample(number, possible_sample, possible_matches, list_of_parameters):
    """
    :param number: Number of syllables in the sample
    :param possible_sample: List from which the syllables are picked
    :param possible_matches: List in which we choose equivalents for the sampled syllables
    :param list_of_parameters: differet sets of parameters we are comparing
    :return: the sample, their equivalents for each set of parameter, their score for each set of parameters
            [s1, s2, s3], [[eq(s1,p1),eq(s1,p2)..],[eq(s2,p1),..],..], [[sc(s1,p1),sc(s1,p2)..],[sc(s2,p1),..],..]
    """
    sample = []
    closest = []
    scores = []
    not_checked = possible_sample
    i = 0
    while i < number and not_checked:
        syll = get_random(1, not_checked)[0]
        not_checked.remove(syll)
        match, score = match_one_w_many_parameters(syll,possible_matches,list_of_parameters)
        if non_trivial(match):
            sample.append(syll)
            closest.append(match)
            scores.append(score)
            i += 1
    return sample, closest, scores


def match_one_w_many_parameters(syllable,possible,list_of_parameters):
    """
    :param syllable: syllable which we are looking for an equivalent
    :param possible: syllables of the targeted language
    :param list_of_parameters: list of sets of parameters
    :return: the list of match and the list of scores for each set of parameters
    """

    def match(syll, poss, sound_dist_obj):
        """
        :param syll: Enter a phonetic syllable
        :param poss: List of phonetic syllable we'll try to match
        :param sound_dist_obj: Instance of SoundDistance class
        :return: the closest syllable to "syllable" from "possible" and the matching score
        """
        closest = ""
        best = 0
        #hypers = []
        for candidate in poss:
            score, param = sound_dist_obj.syllable_similarity(syll, candidate)
            if score > best:
                best = score
                closest = candidate
                # hypers = param
        return closest, round(100 * best, 2)#, hypers

    list_of_matched = []
    list_of_scores = []
    for parameters in list_of_parameters:
        #SoundDistance.__new__(SoundDistance)
        sd = SoundDistance(parameters=parameters)
        try:
            matched = match(syllable, possible, sd)
            list_of_matched.append(matched[0])
            list_of_scores.append(matched[1])
        except:
            list_of_matched.append("Non trouvé")
            list_of_scores.append(0)
    return list_of_matched, list_of_scores


# ------------------   Auxiliary functions    ------------------ #
def non_trivial(liste):
    """
    Checks if there is at least two different elements in the list
    """
    unique = []
    count = 0
    for element in liste:
        if element in unique:
            continue
        else:
            unique.append(element)
            count += 1
            if count == 2:
                return True
    return False


def get_random(number, possible):
    """
    :param number: length of the returned list
    :param possible: list of possible items
    :return: a list of random items of "possible"
    """
    result = []
    length = len(possible)
    for i in range(number):
        rand = random.randint(0,length-1)
        if possible[rand] not in result:
            result.append(possible[rand])
    return result


def record(result,file='parameters_score.txt'):
    with open(file,'a') as record:
        for parameter in result.keys():
            value = round(result[parameter][0],2)
            deviation = round(result[parameter][1],2)
            record.write(f'{parameter} : {value} (+/- {deviation})   ')
        convergence = str(converged(result))+'%'
        record.write('\nConvergence : '+convergence+'\n')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
