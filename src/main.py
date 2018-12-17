# main.py
#
# Copyright 2018 Ayman Bagabas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Playerctl', '2.0')

from gi.repository import Gtk, Gio

from .window import GlyricsWindow

from gi.repository import Playerctl

from glyrics import version as VERSION

from plyr import Query, Database

from time import sleep
from threading import Thread

db = Database("/tmp")

class GlyricsQuery(Query):
    def __init__(self, **kwargs):
        self.database = db
        self.db_autoread = True
        self.useragent = "glyrics/" + VERSION + "(Baby Vanilla) +https://www.github.com/aymanbagabas/glyrics"
        self.force_utf8 = True

class Application(Gtk.Application):
    def __init__(self, version):
        super().__init__(application_id='org.gnome.Glyrics',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.playermanager = Playerctl.PlayerManager()
        self.player = None
        self.metadata = None
        self.queries = []
        
        
    def update_player(self, player):
        win = self.props.active_window
        
        # Disconnect signal from previous player
        if self.player:
            self.player.disconnect(self.id)
            
        self.player = player
        self.id = player.connect("metadata", self.on_metadata, self.playermanager)
        self.metadata_change(player)
        self.playermanager.move_player_to_top(player)
        
        
    def set_player(self, player_name):
        player = Playerctl.Player.new(player_name)
        
        if player != self.player:
            self.update_player(player)
            
            
    def query_callback(self, cache, query):
        win = self.props.active_window
        if query.get_type == "lyrics":
            win.update_lyrics(cache.data.decode())
            
        return 'pre_stop'
    
        
    def metadata_query(self, **args):
        qry = GlyricsQuery(**args)
        self.queries.append(qry)
        Thread(target=qry.commit).start()
        
        
    def metadata_change(self, player):
        print("on metadata, {}".format(player.props.player_name))
        win = self.props.active_window
        
        win.pre_metadata()
        
        subtitle = None
        title = player.get_title()
        artist = player.get_artist()
        album = player.get_album()
        
        if title:
            if artist and album:
                subtitle = "by {} on {}".format(artist, album)
            elif artist and not album:
                subtitle = "by {}".format(artist)
            elif not artist and album:
                subtitle = "on {}".format(artist, album)
                
            self.metadata_query(title=title, artist=artist, album=album, get_type="lyrics", callback=self.query_callback)

        win.set_title(title=title, subtitle=subtitle)
        
    
    def on_metadata(self, player, metadata, manager):
        if self.metadata == metadata:
            return
        self.metadata = metadata
            
        self.metadata_change(player)
        
    def init_player(self, name):
        win = self.props.active_window
        
        player = Playerctl.Player.new_from_name(name)
        
        self.update_player(player)
        self.playermanager.manage_player(player)
        
    
    def on_name_appeared(self, manager, name):
        player = Playerctl.Player.new_from_name(name)
        self.playermanager.manage_player(player)
        
        
    def on_player_appeared(self, manager, player):
        win = self.props.active_window
        
        if len(manager.props.players) == 1:
            self.update_player(player)
        
        win.update_players_menu(self)
        
    
    def on_player_vanished(self, manager, player):
        win = self.props.active_window
        
        if len(manager.props.players) >= 1:
            self.update_player(manager.props.players[-1])
        
        win.update_players_menu(self)
        
        
    def do_startup(self):
        Gtk.Application.do_startup(self)
        
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = GlyricsWindow(application=self)
        win.present()
        
        self.playermanager.connect("name-appeared", self.on_name_appeared)
        self.playermanager.connect("player-appeared", self.on_player_appeared)
        self.playermanager.connect("player-vanished", self.on_player_vanished)
        
        for name in self.playermanager.props.player_names:
            self.init_player(name)
            
        win.update_players_menu(self)
        
        
    def on_quit(self, action, param):
        for q in self.queries:
            Thread(target=q.cancel).start()
        
        self.quit()


def main(version):
    app = Application(version)
    return app.run(sys.argv)
