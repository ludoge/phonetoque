from math import sqrt, pow
import yaml

###### TODO increase importance of consonants DONE
###### TODO try harmonic mean
###### TODO increase importance of voicing DONE
###### TODO deal with drug -> dog problem
###### TODO deal with 'h' absurdity somewhat done
###### TODO "nuelel" and "rabola"

class SoundDistance(object):
    """
    Methods to compute similarity between two sounds, or two syllables, based on properties of sounds as stored in conf
    This is intended to be used to find, for a given syllable in language A, the most similar possible syllable in
    language B.
    Each sound is represented as a unit vector in (number of properties)-dimensional space
    Similarity is given by scalar (dot) product : see https://en.wikipedia.org/wiki/Cosine_similarity
    """
    def __init__(self, consonant_conf='src/consonant_properties.yml', vowel_conf='src/vowel_properties.yml'):
        with open(consonant_conf, encoding="utf-8") as f:
            self.consonant_data = yaml.safe_load(f)

        with open(vowel_conf, encoding="utf-8") as f:
            self.vowel_data = yaml.safe_load(f)

        self.all_consonants = set((" ".join([v for k,v in self.consonant_data.items()][1:])).split(" "))
        self.consonant_properties = [k for k,v in self.consonant_data['properties'].items()]

        self.all_vowels = set(sum(([[x for x in v] for k,v in self.vowel_data.items()][1:]),[]))
        self.vowel_properties = [k for k, v in self.vowel_data['properties'].items()]

        self.all_sounds = set(list(self.all_vowels) + list(self.all_consonants))
        self.all_properties = set(list(self.vowel_properties) + list(self.consonant_properties))

        self.data = {}
        for consonant in self.all_consonants:
            self.data[consonant]={}
            weights = 0
            for property in self.consonant_properties:
                if consonant in self.consonant_data[property].split():
                    weights += self.consonant_data['properties'][property]**2
                    self.data[consonant][property] = self.consonant_data['properties'][property]
                else:
                    self.data[consonant][property] = 0
            #  special treatment for voiced/voiceless axis
            voicedness = self.data[consonant]['voiced']-self.data[consonant]['voiceless']
            self.data[consonant]['voiced'], self.data[consonant]['voiceless'] = voicedness, -voicedness
            weights += self.consonant_data['properties']['voiced'] ** 2

            for property in self.consonant_properties:  # normalization
                self.data[consonant][property] /= sqrt(weights)

            for property in self.vowel_properties:
                self.data[consonant][property] = 0

        for vowel in self.all_vowels:
            self.data[vowel] = {}
            weights = 0
            for property in self.vowel_properties:
                self.data[vowel][property] = self.vowel_data[property][vowel]/self.vowel_data['properties'][property]
                #weights += self.data[vowel][property]**2

            for property in self.vowel_properties:  # normalization
                #  self.data[vowel][property] /= sqrt(weights)
                pass

            for property in self.consonant_properties:
                self.data[vowel][property] = 0

    def detect_sounds(self, str):
        """
        Parses a string to detect known sound symbols
        Necessary because of 0-space chars in sounds (diacritics etc.)
        :param str:
        :return:
        """
        str = str.replace(' ','')
        i = len(str)
        if i == 0:
            return []
        while i > 0:
            if str[:i] in self.all_sounds:
                return [str[:i]] + self.detect_sounds(str[i:])
            else:
                i -= 1
        return self.detect_sounds(str[1:])

    def sound_similarity(self, s1, s2):
        res = 0
        if s1 in self.all_consonants and s2 in self.all_consonants:
            # Cos similarity
            for property in self.consonant_properties:
                try:
                    res += self.data[s1][property]*self.data[s2][property]
                except:
                    return 0
            res = (res+1)/2 # between 0 and 1 for compatibility
        if s1 in self.all_vowels and s2 in self.all_vowels:
            # Euclidean distance
            dimensions = 0
            for property in self.vowel_properties:
                try:
                    res += (self.data[s1][property] - self.data[s2][property])**2
                    dimensions += 1
                except:
                    return 0
            res = 1-res/(2*sqrt(dimensions))

        return res

    def cluster_consonant_vowel(self, sounds):
        """
        instead of comparing sound-by-sound, we cluster together consonants and vowels to then compare those
        :param sounds:
        :return:
        """
        temp = sounds[:]
        i = 0
        while i < len(temp)-1:
            if (temp[i] in self.all_vowels and temp[i+1] in self.all_consonants) or (temp[i] in self.all_consonants and temp[i+1] in self.all_vowels):
                i+=1
                temp[i:i] = "-"
            i += 1
        return("".join(temp).split("-"))

    def _aux_cluster_similarity(self, sounds1, sounds2):
        res = 0
        weights = 0
        d = 0.15
        if len(sounds1) == len(sounds2):
            for i in range(len(sounds1)):
                w = 1
                s = self.sound_similarity(sounds1[i], sounds2[i])
                res += s
                weights += w
            if weights > 0:
                res /= weights
            return res
        elif len(sounds1) >= len(sounds2):
            similarities = [self._aux_cluster_similarity(sounds1[:i]+sounds1[i+1:], sounds2) for i in range(len(sounds1)-1)]
            if similarities:
                return (max(similarities) + d)*0.92*(1-0/(len(sounds1)+1)) - d
            else:
                return 0
        elif len(sounds1) < len(sounds2):
            return self._aux_cluster_similarity(sounds2, sounds1)

    def M(self, results, weights, p=1):
        W = sum(weights)
        w = [x/W for x in weights]
        try:
            return pow(sum(w[i]*pow(results[i],p) for i in range(len(results))),1/p)
        except ZeroDivisionError:
            return 0

    def syllable_similarity(self, s1, s2):
        sounds1, sounds2 = self.detect_sounds(s1), self.detect_sounds(s2)
        clusters1, clusters2 = self.cluster_consonant_vowel(sounds1), self.cluster_consonant_vowel(sounds2)
        res = 0
        adjustment = 1
        if len(clusters1) == len(clusters2) - 1:
            clusters1 = ['h'] + clusters1
            adjustment *= 0.85
        elif len(clusters2) == len(clusters1) - 1:
            clusters2 = ['h'] + clusters2
            adjustment *= 0.85
        if len(clusters1) != len(clusters2) or len(clusters1) == 0:
            return 0
        else:
            results = []
            weights = []
            for i in range(len(clusters1)):
                w = 1
                try:
                    if clusters1[i][0] in self.all_consonants:
                        w = 1.2
                except:
                    pass
                weights.append(w)
                results.append(w*(self._aux_cluster_similarity(clusters1[i], clusters2[i])-1)+1)
            #res = adjustment*sum(results)/sum(weights)
            res = adjustment*min(results)*max(results)
            return res



