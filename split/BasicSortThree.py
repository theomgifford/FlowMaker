from pt_operations import rotate_pt, rotate_pts, orient_pt, translate_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CTriTurn import CTriTurn

class BasicSortThree(Component):
    """A basic intersection of one sample channel and two focusing streams
    
    """
    
    _defaults = {}
    _defaults['in_width'] = 50 # width @ dispersed phase input
    _defaults['waste_width'] = 50 # width @ formed droplet output
    _defaults['sort_width'] = 50 # width @ focus channel inputs
    _defaults['sort_angle'] = 15 # angle of focus channels
    
    _cxns_names = ['in','waste','sort_1','sort_2']
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=_cxns_names):
        #load attributes
        s=structure
        
        comp_key = 'BasicSortThree'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['in_width','waste_width','sort_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        self.focus_angle = 180 - self.sort_angle

        ## below code copies from BasicFocusStreams
        
        theta_rad = self.focus_angle*np.pi/180
        phi = np.arctan(np.sin(theta_rad)*(self.waste_width-self.in_width)/(2*self.sort_width-np.cos(theta_rad)*(self.waste_width-self.in_width)))*180/np.pi
        
        self.length = self.sort_width/np.sin(theta_rad) - 0.5*(self.waste_width-self.in_width)/np.tan(theta_rad)
        
        CStraightTaper(s,startjunc=startjunc,settings={'start_width':self.in_width,'stop_width':self.waste_width,'length':self.length})
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        self.cxns[cxns_names[1]]= stopjunc
        # coords = orient_pt((0.5*taper_length,-0.25*(self.out_width+self.samp_width)),startjunc.direction,startjunc.coords)
        # direction = startjunc.direction+90+phi
        # print(coords)
        # print(type(coords))
        # print(direction)
        # print(type(direction))
        junc1 = Junction(orient_pt((0.5*self.length,0.25*(self.waste_width+self.in_width)),startjunc.direction,startjunc.coords),startjunc.direction+90+phi)
        junc2 = Junction(orient_pt((0.5*self.length,-0.25*(self.waste_width+self.in_width)),startjunc.direction,startjunc.coords),startjunc.direction-90-phi)
        
        side_length = self.sort_width/np.sin((self.focus_angle+phi)*np.pi/180)
        
        CTriTurn(s,startjunc=junc1,settings={'start_width':side_length,'stop_width':self.sort_width,'turn_angle':90-self.focus_angle-phi})
        self.cxns[cxns_names[2]] = s.last.copyjunc()

        CTriTurn(s,startjunc=junc2,settings={'start_width':side_length,'stop_width':self.sort_width,'turn_angle':-(90-self.focus_angle-phi)})
        self.cxns[cxns_names[3]] = s.last.copyjunc()
        
        s.last = self.cxns[cxns_names[1]]
        
        self.top_hor_proj = self.length - self.sort_width*np.sin(self.sort_angle*np.pi/180)
        self.third_side = np.abs(self.sort_width / np.tan((self.focus_angle+phi)*np.pi/180))
        self.top_coords = translate_pt(rotate_pt(translate_pt(self.cxns[cxns_names[2]].coords,(-startjunc.coords[0],-startjunc.coords[1])),-startjunc.direction),(self.sort_width/2*np.cos((self.sort_angle+90)*np.pi/180),self.sort_width/2*np.sin((self.sort_angle+90)*np.pi/180)))
        self.top_length = np.sqrt((self.top_coords[0])**2+(self.top_coords[1]-self.in_width/2)**2)