from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight

class CrossGenerator(Component):
    """A T junction droplet generator
    
    """
    
    _defaults = {}
    _defaults['cxn_width_disp'] = 100 # width @ dispersed phase input
    _defaults['cxn_width_drop'] = 100 # width @ formed droplet output
    _defaults['neck_width_disp'] = 50 # width @ formed droplet output
    _defaults['neck_width_drop'] = 50 # width @ formed droplet output
    _defaults['width_cont'] = 100 # width @ continuous phase input
    _defaults['neck_length_disp'] = 100 # length of input neck
    _defaults['taper_length_disp'] = 100 # length of input taper
    _defaults['neck_length_drop'] = 50 # length of output neck
    _defaults['taper_length_drop'] = 50 # length of output taper
    _defaults['length_cont'] = 200 # length of continuous section (centered)

    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['disp','drop','cont_1','cont_2']):
        #load attributes
        s=structure
        
        comp_key = 'CrossGenerator'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['cxn_width_disp','cxn_width_drop','width_cont'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()

        CStraightTaper(s,startjunc=startjunc,settings={'start_width':self.cxn_width_disp,'stop_width':self.neck_width_disp,'length':self.taper_length_disp})

        CStraight(s,settings={'length':self.neck_length_disp,'width':self.neck_width_disp})

        CStraight(s,settings={'width':self.length_cont,'length':self.width_cont})

        CStraight(s,settings={'length':self.neck_length_drop,'width':self.neck_width_drop})

        CStraightTaper(s,settings={'start_width':self.neck_width_drop,'stop_width':self.cxn_width_drop,'length':self.taper_length_drop})

        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        self.cxns[cxns_names[1]]= stopjunc
        self.cxns[cxns_names[2]] = Junction(orient_pt((self.taper_length_disp+self.neck_length_disp+0.5*self.width_cont,0.5*self.length_cont),startjunc.direction,startjunc.coords),startjunc.direction+90)
        self.cxns[cxns_names[3]] = Junction(orient_pt((self.taper_length_disp+self.neck_length_disp+0.5*self.width_cont,-0.5*self.length_cont),startjunc.direction,startjunc.coords),startjunc.direction-90)
