import tkinter as tk
from tkinter import ttk, messagebox
from idea_utils.PlateModel import Position

class LabeledEntry(tk.Frame):

    def __init__(self, parent, text, initial = None, state = 'normal'):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        self.text = text

        self.label = tk.Label(self, text=self.text)
        self.label.pack(side=tk.LEFT, anchor=tk.E)

        self.entry_text = tk.StringVar(value = "" if initial is None else initial)
        self.entry = tk.Entry(self, width=25, textvariable=self.entry_text, state=state)
        self.entry.pack(side=tk.LEFT, anchor=tk.W)

        return
    
    def get(self):
        return self.entry_text.get()
    
    def set(self, text):
        self.entry_text.set(text)
        return

class AskNewPlate(tk.Toplevel):

    askCount = 1

    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self, self.parent)
        self.name = None
        self.cols = None
        self.rows = None
        self.vertical = True

        values = ["8x12", "4x6"]
        orients = ["Vertical", "Horizontal"]

        self.frame = tk.Frame(self)
        self.frame.pack()


        self.name_entry = LabeledEntry(self.frame, text="Name", initial=f"Plate_{AskNewPlate.askCount + 1}")
        self.name_entry.pack()

        self.rowVar = tk.IntVar(value=8)
        self.colVar = tk.IntVar(value=12)
        self.sizeVar = tk.StringVar(value=values[0])
        self.orientVar = tk.StringVar(value=orients[0])

        self.sizeLabel = tk.Label(self.frame, text="Plate Size")
        self.sizeLabel.pack()
        self.sizeCombo = ttk.Combobox(self.frame, textvariable=self.sizeVar, values=values, state='readonly', width=10)
        self.sizeCombo.pack()
        self.orientCombo = ttk.Combobox(self.frame, textvariable=self.orientVar, values=orients, state='readonly', width=10)
        self.orientCombo.pack()

        self.button = tk.Button(self.frame, text="OK", command=self.onOK)
        self.button.pack()
    

        return

    def onOK(self):
        AskNewPlate.askCount += 1
        self.name = self.name_entry.get()
        if self.name == "":
            self.name = f"Plate_{AskNewPlate.askCount}"
        result = self.sizeVar.get()
        self.rows = 4 if result == "4x6" else 8
        self.cols = 6 if result == "4x6" else 12
        self.vertical = True if self.orientVar.get() == "Vertical" else False
        self.destroy()
        return


class AskNewProject(tk.Toplevel):

    def setup(self, selection):
        self.plate = selection[0]        
        self.position_list = [pos.label for pos in self.plate.getFreeWells()]
        self.selection_pos = selection[1] if selection[1] is not None and selection[1].label in self.position_list else None
        self.start_selection = self.position_list[0] if self.selection_pos is None else self.selection_pos.label
        self.start_position_var.set(self.start_selection)

        return


    def __init__(self, parent, selection, colors, project=None):
        self.parent = parent
        tk.Toplevel.__init__(self, self.parent)

        self.start_position_var = tk.StringVar(value = "")
        self.setup(selection)
        
        self.name = None
        self.number = None
        self.position = None
        self.color = None


        self.frame = tk.Frame(self)

        self.label = tk.Label(self.frame, text="Please Enter a Project Name" if project is None else "Project Name")
        self.label.pack()

        self.name_entry = LabeledEntry(self.frame, text="Name", state='normal' if project is None else 'disabled')  
        self.name_entry.set("" if project is None else project.name)      
        self.name_entry.pack()

        self.number_entry = LabeledEntry(self.frame, text="Number", state='normal' if project is None else 'disabled')
        self.number_entry.set(0 if project is None else project.sample_count)
        self.number_entry.pack()
        
        
        self.start_combo = ttk.Combobox(self.frame, textvariable=self.start_position_var, values=self.position_list, state='readonly', width=10)
        self.start_combo.pack()

        self.color_var = tk.StringVar(value=colors[0])
        self.color_combo = ttk.Combobox(self.frame, textvariable=self.color_var, values=colors, state='readonly', width=20)
        self.color_combo.pack()

        self.button = tk.Button(self.frame, text="OK", command=self.onOk)
        self.button.pack()


        self.name_entry.entry.focus_set()

        self.frame.pack()


        self.transient(self.parent)

        return
    
    def onSelectionChange(self, selection):

        self.setup(selection)   

        return

    def onOk(self):
        self.name = self.name_entry.get()
        num = self.number_entry.get()
        self.number = int(num) if num.isnumeric() else 0
        #and int(num) < self.plate.number_of_wells else 0
        self.position = self.plate.position_from_string(self.start_position_var.get())
        self.color = self.color_var.get()
        self.destroy()


class ExceptionDialog():

    def __init__(self, title='Error', message='', detail=''):

        messagebox.showerror(title=title, message=message, detail=detail)

        return
    