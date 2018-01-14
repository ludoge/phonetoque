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
    args = parser.parse_args()
    if args.action in available_actions:
        try:
            required_args = __import__(f'scripts.{args.action}', globals(), locals(), ['hello'], 0).required_arguments
        except AttributeError:
            required_args = []
        all_args_good = True
        for required_arg in required_args:
            if not required_arg.replace("-","") in args.__dict__:
                #all_args_good = False
                #parser.error(f'Required argument {required_arg} for {args.action} must be specified')
                pass
            pass
        if not all_args_good:
            os.system(f'python scripts/{args.action}.py -h')
        #print([x for x in args.__dict__])

        formatted_args = " ".join([f"{'--' if len(x)>1 else '-'}{x} {args.__dict__[x]}"
                                   for x in args.__dict__ if args.__dict__[x] is not None and not x == "action"])
        #print (formatted_args)

        os.system(f'python scripts/{args.action}.py '+formatted_args)
    else:
        parser.error(f'Invalid scripts. Valid scripts are: {", ".join(available_actions)}')
