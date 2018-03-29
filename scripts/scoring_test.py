from src.scores import Scoring
import argparse
import yaml

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', help='specify the source language of the data used', required=True)
    parser.add_argument('--language2', help='specify the destination language of the data used', required=True)
    parser.add_argument('-i', help='path to input word list', required=True, dest='input_file')
    parser.add_argument('--conf', help='path to configuration file for scripts', default='scripts/script_config.yml')
    args = parser.parse_args()

    with open(args.conf, encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config['language'] = args.language
    config['language2'] = args.language2
    
    english_to_french = Scoring(config)

    score = english_to_french.get_score(args.input_file)
    print(score)