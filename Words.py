class Word():
    def __init__(self,language, spelling, syllables, spelling_ipa, syllables_ipa):
        """
        Class defining the words
        """
        self._language = language
        self._spelling = spelling
        self._syllables = syllables
        self._spelling_ipa = spelling_ipa
        self._syllables_ipa = syllables_ipa

    @property
    def language(self):
        return self._language

    @property
    def spelling(self):
        return self._spelling

    @property
    def syllables(self):
        return self._syllables

    @property
    def spelling_ipa(self):
        return self._spelling_ipa

    @property
    def syllables_ipa(self):
        return self._syllables_ipa