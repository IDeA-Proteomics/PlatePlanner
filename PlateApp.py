
import os
import math
import PlateImage
import Popups
from Popups import LabeledEntry
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from PlateModel import Sample, Project, Plate
from PlateExceptions import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


color_list = ['red', 'orange', 'yellow', 'green', 'purple', 'cyan', 'magenta', 'brown']


class PlateApp(tk.Frame):

    def __init__(self, root):

        self.root_window = root
        tk.Frame.__init__(self, self.root_window)

        # self.root_window.report_callback_exception = self.exceptionHandler

        self.plate = Plate(rows=8, columns=12)
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

        self.createMenu()

        return

    def createMenu(self):

        self.menubar = Menu(self.root_window)

        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.filemenu_new)
        self.filemenu.add_command(label="Open", command=self.filemenu_open)
        self.filemenu.add_command(label="Save", command=self.filemenu_save)        


        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_command(label="To PDF", command=self.filemenu_savepdf)

        self.root_window.config(menu=self.menubar)

        return
    
    def filemenu_new(self):
        asker = Popups.AskNewPlate(self.root_window)
        self.wait_window(asker)
        rows = 8
        cols = 12
        if asker.rows and asker.cols:
            rows = asker.rows
            cols = asker.cols            
        self.plate = Plate(rows=rows, columns=cols)
        self.plate_image.resetPlate(self.plate)
        return

    def filemenu_open(self):
        self.plate = Plate(rows=8, columns=12)
        self.loadFromFile()
        self.plate_image.resetPlate(self.plate)
        return

    def filemenu_save(self):
        self.onSave()
        return

    def filemenu_savepdf(self):
        self.saveImage()
        return

    def saveImage(self):
        filename = filedialog.asksaveasfilename(parent=self.root_window, title="Save Plate Image as PDF", defaultextension='.pdf', filetypes=(("PDF File", "*.pdf"),("All Files", "*.*")))
        if filename:

            # ### Window coords for the screen grab
            # x = self.root_window.winfo_rootx() + self.plate_image.canvas.winfo_x()
            # y = self.root_window.winfo_rooty() + self.plate_image.canvas.winfo_y()
            # x1 = x + self.plate_image.canvas.winfo_width()
            # y1 = y + self.plate_image.canvas.winfo_height()
            ### coords for image on PDF
            image_height = (A4[0] - 30) / self.plate_image.canvas.winfo_width() * self.plate_image.canvas.winfo_height()

            c = canvas.Canvas(filename, pagesize=A4)
            image_bottom = A4[1] - image_height - 50
            self.drawPlate(c, (15, image_bottom), image_height, A4[1])

            label_y = image_bottom
            
            c.setFont("Helvetica", 30)
            for proj in self.plate.projects:
                label_y -= 40
                c.setFillColor(proj.color)
                c.rect(10, label_y, c.stringWidth(proj.name), 30, stroke=0, fill=1)
                c.setFillColor('black')
                c.drawString(10, label_y, proj.name)
            c.save()

        return
    
    def drawPlate(self, canvas, bottom_left, height, width):

        ratio = self.plate.columns / self.plate.rows

        if width > ratio * height:
            width = math.floor(ratio * height)
        elif height > (1/ratio) * width:
            height = math.floor((1/ratio) * width)

        canvas.rect(bottom_left[0], bottom_left[1], width, height, fill=0)
        inset_y = math.floor(height/10)
        well_size = math.floor((height - (2 * inset_y)) / (self.plate.rows))
        well_radius = math.floor(well_size * 0.45)
        inset_x = math.floor((width - ((self.plate.columns) * well_size)) / 2)

        def getWellCenter(position):
            x = bottom_left[0] + inset_x  + (well_size * position.column) + (well_size / 2)
            y = bottom_left[1] + height - inset_y - (well_size * position.row) - (well_size / 2)  
            return (x,y)
        
        
        txh = well_radius // 1.3
        canvas.setFont("Helvetica", txh)
        for well in self.plate.positions:
            label = well.label
            x,y = getWellCenter(well)            
            canvas.setFillColor(self.plate[label].project.color if self.plate[label] else 'blue')
            canvas.circle(x, y, well_radius, stroke=1, fill=1)
            txw = canvas.stringWidth(label)
            cx = x - (txw/2)
            cy = y - (txh/2) * 0.92
            canvas.setFillColor('black')
            canvas.drawString(cx, cy, label)

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
            proj, pos = self.askNewProject()
            if proj:
                self.plate.addProject(proj, pos)
        except (WellNotFreeException, NotEnoughWellsException):
            messagebox.showerror("Error", "Project will not fit!")

        self.redrawList()
        self.plate_image.redrawSamples()
        return
    
    def redrawList(self):
        for widget in self.proj_list_frame.winfo_children():
            widget.destroy()
        for proj in self.plate.projects:
            label = self.createProjectLabel(self.proj_list_frame, proj)
            label.pack(side=tk.TOP)
        
        return
    
    def askNewProject(self):
        colors = [color for color in color_list if color not in [proj.color for proj in self.plate.projects]]
        asker = Popups.AskNewProject(self.root_window, self.plate, colors, self.selected_positions)
        self.plate_image.clearSelection()
        self.selectionChangeListeners.append(asker.onSelectionChange)
        self.wait_window(asker)
        self.selectionChangeListeners.remove(asker.onSelectionChange)
        if asker.name and asker.number:
            rv = (Project(name=asker.name, num_samples=asker.number, color=asker.color), asker.position)
        else:
            rv = (None, None)

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


