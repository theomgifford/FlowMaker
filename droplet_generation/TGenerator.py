from pt_operations import rotate_pt, rotate_pts
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CTriBend import CTriBend

class CSharpTurn(Component):
    """A sharp turn, created from two CTriBend
    
    """
    
    _defaults = {}
    _defaults['turn_angle'] = 90
    _defaults['width_1'] = 50
    _defaults['width_2'] = 50

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CSharpTurn'
        global_keys = ['channel_width','channel_width']
        object_keys = ['width_1','width_2'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.turn_angle==0:
            s.last = startjunc.copyjunc()
            return
        if self.width_1 <= self.width_2:
            interwidth = np.abs(self.width_1/np.cos(0.5*self.turn_angle*np.pi/180))
        elif self.width_1 > self.width_2:
            interwidth = np.abs(self.width_2/np.cos(0.5*self.turn_angle*np.pi/180))
        else:
            print("how did we get here")
            return
        # interwidth = self.width_1
        CTriBend(s,settings={'width_1':self.width_1,'width_2':interwidth,'turn_angle':self.turn_angle/2})
        CTriBend(s,settings={'width_1':interwidth,'width_2':self.width_2,'turn_angle':self.turn_angle/2})
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        
        startjunc.direction = startjunc.direction - 180
        self.cxns = {cxns_names[0]:startjunc, cxns_names[1]:stopjunc}