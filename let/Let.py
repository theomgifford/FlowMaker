
from component import Component

class Let(Component):
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
    def __init__(self, structure, settings, startjunc, cxns_names):
        
        comp_key = 'Let'
        global_keys = ['channel_width']
        object_keys = ['width_cxn'] # which correspond to the extract global_keys
        Component.__init__(self,structure,comp_key,global_keys,object_keys,settings)
        
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
