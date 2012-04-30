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

from math import atan2, degrees

import cocos
from cocos.sprite import Sprite
from cocos.batch import BatchNode
from cocos.actions import *

import settings
from multiplayer import neutral_player


class MapView(cocos.layer.scrolling.ScrollableLayer):
    def __init__(self, map):
        super(MapView, self).__init__()

        self.px_width = settings.LVL_W
        self.px_height = settings.LVL_H
        self.map = map
        self.nodesprites = {}
        self.linksprites = dict([(start, {end: None}) for start, end in self.map.edges_iter()])
        self.fleetsprites = {}
        self.colour_data = settings.COLOUR_DATA['game']

        self.init_node_sprites()
        self.init_link_sprites()
        self.add(BatchNode(), z=3, name="units")

        self.map.add_fleet_listener(self.on_fleet_launched)

    def draw(self):
        for fleet, fleet_spr in self.fleetsprites.items():
            fleet_spr.position = self.pixel_from_map(*fleet.get_pos())
        super(MapView, self).draw()

    def on_model_change(self):
        if self.map.dirty_flag('nodes'):
            self.update_node_sprites()
        if self.map.dirty_flag('links'):
            self.update_link_sprites()
        if self.map.dirty_flag('units'):
            self.update_unit_sprites()

    def on_fleet_launched(self, fleet):
        fleet.add_arrival_listener(self.on_fleet_arrived)
        fleet_sprite = Sprite(
                image=settings.IMAGE_DATA['unit'],
                position=self.pixel_from_map(*fleet.get_pos()),
                color=self.colour_data['unit'][fleet.get_owner()]
            )
        self.fleetsprites[fleet] = fleet_sprite
        self.get('units').add(fleet_sprite)

    def on_fleet_arrived(self, fleet):
        fleet_sprite = self.fleetsprites[fleet]
        self.get('units').remove(fleet_sprite)
        self.fleetsprites.pop(fleet)

    def map_from_pixel(self, x, y):
        """
        convert pixel coordinates into map space
        """
        return (x / settings.LVL_W, y / settings.LVL_H)

    def pixel_from_map(self, x, y):
        """
        convert map space into  pixel coordinates
        """
        return (x * settings.LVL_W, y * settings.LVL_H)

    def init_node_sprites(self, wipe=False):
        if wipe:
            #wipe old sprites
            #for n in self.G.nodes_iter():
            #    self.map.node[n]['sprite'] = None
            self.remove("nodes")

        #make node sprites
        nodes = BatchNode()

        raw_positions = self.map.get_positions()
        rotate_effect = Repeat(RotateBy(-360, 2))
        for n in raw_positions:
            #get node position
            x, y = raw_positions[n]
            pos = (x * settings.LVL_W, y * settings.LVL_H)

            #get type of node
            type = self.map.get_type(n)

            #make sprite
            node_spr = Sprite(
                image=settings.IMAGE_DATA[type],
                position=pos,
            )
            type != "factory" or node_spr.do(rotate_effect)
            self.nodesprites[n] = node_spr
            nodes.add(node_spr)

        #add nodes to map_layer
        self.add(nodes, z=1, name="nodes")

        self.update_node_sprites()

    def init_link_sprites(self, wipe=False):
        if wipe:
            #wipe old sprites
            for start, end in self.map.edges_iter():
                self.linksprites[start][end] = None
            self.remove("links")

        #make links
        links = BatchNode()
        for start, end in self.map.edges_iter():
            #get start and end nodes
            start_node = self.nodesprites[start]
            end_node = self.nodesprites[end]

            #get centre of line
            pos = ((start_node.x + end_node.x) / 2,
                  (start_node.y + end_node.y) / 2)

            #get type of link
            type = self.map.get_type(start, end)

            link_spr = Sprite(
                image=settings.IMAGE_DATA[type],
                position=pos,
                rotation=-degrees(atan2(
                    (end_node.y - start_node.y),
                    (end_node.x - start_node.x),
                ))
            )

            #add link to lists
            self.linksprites[start][end] = link_spr
            links.add(link_spr)

        #add sprites to map_layer
        self.add(links, z=0, name="links")

        self.update_link_sprites()

    def update_link_sprites(self):
        for n1, n2 in self.map.edges_iter():
            highlighted = self.map.get_highlight(n1, n2)
            type = self.map.get_type(n1, n2)

            self.linksprites[n1][n2].color = self.colour_data[type][highlighted]
            self.linksprites[n1][n2].image = settings.IMAGE_DATA[type]

    def update_node_sprites(self):
        for n in self.map.nodes_iter():
            owner = self.map.get_owner(n)
            type = self.map.get_type(n)

            self.nodesprites[n].color = self.colour_data[type][owner]
            if owner is neutral_player():
                self.nodesprites[n].scale = 1.0
            elif self.nodesprites[n].scale is 1.0:
                self.nodesprites[n].do(ScaleTo(2.0, 0.5))

    def update_unit_sprites(self):
        pass
