import sdxf
from pt_operations import rotate_pt, rotate_pts, translate_pts, arc_pts
from junction import Junction
from component import Component
import numpy as np

class CPWBendTaper(Component):
    """
    creates a CPW bend with pinw/gapw/radius
            
    turn_angle: turn_angle is in degrees, positive is CCW, negative is CW
    polyarc: True/False, True draws CPWBend as a polyline, False as arcs and lines
    segments: number of segments that a full 360 bend would use
            
    """
    
    _defaults = {}
    _defaults['turn_angle'] = 90
    _defaults['start_pinw'] = 20
    _defaults['stop_pinw'] = 20
    _defaults['start_gapw'] = 8.372
    _defaults['stop_gapw'] = 8.372
    _defaults['radius'] = 100
    _defaults['polyarc'] = True
    _defaults['segments'] = 180
    
    def __init__(self,structure,startjunc=None,settings={},cxns_names=['in','out']):
        #load default values if necessary
        
        s=structure
#        print('radius',radius)

        comp_key = 'CPWBend'
        global_keys = ['pinw','pinw','gapw','gapw','radius']
        object_keys = ['start_pinw','stop_pinw','start_gapw','stop_gapw','radius'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        settings = self.settings
        
        self.structure=structure
      
        if startjunc is None: startjunc = s.last.copyjunc()
        
        if self.turn_angle==0:
            s.last = startjunc.copyjunc()
            return

        self.start=startjunc.coords
        self.start_angle=startjunc.direction
        self.stop_angle=self.start_angle+self.turn_angle
        
        turn_angle = self.turn_angle
        if turn_angle>0: self.asign=1
        else:            self.asign=-1
       
        #DXF uses the angle of the radial vector for its start and stop angles
        #so we have to rotate our angles by 90 degrees to get them right
        #also it only knows about arcs with CCW sense to them, so we have to rotate our angles appropriately
        self.astart_angle=self.start_angle-self.asign*90
        self.astop_angle=self.stop_angle-self.asign*90
        #calculate location of Arc center
        self.center=rotate_pt( (self.start[0],self.start[1]+self.asign*self.radius),self.start_angle,self.start)
        
        if self.polyarc: self.poly_arc_bend()
        else:       self.arc_bend()

        self.stop=rotate_pt(self.start,self.stop_angle-self.start_angle,self.center)
        self.structure.last = Junction(self.stop,self.stop_angle)
        
        self.cxns = {cxns_names[0]:Junction(self.start,self.start_angle+180),cxns_names[1]:Junction(self.stop,self.stop_angle)}

    def arc_bend(self):
        print("polyarc = False no longer supported!")
        self.poly_arc_bend()
        """  
        #print "start: %d, stop: %d" % (start_angle,stop_angle)
        
        if self.turn_angle>0:
            self.astart_angle=self.start_angle-90
            self.astop_angle=self.stop_angle-90
            #calculate location of Arc center
            self.center=rotate_pt( (self.start[0],self.start[1]+self.radius),self.start_angle,self.start)
        else:
            self.astart_angle=self.stop_angle+90
            self.astop_angle=self.start_angle+90
   
        #make endlines for inner arc
        #start first gap
        points1=[   (self.start[0],self.start[1]+self.pinw/2.),
                    (self.start[0],self.start[1]+self.pinw/2.+self.gapw)
                ]
                
        points1=rotate_pts(points1,self.start_angle,self.start)
        points2=rotate_pts(points1,self.stop_angle-self.start_angle,self.center)
        
        #start 2nd gap
        points3=[   (self.start[0],self.start[1]-self.pinw/2.),
                    (self.start[0],self.start[1]-self.pinw/2.-self.gapw)
                ]
        points3=rotate_pts(points3,self.start_angle,self.start)
        points4=rotate_pts(points3,self.stop_angle-self.start_angle,self.center)

        
        #make inner arcs
        self.structure.drawing.append(sdxf.Line(points1))
        self.structure.drawing.append(sdxf.Arc(self.center,self.radius+self.pinw/2.,self.astart_angle,self.astop_angle))
        self.structure.drawing.append(sdxf.Arc(self.center,self.radius+self.pinw/2.+self.gapw,self.astart_angle,self.astop_angle))
        self.structure.drawing.append(sdxf.Line(points2))
        
        
        self.structure.drawing.append(sdxf.Line(points3))
        self.structure.drawing.append(sdxf.Arc(self.center,self.radius-self.pinw/2.,self.astart_angle,self.astop_angle))
        self.structure.drawing.append(sdxf.Arc(self.center,self.radius-self.pinw/2.-self.gapw,self.astart_angle,self.astop_angle))
        self.structure.drawing.append(sdxf.Line(points4))            
        """    

    def poly_arc_bend(self):
    
        #lower gap
        num_segments = np.abs(np.round(self.segments*self.turn_angle/360)).astype(int) #based on what proportion of 360 the subtended angle is
        
        def taper_arc_pts(start_angle,stop_angle,r1,r2,segments=360):
            pts=[]
            for ii in range(segments):
                try:
                    theta=(start_angle+ii/(segments-1.)*(stop_angle-start_angle))*np.pi/180.
                except:
                    print(stop_angle-start_angle)
                r = r1 + (r2-r1)*((theta*180/np.pi)-start_angle)/(stop_angle-start_angle)
                p=(r*np.cos(theta),r*np.sin(theta))
                pts.append(p)
            return pts
        
        pts1=taper_arc_pts(self.astart_angle,self.astop_angle,self.radius+self.start_pinw/2.+self.start_gapw,self.radius+self.stop_pinw/2.+self.stop_gapw,num_segments)
        pts1.extend(taper_arc_pts(self.astop_angle,self.astart_angle,self.radius+self.stop_pinw/2.,self.radius+self.start_pinw/2.,num_segments))
        pts1.append(pts1[0])
       
        pts2=taper_arc_pts(self.astart_angle,self.astop_angle,self.radius-self.start_pinw/2.,self.radius-self.stop_pinw/2.,num_segments)
        pts2.extend(taper_arc_pts(self.astop_angle,self.astart_angle,self.radius-self.stop_pinw/2.-self.stop_gapw,self.radius-self.start_pinw/2.-self.start_gapw,num_segments))
        pts2.append(pts2[0])
      
        self.structure.drawing.add_lwpolyline(translate_pts(pts1,self.center))
        self.structure.drawing.add_lwpolyline(translate_pts(pts2,self.center))
        
