import os
import copy

#data = open("10kpron.txt",mode="r",encoding="utf8").read()
data = open("1000Pron.txt",mode="r",encoding="utf8").read()
#data = open("allprons.txt",mode="r",encoding="utf8").read()

#print(data)

separators = data.splitlines()[0].split()

raw_prons = data.splitlines()[1:]

#print(raw_prons)

raw_prons = [z for x in raw_prons for y in x.split(" ")[1:] for z in y.split("~") if (not y == "" and len(y) >= 1 and y not in separators)]

print("" in raw_prons)

print(raw_prons)

stop_chars ="̈ᵊ̰̚˞͡ˀ̪̃ʔʰ˩˥ʲ̟̯̬​ˠ̞ʷʱ̝ˁ̻cǀˑ̥̹ˢ̺"

vowels = "iyɨʉɯuɪʏɪʊeøɘɵɤoe̞ø̞əɤ̞o̞ɛœɜɞʌɔæɐaɶäɑɒ"

#replaces rare, unusual sounds with close equivalents in // notation
simplifying = {'ä': 'a', 'ɟ': 'g', 'á': 'a', "ɚ": 'ər', "ʍ": "w", "ɝ": "ər", "ɘ": "ɪ", "ɹ": "r", "õ": "ɔn", "ɱ": "m",
               "œ": "", "ʋ": "w", "ɯ": "ə", "ɻ": "r", "ɧ": "ʃ", "ɬ": "l", "ã": "a", "ɕ": "ʃ", "ɲ": "nj", "ç": "h",
               "ẽ": "e", "ɦ": "h", "g": "ɡ", "ĭ": "ɪ", "ĩ": "ɪ", "ʏ": "ʊ", "χ": "x", "ŏ": "ə", "ɥ": "ju", "ɵ": "ɔ",
               "ʎ": "j", "ʝ": "j", "έ": "e"}

known_syllables = []


def strip_tags(prons):
    prons = [x.replace("/", "").replace("]", "").replace("[", "") for x in prons if len(x) > 2]
    for j in range(len(prons)):
        if prons[j][0] in separators:
            prons[j] = prons[j][1:]
        if prons[j][-1] in separators:
            prons[j] = prons[j][-1]
    return [x for x in prons if len(x) > 0 and x not in separators]


def cleanup(prons):
    for j in range(0, len(prons)):
        for i in range(0, len(separators)):
            prons[j] = prons[j].replace(separators[i], "-")  # makes split much easier
            prons[j] = prons[j].replace("--", "-").replace("ː", "").replace("̩", "").replace("(", "").replace(")", "")
            print(prons[j])
        for c in stop_chars:
            prons[j] = prons[j].replace(c, "")
        for k in simplifying:
            prons[j] = prons[j].replace(k, simplifying[k])
    return [x for x in prons if len(x) > 0]


def is_fully_syllabified(pron):
    return ("." in pron or len(pron) < 4 or has_single_vowel_group(pron)) and has_a_vowel(pron)


def has_a_vowel(pron):
    found_vowel = False
    for j in range(len(pron)):
        if pron[j] in vowels:
            found_vowel = True
    return found_vowel

def has_single_vowel_group(pron):
    """
    detects if a pronunciation only contains a single vowel or group thereof, which usually means it is monosyllabic
    :param pron:
    :return:
    """
    found_vowel = False
    consonant_after_vowel = False
    second_vowel = False
    for j in range(0, len(pron)):
        if pron[j] in vowels:
            if not found_vowel:
                found_vowel = True
            elif consonant_after_vowel:
                second_vowel = True
        else:
            if found_vowel:
                consonant_after_vowel = True
    return found_vowel and not second_vowel


def get_known_syllables(prons):
    res = []
    for pron in prons:
        if is_fully_syllabified(pron):
            split = pron.replace("ˈ", ".").replace("ˌ", ".").split(".")
            res = res + [s for s in split if s not in res]
    return res


def is_syllabified(pron,known):
    """
    Simple heuristic to determine if a pronunciation is already syllabified
    :param pron:
    :return:
    """
    res = True
    if "." in pron:
        res = True
    elif "ˈ" in pron:   # only one intonation mark
        if "ˌ" not in pron:
            split = pron.replace("ˈ", ".").split(".")
            for s in split:
                if len(s) > 4 and s not in known:  # 3 is arbitrary; there are some false positives but not too many
                    res = False
        else:  # both intonation marks
            split = pron.replace("ˈ", ".").replace("ˌ", ".").split(".")
            for s in split:
                if len(s) > 4 and s not in known:
                    res = False
    else:
        res = len(pron) < 5 and has_a_vowel(pron)
    return res


def writeDictFile(prons, filename, weight=1):
    file = open(filename, mode="w", encoding="utf8")
    for pron in prons:
        file.write(str(weight)+pron+"\n")
    file.close()


def getUniqueCharacters(prons):
    uniques=[]
    for pron in prons:
        for char in pron.replace("-",""):
            if char not in uniques:
                uniques.append(char)
    return uniques

def toUnicode(uniques):
    res = {}
    for i in range(0,len(uniques)):
        res[uniques[i]]=chr(97+i)
    return res

def writeTranslateFile(uniques, filename):
    file = open(filename, mode="w", encoding="utf8")
    #file.write("2 3\n")
    #dict  = toUnicode(uniques)
    for unique in uniques:
        #file.write(dict[unique]+"\n")
        file.write(unique + "\n")


stripped = strip_tags(raw_prons)
#print(stripped)
known_syllables = get_known_syllables(stripped)
#print(known_syllables)


prons = [x for x in stripped if is_syllabified(x, known_syllables)]

clean = cleanup(prons)


#writeDictFile(clean,"googleWordlist.txt")
#writeTranslateFile(getUniqueCharacters(clean),"tt.txt")
#writeDictFile(clean,"allpronstest.txt")
#writeTranslateFile(getUniqueCharacters(clean),"allpronstranslate.txt")
writeDictFile(clean,"1ktest.txt", 10)
writeTranslateFile(getUniqueCharacters(clean),"1ktranslate.txt")
#print(getUniqueCharacters(clean))
#print(toUnicode(getUniqueCharacters(clean)))

print(clean)



print(is_syllabified('mʌltiˈmiːdi.ə',known_syllables))
print("mʌlti" in known_syllables)
print(len('ˈpɹɪzən'))
print(has_a_vowel("ʒ"))