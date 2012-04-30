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

import pyglet

import cocos
from cocos.actions import *
from cocos.scenes import *
from cocos.director import director

import settings
import levels
import layers

from multiplayer import current_player


class IntroScene(cocos.scene.Scene):
    def __init__(self):
        super(IntroScene, self).__init__()

        # create layers
        colour_data = settings.COLOUR_DATA['intro']
        bg_layer = cocos.layer.ColorLayer(*colour_data['background'])
        text_layer = cocos.layer.Layer()

        # create label
        name_label = cocos.text.Label(
            "Presenting CWD's",
            font_name='Courier New',
            font_size=40,
            anchor_x='center',
            anchor_y='center',
            color=colour_data['text'],
            position=(settings.SCR_MID_X, settings.SCR_MID_Y),
        )
        name_label.opacity = 0

        #add label to layer
        text_layer.add(name_label)

        #add layers to scene
        self.add(bg_layer)
        self.add(text_layer)

        #text layer actions
        name_label.do(
            Accelerate(FadeIn(4), rate=2) +
            Delay(1) +
            FadeOut(2) +
            CallFunc(self.on_end_intro)  # called when animations are finished
        )

    def on_end_intro(self):
        director.replace(FadeTransition(MenuScene(), duration=1))


class MenuScene(cocos.scene.Scene):
    def __init__(self):
        super(MenuScene, self).__init__()
        colour_data = settings.COLOUR_DATA['menu']
        self.bg_layer = cocos.layer.ColorLayer(*colour_data['background'])
        self.add(self.bg_layer)
        self.add(MainMenu())


class MainMenu(cocos.menu.Menu):
    def __init__(self, title='LINKREASE'):
        super(MainMenu, self).__init__(title=title)
        self.font_title['font_name'] = 'Courier New'
        self.font_title['font_size'] = 60
        self.font_item['font_name'] = 'Courier New'
        self.font_item['font_size'] = 30
        self.font_item_selected['font_name'] = 'Courier New'
        self.font_item_selected['font_size'] = 30

        items = [
            cocos.menu.MenuItem('New Game', self.on_new_game),
            cocos.menu.MenuItem('Options', self.on_options),
            cocos.menu.MenuItem('Quit', pyglet.app.exit),
        ]

        self.create_menu(items, cocos.menu.zoom_in(), cocos.menu.zoom_out())

    def on_new_game(self):
        director.replace(FadeTransition(GameScene(), duration=1))

    def on_options(self):
        pass

    def on_quit(self):
        pass


class GameLayerController(cocos.layer.scrolling.ScrollingManager):
    is_event_handler = True

    def __init__(self, map):
        super(GameLayerController, self).__init__()
        self.scale = settings.ZOOM_MIN

        #store model
        self.map = map

        #create view
        self.map_view = layers.MapView(map)
        self.add(self.map_view)

        #add callback to model
        self.map.add_listener(self.on_model_change)
        self.map.add_fleet_listener(self.on_fleet_launched)

    def on_mouse_press(self, x, y, buttons, modifiers):
        px, py = self.map_view.map_from_pixel(*self.pixel_from_screen(x, y))
        n = self.map.closest_node_to(px, py)
        player = current_player()
        if self.map.get_owner(n) is player:
            self.map.select_node(player, n)

    def on_mouse_release(self, x, y, buttons, modifiers):
        player = current_player()
        source = self.map.selected_node(player)
        target = self.map.targeted_node(player)
        if source is not None and source is not target:
            player = current_player()
            self.map.move_units_to_target(player)
        self.map.select_node(player, None)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        player = current_player()
        if self.map.selected_node(player) is not None:
            px, py = self.map_view.map_from_pixel(*self.pixel_from_screen(x, y))
            n = self.map.closest_node_to(px, py)
            self.map.target_node(player, n)

    def on_mouse_scroll(self, x, y, dx, dy):
        """
        Zoom on mouse scroll.

        x, y: position of mouse on screen
        dx: horizontal scroll value
        dy: vertical scroll value
        """
        #calculate next scale value
        scale = self.scale + (settings.ZOOM_STEP * dy)

        #restrict to bounds
        if scale < settings.ZOOM_MIN:
            scale = settings.ZOOM_MIN
        elif scale > settings.ZOOM_MAX:
            scale = settings.ZOOM_MAX

        if scale != self.scale:
            #set scale
            self.scale = scale
            px, py = self.pixel_from_screen(x, y)
            #set centre point
            self.set_focus(px, py)

    def on_model_change(self):
        self.map_view.on_model_change()

    def on_fleet_launched(self, fleet):
        fleet.add_arrival_listener(self.on_fleet_arrived)
        self.schedule(fleet.step_time)

    def on_fleet_arrived(self, fleet):
        self.map.deploy(fleet.get_target(), fleet.get_num_units(), fleet.get_owner())
        self.unschedule(fleet.step_time)


class GameScene(cocos.scene.Scene):
    def __init__(self, graph=None, player_start=[0]):
        super(GameScene, self).__init__()

        if graph:
            self.G = graph
        else:
            self.G = levels.generate_random_level()

        #add scrolling manager
        self.game_layer_controller = GameLayerController(self.G)
        self.add(self.game_layer_controller)

        #add base_layer
        self.base_layer = cocos.layer.ColorLayer(*settings.COLOUR_DATA['game']['background'])
        self.add(self.base_layer)
