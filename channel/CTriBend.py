from pt_operations import rotate_pt, rotate_pts
from junction import Junction
from component import Component
import numpy as np

class CTriBend(Component):
    """Creates a triangle that bends the track while changes width
    
    start_width: starting width (length of one side of triangle)
    stop_width: ending width (length of second side of triangle)
    turn_angle: ends up being angle between those two sides
    
    """
    
    _defaults = {}
    _defaults['start_width'] = 50
    _defaults['stop_width'] = 50
    _defaults['turn_angle'] = 90

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CTriBend'
        global_keys = ['channel_width','channel_width']
        object_keys = ['start_width','stop_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.turn_angle==0:
            s.last = startjunc.copyjunc()
            return
        
        coords = startjunc.coords
        #define geometry of gaps
        self.turn_angle = (self.turn_angle + 180) % 360 - 180
        y = np.sign(self.turn_angle)*(self.start_width/2-self.stop_width*np.cos(self.turn_angle*np.pi/180))
        y_out = np.sign(self.turn_angle)*(self.start_width/2-self.stop_width*np.cos(self.turn_angle*np.pi/180)/2)
        x = np.abs(self.stop_width*np.sin(self.turn_angle*np.pi/180))
        # y = 200
        # x = 100
        triangle= [ 
            (coords[0],coords[1]+self.start_width/2),
            (coords[0]+x,coords[1]+y),
            (coords[0],coords[1]-self.start_width/2),
            (coords[0],coords[1]+self.start_width/2)
            ]
        
        #rotate structure to proper orientation
        triangle=rotate_pts(triangle,startjunc.direction,coords)

        #create polylines and append to drawing
        s.drawing.add_lwpolyline(triangle)
        
        #update last anchor position
        stop_coords=rotate_pt((coords[0]+x/2,coords[1]+y_out),startjunc.direction,coords)
        stopjunc = Junction(stop_coords,startjunc.direction+self.turn_angle)
        s.last=stopjunc.copyjunc()
        
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}