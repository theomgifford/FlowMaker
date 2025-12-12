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
from channel.CTriTurn import CTriTurn
from channel.CSharpTurn import CSharpTurn
from channel.CSharpBend import CSharpBend
from focusing.CrossGenerator import CrossGenerator
from let.BasicInlet import BasicInlet
from split.BasicSortTwo import BasicSortTwo
from split.BasicSortThree import BasicSortThree
from focusing.BasicFocusStreams import BasicFocusStreams
from focusing.HydrogelGenerator import HydrogelGenerator
from split.SheathSplit import SheathSplit
from split.DropletExtractor import DropletExtractor
from alignment.TetratrianglePos import TetratrianglePos
from alignment.TetratriangleNeg import TetratriangleNeg
from alignment.TetratriangleCrossPos import TetratriangleCrossPos
from alignment.TetratriangleCrossNeg import TetratriangleCrossNeg
from alignment.TetratriangleSeries import TetratriangleSeries
from alignment.TetratriangleCrossSeries import TetratriangleCrossSeries
# from DrawCodes.CAD_codes.cpw.CPWLinearTaper import CPWLinearTaper

defaults = {}
defaults['channel_width'] = 200
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
CSharpBend(chip,settings={'turn_angle':90})

startjunc2 = Junction((1000,5000),60)

CStraight(chip,startjunc=startjunc2)
CTriTurn(chip,settings={'stop_width':np.sqrt(2)*defaults['channel_width'],'turn_angle':120})
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
basic_sort = BasicSortTwo(chip,startjunc=startjunc5,settings={'split_angle':15})
addStraights(chip,basic_sort)

startjunc6 = Junction((4500,9000),0)
basic_focus = BasicFocusStreams(chip,startjunc=startjunc6,settings={'focus_angle':90})
basic_sort3 = BasicSortThree(chip,settings={'waste_width':40,'sort_width':80,'sort_angle':30})
CStraight(chip,settings={'length':600,'width':basic_sort3.settings['waste_width']})
CStraight(chip,startjunc=basic_sort3.cxns['sort_1'],settings={'length':600,'width':basic_sort3.settings['sort_width']})
CStraight(chip,startjunc=basic_sort3.cxns['sort_2'],settings={'length':600,'width':basic_sort3.settings['sort_width']})


CStraight(chip,startjunc=basic_focus.cxns['samp'],settings={'length':600,'width':basic_focus.settings['samp_width']})
CStraight(chip,startjunc=basic_focus.cxns['focus_1'],settings={'length':600,'width':basic_focus.settings['focus_width']})
CStraight(chip,startjunc=basic_focus.cxns['focus_2'],settings={'length':600,'width':basic_focus.settings['focus_width']})

startjunc7 = Junction((4500,1500),0)
hydrogel_gen = HydrogelGenerator(chip,startjunc=startjunc7,settings = {'cxn_width_drop':400});
CStraight(chip,startjunc=hydrogel_gen.cxns['core'],settings={'length':600,'width':hydrogel_gen.settings['cxn_width_core']})
CStraight(chip,startjunc=hydrogel_gen.cxns['drop'],settings={'length':600,'width':hydrogel_gen.settings['cxn_width_drop']})
CStraight(chip,startjunc=hydrogel_gen.cxns['shell_1'],settings={'length':600,'width':hydrogel_gen.settings['cxn_width_shell']})
CStraight(chip,startjunc=hydrogel_gen.cxns['shell_2'],settings={'length':600,'width':hydrogel_gen.settings['cxn_width_shell']})
CStraight(chip,startjunc=hydrogel_gen.cxns['oil_1'],settings={'length':600,'width':hydrogel_gen.settings['width_oil']})
CStraight(chip,startjunc=hydrogel_gen.cxns['oil_2'],settings={'length':600,'width':hydrogel_gen.settings['width_oil']})

startjunc8 = Junction((4500,5000),0)
sheath_split = SheathSplit(chip,startjunc=startjunc8)
addStraights(chip,sheath_split)

settings_drop_extr = DropletExtractor._defaults
startjunc9 = Junction((8500,1500),10-settings_drop_extr['entrance_angle_oil'])
drop_extr = DropletExtractor(chip,startjunc=startjunc9,settings=settings_drop_extr)

startjunc10 = Junction((8500,5000),90)
TetratrianglePos(chip,startjunc=startjunc10)
TetratrianglePos(chip)
TetratriangleNeg(chip,startjunc=startjunc10)
TetratriangleNeg(chip)

startjunc11 = Junction((9000,5000),90)
TetratriangleCrossPos(chip,startjunc=startjunc11)
TetratriangleCrossPos(chip)
TetratriangleCrossNeg(chip,startjunc=startjunc11)
TetratriangleCrossNeg(chip)

TTS_junc_0 = Junction((9000,9000),90)
TetratriangleSeries(chip,startjunc=TTS_junc_0,settings={'layer':0})
TTS_junc_1 = Junction((9500,9000),90)
TetratriangleSeries(chip,startjunc=TTS_junc_1,settings={'layer':1})
TTS_junc_2 = Junction((10000,9000),90)
TetratriangleSeries(chip,startjunc=TTS_junc_2,settings={'layer':2})

TTCS_junc_0 = Junction((10500,9000),90)
TetratriangleCrossSeries(chip,startjunc=TTCS_junc_0,settings={'layer':0})
TTCS_junc_1 = Junction((11000,9000),90)
TetratriangleCrossSeries(chip,startjunc=TTCS_junc_1,settings={'layer':1})
TTCS_junc_2 = Junction((11500,9000),90)
TetratriangleCrossSeries(chip,startjunc=TTCS_junc_2,settings={'layer':2})

#save
saveDir = r'C:\Users\theom\Documents\Scarcelli\Flow CAD'
filename = 'fmv1_test.dxf'
chip.saveas(os.path.join(saveDir,filename))