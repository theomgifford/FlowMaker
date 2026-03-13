from pt_operations import rotate_pt, rotate_pts
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CSharpBend import CSharpBend
# from channel.CTriTurn import CTriTurn
from channel.CStraight import CStraight

class SimpleStraightConnector(Component):
    """
    
    A single CStraight, but your junctions have to be aligned
    
    """
    
    _defaults = {}
    _defaults['target_junc'] = None
    _defaults['width'] = 50
    _defaults['tol'] = 1e-11

    _cxns_names = ['in','out']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        
        #load attributes
        s=structure
        
        comp_key = 'SimpleStraightConnector'
        global_keys = ['channel_width']
        object_keys = ['width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.target_junc is None:
            print("Please specify a target junction")
            return
        
        start_coords = startjunc.coords
        stop_coords = self.target_junc.coords
        x_diff = stop_coords[0]-start_coords[0]
        y_diff = stop_coords[1]-start_coords[1]
        
        coords_dir0 = rotate_pt((x_diff,y_diff),-startjunc.direction)
        self.resid = coords_dir0[1]
        # print(coords_dir0[0])
        # print(coords_dir0[1])
        # print(abs((startjunc.direction-self.target_junc.direction) % 180))
        if abs(self.resid) >= self.tol or abs((startjunc.direction-self.target_junc.direction) % 180) >= self.tol:
            print("Junctions not aligned!")
            return
        
        CStraight(s,startjunc=startjunc,settings={'length':coords_dir0[0],'width':self.width})
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}