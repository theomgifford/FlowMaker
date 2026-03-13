from pt_operations import rotate_pt, rotate_pts, orient_pt, arc_pts, orient_pts
from junction import Junction
from component import Component
import numpy as np

from let.Let import Let
from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight

class DegassedInlet(Let):
    """
    
    creates a inlet/outlet
        
    settings:
        width_body: width of fattest part of inlet
        width_cxn: width of connecting part of inlet
        taper_length: length of tapering section
        length_body: length of fattest part of inlet
        type: see note below
        
        if type is 'auto', 
            if startjunc is specified,
                the Let is a starting Let, and is drawn in the direction of 
                startjunc with the connection at startjunc (the rest of the Let 
                is drawn 'behind' startjunc)
            if startjunc is not specified
                the Let is an ending Let, and is drawn in the opposite 
                direction, with the connection at startjunc (the startjunc and the 
                connection end up being in opposite directions) 
        if type is 'start'
            the Let is a starting Let
        if type is 'end'
            the Let is an ending Let
    """
    _defaults = {}
    _defaults['body_width'] = 3000
    _defaults['cxn_width'] = 50
    _defaults['taper_length'] = 1000
    _defaults['body_length'] = 2000
    _defaults['type'] = 'auto'
    _defaults['segments'] = 180
    
    _defaults['degas_angle'] = 0
    _defaults['degas_width'] = 200
    
    _cxns_names = ['out','degas']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'DegassedInlet'
        global_keys = ['channel_width']
        object_keys = ['cxn_width'] 
        super().__init__(structure,startjunc,settings,comp_key,global_keys,object_keys)
        settings = self.settings
        
        s = structure
        if self.type == 'start':
            s.last = startjunc.reverse()
        elif self.type == 'end':
            startjunc = s.last.reverse()
        else:
            if startjunc is None: # end
                startjunc = s.last.reverse()
            else: # start
                s.last = startjunc.reverse()
                        
        CStraightTaper(s,settings={'start_width':self.cxn_width,'stop_width':self.body_width,'length':self.taper_length})
        
        CStraight(s,settings={'length':self.body_length,'width':self.body_width})
        
        num_segments = np.abs(np.round(self.segments/2)).astype(int)
        smc_pts=arc_pts(-90,90,self.body_width/2,num_segments+1)
        smc_pts.append(smc_pts[0])
        
        subtended_angle = 2 * np.arcsin(self.degas_width/self.body_width) * 180 / np.pi
        
        left_i = (self.degas_angle-subtended_angle/2)/(180/num_segments) + num_segments/2
        right_i = (self.degas_angle+subtended_angle/2)/(180/num_segments) + num_segments/2
        
        curve = smc_pts[np.floor(left_i).astype(int):np.ceil(right_i).astype(int)+1]        
        line = [
                (self.body_width/2,-self.degas_width/2),
                (self.body_width/2,0),
                (self.body_width/2,self.degas_width/2)
            ]
        line = rotate_pts(line,self.degas_angle)
        
        def intersection(P1,m1,P2,m2):
                        
            x1 = P1[0]
            y1 = P1[1]
            x2 = P2[0]
            y2 = P2[1]
            
            x = (m2*x2 - m1*x1 - (y2 - y1))/(m2-m1)
            y = m1*(x-x1) + y1
            
            P = (x,y)
                        
            return P
        
        def slope(P1,P2):
            return (P2[1]-P1[1])/(P2[0]-P1[0])

        degas_pts = []
        degas_pts.append(intersection(curve[0],slope(curve[0],curve[1]),line[0],np.tan(self.degas_angle*np.pi/180)))
        degas_pts.extend(line)
        degas_pts.append(intersection(curve[-1],slope(curve[-1],curve[-2]),line[2],np.tan(self.degas_angle*np.pi/180)))
        degas_pts.extend(reversed(curve[1:-1]))
        degas_pts.append(degas_pts[0])
        
        # print(subtended_angle)
        # print(len(smc_pts))
        # print(left_i)
        # print(right_i)
        # print(len(curve))
        # print(len(degas_pts))
                
        smc_pts=orient_pts(smc_pts,s.last.direction,s.last.coords)
        degas_pts=orient_pts(degas_pts,s.last.direction,s.last.coords)

        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(smc_pts)  
            s.drawing.add_lwpolyline(degas_pts)  
        
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.copyjunc()
        self.cxns[cxns_names[1]] = s.last.add(rotate_pt(line[1],s.last.direction),self.degas_angle)
        
        if self.type == 'start':
            s.last = startjunc.copyjunc()
        elif self.type == 'end':
            s.last = self.cxns[cxns_names[1]]
                        
        self.length = self.body_length = self.taper_length + self.body_width/2
        

    
