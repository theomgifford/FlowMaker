from pt_operations import rotate_pt, rotate_pts, orient_pt, orient_pts, translate_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CTriTurn import CTriTurn
from split.BasicSortThree import BasicSortThree

class PiezoSortRegion(Component):
    """A basic intersection of one sample channel and two focusing streams
    
    """
    
    _defaults = {}
    _defaults['in_width'] = 50 # width @ dispersed phase input
    _defaults['waste_width'] = 50 # width @ formed droplet output
    _defaults['piezo_width'] = 50 # width @ focus channel inputs
    _defaults['sort_width'] = 50 # width @ focus channel inputs
    
    _defaults['sort_angle'] = 15 # angle of focus channels
    
    _defaults['straight_length'] = 500
    _defaults['extra_length'] = 100

    _defaults['minimum_wall_thickness'] = 100
    _defaults['wide_region_length'] = 300
    _defaults['piezo_angle'] = 45
    
    _defaults['filter_channel_width'] = 10
    _defaults['filter_channel_spacing'] = 40
    
    _cxns_names = ['in','piezo_1','piezo_2','sort_1','sort_2','waste']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'PiezoSortRegion'
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

        # sort_straight_length = max(0,self.extra_length/np.cos(self.sort_angle*np.pi/180) + self.sort_width/2*np.tan(self.sort_angle*np.pi/180)- max(0,self.sort_three.third_side))
        sort_straight_length = max(0,self.extra_length/np.cos(self.sort_angle*np.pi/180)-self.sort_three.top_length)
        waste_straight_length = max(0,self.extra_length - self.sort_three.length)
        
        CStraight(s,startjunc=self.sort_three.cxns['waste'],settings={'width':self.waste_width,'length':waste_straight_length})
        self.cxns[cxns_names[5]] = s.last.copyjunc()

        CStraight(s,startjunc=self.sort_three.cxns['sort_1'],settings={'width':self.sort_width,'length':sort_straight_length})
        self.cxns[cxns_names[3]] = s.last.copyjunc()
        
        CStraight(s,startjunc=self.sort_three.cxns['sort_2'],settings={'width':self.sort_width,'length':sort_straight_length})
        self.cxns[cxns_names[4]] = s.last.copyjunc()

        total_fc_width = self.filter_channel_width + self.filter_channel_spacing
        num_fc = int(np.floor((self.straight_length+self.extra_length) / total_fc_width))
        
        fc_height = self.minimum_wall_thickness + self.extra_length * np.tan(self.sort_angle*np.pi/180)
        
        def get_fc_y_pos(x):
            
            if x <= self.straight_length:
                return 0
            else:
                return (x-self.straight_length)*np.tan(self.sort_angle*np.pi/180)
        
        for i in range(num_fc):
            
            x1 = i*total_fc_width
            x2 = x1 + self.filter_channel_width
            
            y1 = get_fc_y_pos(x1)
            y2 = get_fc_y_pos(x2)
            
            fc_upper = [
                (x1,y1+self.in_width/2),
                (x1,fc_height+self.in_width/2),
                (x2,fc_height+self.in_width/2),
                (x2,y2+self.in_width/2),
                ]
            
            if x1 < self.straight_length and x2 > self.straight_length:
                fc_upper.append((self.straight_length,self.in_width/2))
            
            fc_upper.append(fc_upper[0])
            fc_upper = orient_pts(fc_upper,startjunc.direction,startjunc.coords)
            
            fc_lower = [
                (x1,-y1-self.in_width/2),
                (x1,-fc_height-self.in_width/2),
                (x2,-fc_height-self.in_width/2),
                (x2,-y2-self.in_width/2),
                ]
            
            if x1 < self.straight_length and x2 > self.straight_length:
                fc_lower.append((self.straight_length,-self.in_width/2))
            
            fc_lower.append(fc_lower[0])
            fc_lower = orient_pts(fc_lower,startjunc.direction,startjunc.coords)
            
            if s.global_write:
                s.drawing.add_lwpolyline(fc_upper)
                s.drawing.add_lwpolyline(fc_lower)
                
            if (x1 - (self.straight_length+self.sort_three.length))*np.tan(self.sort_angle*np.pi/180) > self.minimum_wall_thickness:
                cc_upper = [
                    (x1,self.waste_width/2),
                    (x1,self.waste_width/2+(x1-self.straight_length-self.sort_three.length)*np.tan(self.sort_angle*np.pi/180)),
                    (x2,self.waste_width/2+(x2-self.straight_length-self.sort_three.length)*np.tan(self.sort_angle*np.pi/180)),
                    (x2,self.waste_width/2)
                    ]
                cc_lower = [
                    (x1,-self.waste_width/2),
                    (x1,-self.waste_width/2-(x1-self.straight_length-self.sort_three.length)*np.tan(self.sort_angle*np.pi/180)),
                    (x2,-self.waste_width/2-(x2-self.straight_length-self.sort_three.length)*np.tan(self.sort_angle*np.pi/180)),
                    (x2,-self.waste_width/2)
                    ]
                
                cc_upper.append(cc_upper[0])
                cc_upper = orient_pts(cc_upper,startjunc.direction,startjunc.coords)
                
                cc_lower.append(cc_lower[0])
                cc_lower = orient_pts(cc_lower,startjunc.direction,startjunc.coords)
                
                if s.global_write:
                    s.drawing.add_lwpolyline(cc_upper)
                    s.drawing.add_lwpolyline(cc_lower)
        x_first = 0
        x_last = num_fc*total_fc_width + self.filter_channel_width
        
        upjunc = Junction(orient_pt(((x_last-x_first)/2,fc_height+self.in_width/2),startjunc.direction,startjunc.coords),90+startjunc.direction)

