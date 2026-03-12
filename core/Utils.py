import json

def read_token(fpath:str) -> str:
    with open(fpath, 'r') as tokenfile:
        token = tokenfile.readline().strip() #It should be on the first line
    #
    return token
#

def load_json_config(cfgfile: str) -> dict:
    with open(cfgfile, "r") as f:
        return json.load(f)
    #
#