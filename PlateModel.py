
import csv
from PlateExceptions import *
from collections import OrderedDict
### Horizontal plates
# position_string_list = [f'{c}{i+1}' for c in 'ABCDEFGH' for i in range(12)]

### Vertical plates
# position_string_list = [f'{c}{i+1}' for i in range(12) for c in 'ABCDEFGH']

row_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Position(object):

    def __init__(self, row, col, idx, lab):

        self.row = row
        self.column = col
        self.index = idx
        self.label = lab
        return
    
    # @classmethod
    # def from_index(cls, idx):
    #     row = "ABCDEFGH".index(position_string_list[idx][:1])
    #     col = int(position_string_list[idx][1:]) -1
    #     lab = position_string_list[idx]
    #     return cls(row, col, idx, lab)

    # @classmethod
    # def from_rowcol(cls, row, col):
    #     row = row
    #     col = col
    #     idx = position_string_list.index(f'{"ABCDEFGH"[row]}{col + 1}')
    #     lab = position_string_list[idx]
    #     return cls(row, col, idx, lab)
    
    # @classmethod
    # def from_string(cls, instr):
    #     idx = position_string_list.index(instr)
    #     return Position.from_index(idx)
    


class Sample(object):

    def __init__(self, project, name, position):
        
        self.project = project
        self.name = name
        self.position = position

        return
    

class Project(object):

    def __init__(self, name, color, num_samples = 0):

        self.name = name
        self.num = num_samples
        self.color = color
        
        self.samples = [Sample(project=self, name=f'Sample{i + 1}', position=None) for i in range(self.num)]

        return
    
    def addSample(self, sample):
        self.samples.append(sample)
        self.num += 1
        return

color_list = ['red', 'orange', 'yellow', 'green', 'purple', 'cyan', 'magenta', 'brown']

class Plate(OrderedDict):

    def __init__(self, rows, columns):
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.position_string_list = [f'{c}{i+1}' for i in range(self.columns) for c in row_letters[:self.rows]]
        self.data = {pos : None for pos in self.position_string_list}
        self.projects = []
        return
    
    @property
    def number_of_wells(self):
        return (self.rows * self.columns) + 1

    def __setitem__(self, key, value):
        if key not in self.data.keys():
            raise KeyError
        if not isinstance(value, Sample):
            raise TypeError("Only samples can be assigned to plate wells")
        self.data[key] = value
    
    def __getitem__(self, key):
        if isinstance(key, Position):
            return self.data[key.label]
        else:
            return self.data[key]

    def getUsedWells(self):
        return [self.position_from_string(key) for key in self.data.keys() if self.data[key] is not None]

    def getFreeWells(self):
        return [self.position_from_string(key) for key in self.data.keys() if self.data[key] is None]

    def getSamples(self):
        return [sample for sample in self.data.values()]

    def addProject(self, project, start_pos):
        start = self.position_string_list.index(start_pos.label)
        wells = self.position_string_list[start:start + project.num]
        if all((self.data[well] == None for well in wells)) and start + project.num < self.number_of_wells:
            self.projects.append(project)
            for well, sample in list(zip(wells, project.samples)):
                self.data[well] = sample
        else:
            raise NotEnoughWellsException

    def position_from_index(self, idx):
        row = row_letters.index(self.position_string_list[idx][:1])
        col = int(self.position_string_list[idx][1:]) -1
        lab = self.position_string_list[idx]
        return Position(row, col, idx, lab)

    def position_from_rowcol(self, row, col):
        row = row
        col = col
        idx = self.position_string_list.index(f'{row_letters[row]}{col + 1}')
        lab = self.position_string_list[idx]
        return Position(row, col, idx, lab)
    
    def position_from_string(self, instr):
        idx = self.position_string_list.index(instr)
        return self.position_from_index(idx)

    
    def outputToFile(self, filename):

        with open(filename, 'w', newline='') as file:

            writer = csv.writer(file)
            
            row = ['Index', 'Position', 'Project', 'Sample']
            writer.writerow(row)
            idx = 0
            for (well, sample) in self.data.items():
                row = [
                    idx,
                    well,
                    sample.project.name if sample is not None else 'EMPTY',
                    sample.name if sample is not None else 'EMPTY'
                ]
                writer.writerow(row)
                idx += 1
        return

    def loadFromFile(self, filename):
        
        with open(filename, 'r') as file:
            reader = csv.reader(file)

            for line in list(reader)[1:]:
                position = line[1]
                proj_name = line[2]
                sample_name = line[3]
                if sample_name != 'EMPTY' and proj_name != 'EMPTY':
                    if proj_name not in [p.name for p in self.projects]:
                        self.projects.append(Project(proj_name, color_list[len(self.projects)%len(color_list)]))
                        project = None
                    for p in self.projects:
                        if p.name == proj_name:
                            project = p
                            break
                    sample = Sample(project, sample_name, self.position_from_string(position))
                    project.addSample(sample)
                    self[position] = sample
                    
        return