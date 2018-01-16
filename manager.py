import argparse
import os

if __name__ == '__main__':
    available_actions = [filename[:-3] for filename in os.listdir('./scripts') if filename[-3:] == ".py"
                         and not filename[:2] == "__"]
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='')
    parser.add_argument('--language', help='specify the language of the data used')
    parser.add_argument('-i')
    parser.add_argument('-o')
    parser.add_argument('--conf', help='path to configuration file for scripts', default='scripts/script_config.yml')
    args = parser.parse_args()
    if args.action in available_actions:
        formatted_args = " ".join([f"{'--' if len(x)>1 else '-'}{x} {args.__dict__[x]}"
                                   for x in args.__dict__ if args.__dict__[x] is not None and not x == "action"])

        # print (formatted_args)

        os.system(f'python -m scripts.{args.action} ' + formatted_args)
    else:
        parser.error(f'Invalid script. Valid scripts are: {", ".join(available_actions)}')
