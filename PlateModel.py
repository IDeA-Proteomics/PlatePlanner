
import csv
from PlateExceptions import *

# position_string_list = [f'{c}{i+1}' for c in 'ABCDEFGH' for i in range(12)]
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

    def __init__(self, name, color, start_position = Position.from_index(95), num_samples = 0):

        self.name = name
        self.start_position = start_position
        self.num = num_samples
        self.color = color

        try:
            self.samples = [Sample(project=self, name=f'Sample{i + 1}', position=Position.from_index(self.start_position.index + i)) for i in range(self.num)]
        except IndexError:
            raise NotEnoughWellsException

        return
    
    def getSamples(self):
        return self.samples
    
    def addSample(self, sample):
        self.samples.append(sample)
        self.num += 1
        if sample.position.index < self.start_position.index:
            self.start_position = sample.position
        return

color_list = ['red', 'orange', 'yellow', 'green', 'purple', 'cyan', 'magenta', 'brown']
    
class Plate(object):

    def __init__(self, project_list):

        self.project_list = project_list

        return

    def addProject(self, project):

        if isinstance(project, Project):
            
            if self.checkFit(project):
                self.project_list.append(project)
            else:
                raise WellNotFreeException


        elif isinstance(project, list) and all(isinstance(proj, Project) for proj in project):

            for proj in project:
                self.addProject(proj)

        return
    
    def checkFit(self, project):
        if project.start_position.index + project.num > 96:
            return False        

        free = [pos.index for pos in self.getUsedWells()]
        for sample in project.getSamples():
            if sample.position.index in free:
                return False
        return True
    
    
    def getSamples(self):

        return [sample for project in self.project_list for sample in project.getSamples()]
    
    def getUsedWells(self):

        return [sample.position for sample in self.getSamples()]
    
    def getFreeWells(self):

        used = [pos.index for pos in self.getUsedWells()]
        return [Position.from_index(i) for i in range(95) if i not in used]
    
    # def checkPlate(self):
    #     seen = set()
    #     duplicates = []
    #     for i in [sample.position.index for project in self.project_list for sample in project]:
    #         if i not in seen:
    #             seen.add(i)
    #         elif i not in duplicates:
    #             duplicates.append(i)

    #     if len(duplicates):
    #         raise WellNotFreeException(Position.from_index(duplicates[0]))



    def outputToFile(self, filename):

        with open(filename, 'w') as file:

            writer = csv.writer(file)

            samples = self.getSamples()
            samples.sort(key=lambda s: s.position.index)

            writer.writerow(['Index', 'Position', 'Project', 'Sample'])
            idx = 0
            for sample in samples:
                while sample.position.index > idx:
                    writer.writerow([idx, Position.from_index(idx).label, 'EMPTY', 'EMPTY'])
                    idx += 1
                writer.writerow([sample.position.index, sample.position.label, sample.project.name, sample.name])
                idx += 1

        return
    
    def loadFromFile(self, filename):

        projects = {}
        used = []
        idx = 0
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for line in list(reader)[1:]:
                well_index = int(line[0])
                if well_index != idx:
                    raise MissingEntryException
                idx += 1
                if well_index not in used:
                    used.append(well_index)
                else:
                    raise DuplicateEntryException
                proj_name = line[2]
                if proj_name == 'EMPTY':
                    continue
                if proj_name not in projects.keys():
                    proj = Project(proj_name, color_list[len(projects)%len(color_list)])
                    projects[proj_name] = proj
                
                sample = Sample(projects[proj_name], line[3], Position.from_index(int(line[0])))
                projects[proj_name].addSample(sample)

        for project in projects.values():
            self.addProject(project)


                






