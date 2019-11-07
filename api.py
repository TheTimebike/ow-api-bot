import json, urllib.parse, http.cookies
http.cookies._is_legal_key = lambda _: True
import requests as _requests
from os import path, makedirs

BASE_ROUTE = "https://owapi.net/api/v3"
STATS_ROUTE = "https://owapi.net/api/v3/u/{0}/stats?platform={1}"
HEROES_ROUTE = "https://owapi.net/api/v3/u/{0}/heroes?platform={1}"
ACHIEVEMENT_ROUTE = "https://owapi.net/api/v3/u/{0}/achievements?platform={1}"

class Config:
    def __init__(self, directory, server_id):
        self.directory = "./{0}/".format(directory)
        self.filepath = "./{0}/{1}.json".format(directory, server_id)
        self.make()
    
    def make(self):
        if not path.exists(self.directory):
            makedirs(self.directory)
        if not path.isfile(self.filepath):
            with open(self.filepath, "w+") as out:
                json.dump({
                    "region": "us",
                    "role": None,
                    "bronze_id": None,
                    "silver_id": None,
                    "gold_id": None,
                    "platinum_id": None,
                    "diamond_id": None,
                    "master_id": None,
                    "grandmaster_id": None,
                    "time": {},
                    "members": {}
                }, out, indent=4)

    def load(self):
        with open(self.filepath, "r") as out:
            config = json.load(out)
        return config

    def save(self, new_config):
        with open(self.filepath, "w+") as out:
            json.dump(new_config, out, indent=4)

    def update(self, key, attr):
        conf = self.load()
        conf[key] = attr
        self.save(conf)

    def get_conversion_table(self, table):
        _index = _requests.get("https://raw.githubusercontent.com/TheTimebike/ow-api-bot/master/conversion_tables/index.json")
        _data_url = _index.json()[table]
        _data = _requests.get(_data_url)
        return _data.json()      

class Api:
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.headers = {
            "X-API-Key": self.api_token,
            "User-agent": "OWMN Bot"
        }

    def get(self, request):
        self._requestData = _requests.get(urllib.parse.quote(request, safe=':/?&=,.'), headers=self.headers)
        #print(json.dumps(self._requestData, indent=4))
        return self._requestData.json()