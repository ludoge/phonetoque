import Wiktionary_scraper

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

    def  addPhoneticSyllable(self, ipa):
        if ipa in self.phoneticSyllables:
            self.phoneticSyllables[ipa].frequency += 1
        else:
            self.phoneticSyllables[ipa] = PhoneticSyllable(ipa)

    def readWords(self, filename):
        wordlist = open(filename, "r").read().split("\n")
        for spelling in wordlist:
            self.add(spelling)

    def fetchPronunciation(self,word):
        if self.language == "EN":
            prons = Wiktionary_scraper.pronunciations_from_wiktionary(word.spelling)
        for pron in prons:
            self.addPronunciation(pron)
            word.addPronunciation(pron)





class Word:
    spelling = ""
    pronunciations = []
    syllabified = []
    frequency = 1;

    def __init__(self, spelling):
        self.spelling = spelling

    def addPronunciation(self, pronunciation):
        self.pronunciations.append(pronunciation)


class Pronunciation:
    ipa = ""
    syllabified = []
    frequency = 1

    def __init__(self, ipa):
        self.ipa = ipa

class Syllable:
    spelling = ""
    frequency = 1

    def __init__(self,spelling):
        self.spelling = spelling


class PhoneticSyllable:
    ipa = ""
    frequency = 1

    def __init__(self, ipa):
        self.ipa = ipa


testmodel = PhoneticModel();
testmodel.addWord("about")
testmodel.fetchPronunciation(testmodel.words["about"])

print (testmodel.pronunciations)
