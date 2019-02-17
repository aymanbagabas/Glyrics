# main.py
#
# Copyright 2019 Ayman Bagabas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Playerctl', '2.0')

from gi.repository import Gtk, Gio, GLib, GObject

from .window import GlyricsWindow

from gi.repository import Playerctl

from plyr import Query, Database

from threading import Thread

db_dir = os.path.join(os.environ["HOME"], ".local/share/glyrics")
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
db = Database(db_dir)
queries = []

class GlyricsQuery(Query):
    def __init__(self, **kwargs):
        self.database = db
        self.db_autoread = True
        self.db_autowrite = True
        self.force_utf8 = True
        self.parallel = 20
        self.providers = 'all'
        # TODO: respect system proxy settings
        self.useragent = "glyrics/" + str(Application.version) + "+https://www.github.com/aymanbagabas/glyrics"

        queries.append(self)


class Application(Gtk.Application):

    version = GObject.Property(type=str, flags=GObject.ParamFlags.CONSTRUCT_ONLY|GObject.ParamFlags.READWRITE)

    def __init__(self, **kwargs):
        super().__init__(application_id='com.aymanbagabas.Glyrics',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)

        self.playermanager = Playerctl.PlayerManager()
        self.player = None

        self.add_main_option("version", ord("v"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Show Glyrics version", None)


    def set_player(self, player):
        win = self.props.active_window

        # Disconnect signal from previous player
        if self.player:
            self.player.disconnect(self.player_id)
        self.player_id = player.connect("metadata", self.on_metadata)

        self.playermanager.move_player_to_top(player)
        self.player = player
        self.on_metadata(player, player.props.metadata)



    def query_commit(self, query, player):
        win = self.props.active_window
        items = query.commit()

        win.stop_spinner()

        if len(items) > 0 and self.player == player \
            and self.player.get_title() == query.title:
                win.set_lyrics(items[0].data.decode())
                # FIXME: Some players like Spotify emits a metadata change signal
                # on events like 'add to queue' and others which cause multiple
                # calls to get contents. Currently, cancelling all other queries
                # is used which is very dirty.
                self.cancel_all_queries()
        elif len(items) == 0 and self.player == player \
            and self.player.get_title() == query.title \
            and len(db.lookup(query)) == 0:
                # No data found
                win.clear_window("No lyrics found")
        else:
                win.clear_window("No lyrics found")

        queries.remove(query)


    def on_metadata(self, player, metadata):
        win = self.props.active_window
        query = GlyricsQuery(get_type="lyrics")
        subtitle = None
        title = player.get_title()
        artist = player.get_artist()
        album = player.get_album()

        win.pre_metadata()

        if title:
            query.title = title
            query.normalize = ("title")
            if artist and album:
                subtitle = "by {} on {}".format(artist, album)
                query.normalize += ("artist", "album")
                query.artist = artist
                query.album = album
            elif artist and not album:
                subtitle = "by {}".format(artist)
                query.normalize += ("artist")
                query.artist = artist
            elif not artist and album:
                subtitle = "on {}".format(artist, album)
                query.normalize += ("album")
                query.album = album

            t = Thread(target=self.query_commit, args=(query, self.player,))
            t.daemon = True
            t.start()
        else:
            win.clear_window("No song info provided")

        win.set_title(title=title, subtitle=subtitle)

    def init_player(self, name):
        win = self.props.active_window
        player = Playerctl.Player.new_from_name(name)

        self.playermanager.manage_player(player)


    def on_name_appeared(self, manager, name):
        player = Playerctl.Player.new_from_name(name)
        self.playermanager.manage_player(player)


    def on_player_appeared(self, manager, player):
        win = self.props.active_window

        if len(manager.props.players) == 1:
            self.set_player(player)

        win.update_players_menu()


    def on_player_vanished(self, manager, player):
        win = self.props.active_window

        if len(manager.props.players) >= 1 \
            and self.player == player:
            self.set_player(manager.props.players[0])

        if len(self.playermanager.props.players) == 0:
            win.clear_window("No player available")

        win.update_players_menu()


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

        if len(self.playermanager.props.players) == 0:
            win.clear_window("No player available")

        win.update_players_menu()


    def cancel_all_queries(self):
        for q in queries:
            Thread(target=q.cancel).start()


    def on_quit(self, action, param):
        self.cancel_all_queries()
        self.quit()


    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if "version" in options:
            print("Glyrics {}".format(self.version))
            return 0

        self.activate()
        return 0

