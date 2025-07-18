import sdxf
from pt_operations import rotate_pts, rotate_pt
from junction import Junction
from component import Component

class CStraight(Component):
    """
    A straight section of channel (its a rectangle)
    """
    
    _defaults = {}
    _defaults['length'] = 200
    _defaults['width'] = 50
    
    def __init__(self,structure,startjunc=None,settings={}, cxns_names = ['in','out']):
        """ Adds a straight section of CPW transmission line of length = length to the structure"""        
        s=structure
        
        comp_key = 'CStraight'
        global_keys = ['channel_width']
        object_keys = ['width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        length = self.length
        width=self.width
                
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.length==0:
                s.last = startjunc.copyjunc()
                return

        coords = startjunc.coords
        
        gap1=[  (coords[0],coords[1]+width/2),
                (coords[0]+length,coords[1]+width/2),
                (coords[0]+length,coords[1]-width/2),
                (coords[0],coords[1]-width/2),
                (coords[0],coords[1]+width/2)
                ]
        
        gap1=rotate_pts(gap1,startjunc.direction,coords)
        
        stop_coords=rotate_pt((coords[0]+length,coords[1]),startjunc.direction,coords)
        stopjunc=Junction(stop_coords,startjunc.direction)
        
        s.last = stopjunc.copyjunc()
        
        s.drawing.add_lwpolyline(gap1)
                
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}

