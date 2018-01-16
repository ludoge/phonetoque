class SyllableProcessor:
    def __init__(self, config, prons=[]):
        self.vowels = config['vowels']
        self.pronunciations = prons
        self.known_syllables = []

    def has_a_vowel(self, pron):
        found_vowel = False
        for j in range(len(pron)):
            if pron[j] in self.vowels:
                found_vowel = True
        return found_vowel

    def is_syllabified(self, pron):
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
                    if len(s) > 4 and s not in self.known_syllables:  # 3 is arbitrary; there are some false positives but not too many
                        res = False
            else:  # both intonation marks
                split = pron.replace("ˈ", ".").replace("ˌ", ".").split(".")
                for s in split:
                    if len(s) > 4 and s not in self.known_syllables:
                        res = False
        else:
            res = len(pron) < 5 and self.has_a_vowel(pron)
        return res

    def is_fully_syllabified(self, pron):
        return ("." in pron or len(pron) < 5 or self.has_single_vowel_group(pron)) and self.has_a_vowel(pron)

    def get_known_syllables(self):
        res = []
        for pron in self.pronunciations:
            if self.is_fully_syllabified(pron):
                split = pron.replace("ˈ", ".").replace("ˌ", ".").split(".")
                res = res + [s for s in split if s not in res and not s == '' and s not in self.known_syllables]
        self.known_syllables = res

    def has_single_vowel_group(self, pron):
        """
        detects if a pronunciation only contains a single vowel or group thereof, which usually means it is monosyllabic
        :param pron:
        :return:
        """
        found_vowel = False
        consonant_after_vowel = False
        second_vowel = False
        for j in range(0, len(pron)):
            if pron[j] in self.vowels:
                if not found_vowel:
                    found_vowel = True
                elif consonant_after_vowel:
                    second_vowel = True
            else:
                if found_vowel:
                    consonant_after_vowel = True
        return found_vowel and not second_vowel
