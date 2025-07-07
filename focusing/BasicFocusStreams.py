from pt_operations import rotate_pt, rotate_pts, orient_pt
import sdxf
from junction import Junction
from component import Component
import numpy as np

from channel.CStraightTaper import CStraightTaper
from channel.CStraight import CStraight
from channel.CTriBend import CTriBend

class BasicFocusStreams(Component):
    """A basic intersection of one sample channel and two focusing streams
    
    """
    
    _defaults = {}
    _defaults['samp_width'] = 50 # width @ dispersed phase input
    _defaults['out_width'] = 50 # width @ formed droplet output
    _defaults['focus_width'] = 50 # width @ formed droplet output
    _defaults['focus_angle'] = 15 # angle of focus channels
    
    def __init__(self, structure,startjunc=None, settings = {}, cxns_names=['samp','out','focus_1','focus_2']):
        #load attributes
        s=structure
        
        comp_key = 'BasicFocusStreams'
        global_keys = ['channel_width','channel_width','channel_width']
        object_keys = ['samp_width','out_width','focus_width'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        if startjunc is None: startjunc=s.last.copyjunc()
        self.cxns = {}
        self.cxns[cxns_names[0]] = startjunc.reverse()
        
        theta_rad = self.focus_angle*np.pi/180
        phi = np.arctan(np.sin(theta_rad)*(self.out_width-self.samp_width)/(2*self.focus_width-np.cos(theta_rad)*(self.out_width-self.samp_width)))*180/np.pi
        
        self.length = self.focus_width/np.sin(theta_rad) - 0.5*(self.out_width-self.samp_width)/np.tan(theta_rad)
        
        CStraightTaper(s,startjunc=startjunc,settings={'start_width':self.samp_width,'stop_width':self.out_width,'length':self.length})
        
        #update last anchor position
        stopjunc = s.last.copyjunc()
        self.cxns[cxns_names[1]]= stopjunc
        # coords = orient_pt((0.5*taper_length,-0.25*(self.out_width+self.samp_width)),startjunc.direction,startjunc.coords)
        # direction = startjunc.direction+90+phi
        # print(coords)
        # print(type(coords))
        # print(direction)
        # print(type(direction))
        junc1 = Junction(orient_pt((0.5*self.length,0.25*(self.out_width+self.samp_width)),startjunc.direction,startjunc.coords),startjunc.direction+90+phi)
        junc2 = Junction(orient_pt((0.5*self.length,-0.25*(self.out_width+self.samp_width)),startjunc.direction,startjunc.coords),startjunc.direction-90-phi)
        
        side_length = self.focus_width/np.sin((self.focus_angle+phi)*np.pi/180)
        
        CTriBend(s,startjunc=junc1,settings={'start_width':side_length,'stop_width':self.focus_width,'turn_angle':90-self.focus_angle-phi})
        self.cxns[cxns_names[2]] = s.last.copyjunc()

        CTriBend(s,startjunc=junc2,settings={'start_width':side_length,'stop_width':self.focus_width,'turn_angle':-(90-self.focus_angle-phi)})
        self.cxns[cxns_names[3]] = s.last.copyjunc()
        
        s.last = self.cxns[cxns_names[1]]

