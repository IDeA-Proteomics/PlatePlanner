
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

    def __init__(self, rows, columns, vertical=True):
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.vertical = vertical
        if self.vertical:
            self.position_string_list = [f'{c}{i+1}' for i in range(self.columns) for c in row_letters[:self.rows]]
        else:
            self.position_string_list = [f'{c}{i+1}' for c in row_letters[:self.rows] for i in range(self.columns)]
        self.data = {pos : None for pos in self.position_string_list}
        self.projects = []
        return
    
    @property
    def number_of_wells(self):
        return (self.rows * self.columns)
    
    @property
    def positions(self):
        return [self.position_from_string(pos) for pos in self.position_string_list]


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
        start = start_pos.index
        if not start + project.num <= self.number_of_wells:
            raise NotEnoughWellsException(project.num, self.number_of_wells - start)
        wells = self.position_string_list[start:start + project.num]
        if all((self.data[well] == None for well in wells)):
            self.projects.append(project)
            for well, sample in list(zip(wells, project.samples)):
                self[well] = sample
        else:
            not_free = [well for well in wells if self[well] != None][0]
            raise WellNotFreeException(not_free)

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

    @classmethod
    def outputCSV(self, writer, plate):
        # if isinstance(plates, list):
        #     for plate in plates:
        #         Plate.outputCSV(writer, plate)
        # else:
        row = ['Index', 'Position', 'Project', 'Sample', str(plate.rows), str(plate.columns), str(plate.vertical)]
        writer.writerow(row)
        idx = 0
        for (well, sample) in plate.data.items():
            row = [
                idx,
                well,
                sample.project.name if sample is not None else 'EMPTY',
                sample.name if sample is not None else 'EMPTY'
            ]
            writer.writerow(row)
            idx += 1
        return
    
    @classmethod
    def saveToFile(self, filename, plates):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for plate in plates:
                Plate.outputCSV(writer, plate)            
        return
        
    @classmethod
    def loadFromFile(cls, filename):
        
        with open(filename, 'r') as file:
            reader = csv.reader(file)

            readList = list(reader)

            def getRCV(line):
                r = int(line[4])
                c = int(line[5])
                v = False if line[6] == 'False' else True
                return (r, c, v)

            # r = int(readList[0][4])
            # c = int(readList[0][5])
            # v = False if readList[0][6] == 'False' else True

            plates = []
            r, c, v = getRCV(readList[0])
            newPlate = Plate(r, c, v)

            pcount = 0

            for line in list(readList)[1:]:
                if line[0] == 'Index':
                    plates.append(newPlate)
                    r, c, v = getRCV(line)
                    newPlate = Plate(r, c, v)
                    continue
                position = line[1]
                proj_name = line[2]
                sample_name = line[3]
                if sample_name != 'EMPTY' and proj_name != 'EMPTY':
                    if proj_name not in [p.name for p in newPlate.projects]:
                        newPlate.projects.append(Project(proj_name, color_list[pcount%len(color_list)]))
                        pcount += 1
                        project = None
                    for p in newPlate.projects:
                        if p.name == proj_name:
                            project = p
                            break
                    sample = Sample(project, sample_name, newPlate.position_from_string(position))
                    project.addSample(sample)
                    newPlate[position] = sample
            plates.append(newPlate)
                    
        return plates