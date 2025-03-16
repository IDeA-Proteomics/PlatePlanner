
import os
import PlateImage
import Popups
from Worklist import WorkList
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from idea_utils.PlateExceptions import *
from idea_utils.PlateModel import Sample, Project, Plate


color_list = ['red', 'green', 'orange', 'purple', 'yellow', 'blue', 'magenta', 'brown', 'cyan']

####  TODO:
###      let Position have a reference to Plate
###      When adding projects, should see some sort of selection indication of wells used based on count - in Popups
###      Right Click Menu
###      When names don't fit, make just the one long one small instead of all of them
###      Make just the name small, but fit the whole number ID since it really is what matters. 


class PlateApp(tk.Frame):

    def __init__(self, root, file=None):

        self.root_window = root
        tk.Frame.__init__(self, self.root_window)

        # self.root_window.report_callback_exception = self.exceptionHandler

        self._current_file = file  ### abspath to currently open file
        self.current_file_string = tk.StringVar(value="" if self._current_file == None else os.path.basename(self._current_file))

        self.plates = [Plate("Plate_1", rows=8, columns=12)]

        self.selected_position = (self.plates[0], None)
        self.selectionChangeListeners = []

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side = tk.TOP)

        self.plate_outer_frame = tk.Frame(self.main_frame)
        self.plate_outer_frame.pack(side=tk.LEFT)        

        self.proj_frame = tk.Frame(self.main_frame)
        self.proj_frame.pack(side=tk.LEFT)

        self.resetPlates()

        self.file_label = tk.Label(self.proj_frame, textvariable=self.current_file_string)
        self.file_label.pack(side=tk.TOP)

        self.add_button = tk.Button(self.proj_frame, text="Add", command=self.onAdd)
        self.add_button.pack(side=tk.TOP)

        self.proj_label = tk.Label(self.proj_frame, text="Projects ", width=50)
        self.proj_label.pack(side=tk.TOP)

        self.proj_list_frame = tk.Frame(self.proj_frame)
        self.proj_list_frame.pack(side=tk.TOP)

        self.createMenu()

        

        ### if initialized with file name, open that file
        if self._current_file is not None:
            self.loadFromFile(self._current_file)

        return

    
    @property
    def current_file(self):
        return self._current_file
    @current_file.setter
    def current_file(self, file):
        if file is not None:
            self._current_file = os.path.abspath(file)
            self.current_file_string.set(os.path.basename(self._current_file))
        else:
            self._current_file = None
            self.current_file_string.set("Unsaved")
        return
    
    def resetPlates(self):
        for widget in self.plate_outer_frame.winfo_children():
            widget.destroy()
        self.plate_frames = []
        self.plate_images = []

        self.plate_frames = [tk.Frame(self.plate_outer_frame) for _ in range(2 if self.plate_count > 1 else 1)]
        for f in self.plate_frames:
            f.pack(side=tk.LEFT, expand=True, fill=tk.Y)

        for i in range(min(4, self.plate_count)):
            platex = 10
            platey = 10
            platew = 900 if self.plate_count == 1 else 600 if self.plate_count < 3 else 450
            platef = 0 if i<1 else i%2
            self.plate_images.append(PlateImage.PlateWidget(self.plate_frames[platef], plate=self.plates[i], platex=platex, platey=platey, platew=platew, onWellClickHandler=self.onWellClick, onWellRightClickHandler=self.onWellRightClick))
        for i in range(len(self.plate_images)):
            self.plate_images[i].pack(side=tk.TOP, anchor=tk.NW)

        self.resetSelection()

        return

    def redrawSamples(self):
        for p in self.plate_images:
            p.redrawSamples()

    
    @property
    def projects(self):
        return {project for plate in self.plates for project in plate.projects}
    
    @property 
    def plate_count(self):
        return len(self.plates)
    
    @property
    def sample_count(self):
        return len([s for p in self.plates for s in p.getSamples()])
    
    def getImage(self, plate):
        for i, p in enumerate(self.plates):
            if p is plate:
                return self.plate_images[i]
        return 
    
    def getNextPlate(self, plate):
        for i, p in enumerate(self.plates):
            if p is plate:
                if self.plate_count > i+1:
                    return self.plates[i+1]
        return None
    
    def resetSelection(self):
        if self.plate_count > 0:
            self.selected_position = (self.plates[0], None)
        else:
            self.selected_position = (None, None)
        return    
        
    def createProjectLabel(self, parent, plate, proj):
        frame = tk.Frame(parent)
        name = tk.Label(frame, text=proj.name, fg=proj.color, bg='white')
        name.pack(side=tk.LEFT)
        in_plate = [s for s in proj.samples if s in plate.getSamples()]
        number = tk.Label(frame, text="{} - {}".format(in_plate[0].number, in_plate[-1].number), bg='white')
        number.pack(side=tk.LEFT)
        return frame

    def createMenu(self):

        self.menubar = Menu(self.root_window)

        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.filemenu_new)
        self.filemenu.add_command(label="Open", command=self.filemenu_open)
        self.filemenu.add_command(label="Save", command=self.filemenu_save) 
        self.filemenu.add_command(label="Save As", command=self.filemenu_saveAs)      

        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Add Plate", command=self.editmenu_add_plate) 
        self.editmenu.add_command(label="Add From File", command=self.editmenu_add_from_file) 
        self.editmenu.add_command(label="Remove Plate", command=self.editmenu_remove_plate) 
        self.editmenu.add_command(label="Remove Project", command=self.editmenu_remove_project) 
        self.editmenu.add_command(label="Move Project", command=self.editmenu_move_project) 
        self.editmenu.add_command(label="Remove Sample", command=self.editmenu_remove_sample) 
        self.editmenu.add_command(label="Add Project", command=self.editmenu_add_project_from_file) 

        self.setupmenu = Menu(self.menubar, tearoff=0)
        self.setupmenu.add_command(label="Create BCA Plate", command=self.setupmenu_create_bca_plate)
        self.setupmenu.add_command(label="Build BCA Worklist", command=self.buildBcaWorklist)


        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        self.menubar.add_cascade(label="Setup", menu=self.setupmenu)
        self.menubar.add_command(label="To PDF", command=self.filemenu_savepdf)

        self.plate_context_menu = Menu(self.root_window, tearoff=0)
        self.plate_context_menu.add_command(label="Add Project", command=self.editmenu_add_project_from_file) 
        self.plate_context_menu.add_command(label="Remove Project", command=self.editmenu_remove_project) 
        self.plate_context_menu.add_command(label="Move Project", command=self.editmenu_move_project)
        self.plate_context_menu.add_command(label="Remove Sample", command=self.editmenu_remove_sample) 

        self.root_window.config(menu=self.menubar)

        return

    def filemenu_new(self):
        asker = Popups.AskNewPlate(self.root_window)
        self.wait_window(asker)
        rows = 8
        cols = 12
        if asker.rows and asker.cols:
            name = asker.name
            rows = asker.rows
            cols = asker.cols 
            vertical = asker.vertical           
        self.plates = [Plate(name = name, rows=rows, columns=cols, vertical=vertical)]
        self.resetPlates()
        self.redrawList()
        self.current_file = None
        return

    def filemenu_open(self):
        filename = filedialog.askopenfilename(parent=self.root_window, title="Open Plate File", filetypes=(("Plate File", "*.plate"),("All Files", "*.*")))
        if filename:
            self.loadFromFile(filename)
            self.current_file = filename
        return

    def filemenu_save(self):
        filename = self.current_file
        if filename:
            self.onSave(filename)
        else:
            self.filemenu_saveAs()
        return
    
    def filemenu_saveAs(self):
        filename = filedialog.asksaveasfilename(parent=self.root_window, title="Save Plate File", defaultextension='.plate', filetypes=(("Plate File", "*.plate"),("All Files", "*.*")))
        if filename:
            self.onSave(filename)
        return

    def filemenu_savepdf(self):
        filename = filedialog.asksaveasfilename(parent=self.root_window, title="Save Plate Image as PDF", defaultextension='.pdf', filetypes=(("PDF File", "*.pdf"),("All Files", "*.*")))
        if filename:
            Plate.saveImage(filename, self.plates)
        return
    

    def editmenu_add_plate(self):
        asker = Popups.AskNewPlate(self.root_window)
        self.wait_window(asker)
        if asker.rows and asker.cols:
            name = asker.name
            rows = asker.rows
            cols = asker.cols 
            vertical = asker.vertical           
            self.addPlate(Plate(name=name, rows=rows, columns=cols, vertical=vertical))
        return
    
    def editmenu_add_from_file(self):
        filename = filedialog.askopenfilename(parent=self.root_window, title="Open Plate File", filetypes=(("Plate File", "*.plate"),("All Files", "*.*")))
        if filename is not None:
            self.loadFromFile(filename, True)
        return
    
    def editmenu_remove_plate(self):
        if self.plate_count>1:
            if self.selected_position[1] is None:
                messagebox.showinfo("Info", "Please Select a Well First")        
            else:
                self.removePlate(self.selected_position[0])
        else:
            messagebox.showinfo("Info", "Can't remove last plate")
        return
    
    def editmenu_remove_sample(self):
        self.removeSample(self.selected_position[0], self.selected_position[1])
        return
    
    def editmenu_remove_project(self):
        self.removeProject(self.selected_position[0], self.selected_position[1])
        return    
    
    def editmenu_move_project(self):
        self.moveProject(self.selected_position[0], self.selected_position[1])
        return    

    def editmenu_add_project_from_file(self):
        filename = filedialog.askopenfilename(parent=self.root_window, title="Open Project File", filetypes=(("xlsx", "*.xlsx"),("All Files", "*.*")))
        if filename:
            self.addProjectFromFile(filename)
        else:
            self.onAdd()
        return

    def setupmenu_create_bca_plate(self):
        self.createBcaPlate()
        return

    def setupmenu_build_bca_worklist(self):
        self.buildBcaWorklist()
        return

    
    def addPlate(self, plate):
        self.plates.append(plate)
        self.resetPlates()
        self.redrawList()
        return
    
    def removePlate(self, plate):
        for i, p in enumerate(self.plates):
            if p is plate:
                self.plates.pop(i)
        self.resetPlates()
        self.redrawList()

    def removeSample(self, plate, position):
        if position and plate[position] is not None:
            plate.removeSample(plate[position])
            # self.resetPlates()
            self.redrawList()
            self.redrawSamples()
        return
    
    def removeProject(self, plate, position):
        if position and plate[position] is not None:
            proj = plate[position].project
            if proj is not None:
                for p in self.plates:
                    p.removeProject(proj)
            # self.resetPlates()
            self.redrawList()
            self.redrawSamples()
        return
    
    def moveProject(self, plate, position):
        if position and plate[position] is not None:
            proj = plate[position].project
            if proj is not None:
                for p in self.plates:
                    p.removeProject(proj)
            self.redrawSamples()
            self.onAdd(proj)
            self.redrawList()
            self.redrawSamples()
        return
    

    def createBcaPlate(self):
        for plate in self.plates:
            self.removePlate(plate)
        newbca = Plate(name="BCA Plate", rows=8, columns=12, vertical=True)
        newbca.addProject(Project(name="Standards", color="dim gray", num_samples=24), start_pos=newbca.position_from_index(0))
        self.addPlate(newbca)
        return
    
    def createBcaSamples(self):

        ### Find and verify BCA plate is only plate, popup error if not
        ###  BCA plate should be 8x12 vertical and have first project called Standards with 24 samples
        ### Create 3 4x6 sample plates
        for i in range(3):
            self.plates.append(Plate(name=f"Samples{i+1}", rows=4, columns=6, vertical=True))

        ### Add projects one by one
        pidx = 1
        for proj in self.plates[0].projects:
            if proj.name == "Standards":
                continue
            while len(self.plates[pidx].getFreeWells()) == 0:
                pidx += 1
            cproj = Project(name=proj.name, color=proj.color)
            for s in proj.samples:
                if s in self.plates[0].getSamples():
                    cproj.addSample(Sample(project=cproj, name=s.name, number=s.number))
            self.addProject(cproj, self.plates[pidx], self.plates[pidx].getFreeWells()[0])
       
        return
    
    def buildBcaWorklist(self):

        if self.plate_count == 1 and self.plates[0].name == "BCA Plate" and self.plates[0].projects[0].name == "Standards" and self.plates[0].projects[0].sample_count == 24:

            self.createBcaSamples()

            ####  DON'T ASK ABOUT STANDARDS
            asker = Popups.AskBcaParams(self, [p for p in self.plates[0].projects if p.name != "Standards"])
            self.wait_window(asker)
            # print("BCA Setup Output")
            # for n,d in asker.dilutions.items():
            #     print(f"{n} {d.get()}")
            dils = {p:d.get() for p,d in asker.dilutions.items()}
            wlist = WorkList.buildBCA(self.plates, dils)

            # for rec in wlist.records:
            #     print(rec)
            filename = filedialog.asksaveasfilename(parent=self.root_window, title="Save Worklist File", defaultextension='.gwl', filetypes=(("Worklist", "*.gwl"),("All Files", "*.*")))
            if filename:
                wlist.saveToFile(filename)

        else:
            messagebox.showerror("Error", "BCA plate must be the one and only plate")        

        return  
    

    def createSepPakPlate(self):

        pass



    
    def onSave(self, filename):
        if filename:
            Plate.saveToFile(filename, self.plates)
            self.current_file = filename
    

    def loadFromFile(self, filename, add=False):
        if filename:
            try:
                if add:
                    for plate in Plate.loadFromFile(filename):
                        self.plates.append(plate)
                else:
                    self.plates = Plate.loadFromFile(filename)
                self.redrawList()
                self.resetPlates()
            except DuplicateEntryException:
                messagebox.showerror("Error", "Plate file has duplicate entries")
            except MissingEntryException:
                messagebox.showerror("Error", "Plate file has missing entries")

        return


    def onWellClick(self, plate, position):
        well = self.getImage(plate).wells[position.index]
        if well.selected:
            self.selected_position = (plate, None)
            well.select(False)
        else:
            if self.selected_position[1] is not None:
                self.getImage(self.selected_position[0]).wells[self.selected_position[1].index].select(False)
            self.selected_position = (plate, position)
            well.select(True)
        
        if self.selectionChangeListeners:
            for listener in self.selectionChangeListeners:
                listener(self.selected_position)
        return
    
    def onWellRightClick(self, plate, position, event):
        if self.selected_position != (plate, position):
            if self.selected_position[1] is not None:
                self.getImage(self.selected_position[0]).wells[self.selected_position[1].index].select(False)
            self.selected_position = (plate, position)
            self.getImage(self.selected_position[0]).wells[self.selected_position[1].index].select(True)
            self.redrawSamples()
        self.plate_context_menu.post(event.x_root, event.y_root)
        self.bindID = self.root_window.bind("<Button-1>", self.hideContextMenu)
        return
    
    def hideContextMenu(self, event):
        self.plate_context_menu.unpost()
        self.root_window.unbind("<Button-1>", self.bindID)
        return

    def addProjectFromFile(self, filename):

        project = Project.createFromSampleList(filename)
        if project:
            self.onAdd(project)
        return

    def addProject(self, proj, plate, pos, first_sample=1, last_sample=None):
        finished = False
        first = first_sample - 1
        last = last_sample - 1 if last_sample is not None else None
        while not finished:
            try:
                plate.addProject(proj, pos, first_sample=first, last_sample=last)
                finished = True
            except WellNotFreeException as e:
                messagebox.showerror("Error", "Project will not fit!\n First occupied well - " + e.message)
                finished = True
            except NotEnoughWellsException as e:
                ###  Add what you can to this plate
                plate.addProject(proj, pos, first_sample=first, last_sample=first + e.avalable - 1)
                self.redrawSamples()
                first = first + e.avalable
                ###  Pick a new plate or cancel

                next_plate = self.getNextPlate(plate)
                if next_plate is not None: 
                    if len(next_plate.getSamples()) == 0:
                        plate = next_plate
                        pos = plate.getFreeWells()[0]
                        continue
                    else:
                        self.selected_position = (next_plate, plate.getFreeWells()[0])
                        asker = Popups.AskPosition(self.root_window, self.selected_position)
                        self.selectionChangeListeners.append(asker.onSelectionChange)
                        self.wait_window(asker)
                        self.selectionChangeListeners.remove(asker.onSelectionChange)
                
                        if asker.position is not None:                    
                        ###  set plate to new plate and run while loop again (set pos to first free well?)
                            plate = asker.plate
                            pos = asker.position
                            continue                    
                        else:  ### User chose Cancel instead of new position
                            finished = True
                else:
                    messagebox.showerror("Error", "Not enough wells in plate.")

        self.redrawList()
        self.resetPlates()    
        

        return

    def onAdd(self, project = None):
        proj, plate, pos, first, last = self.askNewProject(project)
        if proj:    
            self.addProject(proj, plate, pos, first, last)
        return
    
    def redrawList(self):
        for widget in self.proj_list_frame.winfo_children():
            widget.destroy()
        t_label = tk.Label(self.proj_list_frame, text=f"Total Samples :{self.sample_count}")
        t_label.pack(side=tk.TOP)
        for plate in self.plates:
            p_label = tk.Label(self.proj_list_frame, text=plate.name)
            p_label.pack(side=tk.TOP)
            for proj in plate.projects:
                label = self.createProjectLabel(self.proj_list_frame, plate, proj)
                label.pack(side=tk.TOP)        
        return
    
    def askNewProject(self, project=None):
        colors = [color for color in color_list if color not in [proj.color for proj in self.projects]]
        if len(colors) == 0:
            colors = color_list
        if len(self.selected_position[0].getFreeWells()) < 1:
            p = self.getNextPlate(self.selected_position[0])
            if p is not None:
                self.selected_position = (p, None)
            else:
                messagebox.showerror("Error", "There is no free space in the plate")
                return (None, None, None)
        asker = Popups.AskNewProject(self.root_window, self.selected_position, colors, project)
        # self.plate_image.clearSelection()
        self.selectionChangeListeners.append(asker.onSelectionChange)
        self.wait_window(asker)
        self.selectionChangeListeners.remove(asker.onSelectionChange)
        if project is None:
            if asker.name and asker.number:
                rv = (Project(name=asker.name, num_samples=asker.number, color=asker.color), asker.plate, asker.position, asker.first, asker.last)
            else:
                rv = (None, None, None, None, None)
        else:
            project.color = asker.color
            rv = (project, asker.plate, asker.position, asker.first, asker.last)

        return rv  

    def exceptionHandler(self, etype, evalue, etrace):

        Popups.ExceptionDialog(title='Unhandled Exception', 
                               message='An Unhandled Exception was caught by PlateApp!\n\nPress OK to close.\n', 
                               detail=f'type:{etype}\nvalue:{evalue}')
        self.root_window.destroy()

        return

def main():

    root = tk.Tk()

    app = PlateApp(root)
    app.pack()

    root.mainloop()

    return




if (__name__ == '__main__'):


    # print (position_string_list)

    main()


