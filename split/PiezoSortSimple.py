from pt_operations import rotate_pt, rotate_pts, orient_pt, orient_pts, translate_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CTriTurn import CTriTurn
from channel.CUnevenTaper import CUnevenTaper
from split.BasicSortThree import BasicSortThree

class PiezoSortSimple(Component):
    """A basic intersection of one sample channel and two focusing streams
    
    """
    
    _defaults = {}
    _defaults['in_width'] = 50 # width @ droplet input
    _defaults['waste_width'] = 50 # width @ waste channel output
    _defaults['piezo_width'] = 200 # width @ piezo channel inputs
    _defaults['sort_width'] = 50 # width @ sort channel output
    _defaults['focus_width'] = 50# width @ focus channel intersection 
    
    _defaults['sort_angle'] = 15 # angle of outgoing sort channels
    
    _defaults['straight_length'] = 500
    _defaults['nozzle_distance'] = 100 # how far away are nozzles from split

    _defaults['piezo_taper_length'] = 100
    _defaults['piezo_offset'] = 0 # offset between two ends of the taper
    _defaults['fan_width'] = 100

    
    _defaults['filter_channel_width'] = 10
    _defaults['filter_channel_spacing'] = 40
    
    _defaults['layer'] = 0
    
    _cxns_names = ['in','piezo_1','piezo_2','sort_1','sort_2','waste']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'PiezoSortSimple'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['in_width','sort_width','waste_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        ## draw the straight
        
        CStraight(s,startjunc=startjunc,settings={'width':self.in_width,'length':self.straight_length})
        
        ## draw the BasicSortThree
        #5 3 4

        self.sort_three = BasicSortThree(s,settings={'in_width':self.in_width,'waste_width':self.waste_width,'sort_width':self.sort_width,'sort_angle':self.sort_angle})
        
        self.cxns[cxns_names[5]] = self.sort_three.cxns['waste']
        self.cxns[cxns_names[3]] = self.sort_three.cxns['sort_1']
        self.cxns[cxns_names[4]] = self.sort_three.cxns['sort_2']
        
        upjunc = Junction(orient_pt((self.straight_length-self.nozzle_distance,self.in_width/2),startjunc.direction,startjunc.coords),90+startjunc.direction)
        downjunc = Junction(orient_pt((self.straight_length-self.nozzle_distance,-self.in_width/2),startjunc.direction,startjunc.coords),-90+startjunc.direction)
        
        offset_b = (self.piezo_width-self.focus_width-self.piezo_offset)/2
        offset_f = (self.piezo_width-self.focus_width+self.piezo_offset)/2
        
        CUnevenTaper(s,startjunc=upjunc,settings={'start_width':self.focus_width,'add_left':offset_b,'add_right':offset_f,'length':self.piezo_taper_length})
        self.cxns[cxns_names[1]] = s.last.copyjunc()
        CUnevenTaper(s,startjunc=downjunc,settings={'start_width':self.focus_width,'add_left':offset_f,'add_right':offset_b,'length':self.piezo_taper_length})
        self.cxns[cxns_names[2]] = s.last.copyjunc()
        
        s.last = self.cxns[cxns_names[5]].copyjunc()
        
        self.height = self.in_width/2 + self.piezo_taper_length


        
