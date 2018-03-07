import requests
from bs4 import BeautifulSoup
import numpy as np

DEBUG_URL = 'http://127.0.0.1:5000'

def get_word_score(language1, language2, spelling):
    response = requests.post(f'{DEBUG_URL}/translitteration/', data = {'language1': language1, 'language2': language2, 'spelling': spelling})
    data = response.text
    soup = BeautifulSoup(data, "html5lib")
    score = soup.find(id="harmonic_mean").getText()
    return(int(score[:-2]))

def get_score(language1, language2, text_file):
    with open(text_file) as text_file:
        all_scores = []
        not_found = 0
        for word in text_file:
            try:
                score = get_word_score(language1, language2, word)
                all_scores += [score]
            except AttributeError:
                # all_scores += [0]
                not_found += 1
        total_number_of_words = len(all_scores) + not_found
        return f"Total score: {round(np.mean(all_scores),2)}, total number of words: {total_number_of_words}, not found words: {not_found}" 

english_to_french = get_score('english', 'french', '1000CommonWords.txt')
print(english_to_french)
