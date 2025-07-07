from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CTriBend import CTriBend

class BasicSortTwo(Component):
    """A basic V-sorter
    
    """
    
    _defaults = {}
    _defaults['in_width'] = 50
    _defaults['out_width'] = 50
    _defaults['taper_length'] = 100 # length of initial widening
    _defaults['split_angle'] = 15 # width @ formed droplet output

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out_1','out_2']):
        #load attributes
        s=structure
        
        comp_key = 'BasicSortTwo'
        global_keys = ['channel_width','channel_width']
        object_keys = ['in_width','out_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        taper_width = 2*self.out_width/np.cos(self.split_angle*np.pi/180)
        
        CStraightTaper(s,startjunc=startjunc,settings={'start_width':self.in_width,'stop_width':taper_width,'length':self.taper_length})
        
        startjunc1 = Junction(orient_pt((0,taper_width/4),s.last.direction,s.last.coords),s.last.direction)
        startjunc2 = Junction(orient_pt((0,-taper_width/4),s.last.direction,s.last.coords),s.last.direction)

        CTriBend(s,startjunc=startjunc2,settings={'start_width':taper_width/2,'stop_width':self.out_width,'turn_angle':-self.split_angle})
        self.cxns[cxns_names[2]] = s.last.copyjunc()
        
        CTriBend(s,startjunc=startjunc1,settings={'start_width':taper_width/2,'stop_width':self.out_width,'turn_angle':self.split_angle})
        self.cxns[cxns_names[1]] = s.last.copyjunc()

