import argparse
import src.string_cleanup as scl
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

    cleaner = scl.StringCleanup(config)
    raw_prons = cleaner.read_pronunciation_file_as_dict(args.input_file)
    cleaned_prons = [cleaner.simplify_separators(cleaner.cleanup(x)) for x in raw_prons if not cleaner.cleanup(x) == '']
    cleaned_prons = {k: [cleaner.simplify_separators(cleaner.cleanup(x)) for x in v if not cleaner.cleanup(x) == ''] for k,v in raw_prons.items()}

    with open(args.output_file, mode='w', encoding='utf-8') as f:
        for key in cleaned_prons:
            prons = cleaned_prons[key]
            f.write(f"{key} {' '.join(prons)}\n")
