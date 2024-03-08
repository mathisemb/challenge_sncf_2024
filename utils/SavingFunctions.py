import json

def save_holy_dict(holy_dict: dict):
    with open('../features_engineering/holydays.txt', 'w') as f :
        for k, (key, value) in enumerate(holy_dict.items()):
            f.write(f" {key} : {value} \n")
            if (k+1) % 6 == 0 : f.write("\n") 
    with open('../features_engineering/holydays_dict.json', 'w') as json_file:
        json.dump(holy_dict, json_file)

def load_dict(path: str):
    loaded_dict = {}
    with open(path, 'r') as json_file:
            loaded_dict = json.load(json_file)
    return loaded_dict