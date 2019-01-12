# window.py
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

from gi.repository import Gtk, GLib
from .gi_composites import GtkTemplate

@GtkTemplate(ui='/com/aymanbagabas/Glyrics/window.ui')
class GlyricsWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'GlyricsWindow'

    label = GtkTemplate.Child()
    header_bar = GtkTemplate.Child()
    players_group = GtkTemplate.Child()
    players_box = GtkTemplate.Child()
    players_popover = GtkTemplate.Child()
    players_button = GtkTemplate.Child()
    lyrics_window = GtkTemplate.Child()
    lyrics = GtkTemplate.Child()
    spinner = GtkTemplate.Child()

    spinner_timeout_id = None
 
    group = Gtk.RadioButton.new(None)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
        self.players_box.show_all()


    def set_lyrics(self, lyrics):
        self.lyrics.set_text(lyrics)

        if self.spinner_timeout_id:
            self.remove_spinner()
        if self.spinner in self:
            self.remove(self.spinner)
        elif self.label in self:
            self.remove(self.label)
        else:
            return

        self.add(self.lyrics_window)
        pos = self.lyrics_window.get_vadjustment()
        pos.set_value(0)
        self.lyrics_window.set_vadjustment(pos)


    def stop_spinner(self):
        self.spinner.stop()


    def pre_metadata(self):
        if self.label in self:
            self.remove(self.label)
        elif self.lyrics_window in self:
            self.remove(self.lyrics_window)
        else:
            return

        self.add(self.spinner)
        self.spinner.start()


    def set_title(self, title=None, subtitle=None):
        if title:
            self.header_bar.props.title = title
        else:
            self.header_bar.props.title = "Glyrics"
        if subtitle:
            self.header_bar.props.subtitle = subtitle
        else:
            self.header_bar.props.subtitle = None


    def clear_window(self, label=None):
        if self.lyrics_window in self:
            self.remove(self.lyrics_window)
            self.add(self.label)
        elif self.spinner in self:
            self.remove(self.spinner)
            self.add(self.label)
        if label:
            self.label.props.label = label
        else:
            if self.spinner_timeout_id:
                GLib.source_remove(self.spinner_timeout_id)
                self.spinner_timeout_id = None
            self.label.props.label = ""


    def on_radio_toggled(self, radio, player):
        app = self.props.application

        if radio.get_active():
            app.set_player(player)


    def update_players_menu(self):
        app = self.props.application

        # In case of no player available
        if len(app.playermanager.props.players) == 0:
            self.players_button.set_sensitive(False)
            self.set_title()
            return
        else:
            self.players_button.set_sensitive(True)

        for child in self.players_box:
            self.players_box.remove(child)

        for player in app.playermanager.props.players:
            radio = Gtk.RadioButton.new_with_label_from_widget(self.group, player.props.player_name)

            if player == app.player:
                radio.set_active(True)

            self.players_box.add(radio)
            radio.connect("toggled", self.on_radio_toggled, player)

        self.players_box.show_all()
