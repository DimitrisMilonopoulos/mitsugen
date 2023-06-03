from typing import Callable

from gi.repository import Adw, Gdk, Gtk


class ColorPopover(Gtk.Popover):
    def __init__(self, colors, on_color_selected: Callable):
        super().__init__()
        self._on_color_selected = on_color_selected

        # Create a box to hold the color previews
        listbox = Gtk.ListBox(
            vexpand=True,
            hexpand=True,
            show_separators=True,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        self.set_child(listbox)
        self.set_vexpand(True)

        # Create a button for each color
        for i, color in enumerate(colors):
            row = Adw.ActionRow()
            title = f"Color {i+1}"
            row.set_title(title)
            row.set_icon_name("color-picker")
            row.color = color
            button = Gtk.ColorButton()
            button.set_title(title)

            gdk_color = Gdk.RGBA()
            gdk_color.parse(color)
            button.set_rgba(gdk_color)
            button.props.halign = Gtk.Align.END
            button.set_valign(Gtk.Align.CENTER)

            row.add_suffix(button)

            listbox.append(row)

        listbox.connect("row_selected", self.on_color_selected)

    def on_color_selected(self, listbox, row, *args, **kwargs):
        row = listbox.get_selected_row()
        self._on_color_selected(row.color)
