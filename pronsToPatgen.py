import os
import copy

data = open("1000Pron_pruned.txt",mode="r",encoding="utf8").read()

separators = data.splitlines()[0].split()

prons = data.splitlines()[1:]

def cleanup(prons):
    for j in range(0, len(prons)):
        for i in range(0, len(separators)):
            prons[j] = prons[j].replace(separators[i], "-")  # makes split much easier
            prons[j] = prons[j].replace("--","-").replace("ː","").replace("̩","").replace("(","").replace(")","")
            if prons[j][0]=="-":
                prons[j]=prons[j][1:]
            if prons[j][-1]=="-":
                prons[j]=prons[j][:-1]
    return prons

def writeDictFile(prons, filename):
    file = open(filename, mode="w", encoding="utf8")
    for pron in prons:
        file.write("1"+pron+"\n")
    file.close()


def getUniqueCharacters(prons):
    uniques=[]
    for pron in prons:
        for char in pron.replace("-",""):
            if char not in uniques:
                uniques.append(char)
    return uniques

def writeTranslateFile(uniques, filename):
    file = open(filename, mode="w", encoding="utf8")
    file.write("2 3\n")
    for unique in uniques:
        file.write(unique+"\n")

clean = cleanup(prons)
writeDictFile(clean,"DictTest.txt")
writeTranslateFile(getUniqueCharacters(clean),"TranslateTest.txt")
