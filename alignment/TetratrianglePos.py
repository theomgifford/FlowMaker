# import sdxf

import numpy as np

from pt_operations import rotate_pts, rotate_pt
from junction import Junction
from component import Component

class TetratrianglePos(Component):
    """
    An alignment mark made with four triangles that share one vertex (design from Daniel Lewis)
    
    size: side of a square occupied by alignment mark
    vertex_angle: vertex angle of each isosceles triangle
    
    """
    
    _defaults = {}
    _defaults['size'] = 400
    _defaults['vertex_angle'] = 30
    _defaults['spacing'] = 200
    
    _cxns_names = ['center','next']
    
    def __init__(self,structure,startjunc=None,settings={}, cxns_names=_cxns_names):
        """ Adds a straight section of CPW transmission line of length = length to the structure"""        
        s=structure
        
        comp_key = 'TetratrianglePos'
        global_keys = ['amark_size','amark_spacing']
        object_keys = ['size','spacing'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
                
        if startjunc is None: startjunc=s.last.copyjunc()

        coords = startjunc.coords
        
        half_base = 0.5*self.size*np.tan(0.5*self.vertex_angle*np.pi/180)
        
        tri=[  (coords[0],coords[1]),
                (coords[0]-half_base,coords[1]+self.size/2),
                (coords[0]+half_base,coords[1]+self.size/2),
                (coords[0],coords[1])
                ]
        
        tri1=rotate_pts(tri,startjunc.direction,coords)
        tri2=rotate_pts(tri,startjunc.direction+90,coords)
        tri3=rotate_pts(tri,startjunc.direction+180,coords)
        tri4=rotate_pts(tri,startjunc.direction+270,coords)
        
        stop_coords=rotate_pt((coords[0]+self.size+self.spacing,coords[1]),startjunc.direction,coords)
        stopjunc=Junction(stop_coords,startjunc.direction)
        
        s.last = stopjunc.copyjunc()
        
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(tri1)
            s.drawing.add_lwpolyline(tri2)
            s.drawing.add_lwpolyline(tri3)
            s.drawing.add_lwpolyline(tri4)
                
        self.cxns = {cxns_names[0]:startjunc.copyjunc(), cxns_names[1]:stopjunc}

