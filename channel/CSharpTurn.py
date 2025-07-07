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
    _defaults['start_width'] = 50
    _defaults['stop_width'] = 50

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        #load attributes
        s=structure
        
        comp_key = 'CSharpTurn'
        global_keys = ['channel_width','channel_width']
        object_keys = ['start_width','stop_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if self.turn_angle==0:
            s.last = startjunc.copyjunc()
            return
        if self.start_width <= self.stop_width:
            interwidth = np.abs(self.start_width/np.cos(0.5*self.turn_angle*np.pi/180))
        elif self.start_width > self.stop_width:
            interwidth = np.abs(self.stop_width/np.cos(0.5*self.turn_angle*np.pi/180))
        else:
            print("how did we get here")
            return
        # interwidth = self.start_width
        CTriBend(s,settings={'start_width':self.start_width,'stop_width':interwidth,'turn_angle':self.turn_angle/2})
        CTriBend(s,settings={'start_width':interwidth,'stop_width':self.stop_width,'turn_angle':self.turn_angle/2})
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}