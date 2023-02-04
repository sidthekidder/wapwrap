import glob
import os
from collections import defaultdict

import pandas as pd
import re
import uuid
from tqdm import tqdm

config_all_columns = ["timestamp",
"conversationId",
"conversationWithName",
"senderName",
"text",
"language",
"platform"]

regex_left = r'[\u0000-\u001F\u0100-\uFFFF]?'
regex_datetime = r'[^\w]?([0-9./\-]{6,10},?[\sT][0-9:]{5,8}\s?[AP]?M?)[^\w]?\s?[\-\–]?\s'
regex_right = r'(([^:]+):\s)?(.*)'
regex_message = re.compile(f'^{regex_left}{regex_datetime}{regex_right}$')
MAX_EXPORTED_MESSAGES = 1000000

def infer_datetime_regex(f_path, max_messages=100):
    regex_message = re.compile(f'^{regex_left}({regex_datetime}){regex_right}$')
    patterns = defaultdict(int)
    with open(f_path, 'r', encoding="utf8") as f:
        for c, line in enumerate(f):
            if c == max_messages:
                break;
            matches = regex_message.search(line.upper())
            if matches:
                pattern = ""
                first = True
                last = 0
                nums = 0
                for i, l in enumerate(matches.group(1)):
                    if l in '0123456789':
                        if first:
                            pattern += '('
                            first = False
                        nums += 1
                    else:
                        if nums > 0:
                            pattern += '[0-9]'
                            if nums == 4:
                                pattern += '{4}'
                            else:
                                pattern += '{1,2}'
                            last = len(pattern)
                            nums = 0
                        if l in '.*+[]{}()\\|':
                            pattern += '\\'
                        pattern += l
                        if i > 0 and pattern[-2:] in ['AM','PM']:
                            pattern = pattern[:-2] + '[APap][Mm]'
                            last = len(pattern)
                pattern = pattern[0:last] + ')' + pattern[last:]
                patterns[pattern] += 1
    if len(patterns) > 0:
        regex_dt = max(patterns, key=patterns.get)
        # print(f'Datetime regex inferred: {regex_dt}')
    else:
        regex_dt = regex_datetime
    return re.compile(f'^{regex_left}{regex_dt}{regex_right}$')


def get_messages(file_path, max_exported_messages=MAX_EXPORTED_MESSAGES, infer_datetime=True):
    # print('Parsing Whatsapp data...')
    files = [file_path] # glob.glob(os.path.join(file_path, '*.txt'))
    if len(files) == 0:
        # print(f'No input files found under {file_path}')
        exit(0)

    data = parse_messages(files, infer_datetime)
    print('{:,} messages parsed.'.format(len(data)))
    if len(data) < 1:
        # print('Nothing to save.')
        exit(0)
    df = pd.DataFrame(data, columns=config_all_columns)
    # print('Done.')
    return df


def parse_messages(files, infer_datetime):
    data = []
    for f_path in files:
        # print(f'Reading {f_path}')
        f_name = os.path.basename(f_path)
        conversation_id = uuid.uuid4().hex
        participants = set()
        conversation_data = []
        text = None
        if infer_datetime:
            regex_message = infer_datetime_regex(f_path)
        num_lines = sum(1 for _ in open(f_path, 'r', encoding="utf8"))
        with open(f_path, 'r', encoding="utf8") as f:
            for line in tqdm(f, total=num_lines):
                # try to extract meta data from line
                matches = regex_message.search(line)
                if matches is None:
                    if text is None:
                        # We are expecting the first message but could not successfully parse line
                        print(f'Not covered: The line "{line.strip()}" in file {f_path} was ignored')
                    else:
                        # We are parsing a multi-line message, add whole line to existing messages and continue with next line
                        text += '\n' + line.strip()
                    continue
                groups = matches.groups()
                if groups[2] is None:
                    # sender name is missing but otherwise fits the pattern. Assumed to be app info.
                    # print(f'App info: The line "{line.strip()}" in file {f_path} was ignored')
                    continue
                try:
                    # get timestamp of message
                    new_timestamp = pd.to_datetime(groups[0]).timestamp()
                except ValueError:
                    # Datetime could not be parsed
                    # print(f'Could not parse datetime {groups[0]}. False match. Assuming multi-line message instead.')
                    text += '\n' + line.strip()
                    continue
                if text:
                    # Dump previous entry
                    conversation_data += [[timestamp, conversation_id, '', sender_name, text, '', '']]
                    if len(data) + len(conversation_data) >= MAX_EXPORTED_MESSAGES:
                        # dismiss current conversation data
                        print(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                        return data
                # set timestamp
                timestamp = new_timestamp
                # add other senders to participants
                sender_name = groups[2]
                participants.add(sender_name)
                text = groups[3].strip()
            # dump last line
            if text and sender_name:
                conversation_data += [[timestamp, conversation_id, '', sender_name, text, '', '']]
        # fill conversation_with
        if len(participants) == 0:
            conversation_with_name = ''
        else:
            conversation_with_name = '-'.join(sorted(list(participants)))
        for i in range(len(conversation_data)):
            conversation_data[i][2] = conversation_with_name
        # add to existing data
        data.extend(conversation_data)
    return data
