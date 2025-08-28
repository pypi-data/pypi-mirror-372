import epikit
import yaml
import os
from datetime import datetime


class ensemble():

    __version__ = "1.2"

    def __init__(self, infile):

        self.input = infile

        # load data, if present
        with open(infile, 'r') as initdata:
            data = yaml.safe_load(initdata)

        if data:
            for key, value in data.items():
                setattr(self, key, value)

    def write(self, dest):
        with open(dest, 'w') as file:
            yaml.dump(self.__dict__, file)

    def create_ensemble_metadata(self, destination):
        os.makedirs(destination, exist_ok=True)
        self.write_ensemble_metadata(destination)
        self.write_experiments_metadata(destination)

        for e in self.ensemble["experiments"]:
            self.write_experiment_metadata(destination, e)

    def write_ensemble_metadata(self, destination):
        now = datetime.now()
        data = {
            "description": {
                "title": self.ensemble["meta"]["title"],
                "desc":  self.ensemble["meta"]["desc"]
            },
            "release": {
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S")
            },
            "hierarchy": {
                "version": epikit.ensemble.__version__
            }
        }
        with open(destination + "/" + "meta.yaml", 'w') as metadata:
            yaml.dump(data, metadata, sort_keys=False)

    def write_experiments_metadata(self, destination):
        print("writing experiments metadata")

    def write_experiment_metadata(self, destination, experiment):
        print("writing experiment metadata")
        print("  " + experiment["name"])

