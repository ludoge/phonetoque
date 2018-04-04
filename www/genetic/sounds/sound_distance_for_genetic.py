from math import sqrt, pow
import yaml

manner = ['nasal', 'stop', 'sibilant', 'fricative', 'approximant', 'flap', 'trill',
          'lateral_fricative', 'lateral_approximant', 'lateral_flap']
place = ['bilabial', 'labio_dental', 'linguo_labial', 'dental', 'alveolar', 'post_alveolar',
         'retroflex', 'palatal', 'velar', 'uvular', 'pharyngeal', 'epiglottal', 'glottal']
other = ['voiceless', 'voiced', 'r_sound', 'coarticulated']


def hyper_from_property(property):
    if property in manner:
        return 'manner'
    if property in place:
        return 'place'
    if property in other:
        return 'other'
    return None


hyper_parameters = {
    'manner': 1,
    'place': 1,
    'other': 1,
    'closedness': 1,
    'frontness': 1,
    'roundedness': 1,
    'balance': 4
}


class SoundDistance(object):
    """
    Methods to compute similarity between two sounds, or two syllables, based on properties of sounds as stored in conf
    This is intended to be used to find, for a given syllable in language A, the most similar possible syllable in
    language B.
    Each sound is represented as a unit vector in (number of properties)-dimensional space
    Similarity is given by scalar (dot) product : see https://en.wikipedia.org/wiki/Cosine_similarity
    """
    def __init__(self, consonant_conf='consonant_properties_for_genetic.yml',
                 vowel_conf='vowel_properties.yml',
                 parameters=hyper_parameters):
        with open(consonant_conf, encoding="utf-8") as f:
            self.consonant_data_raw = yaml.safe_load(f)

        with open(vowel_conf, encoding="utf-8") as f:
            self.vowel_data = yaml.safe_load(f)

        # We transform the data with the hyper-parameters
        self.consonant_data = self.consonant_data_raw.copy()
        self.consonant_data['properties'] = {}
        for parameter in self.consonant_data_raw['properties']:
            try:
                hyper_param = parameters[parameter]
            except (KeyError,TypeError):
                hyper_param = 1  # default value, but should not happen
            for property, value in self.consonant_data_raw['properties'][parameter].items():
                self.consonant_data['properties'][property] = hyper_param*value

        for property in self.vowel_data['properties']:
            try:
                hyper_param = parameters[property]
            except (KeyError, TypeError):
                hyper_param = 1  # default value, but should not happen
            self.vowel_data['properties'][property] = self.vowel_data['properties'][property]*hyper_param

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
        hypers = []
        if s1 in self.all_consonants and s2 in self.all_consonants:
            # Cos similarity
            for property in self.consonant_properties:
                try:
                    if self.data[s1][property] != 0 and self.data[s2][property]:
                        res += self.data[s1][property]*self.data[s2][property]
                        hypers.append(hyper_from_property(property))
                except:
                    return 0, []
            res = (res+1)/2 # between 0 and 1 for compatibility
        if s1 in self.all_vowels and s2 in self.all_vowels:
            # Euclidean distance
            dimensions = 0
            for property in self.vowel_properties:
                if self.data[s1][property] != 0 or self.data[s2][property] !=0:
                    try:
                        res += (self.data[s1][property] - self.data[s2][property])**2
                        hypers.append(property)
                        dimensions += 1
                    except:
                        return 0, []
            res = 1-res/(hyper_parameters['balance']*sqrt(dimensions))

        return res, flatten(hypers)

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

    # def _aux_cluster_similarity(self, sounds1, sounds2):
    #     res = 0
    #     hypers = []
    #     weights = 0
    #     d = 0.15
    #     if len(sounds1) == len(sounds2):
    #         for i in range(len(sounds1)):
    #             w = 1
    #             s = self.sound_similarity(sounds1[i], sounds2[i])
    #             res += s[0]
    #             hypers += s[1]
    #             weights += w
    #         if weights > 0:
    #             res /= weights
    #         return res, flatten(hypers)
    #     elif len(sounds1) >= len(sounds2):
    #         similarities = []
    #         score = -10000
    #         for i in range(len(sounds1) - 1):
    #             current = self._aux_cluster_similarity(sounds1[:i]+sounds1[i+1:], sounds2)
    #             if current[0] > score:
    #                 score = current[0]
    #                 hypers = current[1]
    #         try:
    #             return (current + d)*0.92*(1-0/(len(sounds1)+1)) - d, flatten(hypers)
    #         except:
    #             return 0, []
    #     elif len(sounds1) < len(sounds2):
    #         return self._aux_cluster_similarity(sounds2, sounds1)

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
            n = len(sounds1)
            alpha = 0.9
            def _decay(i,n):
                """
                Sounds at the start of a cluster matter more
                _decay(n-1,n) = 1
                :param i:
                :param n:
                :return:
                """
                if n > 1 and i < n:
                    a = (1-alpha)/((n)**4)
                    return alpha + a*((i+1)**4)
                else:
                    return 1
            similarities = [self._aux_cluster_similarity(sounds1[:i]+sounds1[i+1:], sounds2)*_decay(i,n) for i in range(n)]
            #print([_decay(i,n) for i in range(n)])
            #print(similarities)
            if similarities:
                return (max(similarities) + d)*0.8*(1-0/(n+10)) - d
            else:
                return 0
        elif len(sounds1) < len(sounds2):
            return self._aux_cluster_similarity(sounds2, sounds1)

    # def M(self, results, weights, p=1):
    #     W = sum(weights)
    #     w = [x/W for x in weights]
    #     try:
    #         return pow(sum(w[i]*pow(results[i],p) for i in range(len(results))),1/p)
    #     except ZeroDivisionError:
    #         return 0

    def syllable_similarity(self, s1, s2):
        print(s1, s2)
        sounds1, sounds2 = self.detect_sounds(s1), self.detect_sounds(s2)
        clusters1, clusters2 = self.cluster_consonant_vowel(sounds1), self.cluster_consonant_vowel(sounds2)
        print(clusters1, clusters2)
        res = 0
        adjustment = 1
        if len(clusters1) == len(clusters2) - 1:
            if 'h' in ''.join(clusters2):
                clusters1 = ['h'] + clusters1
                adjustment *= 0.85
        elif len(clusters2) == len(clusters1) - 1:
            if 'h' in ''.join(clusters1):
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
                        w = 2
                except:
                    print('passed')
                    pass
                weights.append(w)
                results.append(w*(self._aux_cluster_similarity(clusters1[i], clusters2[i])))
            print(results)
            res = adjustment*sum(results)/sum(weights)
            #res = adjustment*min(results)#*max(results)
            return res


