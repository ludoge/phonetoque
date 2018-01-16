import argparse
import sys
sys.path.append('src')  # if there is a better way, please tell me
import string_cleanup as sc
import syllables as sy
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

    raw_prons = sc.read_pronunciation_file_as_list(args.input_file)
    cleaned_prons = [sc.cleanup(x, config) for x in raw_prons if not sc.cleanup(x, config) == '']
    known_syllables = sy.get_known_syllables(cleaned_prons, config)

    syllabified_prons = prons = [sc.simplify_separators(x,config) for x in cleaned_prons if sy.is_syllabified(x, config, known_syllables)]

    with open(args.output_file, mode='w', encoding='utf-8') as f:
        for pron in syllabified_prons:
            f.write(f"{pron}\n")