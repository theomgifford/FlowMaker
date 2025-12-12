# import sdxf

import numpy as np

from pt_operations import rotate_pts, rotate_pt
from junction import Junction
from component import Component

class TetratriangleCrossPos(Component):
    """
    An alignment mark made with four trapezoids and a cross in the middle
    
    size: side of a square occupied by alignment mark
    trap_angle: angle of sides of trapezoid
    cross_width: width of cross in the middle of the mark
    center_ratio: proportion of mark that is the cross in the center
    spacing: space between adjacent alignment marks
    
    
    """
    
    _defaults = {}
    _defaults['size'] = 400
    _defaults['cross_width'] = 20
    _defaults['center_ratio'] = 0.5
    _defaults['trap_angle'] = 30
    _defaults['spacing'] = 200
    
    _cxns_names = ['center','next']
    
    def __init__(self,structure,startjunc=None,settings={}, cxns_names=_cxns_names):
        """ Adds a straight section of CPW transmission line of length = length to the structure"""        
        s=structure
        
        comp_key = 'TetratriangleCrossPos'
        global_keys = ['amark_size','amark_spacing']
        object_keys = ['size','spacing'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
                
        if startjunc is None: startjunc=s.last.copyjunc()
        
        rect_length = self.center_ratio*self.size/2 - self.cross_width/2
        wing = 0.5*self.size*(1-self.center_ratio)*np.tan(self.trap_angle*np.pi/180)
        if self.center_ratio > 1 or self.center_ratio < 0 or rect_length < 0 or 2*wing+self.cross_width > self.size:
            print("bad alignment mark parameters")
            return
        
        coords = startjunc.coords
            
        tiny_square = [  (coords[0]+self.cross_width/2,coords[1]+self.cross_width/2),
                (coords[0]+self.cross_width/2,coords[1]-self.cross_width/2),
                (coords[0]-self.cross_width/2,coords[1]-self.cross_width/2),
                (coords[0]-self.cross_width/2,coords[1]+self.cross_width/2),
                (coords[0]+self.cross_width/2,coords[1]+self.cross_width/2)
                ]
        
        side=[  (coords[0]+self.cross_width/2,coords[1]+self.cross_width/2),
                (coords[0]+self.cross_width/2,coords[1]+self.cross_width/2+rect_length),
                (coords[0]+self.cross_width/2+wing,coords[1]+self.size/2),
                (coords[0]-self.cross_width/2-wing,coords[1]+self.size/2),
                (coords[0]-self.cross_width/2,coords[1]+self.cross_width/2+rect_length),
                (coords[0]-self.cross_width/2,coords[1]+self.cross_width/2),
                (coords[0]+self.cross_width/2,coords[1]+self.cross_width/2)
                ]
        
        tiny_square=rotate_pts(tiny_square,startjunc.direction,coords)
        
        side1=rotate_pts(side,startjunc.direction,coords)
        side2=rotate_pts(side,startjunc.direction+90,coords)
        side3=rotate_pts(side,startjunc.direction+180,coords)
        side4=rotate_pts(side,startjunc.direction+270,coords)
        
        stop_coords=rotate_pt((coords[0]+self.size+self.spacing,coords[1]),startjunc.direction,coords)
        stopjunc=Junction(stop_coords,startjunc.direction)
        
        s.last = stopjunc.copyjunc()
        
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(tiny_square)
            s.drawing.add_lwpolyline(side1)
            s.drawing.add_lwpolyline(side2)
            s.drawing.add_lwpolyline(side3)
            s.drawing.add_lwpolyline(side4)
                
        self.cxns = {cxns_names[0]:startjunc.copyjunc(), cxns_names[1]:stopjunc}

