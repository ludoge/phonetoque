import Wiktionary_scraper
import Syllable_processing

separators = ". ˈ ˌ -".split(" ")

def standardizeSeparators(string):
    w = string[:]
    for i in range(1,len(separators)):
        w = w.replace(separators[i],separators[0])  # makes split much easier
    return w

class PhoneticModel:
    words = dict()
    pronunciations = dict()
    syllables = dict()
    phoneticSyllables = dict()
    language = ""

    def __init__(self, language="EN"):
        self.language = language

    def addWord(self, spelling):  # takes spelling, checks if word already exists, creates and adds it otherwise
        if spelling in self.words:
            self.words[spelling].frequency += 1
        else:
            self.words[spelling] = Word(spelling)

    def addPronunciation(self, ipa):
        if ipa in self.pronunciations:
            self.pronunciations[ipa].frequency += 1
        else:
            self.pronunciations[ipa] = Pronunciation(ipa)

    def addSyllable(self, spelling):
        if spelling in self.syllables:
            self.syllables[spelling].frequency += 1
        else:
            self.syllables[spelling] = Syllable(spelling)

    def addPhoneticSyllable(self, ipa):
        if ipa in self.phoneticSyllables:
            self.phoneticSyllables[ipa].frequency += 1
        else:
            self.phoneticSyllables[ipa] = PhoneticSyllable(ipa)

    def readWords(self, filename):
        wordlist = open(filename, "r").read().split("\n")
        for spelling in wordlist:
            self.addWord(spelling)

    def fetchPronunciation(self,word):
        if self.language == "EN":
            prons = Wiktionary_scraper.pronunciations_from_wiktionary(word.spelling)
            #print (prons)
        for pron in prons:
            self.addPronunciation(pron)
            #print(pron)
            word.addPronunciation(self.pronunciations[pron])

    def fetchAllPronunciations(self):
        for word in self.words.values():
            self.fetchPronunciation(word)

    def syllabifyPronunciation(self, pronunciation):
        p = pronunciation.ipa[:]
        for i in range(1, len(separators)):
            p = p.replace(separators[i], separators[0])  # makes split much easier
        p = p.replace("(", "").replace(")", "").replace("ː", "").replace(" ", "")
        syllabified = p.split(separators[0])
        if not(p in syllabified):
            self.computeSyllabification(pronunciation)
        else:
            for syllable in syllabified:
                self.addPhoneticSyllable(syllable)
            pronunciation.syllabified = syllabified

    def printAllWords(self):
        print("This phonetic model contains the following words:")
        for word in self.words.values():
            print("\t"+word.spelling+" with the following pronunciations:")
            for pronunciation in word.pronunciations:
                print("\t\t"+pronunciation.ipa)



class Word:

    def __init__(self, spelling):
        self.spelling = spelling
        self.pronunciations = [];
        self.syllabified = []
        self.frequency = 1

    def addPronunciation(self, pronunciation):
        self.pronunciations.append(pronunciation)


class Pronunciation:

    def __init__(self, ipa):
        self.ipa = ipa
        self.frequency = 1
        self.syllabified = []

class Syllable:

    def __init__(self,spelling):
        self.spelling = spelling
        self.frequency = 1


class PhoneticSyllable:

    def __init__(self, ipa):
        self.ipa = ipa
        self.frequency = 1


testmodel = PhoneticModel();
testmodel.readWords("10Words.txt")
testmodel.fetchPronunciation(testmodel.words["abaci"])
testmodel.fetchAllPronunciations()
testmodel.printAllWords()
