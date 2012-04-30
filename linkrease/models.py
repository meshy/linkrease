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

from math import sqrt

import networkx as nx

import settings
import levels

DIRTY_FLAG_KEYS = ['nodes', 'links', 'units', 'positions']


class Map(object):

    def __init__(self, base_graph):
        self._G = base_graph or levels.generate_random_level()
        self._selected_node = dict([(p, None) for p in settings.PLAYER])
        self._targeted_node = dict([(p, None) for p in settings.PLAYER])
        self._fleet = []
        self._listeners = []
        self._fleet_listeners = []
        self._dirty_flags = dict([(f, False) for f in DIRTY_FLAG_KEYS])

        # set up nodes
        for n in self._G.nodes_iter():
            #sets 'garrison' property only if not already set
            self.get_garrison(n)
        # set up all edges
        for n1, n2 in self._G.edges_iter():
            #sets 'creased' property only if not already set
            self.get_creased(n1, n2)
            #removes highlights
            self.set_highlight(n1, n2, False)

            if settings.ADD_RANDOM_CREASES:
                if (n1 % 3) == 0 and (n2 % 3) == 0:
                    self.set_creased(n1, n2, True)

    def add_listener(self, callback):
        self._listeners.append(callback)

    def add_fleet_listener(self, callback):
        self._fleet_listeners.append(callback)

    def notify_listeners(self):
        [callback() for callback in self._listeners]

    def notify_fleet_listeners(self, fleet):
        [callback(fleet) for callback in self._fleet_listeners]

    def dirty_flag(self, flag, clear_flag=True):
        flag = self._dirty_flags[flag]
        if clear_flag:
            self._dirty_flags[flag] = False
        return flag

    def set_owner(self, n, player, no_event=False):
        self._G.node[n]['owner'] = player
        no_event or self.notify_listeners()

    def get_owner(self, n):
        return self._G.node[n]['owner']

    def get_weight(self, n1, n2):
        return self._G.edge[n1][n2]['weight']

    def set_weight(self, n1, n2, weight):
        self._G.edge[n1][n2]['weight'] = weight

    def nodes_iter(self):
        return self._G.nodes_iter()

    def edges_iter(self):
        return self._G.edges_iter()

    def get_creased(self, n1, n2):
        """
        sets 'creased' property to False if not already set
        """
        try:
            return self._G.edge[n1][n2]['creased']
        except KeyError:
            self.set_creased(n1, n2, False, no_event=True)
        return False

    def set_creased(self, n1, n2, creased, no_event=False):
        #set flag
        self._G.edge[n1][n2]['creased'] = creased

        #set weight
        positions = self.get_positions()
        dx = positions[n1][0] - positions[n2][0]
        dy = positions[n1][1] - positions[n2][1]
        ratio = settings.UNIT_SPEED['ratio'] if creased else 1.0
        weight = sqrt(dx * dx + dy * dy) * ratio
        self.set_weight(n1, n2, weight)
        no_event or self.notify_listeners()

    def get_highlight(self, n1, n2):
        """
        sets 'highlight' property to False if not already set
        """
        try:
            return self._G.edge[n1][n2]['highlight']
        except KeyError:
            self.set_highlight(n1, n2, False, no_event=True)
        return False

    def set_highlight(self, n1, n2, highlight, no_event=False):
        self._G.edge[n1][n2]['highlight'] = highlight
        no_event or self.notify_listeners()

    def get_factory(self, n):
        """
        sets 'factory' property to False if not already set
        """
        try:
            return self._G.node[n]['factory']
        except KeyError:
            self.set_factory(n, False, no_event=True)
        return False

    def set_factory(self, n, factory, no_event=False):
        self._G.node[n]['factory'] = factory
        no_event or self.notify_listeners()

    def get_garrison(self, n):
        """
        sets 'garrison' property to False if not already set
        """
        try:
            return self._G.node[n]['garrison']
        except KeyError:
            self.set_garrison(n, 0, no_event=True)
        return 0

    def set_garrison(self, n, garrison, no_event=False):
        self._G.node[n]['garrison'] = garrison
        self._dirty_flags['units'] = True
        self._dirty_flags['nodes'] = True
        no_event or self.notify_listeners()

    def deploy(self, n, units, player, no_event=False):
        owner = self.get_owner(n)
        if player is owner:
            self.set_garrison(n, self.get_garrison(n), no_event=True)
        else:
            units_left = self.get_garrison(n) - units
            if units_left < 0:
                self.set_owner(n, player, no_event=True)
                self.set_garrison(n, -units_left, no_event=True)
            else:
                self.set_garrison(n, units_left, no_event=True)
        self.notify_listeners()

    def get_positions(self):
        return self._G.pos

    def get_type(self, n1, n2=None):
        if n2 is None:
            return "factory" if self.get_factory(n1) else "node"
        else:
            return "crease" if self.get_creased(n1, n2) else "link"

    def shortest_path(self, source, target):
        return nx.shortest_path(self._G, source=source, target=target, weighted=True)

    def closest_node_to(self, x, y):
        """
        Returns the closest node to a point.

        pre: 0.0 <= x <= 1.0
        pre: 0.0 <= y <= 1.0
        pre: self.number_of_nodes > 0
        """
        #force to float
        x *= 1.0
        y *= 1.0

        #init
        dist = 2.0
        node = None

        for n, (nx, ny) in self.get_positions().items():
            dx = x - nx
            dy = y - ny
            new_dist = dx * dx + dy * dy
            if new_dist <= dist:
                dist = new_dist
                node = n
        return node

    def select_node(self, player, node, set_target=True):
        self._selected_node[player] = node
        if set_target:
            self.target_node(player, node)

    def selected_node(self, player):
        return self._selected_node[player]

    def target_node(self, player, node, force=False):
        if force or self._targeted_node[player] != node:
            self._targeted_node[player] = node
            self._dirty_flags['links'] = True
            self._dirty_flags['nodes'] = True
            self.highlight_route(player)
            self.notify_listeners()

    def targeted_node(self, player):
        return self._targeted_node[player]

    def remove_fleet(self, fleet):
        self._fleet.remove(fleet)

    def highlight_route(self, player):
        source = self._selected_node[player]
        target = self._targeted_node[player]

        #wipe all other highlighting
        for n1, n2 in self._G.edges_iter():
            self.set_highlight(n1, n2, False, no_event=True)

        #set highlight on new route
        if source is not None and source is not target:
            path = nx.shortest_path(self._G, source=source, target=target, weighted=True)
            for n in xrange(len(path) - 1):
                self.set_highlight(path[n], path[n + 1], True, no_event=True)

    def move_units_to_target(self, player, units=None):
        source = self._selected_node[player]
        target = self._targeted_node[player]
        if source is not None and source is not target:
            fleet = Fleet(1, player, self, source, target)
            self._fleet.append(fleet)
            self._dirty_flags['units'] = True
            self.notify_listeners()
            self.notify_fleet_listeners(fleet)


