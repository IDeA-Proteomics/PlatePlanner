import tkinter as tk
import math
from PlateModel import Sample, Project, Position, position_string_list


###
###   w is width of box, h is height of box, radius is radius of well
###
###
class Well(tk.Canvas):
    def __init__(self, parent, plate, position, w, h):
        self.parent = parent
        tk.Canvas.__init__(self, self.parent, width=w, height=h, bg='white')

        self.plate = plate

        self.position = position
        self.w = w
        self.h = h
        self.radius = math.floor(min(self.h, self.w) * 0.45)
        self.selected = False

        self._draw()

        self.bind('<ButtonPress-1>', self.onPress)
        self.bind('<ButtonRelease-1>', self.onRelease)

        return
    
    def _draw(self):
        self.config(bg='magenta' if self.selected else 'white')
        fill = 'blue' if self.plate[self.position] is None else self.plate[self.position].project.color

        self.well = self.create_oval(self.w/2 - self.radius, self.h/2 - self.radius, self.w/2 + self.radius, self.h/2 + self.radius, fill=fill)
        self.create_text(self.w / 2, self.h / 2, text=self.position.label)
        return
    
    def redraw(self):
        self.delete(self.well)
        self._draw()
        return
    
    def onPress(self, event):
        self.parent.onWellPress(self.position)

    def onRelease(self, event):
        self.parent.onWellRelease(self.position, event)

    def select(self, selected=True):
        self.selected = selected
        self.redraw()
        return


class PlateWidget(tk.Frame):

    def __init__(self, parent, plate, platex, platey, platew, onSelectionChange = None):

        self.parent = parent
        tk.Frame.__init__(self, self.parent)

        self.plate = plate
        self.onSelectionChange = onSelectionChange

        self.x = platex
        self.y = platey
        self.w = platew
        self.h = math.floor(self.w * (8/12))

        self.selecting = False
        self.selection_start = None
        self.selection_end = None

        self.draw()

        return
    
    def draw(self):


        self.canvas = tk.Canvas(self, width=(self.x * 2) + self.w, height=(self.y * 2) + self.h, bg='black')
        self.canvas.create_polygon(self.x, self.y, 
                                   self.x, self.y + self.h, 
                                   self.x + self.w, self.y + self.h, 
                                   self.x + self.w, self.y, 
                                   fill='white')

        self.wells = []

        inset_y = math.floor(self.h / 10)

        self.well_size = math.floor((self.h - (2 * inset_y)) / 7)

        inset_x = math.floor((self.w - (11* self.well_size)) / 2)

        self.start_x = self.x + inset_x
        self.start_y = self.y + inset_y

        ### For Vertical plates
        for j in range(12):
            for i in range(8):
                well = Well(self, self.plate, Position.from_rowcol(i, j), self.well_size, self.well_size)
                self.wells.append(well)
                xpos = self.start_x + (j * self.well_size)
                ypos = self.start_y + (i * self.well_size)
                self.canvas.create_window(xpos, ypos, window=well)

        ###  For Horizontal plates
        # for j in range(8):
        #     for i in range(12):
        #         well = Well(self, Position.from_rowcol(j, i), self.well_size, self.well_size)
        #         self.wells.append(well)
        #         xpos = self.start_x + (i * self.well_size)
        #         ypos = self.start_y + (j * self.well_size)
        #         self.canvas.create_window(xpos, ypos, window=well)


        self.canvas.pack()

        return
    
    def redrawSamples(self):

        for well in self.wells:
            well.redraw()

        return
    
    def getWellXY(self, x, y):
        row = math.floor((y - self.start_y) / self.well_size)
        col = math.floor((x - self.start_x) / self.well_size)
        return self.wells[Position.from_rowcol(row, col).index]
    

    def clearSelection(self):
        self.selection_start = None
        self.selection_end = None
        if self.onSelectionChange:
            self.onSelectionChange([])
        return
    
    def onWellPress(self, position):

        self.selecting = True
        self.selection_start = self.wells[position.index]

        return
    
    def onWellRelease(self, position, event):

        if self.selection_start is not None:
            self.selecting = False
            self.selection_end = self.getWellXY(event.x + (position.column * self.well_size) + self.start_x, event.y + (position.row * self.well_size) + self.start_y)        

            start_index = self.wells.index(self.selection_start)
            end_index = self.wells.index(self.selection_end)

            if (self.selection_end is self.selection_start) and self.selection_start.selected:
                self.selection_start.select(False)

            else:
                if end_index < start_index:
                    temp = end_index
                    end_index = start_index
                    start_index = temp

                for well in self.wells:
                    if self.wells.index(well) in range(start_index, end_index + 1):
                        well.select()
                    else:
                        well.select(False)
            
            if self.onSelectionChange:
                self.onSelectionChange([well.position for well in self.wells if well.selected])

        return