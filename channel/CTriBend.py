from pt_operations import rotate_pt, rotate_pts
from junction import Junction
from component import Component
import numpy as np

class CTriBend(Component):
    """Creates a triangle that bends the track while changes width
    
    width_1: starting width (length of one side of triangle)
    width_2: ending width (length of second side of triangle)
    turn_angle: ends up being angle between those two sides
    
    """
    
    _defaults = {}
    _defaults['width_1'] = 50
    _defaults['width_2'] = 50
    _defaults['turn_angle'] = 90

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CTriBend'
        global_keys = ['channel_width','channel_width']
        object_keys = ['width_1','width_2'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.turn_angle==0:
            s.last = startjunc.copyjunc()
            return
        
        coords = startjunc.coords
        #define geometry of gaps
        y = np.sign(self.turn_angle)*(self.width_1/2-self.width_2*np.cos(self.turn_angle*np.pi/180))
        y_out = np.sign(self.turn_angle)*(self.width_1/2-self.width_2*np.cos(self.turn_angle*np.pi/180)/2)
        x = np.abs(self.width_2*np.sin(self.turn_angle*np.pi/180))
        # y = 200
        # x = 100
        triangle= [ 
            (coords[0],coords[1]+self.width_1/2),
            (coords[0]+x,coords[1]+y),
            (coords[0],coords[1]-self.width_1/2),
            (coords[0],coords[1]+self.width_1/2)
            ]
        
        #rotate structure to proper orientation
        triangle=rotate_pts(triangle,startjunc.direction,coords)

        #create polylines and append to drawing
        s.drawing.add_lwpolyline(triangle)
        
        #update last anchor position
        stop_coords=rotate_pt((coords[0]+x/2,coords[1]+y_out),startjunc.direction,coords)
        stopjunc = Junction(stop_coords,startjunc.direction+self.turn_angle)
        s.last=stopjunc.copyjunc()
        
        startjunc.direction = startjunc.direction - 180
        self.cxns = {cxns_names[0]:startjunc, cxns_names[1]:stopjunc}