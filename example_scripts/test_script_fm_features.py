# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 13:49:17 2022

@author: Kollarlab
"""
import os
import numpy as np

# replace with MaskMaker filepath
# os.chdir(r"C:\Users\KollarLab\Documents\GitHub\MaskMaker")

from mask import Chip, ChipBorder

from junction import Junction

from channel.CBend import CBend
from channel.CStraight import CStraight
from channel.CStraightTaper import CStraightTaper
from channel.CBendTaper import CBendTaper
from channel.CTriBend import CTriBend
from channel.CSharpTurn import CSharpTurn
from focusing.CrossGenerator import CrossGenerator
from let.BasicInlet import BasicInlet
from sorting.BasicSortTwo import BasicSortTwo
from focusing.BasicFocusStreams import BasicFocusStreams
# from DrawCodes.CAD_codes.cpw.CPWLinearTaper import CPWLinearTaper

defaults = {}
defaults['channel_width'] = 100
defaults['radius'] = 500

chip = Chip(20000)
chip.defaults = defaults

def addStraights(structure,component):
    for key in component.cxns:
        CStraight(structure,settings = {'length':600}, startjunc = component.cxns[key])

ChipBorder(chip)

startjunc1 = Junction((1000,1000),60)

CStraight(chip,startjunc=startjunc1)
CStraight(chip,settings={'length':300})
CBend(chip)
CStraightTaper(chip,settings={'stop_width':200})
CBendTaper(chip,settings={'turn_angle':-90,'start_width':200})
CStraight(chip)

startjunc2 = Junction((1000,5000),60)

CStraight(chip,startjunc=startjunc2)
CTriBend(chip,settings={'stop_width':np.sqrt(2)*defaults['channel_width'],'turn_angle':120})
CStraight(chip,settings={'width':np.sqrt(2)*defaults['channel_width'],'length':500})

startjunc3 = Junction((1000,9000),60)

CStraight(chip,startjunc=startjunc3,settings={'width':200,'length':500})
CSharpTurn(chip,settings={'start_width':200,'turn_angle':120})
CStraight(chip)
CSharpTurn(chip,settings={'stop_width':200,'turn_angle':-60})
CStraight(chip,settings={'width':200,'length':500})
CSharpTurn(chip,settings={'start_width':200,'turn_angle':-60})
CStraight(chip)

startjunc3 = Junction((1000,13000),60)
cross_gen = CrossGenerator(chip,startjunc=startjunc3)
addStraights(chip,cross_gen)

startjunc4 = Junction((5000,17000),0)

BasicInlet(chip,startjunc=startjunc4)
CStraight(chip,settings={'length':3000})
BasicInlet(chip)

startjunc5 = Junction((4500,13000),0)
basic_sort = BasicSortTwo(chip,startjunc=startjunc5)
addStraights(chip,basic_sort)

startjunc6 = Junction((4500,9000),0)
basic_focus = BasicFocusStreams(chip,startjunc=startjunc6)

CStraight(chip,startjunc=basic_focus.cxns['samp'],settings={'length':600,'width':basic_focus.settings['samp_width']})
CStraight(chip,startjunc=basic_focus.cxns['out'],settings={'length':600,'width':basic_focus.settings['out_width']})
CStraight(chip,startjunc=basic_focus.cxns['focus_1'],settings={'length':600,'width':basic_focus.settings['focus_width']})
CStraight(chip,startjunc=basic_focus.cxns['focus_2'],settings={'length':600,'width':basic_focus.settings['focus_width']})


#save
saveDir = r'C:\Users\theom\Documents\Scarcelli\Flow CAD'
filename = 'fmv1_test.dxf'
chip.saveas(os.path.join(saveDir,filename))