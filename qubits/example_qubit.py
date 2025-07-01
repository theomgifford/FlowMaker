# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 18:18:15 2022

@author: Theo
"""

import numpy as np
from component import Component
from pt_operations import rotate_pt, rotate_pts, translate_pts, arc_pts, orient_pts, mirror_pts, translate_pt, orient_pt
from junction import Junction
from component import Component

from qubits.notch import QubitNotchFromJunc

class ExampleQubit(Component):
    """
    
    Example qubit mainly for development purposes. Paddles are rounded
    rectangles.
    
    settings:
        pinw: pinw of CPW the notch attaches to
        gapw: gapw of CPW the notch attaches to
        taper_angle: inner angle of tapers on both sides of the notch
        notch_type: currently only takes 'trapezoid'
        leftright: if refjunc.direction is up, draws the notch on the 'left' or
            'right' side of the CPW
        refjunc: endpoint of CPW the notch attaches to
        offset: if refjunc.direction is up, positive offset shifts the notch 
            down along the CPW
        paddle_length: full length of paddle (including paddle "caps")
        paddle_width: width of paddle (diameter of paddle "caps")
        paddle_gap: distance between paddles
        h_padding: distance between notch taper and paddle
        v_padding: distance between notch wall and paddle
    
    """
    _defaults = {}
    _defaults['pinw'] = 20
    _defaults['gapw'] = 8.372
    _defaults['refjunc'] = None
    _defaults['paddle_width'] = 20
    _defaults['paddle_length'] = 100
    _defaults['paddle_gap'] = 5
    _defaults['taper_angle'] = 60
    _defaults['h_padding'] = 10
    _defaults['v_padding'] = 20
    _defaults['offset'] = 0
    _defaults['pin_gap'] = 8.372
    _defaults['leftright'] = 'right'
    
    def __init__(self,structure,settings):
        
        s = structure
        
        comp_key = 'ExampleQubit'
        global_keys = ['pinw','gapw','pin_gap']
        object_keys = ['pinw','gapw','gapw'], # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
             
        if self.refjunc is None:
            print("please provide refjunc for qubit")
            return
        
        coords = self.refjunc.coords
        direction = self.refjunc.direction + 180
        
        radius = self.paddle_width/2
        
        # define paddle shape
        pts1 = translate_pts(arc_pts(270,90,radius,90),(radius,radius)) 
        pts2 = [(radius,2*radius),(self.paddle_length-radius,2*radius)]
        pts3 = translate_pts(arc_pts(90,-90,radius,90),(self.paddle_length-radius,radius))
        pts4 = [(self.paddle_length-radius,0),(radius,0)]
        paddle_pts = pts1 + pts2 + pts3 + pts4
        
        tf = np.tan(np.pi*self.taper_angle/180)
        
        self.height = self.pin_gap - (self.gapw + 0.5*self.pinw) + 2*self.paddle_width + self.paddle_gap + self.v_padding
        self.length = self.paddle_length + 2*self.height/tf + 2*self.h_padding
        
        # translate paddle shape to correct locations
        coords_p1 = orient_pt((self.offset+self.h_padding+self.height/tf,self.pin_gap + self.pinw/2),direction,coords)
        paddle1 = orient_pts(paddle_pts,direction,coords_p1)
        
        coords_p2 = orient_pt((self.offset+self.h_padding+self.height/tf,self.pin_gap + self.pinw/2 + self.paddle_width + self.paddle_gap),direction,coords)
        paddle2 = orient_pts(paddle_pts,direction,coords_p2)
        
        # decide which side the qubit goes on
        if self.leftright == 'left':
            paddle1 = mirror_pts(paddle1,direction,coords)
            paddle2 = mirror_pts(paddle2,direction,coords)
        elif self.leftright != 'right':
            print('invalid option passed for leftright, default value \'right\' used')
        
        s.drawing.add_lwpolyline(paddle1)
        s.drawing.add_lwpolyline(paddle2)
        
        QubitNotchFromJunc(s,settings = {'pinw': self.pinw,
                                         'gapw': self.gapw,
                                         'height': self.height,
                                         'length': self.length,
                                         'taper_angle': self.taper_angle,
                                         'leftright': self.leftright,
                                         'refjunc': self.refjunc,
                                         'offset': self.offset})
