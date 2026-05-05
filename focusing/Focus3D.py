from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from focusing.BasicFocusStreams import BasicFocusStreams
from channel.CStraight import CStraight

class Focus3D(Component):
    """
    
    Basic design of 3D hydrodynamic focusing junction
    
    based on Chang et al. 2007
    
    """
    
    _defaults = {}
    
    _defaults['samp_width'] = 20 # width @ two sample inputs
    _defaults['top_width'] = 100 # width @ input responsible for top focusing
    _defaults['bottom_width'] = 20 # width @ 2 inputs responsible for bottom focusing
    _defaults['side_width'] = 100 # width @ 2 inputs responsible for horizontal focusing
    _defaults['out_width'] = 100 # width of output
    # _defaults['layer'] = 0 # layers are actually outside of the component
    _defaults['gap_1'] = 100
    _defaults['gap_2'] = 100
    
    _cxns_names = ['top','samp_1','samp_2','bottom_1','bottom_2','side_1','side_2','out']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'Focus3D'
        global_keys = ['channel_width','channel_width','channel_width','channel_width','channel_width']
        object_keys = ['samp_width','out_width','top_width','bottom_width','side_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        focus_1 = BasicFocusStreams(s,startjunc=startjunc,settings = {
            'samp_width':self.top_width,
            'out_width':self.top_width,
            'focus_width':self.samp_width,
            'focus_angle':90
            })
        self.cxns[cxns_names[1]] = focus_1.cxns['focus_1']
        self.cxns[cxns_names[2]] = focus_1.cxns['focus_2']
        
        CStraight(s,settings={
            'width':self.top_width,
            'length':self.gap_1
            })
        
        focus_2 = BasicFocusStreams(s,settings = {
            'samp_width':self.top_width,
            'out_width':self.top_width,
            'focus_width':self.bottom_width,
            'focus_angle':90
            })
        self.cxns[cxns_names[3]] = focus_2.cxns['focus_1']
        self.cxns[cxns_names[4]] = focus_2.cxns['focus_2']
        
        CStraight(s,settings={
            'width':self.top_width,
            'length':self.gap_2
            })
        
        focus_3 = BasicFocusStreams(s,settings = {
            'samp_width':self.top_width,
            'out_width':self.out_width,
            'focus_width':self.side_width,
            'focus_angle':90
            })
        self.cxns[cxns_names[5]] = focus_3.cxns['focus_1']
        self.cxns[cxns_names[6]] = focus_3.cxns['focus_2']
        
        self.cxns[cxns_names[7]] = s.last

