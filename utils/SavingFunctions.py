import json

def save_holy_dict(holy_dict: dict, name = 'holydays', path = '../features_engineering/' ):
    
    seq_length = 6 if name[:8] == 'holydays' else 3

    with open(path + name + '.txt', 'w') as f :
        for k, (key, value) in enumerate(holy_dict.items()):
            f.write(f" {key} : {value} \n")
            if (k+1) % seq_length == 0 : f.write("\n") 

    with open(path + name + '.json', 'w') as json_file:
        json.dump(holy_dict, json_file)


def load_dict(name = 'holydays', path = '../features_engineering/' ):
    loaded_dict = {}
    with open(path + name + '.json', 'r') as json_file:
            loaded_dict = json.load(json_file)
    return loaded_dict