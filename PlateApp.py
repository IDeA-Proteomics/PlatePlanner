

import PlateImage
import Popups
from Popups import LabeledEntry
import tkinter as tk
from tkinter import messagebox, filedialog
from PlateModel import Sample, Project, Plate, position_string_list
from PlateExceptions import *


color_list = ['red', 'orange', 'yellow', 'green', 'purple', 'cyan', 'magenta', 'brown']


class PlateApp(tk.Frame):

    def __init__(self, root):

        self.root_window = root
        tk.Frame.__init__(self, self.root_window)

        self.root_window.report_callback_exception = self.exceptionHandler

        self.plate = Plate([])
        self.selected_positions = []
        self.selectionChangeListeners = []

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side = tk.TOP)

        self.plate_frame = tk.Frame(self.main_frame)
        self.plate_frame.pack(side=tk.LEFT)

        self.proj_frame = tk.Frame(self.main_frame)
        self.proj_frame.pack(side=tk.LEFT)

        self.plate_image = PlateImage.PlateWidget(self.plate_frame, plate=self.plate, platex=10, platey=10, platew=600, onSelectionChange=self.onPlateSelectionChange)
        self.plate_image.pack()

        self.add_button = tk.Button(self.proj_frame, text="Add", command=self.onAdd)
        self.add_button.pack(side=tk.TOP)

        self.proj_label = tk.Label(self.proj_frame, text="Projects ", width=50)
        self.proj_label.pack(side=tk.TOP)

        self.proj_list_frame = tk.Frame(self.proj_frame)
        self.proj_list_frame.pack(side=tk.TOP)

        self.save_button = tk.Button(self.proj_frame, text="Save", command=self.onSave)
        self.save_button.pack(side=tk.TOP)

        self.load_button = tk.Button(self.proj_frame, text="Load", command=self.loadFromFile)
        self.load_button.pack(side=tk.TOP)

        return
    
    def onSave(self):
        filename = filedialog.asksaveasfilename(parent=self.root_window, title="Save Plate File", defaultextension='.plate', filetypes=(("Plate File", "*.plate"),("All Files", "*.*")))
        if filename:
            self.plate.outputToFile(filename)
    
    def loadFromFile(self):
        filename = filedialog.askopenfilename(parent=self.root_window, title="Open Plate File", filetypes=(("Plate File", "*.plate"),("All Files", "*.*")))
        if filename:
            try:
                self.plate.loadFromFile(filename)
            except DuplicateEntryException:
                messagebox.showerror("Error", "Plate file has duplicate entries")
            except MissingEntryException:
                messagebox.showerror("Error", "Plate file has missing entries")
            self.redrawList()
            self.plate_image.redrawSamples()

        return
    
    def createProjectLabel(self, parent, proj):

        frame = tk.Frame(parent)
        name = tk.Label(frame, text=proj.name, fg=proj.color, bg='white')
        name.pack(side=tk.LEFT)
        number = tk.Label(frame, text=proj.num, bg='white')
        number.pack(side=tk.LEFT)

        return frame

    def onPlateSelectionChange(self, selected_positions):

        self.selected_positions = selected_positions
        if self.selectionChangeListeners:
            for listener in self.selectionChangeListeners:
                listener(self.selected_positions)

        return

    def onAdd(self):
        try:
            proj = self.askNewProject()
            if proj:
                self.plate.addProject(proj)
        except (WellNotFreeException, NotEnoughWellsException):
            messagebox.showerror("Error", "Project will not fit!")

        self.redrawList()
        self.plate_image.redrawSamples()
        return
    
    def redrawList(self):
        for widget in self.proj_list_frame.winfo_children():
            widget.destroy()
        for proj in self.plate.project_list:
            label = self.createProjectLabel(self.proj_list_frame, proj)
            label.pack(side=tk.TOP)
        
        return
    
    def askNewProject(self):
        colors = [color for color in color_list if color not in [proj.color for proj in self.plate.project_list]]
        asker = Popups.AskNewProject(self.root_window, self.plate.getFreeWells(), colors, self.selected_positions)
        self.plate_image.clearSelection()
        self.selectionChangeListeners.append(asker.onSelectionChange)
        self.wait_window(asker)
        self.selectionChangeListeners.remove(asker.onSelectionChange)
        if asker.name and asker.number:
            rv = Project(name=asker.name, start_position=asker.position, num_samples=asker.number, color=asker.color)
        else:
            rv = None

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


    print (position_string_list)

    main()


