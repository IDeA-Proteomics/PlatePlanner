
import os
import PlateImage
import Popups
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from PlateModel import Sample, Project, Plate
from PlateExceptions import *


color_list = ['red', 'orange', 'yellow', 'green', 'purple', 'cyan', 'magenta', 'brown']

####  TODO:
####     wrap long projects to second plate
###      let Position have a reference to Plate
###      fix color wheel issues
###      When adding projects, should see some sort of selection indication of wells used based on count - in Popups
###      Right Click Menu
###      Display file name on PDF
###      Add From Sample List


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

        self.plate_frames = [tk.Frame(self.plate_outer_frame) for _ in range(2 if self.plate_count > 2 else 1)]
        for f in self.plate_frames:
            f.pack(side=tk.LEFT)

        for i in range(min(4, self.plate_count)):
            platex = 10
            platey = 10
            platew = 900 if self.plate_count == 1 else 600 if self.plate_count < 3 else 450
            platef = 0 if i<2 else 1
            self.plate_images.append(PlateImage.PlateWidget(self.plate_frames[platef], plate=self.plates[i], platex=platex, platey=platey, platew=platew, onWellClickHandler=self.onWellClick))
        for i in range(len(self.plate_images)):
            self.plate_images[i].pack(side=tk.TOP, anchor=tk.NW)

        self.resetSelection()

        return
    
    @property
    def projects(self):
        return {project for plate in self.plates for project in plate.projects}
    
    @property 
    def plate_count(self):
        return len(self.plates)
    
    def getImage(self, plate):
        for i, p in enumerate(self.plates):
            if p is plate:
                return self.plate_images[i]
        return None
    
    def resetSelection(self):
        self.selected_position = (self.plates[0], None)
        return

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
        self.editmenu.add_command(label="Remove Sample", command=self.editmenu_remove_sample) 


        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        self.menubar.add_command(label="To PDF", command=self.filemenu_savepdf)

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
        self.loadFromFile(filename, True)
        return
    
    def editmenu_remove_plate(self):
        self.removePlate(self.selected_position[0])
        return
    
    def editmenu_remove_sample(self):
        self.removeSample(self.selected_position[0], self.selected_position[1])
        return
    
    def editmenu_remove_project(self):
        self.removeProject(self.selected_position[0], self.selected_position[1])
        return        
    
    def addPlate(self, plate):
        self.plates.append(plate)
        self.resetPlates()
        self.redrawList()
        return
    
    def removePlate(self, plate):
        # self.plates.remove(plate)
        for i, p in enumerate(self.plates):
            if p is plate:
                self.plates.pop(i)
        self.resetPlates()
        self.redrawList()
        self.resetSelection()

    def removeSample(self, plate, position):
        if position:
            plate.removeSample(plate[position])
            self.resetPlates()
            self.redrawList()
            self.resetSelection()
        return
    
    def removeProject(self, plate, position):
        if position:        
            plate.removeProject(plate[position].project)
            self.resetPlates()
            self.redrawList()
            self.resetSelection()
        return

    
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
                # self.current_file = filename
            except DuplicateEntryException:
                messagebox.showerror("Error", "Plate file has duplicate entries")
            except MissingEntryException:
                messagebox.showerror("Error", "Plate file has missing entries")

        return
    
    def createProjectLabel(self, parent, proj):

        frame = tk.Frame(parent)
        name = tk.Label(frame, text=proj.name, fg=proj.color, bg='white')
        name.pack(side=tk.LEFT)
        number = tk.Label(frame, text=proj.num, bg='white')
        number.pack(side=tk.LEFT)

        return frame

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
    
    # def onPlateSelectionChange(self, selected_positions):

    #     self.selected_positions = selected_positions
    #     if self.selectionChangeListeners:
    #         for listener in self.selectionChangeListeners:
    #             listener(self.selected_positions)

    #     return

    def onAdd(self):
        try:
            proj, plate, pos = self.askNewProject()
            if proj:
                plate.addProject(proj, pos)
                self.redrawList()
                self.getImage(plate).redrawSamples()
        except WellNotFreeException as e:
            messagebox.showerror("Error", "Project will not fit!\n First occupied well - " + e.message)
        except NotEnoughWellsException as e:
            messagebox.showerror("Error", "Not Enough Wells\n" + e.message)
        

        return
    
    def redrawList(self):
        for widget in self.proj_list_frame.winfo_children():
            widget.destroy()
        for plate in self.plates:
            p_label = tk.Label(self.proj_list_frame, text=plate.name)
            p_label.pack(side=tk.TOP)
            for proj in plate.projects:
                label = self.createProjectLabel(self.proj_list_frame, proj)
                label.pack(side=tk.TOP)
        
        return
    
    def askNewProject(self):
        colors = [color for color in color_list if color not in [proj.color for proj in self.projects]]
        if len(colors) == 0:
            colors = color_list
        asker = Popups.AskNewProject(self.root_window, self.selected_position, colors)
        # self.plate_image.clearSelection()
        self.selectionChangeListeners.append(asker.onSelectionChange)
        self.wait_window(asker)
        self.selectionChangeListeners.remove(asker.onSelectionChange)
        if asker.name and asker.number:
            rv = (Project(name=asker.name, num_samples=asker.number, color=asker.color), asker.plate, asker.position)
        else:
            rv = (None, None, None)

        return rv
    

    def exceptionHandler(self, etype, evalue, etrace):

        Popups.ExceptionDialog(title='Unhandled Exception', 
                               message='An Unhandled Exception was caught by PlateApp!\n\nPress OK to close.\n', 
                               detail=f'type:{etype}\nvalue:{evalue}')
        self.root_window.destroy()

        return

def main():

    root = tk.Tk()

    app = PlateApp(root, '/home/david/IDeA_Scripts/TestData/testPlate.plate')
    app.pack()

    root.mainloop()

    return




if (__name__ == '__main__'):


    # print (position_string_list)

    main()


