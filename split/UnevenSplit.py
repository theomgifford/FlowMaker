from pt_operations import rotate_pt, rotate_pts, orient_pt, orient_pts, translate_pts, translate_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CTriTurn import CTriTurn

class UnevenSplit(Component):
    """A basic V-sorter
    
    """
    
    _defaults = {}
    _defaults['in_width'] = 50
    _defaults['left_width'] = 50
    _defaults['right_width'] = 50
    _defaults['left_offset'] = 0
    _defaults['right_offset'] = 0
    _defaults['left_angle'] = 15
    _defaults['right_angle'] = 15
    _defaults['left_initial_angle'] = 0
    _defaults['right_initial_angle'] = 0
    
    _defaults['start'] = 'in'
    _defaults['end'] = 'left'
    
    _cxns_names = ['in','left','right']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'UnevenSplit'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['in_width','left_width','right_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None:
            startjunc=s.last.copyjunc()
        else:
            s.last = startjunc.copyjunc()
                    
        A = (0,self.in_width/2)
        B = (0,-self.in_width/2)
        C = (self.left_offset*np.cos(self.left_initial_angle*np.pi/180),self.in_width/2 + self.left_offset*np.sin(self.left_initial_angle*np.pi/180))
        D = (self.right_offset*np.cos(self.right_initial_angle*np.pi/180),-self.in_width/2 - self.right_offset*np.sin(self.right_initial_angle*np.pi/180))
        
        M = np.array([
            [-np.tan(self.left_angle*np.pi/180),1],
            [-np.tan(-self.right_angle*np.pi/180),1]
            ])
        
        b = np.array([
            [-self.left_width*np.sqrt(1+(np.tan(self.left_angle*np.pi/180))**2)+C[1]-np.tan(self.left_angle*np.pi/180)*C[0]],
            [self.right_width*np.sqrt(1+(np.tan(-self.right_angle*np.pi/180))**2)+D[1]-np.tan(-self.right_angle*np.pi/180)*D[0]]
            ])
        
        # G = tuple(np.transpose(np.linalg.solve(M,b)))
        G = np.linalg.solve(M,b)
        G = (G[0][0],G[1][0])
    
        # print(G)
        
        E = (G[0]+self.left_width*np.cos((self.left_angle+90)*np.pi/180),G[1]+self.left_width*np.sin((self.left_angle+90)*np.pi/180))
        F = (G[0]+self.right_width*np.cos((-self.right_angle-90)*np.pi/180),G[1]+self.right_width*np.sin((-self.right_angle-90)*np.pi/180))

        poly = [A,C,E,G,F,D,B,A]
        
        origin = (0,0)
        cxn1 = (G[0]+self.left_width*np.cos((self.left_angle+90)*np.pi/180)/2,G[1]+self.left_width*np.sin((self.left_angle+90)*np.pi/180)/2)
        cxn2 = (G[0]+self.right_width*np.cos((-self.right_angle-90)*np.pi/180)/2,G[1]+self.right_width*np.sin((-self.right_angle-90)*np.pi/180)/2)
        
        self.cxns = {}
        if self.start == 'left':
            
            poly = translate_pts(rotate_pts(poly,180-self.left_angle,cxn1),(-cxn1[0],-cxn1[1]))
            in_junc = Junction(translate_pt(rotate_pt(origin,180-self.left_angle,cxn1),(-cxn1[0],-cxn1[1])),-self.left_angle)
            cxn1_junc = Junction((0,0),180)         
            cxn2_junc = Junction(translate_pt(rotate_pt(cxn2,180-self.left_angle,cxn1),(-cxn1[0],-cxn1[1])),180-self.left_angle-self.right_angle)

        elif self.start == 'right':
            
            poly = translate_pts(rotate_pts(poly,-(180-self.right_angle),cxn2),(-cxn2[0],-cxn2[1]))
            in_junc = Junction(translate_pt(rotate_pt(origin,-(180-self.right_angle),cxn2),(-cxn2[0],-cxn2[1])),self.right_angle)
            cxn1_junc = Junction(translate_pt(rotate_pt(cxn1,-(180-self.right_angle),cxn2),(-cxn2[0],-cxn2[1])),-(180-self.left_angle-self.right_angle))
            cxn2_junc = Junction((0,0),180)         

        else:
            
            in_junc = Junction((0,0),180)  
            cxn1_junc = Junction(cxn1,self.left_angle)
            cxn2_junc = Junction(cxn2,-self.right_angle)
        
        poly = orient_pts(poly,startjunc.direction,startjunc.coords)
        
        self.cxns[cxns_names[0]] = Junction(orient_pt(in_junc.coords,startjunc.direction,startjunc.coords),in_junc.direction+startjunc.direction)
        self.cxns[cxns_names[1]] = Junction(orient_pt(cxn1_junc.coords,startjunc.direction,startjunc.coords),cxn1_junc.direction+startjunc.direction)
        self.cxns[cxns_names[2]] = Junction(orient_pt(cxn2_junc.coords,startjunc.direction,startjunc.coords),cxn2_junc.direction+startjunc.direction)
        
        self.poly = poly
        
        if s.global_write and s.local_write:
            s.drawing.add_lwpolyline(poly)
            
        s.last = self.cxns[self.end]