class Fleet(object):
    def __init__(self, units, player, map, source, target):
        self._units = units
        self._player = player
        self._map = map
        self._positions = self._map.get_positions()
        self._source = source
        self._target = target
        self._next = self. _map.shortest_path(self._source, self._target)[1]
        self._dist_from_prev = 0
        self._jump_dist = self._map.get_weight(self._source, self._next)
        self._listeners = []

    def add_arrival_listener(self, callback):
        self._listeners.append(callback)

    def _arrive(self):
        [callback(self) for callback in self._listeners]
        self._map.remove_fleet(self)

    def step_time(self, dt, *args, **kwargs):
        while dt > 0.0:
            link_type = self._map.get_type(self._source, self._next)
            dist = settings.UNIT_SPEED[link_type] * dt
            self._dist_from_prev += dist
            if self._dist_from_prev - self._jump_dist >= 0.0:  # on next node
                #move to next node
                self._source = self._next
                try:
                    self._next = self._map.shortest_path(self._source, self._target)[1]
                except IndexError:  # on last node, jump to bottom
                    break
                self._jump_dist = self._map.get_weight(self._source, self._next)

                #reduce dt
                dist -= (self._dist_from_prev - self._jump_dist)
                dt -= dist * settings.UNIT_SPEED[link_type]
                self._dist_from_prev = 0.0
            else:
                dt = 0
        if self._source == self._next:  # on last node
            self._arrive()

    def get_num_units(self):
        return self._units

    def get_target(self):
        return self._target

    def get_owner(self):
        return self._player

    def get_pos(self):
        ratio_complete = self._dist_from_prev / self._jump_dist
        positions = self._positions
        s = self._source
        n = self._next

        dx = positions[n][0] - positions[s][0]
        dy = positions[n][1] - positions[s][1]
        return ((dx * ratio_complete) + positions[s][0],
                (dy * ratio_complete) + positions[s][1])
