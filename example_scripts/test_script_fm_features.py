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
# from DrawCodes.CAD_codes.cpw.CPWLinearTaper import CPWLinearTaper

defaults = {}
defaults['channel_width'] = 100
defaults['radius'] = 500

chip = Chip(20000)
chip.defaults = defaults

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
CTriBend(chip,settings={'width_2':np.sqrt(2)*defaults['channel_width'],'turn_angle':120})
CStraight(chip,settings={'width':np.sqrt(2)*defaults['channel_width'],'length':500})

startjunc3 = Junction((1000,10000),60)

CStraight(chip,startjunc=startjunc3,settings={'width':200,'length':500})
CSharpTurn(chip,settings={'width_1':200,'turn_angle':120})
CStraight(chip)
CSharpTurn(chip,settings={'width_2':200,'turn_angle':-60})
CStraight(chip,settings={'width':200,'length':500})
CSharpTurn(chip,settings={'width_1':200,'turn_angle':-60})
CStraight(chip)


#save
saveDir = r'C:\Users\theom\Documents\Scarcelli\Flow CAD'
filename = 'fmv1_test.dxf'
chip.saveas(os.path.join(saveDir,filename))