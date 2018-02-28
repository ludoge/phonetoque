import argparse
import random as rd
import src.provisioning as pr
import src.syllables as sy
import src.string_cleanup as sc
import yaml

if __name__ == '__main__':
    """
    Command to run this test
    python .\manager.py precision_test --language english -i weightedTest.txt
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', help='specify the language of the data used', required=True)
    parser.add_argument('-i', help='path to input word list', required=True, dest='input_file')
    parser.add_argument('--conf', help='path to configuration file for scripts', default='scripts/script_config.yml')
    args = parser.parse_args()
    with open(args.conf, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    available_languages = config['ipa_hyphenation_dict']

    if args.language not in available_languages:
        parser.error(f"Language \"{args.language}\" not available."
                     f"\nAvailable languages: {' ,'.join(available_languages)} ")

    config['simplifying'] = config['simplifying'][args.language]
    config['hyphenation_dict'] = config['hyphenation_dict'][args.language]
    config['ipa_hyphenation_dict'] = config['ipa_hyphenation_dict'][args.language]
    config['language'] = args.language

    request = pr.PhonetoqueRequest(config)

    with open(args.input_file, 'r', encoding="utf8") as input_file:
        word_list = input_file.read().split()
        for j in range(1,20): # to run the precision test on 20 random samples of 1500 words
            true = 0
            false = 0
            random_sample = rd.sample(word_list, 1500)
            for word in random_sample:
                cleaned = word.replace('10', '')
                unified_word = cleaned.replace('-', '')
                to_validate = request.get_ipa_syllabification(unified_word)
                if cleaned == to_validate:
                    true += 1
                else:
                    false +=1
            print(round(true/(true + false),3))

