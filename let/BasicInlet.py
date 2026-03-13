from pt_operations import rotate_pt, rotate_pts, orient_pt, arc_pts, orient_pts
from junction import Junction
from component import Component
import numpy as np

from let.Let import Let
from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight

class BasicInlet(Let):
    """
    
    creates a inlet/outlet
        
    settings:
        body_width: width of fattest part of inlet
        cxn_width: width of connecting part of inlet
        taper_length: length of tapering section
        body_length: length of fattest part of inlet
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
    
    _cxns_names = ['out']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'BasicInlet'
        global_keys = ['channel_width']
        object_keys = ['cxn_width'] 
        super().__init__(structure,startjunc,settings,comp_key,global_keys,object_keys)
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
        pts=arc_pts(-90,90,self.body_width/2,num_segments+1)
        pts.append(pts[0])
        pts=orient_pts(pts,s.last.direction,s.last.coords)
        
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(pts)  
        
        s.last = startjunc.copyjunc()
        self.cxns = {cxns_names[0]:startjunc.copyjunc()}
        
        self.length = self.body_length = self.taper_length + self.body_width/2
        

    
