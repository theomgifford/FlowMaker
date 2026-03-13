from pt_operations import rotate_pt, rotate_pts, orient_pt, arc_pts, translate_pts, orient_pts
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraight import CStraight
from channel.CSharpBend import CSharpBend
from channel.CStraightTaper import CStraightTaper

from split.UnevenSplit import UnevenSplit

from connectors.SimpleStraightConnector import SimpleStraightConnector

class SheathSplitCrossoverInlet(Component):
    """An inlet that has a more robust split into two sheath streams
    
    
    """
    
    _defaults = {}
    
    _defaults['body_width'] = 3000
    _defaults['taper_length'] = 1000
    _defaults['body_length'] = 2000
    _defaults['segments'] = 180
        
    _defaults['middle_gap'] = 0
    
    _defaults['inside_angle'] = 20
    _defaults['outside_angle'] = 0
    _defaults['cxn_angle'] = 0
    
    _defaults['inside_width'] = 100
    _defaults['outside_width'] = 100
    _defaults['cxn_width'] = 100
        
    _cxns_names = ['left','right']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'SheathSplitCrossoverInlet'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['cxn_width','inside_width','outside_width'] 
        super().__init__(structure,comp_key,global_keys,object_keys,settings)
                
        if startjunc is None:
            print("Please specify a startjunc")
            return
        
        CStraightTaper(s,startjunc=startjunc.reverse(),settings={'start_width':self.middle_gap,'stop_width':self.body_width,'length':self.taper_length})
        
        origin = s.last.reverse()
        # print(origin)
        
        r = self.body_width/2
        x = self.body_length
        y = self.body_width/2 + self.outside_width
        theta = (np.arctan(y/x)-np.arctan(r/np.sqrt(x**2+y**2-r**2)))*180/np.pi
        self.theta = theta
        # int_x = self.body_length + r*np.cos(theta*np.pi/180)
        # int_y = r*np.sin(theta*np.pi/180)
        
        pts = []
        pts.append((0,self.body_width/2+self.outside_width))
        pts.extend(translate_pts(arc_pts(90-theta,-(90-theta),r,self.segments+1),(x,0)))
        pts.append((0,-(self.body_width/2+self.outside_width)))
        pts.append(pts[0])
        
        pts = orient_pts(pts,s.last.direction,s.last.coords)
        
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(pts)
            
        top_settings = {}
        top_settings['in_width'] = self.cxn_width
        top_settings['left_width'] = self.inside_width
        top_settings['right_width'] = self.outside_width
        top_settings['left_offset'] = 0
        top_settings['right_offset'] = 0
        top_settings['left_angle'] = self.inside_angle - self.cxn_angle
        top_settings['right_angle'] = self.cxn_angle - self.outside_angle
        top_settings['left_initial_angle'] = 0
        top_settings['right_initial_angle'] = 0
        top_settings['start'] = 'right'
                
        bot_settings = {}
        bot_settings['in_width'] = self.cxn_width
        bot_settings['left_width'] = self.outside_width
        bot_settings['right_width'] = self.inside_width
        bot_settings['left_offset'] = 0
        bot_settings['right_offset'] = 0
        bot_settings['left_angle'] = self.cxn_angle - self.outside_angle
        bot_settings['right_angle'] = self.inside_angle - self.cxn_angle
        bot_settings['left_initial_angle'] = 0
        bot_settings['right_initial_angle'] = 0
        bot_settings['start'] = 'left'
        
        s.local_write = False
        template_split = UnevenSplit(s, startjunc = Junction((0,0),self.outside_angle+origin.direction), settings = top_settings)
        s.local_write = True
        
        G = template_split.poly[3]
        
        OT1 = Junction(orient_pt((0,self.body_width/2+self.outside_width/2),origin.direction,origin.coords),origin.direction)
        OB1 = Junction(orient_pt((0,-(self.body_width/2+self.outside_width/2)),origin.direction,origin.coords),origin.direction)
                
        CSharpBend(s,startjunc=OT1,settings={'width':self.outside_width,'turn_angle':self.outside_angle,'segments':360})
        OT2 = s.last.copyjunc()
        CSharpBend(s,startjunc=OB1,settings={'width':self.outside_width,'turn_angle':-self.outside_angle,'segments':360})
        OB2 = s.last.copyjunc()
        
        taper_angle = 180/np.pi * np.arctan((self.body_width/2-self.middle_gap/2)/self.taper_length)
        taper_wall_angle = 90 - taper_angle
        
        IT1 = Junction(orient_pt((self.taper_length-self.inside_width/2 * np.cos(taper_angle*np.pi/180),self.middle_gap/2+self.inside_width/2 * np.sin(taper_angle*np.pi/180)),origin.direction,origin.coords),origin.direction + taper_wall_angle)
        IB1 = Junction(orient_pt((self.taper_length-self.inside_width/2 * np.cos(taper_angle*np.pi/180),-(self.middle_gap/2+self.inside_width/2 * np.sin(taper_angle*np.pi/180))),origin.direction,origin.coords),origin.direction - taper_wall_angle)
        
        CSharpBend(s,startjunc=IT1,settings={'width':self.inside_width,'turn_angle':self.inside_angle - taper_wall_angle,'segments':360})
        IT2 = s.last.copyjunc()
        CSharpBend(s,startjunc=IB1,settings={'width':self.inside_width,'turn_angle':-(self.inside_angle - taper_wall_angle),'segments':360})
        IB2 = s.last.copyjunc()
        
                
        J1 = Junction((OT2.coords[0] + self.outside_width/2 * np.sin(OT2.direction * np.pi/180),OT2.coords[1] - self.outside_width/2 * np.cos(OT2.direction*np.pi/180)),OT2.direction)
        J2 = Junction((IT2.coords[0] - self.inside_width/2 * np.sin(IT2.direction * np.pi/180),IT2.coords[1] + self.inside_width/2 * np.cos(IT2.direction*np.pi/180)),IT2.direction)
        
        # print(OT1)
        # print(OT2)
        # print(OB1)
        # print(OB2)
        # print(IT1)
        # print(IT2)
        # print(IB1)
        # print(IB2)
        # print(J1)
        # print(J2)
        
        M = np.array([
            [-np.tan(J1.direction*np.pi/180),1],
            [-np.tan(J2.direction*np.pi/180),1]
            ])
        
        b = np.array([
            [-np.tan(J1.direction*np.pi/180)*J1.coords[0] + J1.coords[1]],
            [-np.tan(J2.direction*np.pi/180)*J2.coords[0] + J2.coords[1]]
            ])
        
        GT = np.linalg.solve(M,b)
        GT = (GT[0][0],GT[1][0])
        
        # print(GT)
        # print(G)
        
        # print(E_real)
        # print(E)
        
        ST = Junction((GT[0]-G[0],GT[1]-G[1]),self.outside_angle + origin.direction)
              
        ref = np.array([
            [np.cos(2*origin.direction*np.pi/180),np.sin(2*origin.direction*np.pi/180)],
            [np.sin(2*origin.direction*np.pi/180),-np.cos(2*origin.direction*np.pi/180)]
            ])        
        
        # print(ST.coords[0]-origin.coords[0])
        # print(ST.coords[1]-origin.coords[1])
        # print(np.array([[ST.coords[0]-origin.coords[0]],[ST.coords[1]-origin.coords[1]]]))
        # print(np.matmul(ref,np.array([[ST.coords[0]-origin.coords[0]],[ST.coords[1]-origin.coords[1]]])))
        SB = np.matmul(ref,np.array([[ST.coords[0]-origin.coords[0]],[ST.coords[1]-origin.coords[1]]])) + np.array([[origin.coords[0]],[origin.coords[1]]])
                
        SB = Junction((SB[0][0],SB[1][0]),origin.direction-self.outside_angle)
        
        # print(SB)

        # print(ST)
        
        top_split = UnevenSplit(s,startjunc=ST,settings=top_settings)
        bot_split = UnevenSplit(s,startjunc=SB,settings=bot_settings)
        
        SimpleStraightConnector(s,startjunc=OT2,settings={'target_junc':top_split.cxns['right']})
        SimpleStraightConnector(s,startjunc=IT2,settings={'target_junc':top_split.cxns['left']})
        SimpleStraightConnector(s,startjunc=OB2,settings={'target_junc':bot_split.cxns['left']})
        SimpleStraightConnector(s,startjunc=IB2,settings={'target_junc':bot_split.cxns['right']})
        
        self.cxns = {}
        self.cxns[cxns_names[0]] = top_split.cxns['in']
        self.cxns[cxns_names[1]] = bot_split.cxns['in']
        
        # print(inside_connector.resid)
        # print(outside_connector.resid)