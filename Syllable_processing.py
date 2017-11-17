# coding: utf-8
import os
import copy
import collections
import operator
import pickle
import math

filename = "1000Pron_pruned.txt"
file = open(filename, 'r', encoding="utf8")
separators = file.readline().replace("\n", "").split(" ")
pronunciationList = file.read().splitlines()[1:]

allSyllables=[]

def possibleSplitPatterns(n):
    if n <= 1:
        return [[0]]
    else:
        previous = possibleSplitPatterns(n-1)
        res = previous[:]
        for pattern in previous:
            res.append(pattern+[n-1])
        return res

def generatePatternsUpTo(n):
    patterns = [[[0]]]
    try:
        f=open(".patterns","rb")
        patterns = pickle.load(f)
    except:
        pass
    k = len(patterns)
    for i in range(k,n):
        print(i)
        previous = patterns[i-1]
        patterns.append(previous[:])
        for pattern in previous:
            patterns[i].append(pattern+[i])
    return patterns

def writePatterns(n):
    patterns = generatePatternsUpTo(n)
    try:
        os.remove(".patterns")
    except:
        pass
    f = open(".patterns", 'wb')
    pickle.dump(patterns,f)

def splitBy(word, pattern):
    if len(word)==0:
        pass
    elif len(pattern)==1:
        result = [word[:pattern[0]],word[pattern[0]:]]
        if "" in result:
            result.remove("")
        return result
    else:
        return splitBy(word[:(pattern[-1])],pattern[:-1])+[word[pattern[-1]:]]



for pronunciation in pronunciationList:
    w = copy.copy(pronunciation)
    for i in range(1,len(separators)):
        w = w.replace(separators[i],separators[0]) #makes split much easier
    w = w.replace("(","").replace(")","").replace("ː","").replace(" ","")
    for syllable in w.split(separators[0]):
        if len(syllable)>0:
            allSyllables.append(syllable)

distinctSyllables = set(allSyllables)
numDistinct = len(distinctSyllables)
countedSyllables = collections.Counter(allSyllables)
countedSyllables = {k: v/numDistinct for k, v in countedSyllables.items()}

def writeSyllableFrequencies(countedSyllableDict, filename):
    try:
        os.rename(filename, filename+".previous")
    except:
        pass
    f = open(filename,'w+', encoding="utf-8")
    od = collections.OrderedDict(sorted(countedSyllableDict.items(), key=operator.itemgetter(1), reverse=True))
    for syllable in od:
        f.write("%s: %f\n"%(syllable, countedSyllableDict[syllable]))

def splitScore(splitWord, countedSyllableDict):#takes a list of strings representing syllables and a frequency dictionary
    result = 1
    minfreq = 0.000000000007 #frequency used for unknown syllables
    for syllable in splitWord:
        try:
            result *= (countedSyllableDict[syllable])
        except:
            result *= minfreq
    return result


def possibleSplits(word):
    n=len(word)
    patterns = possibleSplitPatterns(n)
    res = []
    for pattern in patterns:
        res.append(splitBy(word,pattern))
    return res

"""
print(distinctSyllables)
print(countedSyllables["ə"])

print(len(distinctSyllables))
"""
#print (possibleSplits("test",20))

#print (possibleSplitPatterns(3))
#print(possibleSplits("the quick brown fox"))


allsplits = generatePatternsUpTo(10)

word = "tɛləvɪʒən"

bestSplit=[]
bestScore=-100000

splits = possibleSplits(word)

for split in splits:
    score = splitScore(split,countedSyllables)
    print(split)
    print(score)
    if score>bestScore:
        bestScore=score
        bestSplit=split
print("\n")
print(bestSplit)
print(bestScore)

writeSyllableFrequencies(countedSyllables,"sylllable_freqs.txt")