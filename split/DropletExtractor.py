from pt_operations import rotate_pt, rotate_pts, orient_pt, translate_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CSharpTurn import CSharpTurn
from channel.CUnevenTaper import CUnevenTaper
from channel.CTriTurn import CTriTurn

class DropletExtractor(Component):
    """Extracts droplets from oil using an aqueous phase
    
    """
    
    _defaults = {}
    
    _defaults['entrance_angle_oil'] = 30
    _defaults['entrance_angle_aq'] = 40
    _defaults['exit_angle_oil'] = 60
    _defaults['exit_angle_aq'] = 15
    
    _defaults['length_in'] = 700
    _defaults['length_straight'] = 2000
    _defaults['length_out'] = 4000
    
    _defaults['cxn_width_oil_in'] = 400
    _defaults['cxn_width_aq_in'] = 500
    _defaults['cxn_width_oil_out'] = 300
    _defaults['cxn_width_aq_out'] = 400
    
    _defaults['straight_width_oil'] = 200
    _defaults['straight_width_aq'] = 250

    _cxns_names = ['oil_in','aq_in','oil_out','aq_out']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'DropletExtractor'
        global_keys = ['channel_width','channel_width']
        object_keys = ['cxn_width_oil_in','cxn_width_aq_out'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        # print(startjunc)
        first_turn = CTriTurn(s,startjunc=startjunc,settings={'turn_angle':self.entrance_angle_oil,'start_width':self.cxn_width_oil_in,'stop_width':self.cxn_width_oil_in})
        
        oil_junc = first_turn.cxns['out']
        # print(oil_junc)
        CUnevenTaper(s,settings={'add_left':-(self.cxn_width_oil_in-self.straight_width_oil),'start_width':self.cxn_width_oil_in,'stop_width':self.cxn_width_oil_in,'length':self.length_in})
        CStraight(s,settings={'width':self.straight_width_oil,'length':self.length_straight})
        CUnevenTaper(s,settings={'add_left':self.cxn_width_oil_out-self.straight_width_oil,'start_width':self.straight_width_oil,'length':self.length_out})
        CTriTurn(s,settings={'turn_angle':self.exit_angle_oil,'start_width':self.cxn_width_oil_out,'stop_width':self.cxn_width_oil_out})
        self.cxns[cxns_names[2]] = s.last.copyjunc()
        
        self.horizontal = oil_junc.direction
        
        # print(startjunc.direction)
        # print(self.entrance_angle_oil)
        water_junc = Junction(translate_pt(oil_junc.coords,rotate_pt((0,-(self.cxn_width_oil_in+self.cxn_width_aq_in)/2),self.horizontal)),self.horizontal)
        # print(water_junc)
        CUnevenTaper(s,startjunc=water_junc,settings={'add_right':-(self.cxn_width_aq_in-self.straight_width_aq),'start_width':self.cxn_width_aq_in,'length':self.length_in})
        CStraight(s,settings={'width':self.straight_width_aq,'length':self.length_straight})
        CUnevenTaper(s,settings={'add_right':self.cxn_width_aq_out-self.straight_width_aq,'start_width':self.straight_width_aq,'length':self.length_out})
        CTriTurn(s,settings={'turn_angle':-self.exit_angle_aq,'start_width':self.cxn_width_aq_out,'stop_width':self.cxn_width_aq_out})
        self.cxns[cxns_names[3]] = s.last.copyjunc()

        CTriTurn(s,startjunc=water_junc.reverse(),settings={'turn_angle':self.entrance_angle_aq,'start_width':self.cxn_width_aq_in,'stop_width':self.cxn_width_aq_in})
        self.cxns[cxns_names[1]] = s.last.copyjunc()
