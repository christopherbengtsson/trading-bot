import json
from termcolor import cprint


def print_json(message):
    try:
        json_message = json.dumps(message, indent=4)
        print(json_message)
    except:
        cprint('Unable to prettify Json', 'red', attrs=['bold'])
        print(message)
