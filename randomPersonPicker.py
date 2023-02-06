import configparser
import json
import sys
import random
import requests
import os
from dotenv import load_dotenv

load_dotenv()


WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PICKER_NAME = os.getenv('PICKER_NAME')
PICKER_EMOJI = os.getenv('PICKER_EMOJI')
PICKER_COLOR = os.getenv('PICKER_COLOR')
PICKED_SECTION_NAME = os.getenv('PICKED_SECTION_NAME')
NOT_PICKED_SECTION_NAME = os.getenv('NOT_PICKED_SECTION_NAME')


def send_to_slack(picked_person: str, already_picked: list, remaining_not_picked: list):
    url = WEBHOOK_URL
    title = (f":squirrel: New person picked for daily :squirrel:")
    message = (
        f"The chosen one is: {picked_person}\n\nPersons already picked : {', '.join(already_picked)}\n\nPersons yet to be picked: {', '.join(remaining_not_picked)}")
    slack_data = {
        "username": PICKER_NAME,
        "icon_emoji": PICKER_EMOJI,
        "attachments": [
            {
                "color": PICKER_COLOR,
                "fields": [
                    {
                        "title": title,
                        "value": message,
                        "short": "false",
                    }
                ]
            }
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json",
               'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)


def read_file_return_config(file_path: str):
    config = configparser.ConfigParser()
    config.read(file_path)

    return config


def return_section_value(config: configparser.ConfigParser, section_name: str, section_value: str):
    return config[section_name][section_value]


def write_section_value(config: configparser.ConfigParser, section_name: str, section_value: str, value: str):
    config[section_name][section_value] = value


def pick_random_person_and_populate(picked: list, not_picked: list):
    if len(not_picked) == 0:
        not_picked = [None] * len(picked)
        for i in range(len(picked)):
            not_picked[i] = picked[i]

        picked = []

    index_picked = random.randrange(0, len(not_picked))
    person_picked = not_picked[index_picked]
    picked.append(person_picked)
    not_picked.remove(person_picked)

    result = dict()
    result['person_picked'] = person_picked
    result['picked'] = picked
    result['not_picked'] = not_picked

    return result


def main():
    file_name = './persons.txt'
    value_name = 'persons'
    picked_section_name = PICKED_SECTION_NAME
    not_picked_section_name = NOT_PICKED_SECTION_NAME

    config = read_file_return_config(file_name)

    picked = return_section_value(
        config, picked_section_name, value_name).split()
    not_picked = return_section_value(
        config, not_picked_section_name, value_name).split()

    results = pick_random_person_and_populate(picked, not_picked)

    write_section_value(config, picked_section_name,
                        value_name, ' '.join(results['picked']))
    write_section_value(config, not_picked_section_name,
                        value_name, ' '.join(results['not_picked']))

    with open(file_name, 'w') as configfile:
        config.write(configfile)

    send_to_slack(results['person_picked'],
                  results['picked'], results['not_picked'])


if __name__ == '__main__':
    main()
