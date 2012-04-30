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

import networkx as nx

import models
import settings


def generate_random_level(nodes=180, radius=0.1, repel=0.05, players=2):
    """
    Generates random graph.
    Occupies one planet per player.

    pre: nodes > 0
    pre: players > nodes
    pre: players > 0
    """
    #generate level
    G = None
    while G is None or not nx.is_connected(G):
        G = nx.random_geometric_graph(
            n=nodes,
            radius=radius,
            repel=repel,
        )

    #setup map
    map = models.Map(G)
    for n in xrange(nodes):
        p = n + 1 if n < players else 0
        map.set_owner(n, settings.PLAYER[p])
        if p is not 0:
            map.set_factory(n, True)
            map.set_garrison(n, 10)
    return map
