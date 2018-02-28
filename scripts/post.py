import argparse
import src.provisioning as pr
import src.syllables as sy
import src.string_cleanup as sc
import yaml

if __name__ == '__main__':
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


    cleaner = sc.StringCleanup(config)
    raw_data = cleaner.read_pronunciation_file_as_dict(args.input_file)
    clean_data = {k: [cleaner.simplify_separators(cleaner.cleanup(x)) for x in v] for k, v in raw_data.items()}

    request = pr.PhonetoqueRequest(config)
 
 
    request.pronunciations = clean_data
    # request.prepare_data()

    # request.post_all_words()

    request.get_all_syllables()
    print("got all syllables")
    request.get_max_syllables()
    print("got max syllables")
    request.get_similar_syllables()
    # request.post_all_syllables()