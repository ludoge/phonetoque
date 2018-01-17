import argparse
import src.string_cleanup as sc
import src.syllables as sy
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', help='specify the language of the data used', required=True)
    parser.add_argument('-i', help='path to input word list', required=True, dest='input_file')
    parser.add_argument('-o', help='path to output file', required=True, dest='output_file')
    parser.add_argument('--conf', help='path to configuration file for scripts', default='scripts/script_config.yml')
    args = parser.parse_args()

    with open(args.conf, mode='r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config['simplifying'] = config['simplifying'][args.language]

    cleaner = sc.StringCleanup(config)
    raw_prons = cleaner.read_pronunciation_file_as_list(args.input_file)
    cleaned_prons = [cleaner.cleanup(x) for x in raw_prons if not cleaner.cleanup(x) == '']

    sc = sy.SyllableProcessor(config, cleaned_prons)
    sc.get_known_syllables()

    syllabified_prons = [cleaner.simplify_separators(x) for x in cleaned_prons if sc.is_syllabified(x)]

    with open(args.output_file, mode='w', encoding='utf-8') as f:
        for pron in syllabified_prons:
            print(pron)
            f.write(f"{pron}\n")