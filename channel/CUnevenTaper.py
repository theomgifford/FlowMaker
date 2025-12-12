from pt_operations import rotate_pt, rotate_pts
import sdxf
from junction import Junction
from component import Component

class CUnevenTaper(Component):
    """
    A section of channel which (linearly) tapers from start_width, adding width on the right and/or left
    
    """
    
    _defaults = {}
    _defaults['length'] = 200
    _defaults['start_width'] = 50
    _defaults['add_left'] = 0
    _defaults['add_right'] = 0

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CUnevenTaper'
        global_keys = ['channel_width']
        object_keys = ['start_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.length==0:
                s.last = startjunc.copyjunc()
                return
        
        coords = startjunc.coords
        #define geometry of gaps
        gap1= [ 
            (coords[0],coords[1]+self.start_width/2),
            (coords[0]+self.length,coords[1]+self.start_width/2+self.add_left),
            (coords[0]+self.length,coords[1]-self.start_width/2-self.add_right),
            (coords[0],coords[1]-self.start_width/2),
            (coords[0],coords[1]+self.start_width/2)
            ]
        
        #rotate structure to proper orientation
        gap1=rotate_pts(gap1,startjunc.direction,coords)

        #create polylines and append to drawing
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(gap1)
        
        #update last anchor position
        stop_coords=rotate_pt((coords[0]+self.length,coords[1]+(self.add_left-self.add_right)/2),startjunc.direction,coords)
        stopjunc = Junction(stop_coords,startjunc.direction)
        s.last=stopjunc.copyjunc()
        
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}