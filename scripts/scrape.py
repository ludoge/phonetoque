import argparse
import src.wiktionary_scraper as ws
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', help='specify the language of the data used', required=True)
    parser.add_argument('-i', help='path to input word list', required=True, dest='input_file')
    parser.add_argument('-o', help='path to output file', required=True, dest='output_file')
    parser.add_argument('--conf', help='path to configuration file for scripts', default='scripts/script_config.yml')
    args = parser.parse_args()

    with open(args.conf, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    available_languages = config['scraper_languages']

    if args.language not in available_languages:
        parser.error(f"Language \"{args.language}\" not available."
                     f"\nAvailable languages: {' ,'.join(available_languages)} ")

    scraper = ws.Scraper(args.language)
    scraper.read_word_list(args.input_file)
    scraper.write_line_by_line(args.output_file)
