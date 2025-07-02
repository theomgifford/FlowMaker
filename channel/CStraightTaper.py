from pt_operations import rotate_pt, rotate_pts
import sdxf
from junction import Junction
from component import Component

class CStraightTaper(Component):
    """A section of channel which (linearly) tapers from start_width to stop_width over length"""
    
    _defaults = {}
    _defaults['length'] = 200
    _defaults['start_width'] = 50
    _defaults['stop_width'] = 50

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CStraightTaper'
        global_keys = ['channel_width','channel_width']
        object_keys = ['start_width','stop_width'] # which correspond to the extract global_keys
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
            (coords[0]+self.length,coords[1]+self.stop_width/2),
            (coords[0]+self.length,coords[1]-self.stop_width/2),
            (coords[0],coords[1]-self.start_width/2),
            (coords[0],coords[1]+self.start_width/2)
            ]
        
        #rotate structure to proper orientation
        gap1=rotate_pts(gap1,startjunc.direction,coords)

        #create polylines and append to drawing
        s.drawing.add_lwpolyline(gap1)
        
        #update last anchor position
        stop_coords=rotate_pt((coords[0]+self.length,coords[1]),startjunc.direction,coords)
        stopjunc = Junction(stop_coords,startjunc.direction)
        s.last=stopjunc.copyjunc()
        
        startjunc.direction = startjunc.direction - 180
        self.cxns = {cxns_names[0]:startjunc, cxns_names[1]:stopjunc}