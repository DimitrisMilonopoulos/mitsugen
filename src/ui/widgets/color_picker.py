import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Gdk

from .material import MATERIAL


def rgb_to_hex(r, g, b):
    if isinstance(r, float):
        r *= 255
        g *= 255
        b *= 255
    return "#{0:02X}{1:02X}{2:02X}".format(int(r), int(g), int(b))


def color_to_hex(color):
    return rgb_to_hex(color.red, color.green, color.blue)


def get_font_markup(fontdesc, text):
    return f'<span font_desc="{fontdesc}">{text}</span>'


class MaterialColorDialog(Gtk.ColorChooserDialog):
    """Color chooser dialog with Material design colors"""

    def __init__(self, title, parent):
        Gtk.ColorChooserDialog.__init__(self)
        self.set_title(title)
        self.set_transient_for(parent)
        self.set_modal(True)
        # build list of material colors in Gdk.RGBA format
        color_values = []
        for color_name in MATERIAL.colors:
            colors = MATERIAL.get_palette(color_name)
            for col in colors:
                color = Gdk.RGBA()
                color.parse(col)
                color_values.append(color)
        num_colors = 14
        self.add_palette(Gtk.Orientation.HORIZONTAL, num_colors, color_values)
        self.set_property("show-editor", False)

    def get_color(self):
        selected_color = self.get_rgba()
        return color_to_hex(selected_color)
