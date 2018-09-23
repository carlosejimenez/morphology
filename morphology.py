import math
import os
import re
import sys


# Returns definition for words in a dictionary.
def get_definition(word, entry, source):
    if len(entry) > 1:
        root = entry[2]
        
    else:
        root = word

    return word + ' ' + entry[0] + ' ROOT=' + root + ' SOURCE=' + source


# Returns a set of parses for all successful grammar rules.
def morphologies(word, rules):
    parses = set()
    for rule in rules:
        if rule[0] == 'SUFFIX':
            pattern = rule[1] + '$'
            
        else:
            pattern = '^' + rule[1]
            
        match = re.search(pattern, word)
        
        if match:
            i, f = map(int, match.span())
            if rule[2] == '-':
                sub_parses = morphologies(word[:i] + word[f:], rules)
                if len(sub_parses) > 0:
                    for sub_parse in sub_parses:
                        if re.search(rule[3], sub_parse[len(word) - f + i:]):
                            sub_parse = sub_parse.replace(rule[3], rule[5])
                            parses.add(sub_parse.replace(word[:i] + word[f:], word))
                            
                if (word[:i] + word[f:]).lower() in internal_dict:
                    for definition in internal_dict[(word[:i] + word[f:]).lower()]:
                        if definition[0] == rule[3]:
                            parse = word + ' ' + rule[5] + ' ROOT=' + word[:i] + word[f:] + ' SOURCE=morphology'
                            parses.add(parse)
                            
            else:
                sub_parses = morphologies(word[:i] + rule[2] + word[f:], rules)
                if len(sub_parses) > 0:
                    for sub_parse in sub_parses:
                        if re.search(rule[3], sub_parse[len(word) + len(rule[2]) - f + i:]):
                            sub_parse = sub_parse.replace(rule[3], rule[5])
                            parses.add(sub_parse.replace(word[:i] + rule[2] + word[f:], word))

                if (word[:i] + rule[2] + word[f:]).lower() in internal_dict:
                    for definition in internal_dict[(word[:i] + rule[2] + word[f:]).lower()]:

                        if definition[0] == rule[3]:
                            parse = word + ' ' + rule[5] + ' ROOT=' + word[:i] + rule[2] + word[ f:] + ' SOURCE=morphology'
                            parses.add(parse)
                            
        else:
            continue

    return parses

dictionary_file = open(sys.argv[1], "rt")
rules_file = open(sys.argv[2], 'rt')
test_file = open(sys.argv[3], 'rt')

internal_dict = {}

parses = {}

line_list = [line.strip().split(' ') for line in dictionary_file.readlines()]
dictionary_file.close()
for line in line_list:

    if line[0].lower() in internal_dict:
        internal_dict[line[0].lower()].append(line[1::])
        
    else:
        internal_dict[line[0].lower()] = [line[1::]]

rules = {tuple(re.split(r'\s+', line.strip()[:-1:])) for line in rules_file.readlines()}
rules_file.close()
tests = [line.strip() for line in test_file.readlines()]
test_file.close()

for word in tests:
    if word.lower() in internal_dict:
        for each_definition in internal_dict[word.lower()]:
            definition = get_definition(word.lower(), each_definition, 'dictionary').split(' ')

            if definition[0] in parses:
                parses[definition[0]].append(definition[1:])
                
            else:
                parses[definition[0]] = [definition[1:]]

    else:
        forms = morphologies(word.lower(), rules)
        if len(forms) > 0:
            for form in morphologies(word.lower(), rules):
                forms_list = form.split(' ')
                if forms_list[0] in parses:
                    parses[forms_list[0]].append(forms_list[1:])
                    
                else:
                    parses[forms_list[0]] = [forms_list[1:]]
                    
        else:
            default_parse = [['noun', 'ROOT=' + word.lower(), 'SOURCE=default']]
            parses[word.lower()] = default_parse

for word in parses:
    for parse in parses[word]:
        print(word, end='')
        for part in parse:
            print(' ' + part, end='')
        print()
    print()
