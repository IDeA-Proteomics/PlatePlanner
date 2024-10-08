import tkinter as tk
from tkinter import ttk
from PlateModel import position_string_list, Position

class LabeledEntry(tk.Frame):

    def __init__(self, parent, text):
        self.parent = parent
        tk.Frame.__init__(self, self.parent)
        self.text = text

        self.label = tk.Label(self, text=self.text)
        self.label.pack(side=tk.LEFT, anchor=tk.E)

        self.entry_text = tk.StringVar(value = "")
        self.entry = tk.Entry(self, width=25, textvariable=self.entry_text)
        self.entry.pack(side=tk.LEFT, anchor=tk.W)

        return
    
    def get(self):
        return self.entry_text.get()
    
    def set(self, text):
        self.entry_text.set(text)
        return


class AskNewProject(tk.Toplevel):

    def __init__(self, parent, positions, colors, selection=None):
        self.parent = parent
        tk.Toplevel.__init__(self, self.parent)

        
        self.name = None
        self.number = None
        # self.start_row = "ABCDEFGH".index(start_position[:1])
        # self.start_column = int(start_position[1:])
        self.position = None
        self.color = None

        self.position_list = [pos.label for pos in positions]
        self.selection = selection
        self.start_selection = self.position_list[0] if not selection or selection[0].label not in self.position_list else selection[0].label

        self.frame = tk.Frame(self)

        self.label = tk.Label(self.frame, text="Please Enter a Project Name")
        self.label.pack()

        self.name_entry = LabeledEntry(self.frame, text="Name")
        self.name_entry.pack()

        self.number_entry = LabeledEntry(self.frame, text="Number")
        self.number_entry.set(str(len(selection)))
        self.number_entry.pack()

        
        self.start_position_var = tk.StringVar(value = self.start_selection)
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
        # self.grab_set()
        # self.parent.wait_window(self)

        return
    
    def onSelectionChange(self, selection):

        self.selection = selection

        self.start_selection = self.position_list[0] if not self.selection or self.selection[0].label not in self.position_list else self.selection[0].label
        self.start_position_var.set(self.start_selection)



        self.number_entry.set(str(len(self.selection)))
        

        return

    def onOk(self):
        self.name = self.name_entry.get()
        num = self.number_entry.get()
        self.number = int(num) if num.isnumeric() and int(num) < 97 else 0
        # self.start_row = "ABCDEFGH".index(start_position[:1])
        # self.start_column = int(start_position[1:])
        self.position = Position.from_string(self.start_position_var.get())
        self.color = self.color_var.get()
        self.destroy()