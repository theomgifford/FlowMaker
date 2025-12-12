from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from focusing.BasicFocusStreams import BasicFocusStreams

from mask import Chip

class HydrogelGenerator(Component):
    """
    
    A 5-input droplet generator
    
    draws all three layers
    
    """
    
    _defaults = {}
    
    _defaults['cxn_width_core'] = 200 # width @ core input
    _defaults['neck_width_core'] = 100 # width of core neck
    _defaults['neck_length_core'] = 100 # length of core neck
    _defaults['taper_length_core'] = 100 # length of core taper

    _defaults['cxn_width_shell'] = 200 # width @ core input
    _defaults['neck_width_shell'] = 250 # width of core neck
    _defaults['neck_length_shell'] = 40 # length of core neck
    _defaults['taper_length_shell'] = 80 # length of core taper
    _defaults['out_width_shell'] = 300
    _defaults['focus_angle_shell'] = 50
    
    _defaults['width_oil'] = 350;
    _defaults['length_oil'] = 500;
    
    _defaults['cxn_width_drop'] = 400 # width @ core input
    _defaults['neck_width_drop'] = 300 # width of core neck
    _defaults['neck_length_drop'] = 300 # length of core neck
    _defaults['taper_length_drop'] = 300 # length of core taper
    
    _defaults['layer'] = 0
    
    _cxns_names = ['core','drop','shell_1','shell_2','oil_1','oil_2']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'HydrogelGenerator'
        global_keys = ['channel_width']
        object_keys = ['cxn_width_drop'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        if not self.layer in {0,1,2}:
            self.layer = 0
            print('automatically set layer to 1')
        
        s.local_write = False
        
        if self.layer == 0:
            s.local_write = True
        
        CStraightTaper(s,startjunc=startjunc,settings={'start_width':self.cxn_width_core,'stop_width':self.neck_width_core,'length':self.taper_length_core})

        CStraight(s,settings={'length':self.neck_length_core,'width':self.neck_width_core})
        
        if self.layer == 1:
            s.local_write = True
            
        shell_focus = BasicFocusStreams(s, settings = {'samp_width':self.neck_width_core,'out_width':self.out_width_shell,'focus_width':self.cxn_width_shell,'focus_angle':self.focus_angle_shell})
        
        CStraightTaper(s,settings={'start_width':self.out_width_shell,'stop_width':self.neck_width_shell,'length':self.taper_length_shell})

        CStraight(s,settings={'length':self.neck_length_shell,'width':self.neck_width_shell})
        
        if self.layer == 2:
            s.local_write = True
        
        CStraight(s,settings={'width':self.length_oil,'length':self.width_oil})

        CStraight(s,settings={'length':self.neck_length_drop,'width':self.neck_width_drop})

        CStraightTaper(s,settings={'start_width':self.neck_width_drop,'stop_width':self.cxn_width_drop,'length':self.taper_length_drop})

        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        self.cxns[cxns_names[1]]= stopjunc
        self.cxns[cxns_names[2]] = shell_focus.cxns['focus_1']
        self.cxns[cxns_names[3]] = shell_focus.cxns['focus_2']
        self.cxns[cxns_names[4]] = Junction(orient_pt((self.taper_length_core+self.neck_length_core+shell_focus.length+self.taper_length_shell+self.neck_length_shell+0.5*self.width_oil,0.5*self.length_oil),startjunc.direction,startjunc.coords),startjunc.direction+90)
        self.cxns[cxns_names[5]] = Junction(orient_pt((self.taper_length_core+self.neck_length_core+shell_focus.length+self.taper_length_shell+self.neck_length_shell+0.5*self.width_oil,-0.5*self.length_oil),startjunc.direction,startjunc.coords),startjunc.direction-90)
        
        # reset local_write
        s.local_write = True
