from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraight import CStraight

class SheathSplit(Component):
    """A T junction droplet generator
    
    """
    
    _defaults = {}
    _defaults['width'] = 100 # width @ dispersed phase input
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out_1','out_2']):
        #load attributes
        s=structure
        
        comp_key = 'SheathSplit'
        global_keys = ['channel_width']
        object_keys = ['width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()

        CStraight(s,startjunc=startjunc,settings={'length':self.width,'width':self.width})
        
        #update last anchor position
        self.cxns[cxns_names[1]]= Junction(orient_pt((0.5*self.width,0.5*self.width),startjunc.direction,startjunc.coords),startjunc.direction+90)
        self.cxns[cxns_names[2]] =  Junction(orient_pt((0.5*self.width,-0.5*self.width),startjunc.direction,startjunc.coords),startjunc.direction-90)
        s.last = self.cxns[cxns_names[1]];
