
import csv
from PlateExceptions import *
from collections import OrderedDict
### Horizontal plates
# position_string_list = [f'{c}{i+1}' for c in 'ABCDEFGH' for i in range(12)]

### Vertical plates
position_string_list = [f'{c}{i+1}' for i in range(12) for c in 'ABCDEFGH']

class Position(object):

    def __init__(self, row, col, idx, lab):

        self.row = row
        self.column = col
        self.index = idx
        self.label = lab
        return
    
    @classmethod
    def from_index(cls, idx):
        row = "ABCDEFGH".index(position_string_list[idx][:1])
        col = int(position_string_list[idx][1:]) -1
        lab = position_string_list[idx]
        return cls(row, col, idx, lab)

    @classmethod
    def from_rowcol(cls, row, col):
        row = row
        col = col
        idx = position_string_list.index(f'{"ABCDEFGH"[row]}{col + 1}')
        lab = position_string_list[idx]
        return cls(row, col, idx, lab)
    
    @classmethod
    def from_string(cls, instr):
        idx = position_string_list.index(instr)
        return Position.from_index(idx)
    


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

    def __init__(self):
        super().__init__()
        self.data = {pos : None for pos in position_string_list}
        self.projects = []
        return

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
        return [Position.from_string(key) for key in self.data.keys() if self.data[key] is not None]

    def getFreeWells(self):
        return [Position.from_string(key) for key in self.data.keys() if self.data[key] is None]

    def getSamples(self):
        return [sample for sample in self.data.values()]

    def addProject(self, project, start_pos):
        wells = position_string_list[position_string_list.index(start_pos.label):position_string_list.index(start_pos.label) + project.num]
        if all((self.data[well] == None for well in wells)):
            self.projects.append(project)
            for well, sample in list(zip(wells, project.samples)):
                self.data[well] = sample
        else:
            raise NotEnoughWellsException

    
    def outputToFile(self, filename):

        with open(filename, 'w', newline='') as file:

            writer = csv.writer(file)
            
            row = ['Index', 'Position', 'Project', 'Sample']
            print(row)
            writer.writerow(row)
            idx = 0
            for (well, sample) in self.data.items():
                row = [
                    idx,
                    well,
                    sample.project.name if sample is not None else 'EMPTY',
                    sample.name if sample is not None else 'EMPTY'
                ]
                print(row)
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
                    sample = Sample(project, sample_name, Position.from_string(position))
                    project.addSample(sample)
                    self[position] = sample
                    
        return

    

    
# class OldPlate(object):

#     def __init__(self, project_list):

#         self.project_list = project_list

#         return

#     def addProject(self, project):

#         if isinstance(project, Project):
            
#             if self.checkFit(project):
#                 self.project_list.append(project)
#             else:
#                 raise WellNotFreeException


#         elif isinstance(project, list) and all(isinstance(proj, Project) for proj in project):

#             for proj in project:
#                 self.addProject(proj)

#         return
    
#     def checkFit(self, project):
#         if project.start_position.index + project.num > 96:
#             return False        

#         used = [pos.index for pos in self.getUsedWells()]
#         for sample in project.getSamples():
#             if sample.position.index in used:
#                 return False
#         return True
    
    
#     def getSamples(self):

#         return [sample for project in self.project_list for sample in project.getSamples()]
    
#     def getUsedWells(self):

#         return [sample.position for sample in self.getSamples()]
    
#     def getFreeWells(self):

#         used = [pos.index for pos in self.getUsedWells()]
#         return [Position.from_index(i) for i in range(95) if i not in used]



#     def outputToFile(self, filename):

#         with open(filename, 'w') as file:

#             writer = csv.writer(file)

#             samples = self.getSamples()
#             samples.sort(key=lambda s: s.position.index)

#             writer.writerow(['Index', 'Position', 'Project', 'Sample'])
#             idx = 0
#             for sample in samples:
#                 while sample.position.index > idx:
#                     writer.writerow([idx, Position.from_index(idx).label, 'EMPTY', 'EMPTY'])
#                     idx += 1
#                 writer.writerow([sample.position.index, sample.position.label, sample.project.name, sample.name])
#                 idx += 1
#             while idx < 96:
#                 writer.writerow([idx, Position.from_index(idx).label, 'EMPTY', 'EMPTY'])
#                 idx += 1

#         return
    
#     def loadFromFile(self, filename):

#         projects = {}
#         used = []
#         idx = 0
#         with open(filename, 'r') as file:
#             reader = csv.reader(file)
#             for line in list(reader)[1:]:
#                 well_index = int(line[0])
#                 if well_index != idx:
#                     raise MissingEntryException
#                 idx += 1
#                 if well_index not in used:
#                     used.append(well_index)
#                 else:
#                     raise DuplicateEntryException
#                 proj_name = line[2]
#                 if proj_name == 'EMPTY':
#                     continue
#                 if proj_name not in projects.keys():
#                     proj = Project(proj_name, color_list[len(projects)%len(color_list)])
#                     projects[proj_name] = proj
                
#                 sample = Sample(projects[proj_name], line[3], Position.from_index(int(line[0])))
#                 projects[proj_name].addSample(sample)

#         for project in projects.values():
#             self.addProject(project)


                






