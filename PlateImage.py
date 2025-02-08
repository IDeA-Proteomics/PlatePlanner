import tkinter as tk
import math
from PlateModel import Sample, Project, Position  ###, position_string_list


###
###   w is width of box, h is height of box, radius is radius of well
###
###
class Well(tk.Canvas):
    def __init__(self, parent, plate, position, w, h, onClickHandler):
        self.parent = parent
        tk.Canvas.__init__(self, self.parent, width=w, height=h, bg='white')

        self.plate = plate

        self.position = position
        self.w = w
        self.h = h
        self.radius = math.floor(min(self.h, self.w) * 0.45)
        self.selected = False
        self.onClickHandler = onClickHandler

        self._draw()
        
        self.bind('<Button-1>', self.onClick)
        # self.bind('<ButtonPress-1>', self.onPress)
        # self.bind('<ButtonRelease-1>', self.onRelease)
        # self.bind('<B1-Motion>', self.onMove)

        return
    
    def _draw(self):
        self.config(bg='magenta' if self.selected else 'white')
        fill = 'white' if self.plate[self.position] is None else self.plate[self.position].project.color

        self.well = self.create_oval(self.w/2 - self.radius, self.h/2 - self.radius, self.w/2 + self.radius, self.h/2 + self.radius, fill=fill)
        t = self.plate[self.position].number if self.plate[self.position] is not None else ""
        self.create_text(self.w / 2, self.h / 2, text=t, font=('Arial', int(self.radius/1.5)))
        return
    
    def redraw(self):
        self.delete(self.well)
        self._draw()
        return
    
    def onClick(self, event):
        self.onClickHandler(self)
    
    # def onPress(self, event):
    #     self.onPressHandler(self.position)

    # def onRelease(self, event):
    #     self.onReleaseHandler(self.position, event)

    # def onMove(self, event):
    #     self.onMoveHandler(self.position, event)

    def select(self, selected=True):
        self.selected = selected
        self.redraw()
        return


class PlateWidget(tk.Frame):

    def __init__(self, parent, plate, platex, platey, platew, onWellClickHandler = None):

        self.parent = parent
        tk.Frame.__init__(self, self.parent)

        self.plate = plate
        self.onWellClickHandler = onWellClickHandler

        self.x = platex
        self.y = platey
        self.w = platew
        self.h = math.floor(self.w * (self.plate.rows/self.plate.columns))

        # self.selecting = False
        # self.selection_start = None
        # self.selection_end = None

        self.draw()

        return
    
    def draw(self):


        self.canvas = tk.Canvas(self, width=  self.w, height=  self.h + 30, bg='black')
        self.canvas.create_polygon(self.x, self.y, 
                                   self.x, self.y + self.h + 30, 
                                   self.x + self.w, self.y + self.h + 30, 
                                   self.x + self.w, self.y, 
                                   fill='white')

        self.wells = []

        inset_y = math.floor(self.h / 10)

        self.well_size = math.floor((self.h - (2 * inset_y)) / (self.plate.rows))

        inset_x = math.floor((self.w - ((self.plate.columns)* self.well_size)) / 2)

        text_height = inset_x / 3

        self.start_x = self.x + inset_x
        self.start_y = self.y + inset_y + text_height
        self.end_x = self.start_x + (self.w - (2 * inset_x))
        self.end_y = self.start_y + (self.h - (2 * inset_y))

        
        self.canvas.create_text(self.x, self.end_y, text=self.plate.name, font=('Arial', int(text_height)), anchor=tk.NW)
        for i in range(self.plate.columns):            
            xpos = self.start_x + (i * self.well_size) + (self.well_size / 2)
            ypos = self.start_y
            self.canvas.create_text(xpos, ypos, text=str(i+1), font=('Arial', int(text_height)), anchor=tk.S)

        for i in range(self.plate.rows):
            xpos = self.start_x - (inset_x / 10)
            ypos = self.start_y + (i * self.well_size) + (self.well_size / 2)
            self.canvas.create_text(xpos, ypos, text="ABCDEFGH"[i], font=('Arial', int(text_height)), anchor=tk.E)


        for pos in self.plate.positions:
            well = Well(self, self.plate, pos, self.well_size, self.well_size, self.onWellClick)
            self.wells.append(well)
            xpos = self.start_x + (pos.column * self.well_size)
            ypos = self.start_y + (pos.row * self.well_size)
            self.canvas.create_window(xpos, ypos, window=well, anchor=tk.NW)

        self.canvas.pack()

        return
    
    def redrawSamples(self):

        for well in self.wells:
            well.redraw()

        return
    
    def resetPlate(self, plate):
        self.plate = plate
        self.canvas.destroy()
        self.draw()
    
    def getWellXY(self, x, y):
        if x < self.start_x:
            x = self.start_x
        if x > self.end_x:
            x = self.end_x
        if y < self.start_y:
            y = self.start_y
        if y > self.end_y:
            y = self.end_y
        row = math.floor((y - self.start_y) / self.well_size)
        col = math.floor((x - self.start_x) / self.well_size)
        return self.wells[self.plate.position_from_rowcol(row, col).index]
    

    def onWellClick(self, well):
        self.onWellClickHandler(self.plate, well.position)


        