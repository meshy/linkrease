#This file is part of linkrease.

#linkrease is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#linkrease is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with linkrease.  If not, see <http://www.gnu.org/licenses/>.

from pyglet import image


SKIP_INTRO = False
ADD_RANDOM_CREASES = True

SCR_W = 700
SCR_H = 700
SCR_MID_X = SCR_W / 2
SCR_MID_Y = SCR_H / 2

LVL_W = SCR_W * 2.0
LVL_H = SCR_H * 2.0
LVL_MID_X = LVL_W / 2
LVL_MID_Y = LVL_H / 2

BEZEL_X = 20.0
BEZEL_Y = BEZEL_X

ZOOM_MIN = 0.5
ZOOM_MAX = 2.0
ZOOM_STEP = 0.1

PLAYER = ['NEUTRAL', 'player1', 'player2']

COLOUR_DATA = {
               'intro': {
                          'background': (255, 255, 255, 255),
                          'text': (0, 0, 0, 0),
                          },
               'menu': {
                        'background': (0, 0, 0, 0),
                        'text': (0, 0, 0, 0),
                        },
               'game': {
                        'background': (255, 255, 255, 255),
                        'link': {
                                 False: (0, 192, 192),  # standard
                                 True: (0, 0, 0),  # highlighted
                                 },
                        'crease': {
                                   False: (0, 128, 192),  # standard
                                   True: (0, 0, 0),  # highlighted
                                   },
                        'node': {
                                 PLAYER[0]: (192, 192, 192),
                                 PLAYER[1]: (0, 160, 0),
                                 PLAYER[2]: (160, 0, 0),
                                 },
                        'factory': {
                                    PLAYER[0]: (192, 192, 192),
                                    PLAYER[1]: (0, 160, 0),
                                    PLAYER[2]: (160, 0, 0),
                                    },
                        'unit': {
                                 PLAYER[0]: (192, 192, 192),
                                 PLAYER[1]: (0, 160, 0),
                                 PLAYER[2]: (160, 0, 0),
                                 },
                        },
               }

IMAGE_DATA = {
              'node': image.load('node.png'),
              'factory': image.load('factory.png'),
              'link': image.load('link.png'),
              'crease': image.load('crease.png'),
              'unit': image.load('unit.png'),
              }

UNIT_SPEED = {  # per second
              'link': 0.06,
              'crease': 0.2,
             }

UNIT_SPEED['ratio'] = UNIT_SPEED['link'] / UNIT_SPEED['crease']
