import pyphen, requests, json
#pyphen.language_fallback('ipa_en')
ipa_dic = pyphen.Pyphen(lang='ipa_en')
spelling_dic = pyphen.Pyphen(lang='en')

URL = "http://127.0.0.1:5000"
LANGUAGE = "english"


print(ipa_dic.inserted("sʌbdʒɛktɪv"))  # use dark magic space trick in the future

wordlist = "allprons.txt"
data = open(wordlist, mode="r", encoding="utf8").read()

separators = data.splitlines()[0].split()

raw_data = data.splitlines()[1:]

#print(raw_data)

stop_chars ="̈ᵊ̰̚˞͡ˀ̪̃ʔʰ˩˥ʲ̟̯̬​ˠ̞ʷʱ̝ˁ̻cǀˑ̥̹ˢˈˈ̺͡"

vowels = "iyɨʉɯuɪʏɪʊeøɘɵɤoe̞ø̞əɤ̞o̞ɛœɜɞʌɔæɐaɶäɑɒ"

#replaces rare, unusual sounds with close equivalents in // notation
simplifying = {'ä': 'a', 'ɟ': 'g', 'á': 'a', "ɚ": 'ər', "ʍ": "w", "ɝ": "ər", "ɘ": "ɪ", "ɹ": "r", "õ": "ɔn", "ɱ": "m",
               "œ": "", "ʋ": "w", "ɯ": "ə", "ɻ": "r", "ɧ": "ʃ", "ɬ": "l", "ã": "a", "ɕ": "ʃ", "ɲ": "nj", "ç": "h",
               "ẽ": "e", "ɦ": "h", "g": "ɡ", "ĭ": "ɪ", "ĩ": "ɪ", "ʏ": "ʊ", "χ": "x", "ŏ": "ə", "ɥ": "ju", "ɵ": "ɔ",
               "ʎ": "j", "ʝ": "j", "έ": "e"}

def simplify(string):
    if string in simplifying:
        return simplifying[string]
    else:
        return string

def cleanup(prons):
    for j in range(0, len(prons)):
        for i in range(0, len(separators)):
            prons[j] = "".join([c for c in prons[j] if not c in separators])
            prons[j] = prons[j].replace("--", "-").replace("ː", "").replace("̩", "").replace("(", "").replace(")", "")
        for c in stop_chars:
            prons[j] = "".join([c for c in prons[j] if not c in stop_chars])
        for k in simplifying:
            prons[j] = prons[j].replace(k, simplifying[k])
    return [x for x in prons if len(x) > 0]

def strip_tags(prons):
    prons = [x.replace("/", "").replace("]", "").replace("[", "") for x in prons if len(x) > 2]
    for j in range(len(prons)):
        if prons[j][0] in separators:
            prons[j] = prons[j][1:]
        if prons[j][-1] in separators:
            prons[j] = prons[j][-1]
        prons[j] = "".join([simplify(c) for c in prons[j]])
    return [x for x in prons if len(x) > 0 and x not in separators]

words = []

pronunciations = {}
for line in raw_data:
    word = line.split(" ")[0]
    word = spelling_dic.inserted(""+word+"").strip()
    words.append(word)
    prons = [x for x in line.split(" ")[1:] if (not x == "")]
    prons = cleanup(strip_tags(prons))
    prons = [ipa_dic.inserted(""+x+"").strip() for x in prons]
    pronunciations[word]=prons

#print(pronunciations)

'''
payload = {
      "language": "english",
      "spelling": "shiba",
      "spelling_ipa": u"ʃibə",
      "syllables": "[u'shi',u'ba']",
      "syllables_ipa": "['ʃi','bə']"
    }
response = requests.post(f"{URL}/{LANGUAGE}_words/", headers={'Content-Type': 'application/json'}, data=json.dumps(payload))

print(response.text) #TEXT/HTML
print(response.status_code, response.reason) #HTTP
'''

print([word for word in pronunciations])

def post_to_db(word):
    spelling = word.replace("-","")
    syllables = word.split("-")
    for pronunciation in pronunciations[word]:
        spelling_ipa = pronunciation.replace("-","")
        syllables_ipa = pronunciation.split("-")

        payload = {
            "language": LANGUAGE,
            "spelling": spelling,
            "spelling_ipa": spelling_ipa,
            "syllables": syllables,
            "syllables_ipa": syllables_ipa
        }
        response = requests.post(f"{URL}/{LANGUAGE}_words/", headers={'Content-Type': 'application/json'},
                                 data=json.dumps(payload))
        print(response.text)

for word in words:
    post_to_db(word)