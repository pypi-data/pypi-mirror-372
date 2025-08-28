import epikit
import yaml
import os
from datetime import datetime

class inputdeck():

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
                "version": "v1.0.0"
            }
        }
        with open(destination + "/" + "meta.yaml", 'w') as metadata:
            yaml.dump(data, metadata, sort_keys=False)

    def write_experiments_metadata(self, destination):
        print("writing experiments metadata")

    def write_experiment_metadata(self, destination, experiment):
        print("writing experiment metadata")
        print("  " + experiment["name"])



class workflow():

    def __init__(self, infile="workflow.init", cell_line=None, description=None, experiment=None, replicate=0, 
                 resolution=100000, rootdir=",", timeunits='hrs', timevalues=[], treatments=[], ):

        # set defaults 
        self.cell_line   = cell_line 
        self.description = description
        self.experiment  = experiment 
        self.replicate   = replicate 
        self.resolution  = resolution
        self.rootdir     = os.path.abspath(rootdir)
        self.timeunits   = timeunits
        self.timevalues  = timevalues
        self.treatments  = treatments 
        self.version     = epikit.__version__

        # load data, if present
        with open(self.rootdir + "/" + infile, 'r') as initdata:
            data = yaml.safe_load(initdata)

        if data:
            for key, value in data.items():
                setattr(self, key, value)

        self.add_experimental_design()

    def __str__(self):
        return f"cell_line: {self.cell_line}\ndescription: {self.description}\nexperiment: {self.experiment}\nreplicate: {self.replicate}\nresolution: {self.resolution}\nrootdir: {self.rootdir}\ntimeunits: {self.timeunits}\ntimevalues: {self.timevalues}\ntreatments: {self.treatments}\nversion: {self.version}\ndatasets: " + str(self.datasets)

    def add_experimental_design(self):
        self.datasets = [] 
        with open(self.rootdir + "/experimental_design.csv") as ed:
            # this reader will skip the first line of a csv file (the column names)
            edfile = csv.DictReader(ed, delimiter=',')
            self.datasets.append([])
            self.datasets.append([])
            for row in edfile:
                self.datasets[0].append(row['filename_0'])
                self.datasets[1].append(row['filename_1'])

    def write(self, dest):
        with open(dest, 'w') as file:
            yaml.dump(self.__dict__, file)
