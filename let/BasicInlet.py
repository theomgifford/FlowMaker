from pt_operations import rotate_pt, rotate_pts, orient_pt, arc_pts, orient_pts
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight

class BasicInlet(Component):
    """
    
    creates a inlet/outlet
        
    settings:
        width_body: width of fattest part of inlet
        width_cxn: width of connecting part of inlet
        taper_length: length of tapering section
        length_body: length of fattest part of inlet
        type: see note below
        
        if type is 'auto', 
            if startjunc is specified,
                the Let is a starting Let, and is drawn in the direction of 
                startjunc with the connection at startjunc (the rest of the Let 
                is drawn 'behind' startjunc)
            if startjunc is not specified
                the Let is an ending Let, and is drawn in the opposite 
                direction, with the connection at startjunc (the startjunc and the 
                connection end up being in opposite directions) 
        if type is 'start'
            the Let is a starting Let
        if type is 'end'
            the Let is an ending Let
    """
    _defaults = {}
    _defaults['body_width'] = 3000
    _defaults['cxn_width'] = 50
    _defaults['taper_length'] = 1000
    _defaults['body_length'] = 2000
    _defaults['type'] = 'auto'
    _defaults['segments'] = 180
    

    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['out']):
        #load attributes
        s=structure
        
        comp_key = 'BasicInlet'
        global_keys = ['channel_width']
        object_keys = ['cxn_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        s = structure
        if self.type == 'start':
            s.last = startjunc.reverse()
        elif self.type == 'end':
            startjunc = s.last.reverse()
        else:
            if startjunc is None: # end
                startjunc = s.last.reverse()
            else: # start
                s.last = startjunc.reverse()
                        
        CStraightTaper(s,settings={'start_width':self.cxn_width,'stop_width':self.body_width,'length':self.taper_length})
        
        CStraight(s,settings={'length':self.body_length,'width':self.body_width})
        
        num_segments = np.abs(np.round(self.segments/2)).astype(int)
        pts=arc_pts(-90,90,self.body_width/2,num_segments)
        pts.append(pts[0])
        pts=orient_pts(pts,s.last.direction,s.last.coords)
        s.drawing.add_lwpolyline(pts)  
        
        s.last = startjunc.copyjunc()
        self.cxns = {cxns_names[0]:startjunc.copyjunc()}
        

    