if __name__ == '__main__':
    sd = SoundDistance(consonant_conf='consonant_properties.yml', vowel_conf='vowel_properties.yml')
    print(sd.data['l']['lateral_approximant'])
    print(sd.data['l̥'])
    print(sd.data['l̥'])

    print(sd.sound_similarity('l', 'l'))
    print(sd.sound_similarity('l', 'l̥'))
    print(sd.sound_similarity('l', 'p'))
    print(sd.sound_similarity('l', 'b'))
    print(sd.sound_similarity('f', 'v'))

    print(sd.sound_similarity('a','l'))
    print(sd.sound_similarity('ə','ɘ'))
    print(sd.sound_similarity('ə', 'i'))
    print(sd.sound_similarity('ɒ', 'i'))

    print(sd.detect_sounds('e̞ø̞'))

    #print(sd.syllable_similarity('kæt', 'kɑt'))
    print(sd.syllable_similarity('kæt', 'dɔɡ'))

    print(sd.syllable_similarity('kæt', 'dʌk'))
    print(sd.syllable_similarity('dɔɡ', 'dʌk'))
    print(sd.syllable_similarity('dɔɡ', 'dɔɡz'))
    print(sd.syllable_similarity('dɔɡz', 'dɔɡzz'))
    print(sd.syllable_similarity('dɔz', 'ftɔzz'))
    print(sd.syllable_similarity('dɔɡ', 'ɡɔd'))
    print(sd.syllable_similarity('bəʊn', 'bon'))
    print(sd.syllable_similarity('bəʊn', 'bəʊt'))
    print(sd.syllable_similarity('ʃən', 'ʃɛl'))
    print(sd.syllable_similarity('fɛt', 'fənt'))
    print(sd.syllable_similarity('t', 'nt'))
    #print(sd.syllable_similarity('ʁɛst', 'ɹest'))
    print(sd.syllable_similarity('dʒɹʌɡ', 'dɔɡ'))
    print(sd.syllable_similarity('dʒɹʌɡ', 'dʁɔɡ'))
    print(sd.syllable_similarity('hot','ot'))
    #print(sd.syllable_similarity('n', 'p'))
    #print(sd.syllable_similarity('dʒɹ', 'dʁ'))
    #print(sd.syllable_similarity('dʒɹ', 'd'))
    #print(sd.syllable_similarity('dʒ', 'd'))
    #print(sd.syllable_similarity('leɪt', 'lit'))
    print(sd.syllable_similarity('ɡœl','ɡəl'))
    print(sd.syllable_similarity('ɡən','ɡəl'))
    print(sd.data['p'])
    print(sd.data['m'])
    print(sd.syllable_similarity('dʒɹʌɡ', 'dɔɡ'))
    print(sd.syllable_similarity('dʒɹʌɡ', 'dʁɔɡ'))
    print(sd.syllable_similarity('dɹɔ','bjɔ'))
    print(sd.syllable_similarity('dɔɡz', 'dɔɡzz'))
    print(sd.syllable_similarity('bəʊn', 'bon'))
    print(sd.syllable_similarity('dɔɡ', 'dʌk'))
    print(sd.syllable_similarity('tbi', 'beɪ'))
    print(sd.syllable_similarity('bi', 'beɪ'))











