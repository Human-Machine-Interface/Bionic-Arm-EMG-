import os
import ast
import json

def get_dict(path):
    print(path)
    if not os.path.isfile(path):
        id_dict = {1: [1]}
        just_created = True
        with open('subjects_id_list.txt', 'w') as file:
            file.write(json.dumps(id_dict))
    else:
        with open('subjects_id_list.txt', 'r') as file:
            id_dict = ast.literal_eval(file.read())
        just_created = False
    return id_dict, just_created

def input_in_list(str, list_):
    if str not in list_:
        raise Exception("Choose a valid option. Try again")

def give_options(path, input_str):
    input_in_list(int(input_str), [1,2,3])
    id_dict, just_created = get_dict(path)

    if(input_str == "1"):
        if  just_created:
            experiment_num = 1
            id_subject = 1

        else:
            last_key = int(list(id_dict.keys())[-1])
            id_subject = last_key + 1
            experiment_num = 1
            id_dict[id_subject] = [experiment_num]

        with open('subjects_id_list.txt', 'w') as file:
            file.write(json.dumps(id_dict))

    elif (input_str == "2"):
        with open('subjects_id_list.txt', 'r') as file:
            registered_subjects = list(ast.literal_eval(file.read()).keys())
        id_subject = input("Great! The registered subjects are {}. Please choose one:".format(registered_subjects))
        input_in_list(id_subject, registered_subjects)
        experiment_num = id_dict[id_subject][-1] + 1
        id_dict[id_subject].append(experiment_num)
    elif (input_str == "3"):
        with open('subjects_id_list.txt', 'r') as file:
            registered_subjects = list(ast.literal_eval(file.read()).keys())
        id_subject = input("Great! The registered subjects are {}. Please choose one:".format(registered_subjects))
        input_in_list(id_subject, registered_subjects)
        with open('subjects_id_list.txt', 'r') as file:
            registered_experiments = ast.literal_eval(file.read())[id_subject]
        experiment_num = input("Great! The registered experiments for subject number {} are {}. Please choose one:".format(id_subject,registered_experiments))
        input_in_list(int(experiment_num), registered_experiments)

    with open('subjects_id_list.txt', 'w') as file:
        file.write(json.dumps(id_dict))
    return id_subject, experiment_num