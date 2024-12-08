
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

        self.plates = [Plate(rows=8, columns=12), Plate(rows=8, columns=12), Plate(rows=4, columns=6), Plate(rows=4, columns=6)]

        self.selected_position = (self.plates[0], None)
        self.selectionChangeListeners = []

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side = tk.TOP)

        self.plate_outer_frame = tk.Frame(self.main_frame)
        self.plate_outer_frame.pack(side=tk.LEFT)

        self.plate_frames = [tk.Frame(self.plate_outer_frame) for _ in range(2 if self.plate_count > 2 else 1)]
        for f in self.plate_frames:
            f.pack(side=tk.LEFT)

        self.proj_frame = tk.Frame(self.main_frame)
        self.proj_frame.pack(side=tk.LEFT)

        self.plate_images = []
        for i in range(min(4, self.plate_count)):
            platex = 10
            platey = 10
            platew = 900 if self.plate_count < 3 else 450
            platef = 0 if i<2 else 1
            self.plate_images.append(PlateImage.PlateWidget(self.plate_frames[platef], plate=self.plates[i], platex=platex, platey=platey, platew=platew, onWellClickHandler=self.onWellClick))
        for i in range(len(self.plate_images)):
            self.plate_images[i].pack(side=tk.TOP, anchor=tk.NW)

        self.add_button = tk.Button(self.proj_frame, text="Add", command=self.onAdd)
        self.add_button.pack(side=tk.TOP)

        self.proj_label = tk.Label(self.proj_frame, text="Projects ", width=50)
        self.proj_label.pack(side=tk.TOP)

        self.proj_list_frame = tk.Frame(self.proj_frame)
        self.proj_list_frame.pack(side=tk.TOP)

        self.createMenu()

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
            vertical = asker.vertical           
        self.plates = [Plate(rows=rows, columns=cols, vertical=vertical)]
        self.redrawList()
        self.plate_image.resetPlate(self.plate)
        return

    def filemenu_open(self):
        self.loadFromFile()
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
                self.plate = Plate.loadFromFile(filename)
            except DuplicateEntryException:
                messagebox.showerror("Error", "Plate file has duplicate entries")
            except MissingEntryException:
                messagebox.showerror("Error", "Plate file has missing entries")
            self.redrawList()
            self.plate_image.resetPlate(self.plate)

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
        for proj in self.projects:
            label = self.createProjectLabel(self.proj_list_frame, proj)
            label.pack(side=tk.TOP)
        
        return
    
    def askNewProject(self):
        colors = [color for color in color_list if color not in [proj.color for proj in self.projects]]
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

    app = PlateApp(root)
    app.pack()

    root.mainloop()

    return




if (__name__ == '__main__'):


    # print (position_string_list)

    main()