def flatten(seq):
    return [i for i in set(seq)]


if __name__ == '__main__':
    sd = SoundDistance(consonant_conf='consonant_properties_for_genetic.yml', vowel_conf='vowel_properties.yml')
    # print(sd.data['l']['lateral_approximant'])
    # print(sd.data['l'])
    # print(sd.data['l̥'])
    #
    # print(sd.data['œ'])
    # print(sd.sound_similarity('ø', 'œ'))
    #
    #
    # print(sd.sound_similarity('l', 'l'))
    # print(sd.sound_similarity('l', 'l̥'))
    # print(sd.sound_similarity('l', 'p'))
    # print(sd.sound_similarity('l', 'b'))
    # print(sd.sound_similarity('f', 'v'))
    #
    # print(sd.sound_similarity('a','l'))
    # print(sd.sound_similarity('ə','ɘ'))
    # print(sd.sound_similarity('ə', 'i'))
    # print(sd.sound_similarity('ɒ', 'i'))
    #
    # print(sd.detect_sounds('e̞ø̞'))

    print('cat cat',sd.syllable_similarity('kæt', 'kɑt'))
    print('kæt', 'dɔɡ',sd.syllable_similarity('kæt', 'dɔɡ'))

    # print(sd.syllable_similarity('kæt', 'dʌk'))
    # print(sd.syllable_similarity('dɔɡ', 'dʌk'))
    print('dog dogs',sd.syllable_similarity('dɔɡ', 'dɔɡz'))
    # print(sd.syllable_similarity('dɔɡz', 'dɔɡzz'))
    # print(sd.syllable_similarity('dɔz', 'ftɔzz'))
    print('dog god',sd.syllable_similarity('dɔɡ', 'ɡɔd'))
    print('bone bonne',sd.syllable_similarity('bəʊn', 'bon'))
    # print(sd.syllable_similarity('bəʊn', 'bəʊt'))
    # print(sd.syllable_similarity('ʃən', 'ʃɛl'))
    # print(sd.syllable_similarity('fɛt', 'fənt'))
    # print(sd.syllable_similarity('t', 'nt'))
    # #print(sd.syllable_similarity('ʁɛst', 'ɹest'))
    # print(sd.syllable_similarity('dʒɹʌɡ', 'dɔɡ'))
    # print(sd.syllable_similarity('dʒɹʌɡ', 'dʁɔɡ'))
    # print(sd.syllable_similarity('hot','ot'))
    # #print(sd.syllable_similarity('n', 'p'))
    # #print(sd.syllable_similarity('dʒɹ', 'dʁ'))
    # #print(sd.syllable_similarity('dʒɹ', 'd'))
    # #print(sd.syllable_similarity('dʒ', 'd'))
    # #print(sd.syllable_similarity('leɪt', 'lit'))
    # print(sd.syllable_similarity('ɡœl','ɡəl'))
    # print(sd.syllable_similarity('ɡən','ɡəl'))
    # print(sd.data['p'])
    # print(sd.data['m'])
    # print(sd.syllable_similarity('dʒɹʌɡ', 'dɔɡ'))
    # print(sd.syllable_similarity('dʒɹʌɡ', 'dʁɔɡ'))
    # print(sd.syllable_similarity('dɹɔ','bjɔ'))
    # print(sd.syllable_similarity('dɔɡz', 'dɔɡzz'))
    # print(sd.syllable_similarity('bəʊn', 'bon'))
    # print(sd.syllable_similarity('dɔɡ', 'dʌk'))
    # print(sd.syllable_similarity('tbi', 'beɪ'))
    # print(sd.syllable_similarity('bi', 'beɪ'))
    #










