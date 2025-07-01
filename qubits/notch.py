# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 17:53:20 2022

@author: Theo Gifford
"""

import numpy as np
from component import Component
from pt_operations import rotate_pt, rotate_pts, translate_pts, orient_pts, mirror_pts
from junction import Junction
from component import Component

class QubitNotchFromJunc(Component):
    """
    Draws a qubit notch based on a cxn junction
    
    settings:
        pinw: pinw of CPW the notch attaches to
        gapw: gapw of CPW the notch attaches to
        height: height of notch from base to base
        taper_angle: inner angle of tapers on both sides of the notch
        notch_type: currently only takes 'trapezoid'
        length: full length of the notch, along the CPW
        leftright: if refjunc.direction is up, draws the notch on the 'left' or
            'right' side of the CPW
        refjunc: endpoint of CPW the notch attaches to
        offset: if refjunc.direction is up, positive offset shifts the notch 
            down along the CPW
    
    essentially, pass it a 'in' or 'out' junction of a straight and it draws
    the notch on that straight
    
    thinking:
        - should it take a startjunc or a CPWStraight as an argument
        - should startjunc be moved to settings for all Components, along with
          cxns_names_defaults? idk it just seems wrong suddenly
    
    """
    _defaults = {}
    _defaults['pinw'] = 20
    _defaults['gapw'] = 8.372
    _defaults['height'] = 100
    _defaults['taper_angle'] = 60 # (0-90]
    _defaults['notch_type'] = 'trapezoid' # / bevel / etc idk
    _defaults['length'] = 500
    _defaults['leftright'] = 'right'
    _defaults['refjunc'] = None
    _defaults['offset'] = 0
    
    def __init__(self, structure, settings = {}):
        
        s = structure
        
        comp_key = 'QubitNotchFromJunc'
        global_keys = ['pinw','gapw']
        object_keys = ['pinw','gapw'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)        
        
        if self.refjunc is None:
            print("please provide refjunc for notch")
            return
        
        coords = self.refjunc.coords
        direction = self.refjunc.direction + 180
        d_to_gnd = self.gapw + 0.5*self.pinw
        
        if self.notch_type == 'trapezoid':
            tf = np.tan(np.pi*self.taper_angle/180)
            pts = [(0,d_to_gnd),
                   (self.height/tf,d_to_gnd+self.height),
                   (self.length - self.height/tf,d_to_gnd+self.height),
                   (self.length,d_to_gnd),
                   (0,d_to_gnd)]
            
            pts = translate_pts(pts,(self.offset,0))
            pts = orient_pts(pts,direction,coords)
            
            if self.leftright == 'left':
                pts = mirror_pts(pts,direction,coords)
            
            s.drawing.add_lwpolyline(pts)
        else:
            valid_notch_types = ['trapezoid']
            print('Invalid notch_type for QubitNotchFromJunc at {}. Supported notch_types are {}'.format(coords,valid_notch_types))
            return

        
        