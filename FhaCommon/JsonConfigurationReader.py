from collections import namedtuple
import json


class JsonConfigurationReader:
    def __init__(self, directory):
        self.directory = directory

    def read(self, file):
        with open(self.directory + file + '.json') as myFile:
            data = myFile.read()

        return json.loads(data, object_hook=self._decoder)

    def _decoder(self, dict):
        return namedtuple('X', dict.keys())(*dict.values())


default_reader = JsonConfigurationReader('/home/pi/Projects/FeldsparConfiguration/')

