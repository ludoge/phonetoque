def has_a_vowel(pron, config):
    vowels = config['vowels']
    found_vowel = False
    for j in range(len(pron)):
        if pron[j] in vowels:
            found_vowel = True
    return found_vowel


def is_syllabified(pron, config, known):
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
        res = len(pron) < 5 and has_a_vowel(pron, config)
    return res


def is_fully_syllabified(pron, config):
    return ("." in pron or len(pron) < 5 or has_single_vowel_group(pron, config)) and has_a_vowel(pron, config)


def get_known_syllables(prons, config):
    res = []
    for pron in prons:
        if is_fully_syllabified(pron, config):
            split = pron.replace("ˈ", ".").replace("ˌ", ".").split(".")
            res = res + [s for s in split if s not in res and not s == '']
    return res


def has_single_vowel_group(pron, config):
    """
    detects if a pronunciation only contains a single vowel or group thereof, which usually means it is monosyllabic
    :param pron:
    :return:
    """
    vowels = config['vowels']
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
