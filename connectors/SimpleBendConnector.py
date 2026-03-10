from pt_operations import rotate_pt, rotate_pts
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CSharpBend import CSharpBend
# from channel.CTriTurn import CTriTurn
from channel.CStraight import CStraight

class SimpleBendConnector(Component):
    """A sharp turn, created from two CTriTurn
    
    """
    
    _defaults = {}
    _defaults['target_junc'] = None
    _defaults['width'] = 50

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['in','out']):
        
        #load attributes
        s=structure
        
        comp_key = 'SimpleBendConnector'
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
        d = np.sqrt(x_diff**2+y_diff**2)
        theta_d = self.target_junc.direction - startjunc.direction
        theta_3 = -np.arctan(y_diff/x_diff)*180/np.pi
        theta_a = 180-self.target_junc.direction-theta_3
        theta_b = startjunc.direction+theta_3

        a = np.abs(np.sin(theta_a*np.pi/180)*d/np.sin(theta_d*np.pi/180))
        b = np.abs(np.sin(theta_b*np.pi/180)*d/np.sin(theta_d*np.pi/180))
        
        length_turn = np.abs(0.5*self.width/np.tan(theta_d/2*np.pi/180))
        
        length_1 = a - length_turn
        length_2 = b - length_turn
        
        CStraight(s,startjunc=startjunc,settings={'width':self.width,'length':length_1})
        # print(-(180-theta_d))
        CSharpBend(s,settings={'width':self.width,'turn_angle':-(180-theta_d)})
        CStraight(s,settings={'width':self.width,'length':length_2})
        
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        
        self.cxns = {cxns_names[0]:startjunc.reverse(), cxns_names[1]:stopjunc}