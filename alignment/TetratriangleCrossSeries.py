# import sdxf

import numpy as np

from pt_operations import rotate_pts, rotate_pt
from junction import Junction
from component import Component

from alignment.TetratriangleCrossPos import TetratriangleCrossPos
from alignment.TetratriangleCrossNeg import TetratriangleCrossNeg

class TetratriangleCrossSeries(Component):
    """
    A series of Tetratriangle alignment marks. Each layer contains a negative
    and subsequent positive mark.
    
    size: side of a square occupied by alignment mark
    vertex_angle: vertex angle of each isosceles triangle
    
    """
    
    _defaults = {}
    
    _defaults['size'] = 400
    _defaults['cross_width'] = 20
    _defaults['center_ratio'] = 0.5
    _defaults['trap_angle'] = 30
    _defaults['neg_gap'] = 20
    _defaults['spacing'] = 200
    
    _defaults['layer'] = 0
    
    _cxns_names = []
    
    def __init__(self,structure,startjunc=None,settings={}, cxns_names=_cxns_names):
        """ Adds a straight section of CPW transmission line of length = length to the structure"""        
        s=structure
        
        comp_key = 'TetratriangleCrossSeries'
        global_keys = ['amark_size','amark_spacing']
        object_keys = ['size','spacing'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
                
        if startjunc is None: startjunc=s.last.copyjunc()
        
        if not isinstance(self.layer,int):
            print("layer is not an integer")
            return
        
        coords = startjunc.coords

        mark_settings = {}
        mark_settings['size'] = self.size
        mark_settings['cross_width'] = self.cross_width
        mark_settings['center_ratio'] = self.center_ratio
        mark_settings['spacing'] = self.spacing
        mark_settings['trap_angle'] = self.trap_angle
        mark_settings['neg_gap'] = self.neg_gap
        
        pos_junc = Junction(rotate_pt((coords[0]+self.layer*(self.size+self.spacing),coords[1]),startjunc.direction,coords),startjunc.direction)
        pos_junc = pos_junc.reverse()
        
        TetratriangleCrossPos(s,startjunc=pos_junc,settings=mark_settings)
        
        # print(pos_junc)
        # print(self.layer)
        
        if self.layer >= 1:
            TetratriangleCrossNeg(s,settings=mark_settings)

            
        
                
