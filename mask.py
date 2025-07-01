# -*- coding: utf-8 -*-
"""
Created on Wednesday, Oct. 25 2017

A reduced version of MaskMakerPro. This provides a set of functions for drawing masks

@author: Mattias Fitzpatrick

reduced by Theo Gifford. The focus of the reduction is to make the script a bit
clearer, and "reset" the number of components and functions, many of which we
won't really need. It should also be easier to add new components to the library.

New features:
    defaults for more complex objects
    ability to store connection points of various components
###############################################################################
"""
import ezdxf
from junction import Junction
# from pt_operations import translate_pts

class MaskError:
    """MaskError is an exception to be raised whenever invalid parameters are used in one of the MaskMaker functions, value is just a string"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
   
#===============================================================================       
#   CHIP GENERATION    
#===============================================================================
"""
Made with our current process in mind, where we design a chip and copy-paste it
onto a mask template.

arguments:
    size: length of a side of the square chip
    start: junction that will be the initial position for the design

attributes:
    last: current position and direction, is a junction
    size: length of a side of the square chip
    defaults: dictionary of default values (ex: {'pinw':8.372})
    drawing: sdxf.Drawing() object which stores the CAD objects appended by the
        various components
    saveas(file): more convenient call to save drawing as dxf
"""
class Chip:
    def __init__(self, size, start=Junction((0,0),0)):
        self.last = start
        self.size = size
        self.defaults = {}
        
        self.doc = ezdxf.new("R2010")
        self.drawing = self.doc.modelspace()
        
        self.block_i = 0 # used in ImportedDXF
        
    def saveas(self,file):
        self.doc.saveas(file)

class ChipBorder:
    """Chip border for dicing"""
    def __init__(self,structure):
        
        s=structure
        
        pts = [(0,0),(0,s.size),(s.size,s.size),(s.size,0),(0,0)]  
        s.drawing.add_lwpolyline(pts)