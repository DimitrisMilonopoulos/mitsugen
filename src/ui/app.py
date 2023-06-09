import re

import gi

from applier.domain import ApplierDomain
from ui.widgets.colors_popover import ColorPopover

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk


def hex_to_gdk_rgba(hex_color: str):
    color = Gdk.RGBA()
    color.parse(hex_color)
    return color


def color_title(color_name: str):
    return re.sub(r"\B([A-Z])", r" \1", color_name).title()


class MainWindow(Gtk.ApplicationWindow):
    def __init__(
        self,
        applier_domain: ApplierDomain,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._applier_domain = applier_domain
        self.box1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            margin_bottom=5,
            margin_top=5,
            margin_end=5,
            margin_start=5,
            spacing=5,
        )
        self.box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_bottom=5)
        self.box3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_bottom=5)

        scrolled_window = self._create_scrolled_window()
        scrolled_window.set_child(self.box1)
        self.set_child(scrolled_window)
        # self.set_child(self.box1)
        self.box1.append(self.box2)
        self.box1.append(self.box3)
        self.set_default_size(600, 600)
        self.set_title("Mitsugen")

        self.box2.set_margin_start(10)
        self.box2.set_margin_end(10)
        # add outline to box2
        self.box2.append(self._add_wallpaper_image())
        file_picker_button = Gtk.Button(label="Select Wallpaper")
        file_picker_button.connect("clicked", self.on_file_picker_button_clicked)
        self._color_buttons: dict[str, Gtk.ColorButton] = {}

        options_listbox = Gtk.ListBox(
            vexpand=True,
            hexpand=True,
            show_separators=True,
            selection_mode=Gtk.SelectionMode.NONE,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        options_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        options_listbox.set_css_classes(["boxed-list"])
        options_listbox.append(self._add_light_theme_switch())

        options_preference_group = Adw.PreferencesGroup(
            title="Apply Options", margin_top=20
        )
        options_preference_group.set_description("Set options for applying the theme")
        options_preference_group.add(options_listbox)
        self.box2.append(options_preference_group)

        listbox = Gtk.ListBox(
            vexpand=True,
            hexpand=True,
            show_separators=True,
            selection_mode=Gtk.SelectionMode.NONE,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.set_css_classes(["boxed-list"])

        preference_group = Adw.PreferencesGroup(title="Color Scheme", margin_top=20)
        preference_group.set_description("Preview or adjust the color scheme")
        preference_group.add(self._generate_color_list())
        preference_group.add(listbox)
        # self.box2.append(self._generate_color_list())

        self._listbox = listbox
        self._color_key_items = {}
        for color_key in self._applier_domain.scheme.keys():
            self._listbox.append(self._add_color_pick_button(color_key))
        self.box2.append(preference_group)
        headerbar = Gtk.HeaderBar()
        headerbar.pack_end(self.create_button_apply_colorscheme())
        headerbar.pack_start(file_picker_button)

        self.set_titlebar(headerbar)

    def _set_colors_popover(self) -> None:
        def on_menu_item_activated(color):
            self._applier_domain.reset_scheme(color)
            self.reset_buttons()

        self._colors_popover = ColorPopover(
            self._applier_domain.top_colors, on_menu_item_activated
        )

    def _generate_color_list(self) -> Gtk.DropDown:
        self._set_colors_popover()
        # Create a button to enable the popover
        button = Gtk.Button(label="Select Different Accent")

        def show_popover(*args, **kwargs):
            self._colors_popover.set_position(Gtk.PositionType.BOTTOM)
            self._colors_popover.set_autohide(True)
            self._colors_popover.set_parent(button)
            self._colors_popover.set_focus_on_click(False)
            self._colors_popover.show()

        button.connect("clicked", show_popover, button)
        # set button max width
        button.set_hexpand(False)
        return button

    def _add_wallpaper_image(self):
        self.wallpaper_label = Gtk.Label(
            label=self._applier_domain._generation_options.wallpaper_path
            or "No wallpaper selected"
        )
        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        image = Gtk.Image()
        image.set_from_file(self._applier_domain._generation_options.wallpaper_path)
        image.set_pixel_size(100)
        self.wallpaper_image = image
        switch_box.append(image)
        switch_box.append(self.wallpaper_label)
        switch_box.set_spacing(5)
        return switch_box

    def create_button_apply_colorscheme(self):
        button = Gtk.Button(label="Apply")
        button.props.valign = Gtk.Align.CENTER
        button.props.halign = Gtk.Align.CENTER
        button.connect("clicked", self.apply_theme)
        return button

    def file_pick_callback(self, dialog, result, *args, **kwargs):
        try:
            file = dialog.open_finish(result)
            path = file.get_path() if file else None
            if path:
                self._applier_domain.set_wallpaper_path(path)
                self._applier_domain.reset_scheme()
                self.reset_wallpaper()
                self.reset_buttons()
                self._set_colors_popover()

        except GLib.Error as error:
            print(f"Error opening file: {error.message}")

    def reset_wallpaper(self):
        self.wallpaper_label.set_text(
            self._applier_domain._generation_options.wallpaper_path
            or "No wallpaper selected"
        )
        self.wallpaper_image.set_from_file(
            self._applier_domain._generation_options.wallpaper_path
        )

    def on_file_picker_button_clicked(self, button):
        folder_path = Gio.File.new_for_path(
            self._applier_domain._generation_options.wallpaper_path or "~/"
        )
        open_dialog = Gtk.FileDialog.new()
        open_dialog.set_title("Open File")

        open_dialog.open(self, None, self.file_pick_callback)

    def apply_theme(self, *args, **kwargs):
        self._applier_domain.apply_theme()

    def _create_scrolled_window(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        return scrolled_window

    def _add_color_pick_button(self, color_key: str = "primary"):
        action_row = Adw.ActionRow()
        action_row.set_title(color_title(color_key))
        action_row.set_subtitle(color_key)
        action_row.set_icon_name("color-picker")

        button = Gtk.ColorButton()
        button.set_title(color_key)
        # set default color from hex
        button.set_rgba(hex_to_gdk_rgba(self._applier_domain.scheme[color_key]))
        button.props.halign = Gtk.Align.END

        button.connect("color-set", self.on_dialog_response)

        button.set_valign(Gtk.Align.CENTER)
        # Add button to action_row
        action_row.add_suffix(button)

        self._color_buttons[color_key] = button
        return action_row

    def switch_switched(self, switch, state: bool):
        print(f"The switch has been switched {'on' if state else 'off'}")
        self._applier_domain.set_lightmode_enabled(state)
        self._applier_domain.reset_scheme()
        self.reset_buttons()

    def reset_buttons(self):
        for color_key in self._applier_domain.scheme.keys():
            self._color_buttons[color_key].set_rgba(
                hex_to_gdk_rgba(self._applier_domain.scheme[color_key])
            )

    def _add_light_theme_switch(self):
        action_row = Adw.ActionRow()
        action_row.set_title("Light Theme")
        action_row.set_subtitle("Enable light theme configuration")

        self.light_theme_switch = Gtk.Switch()
        self.light_theme_switch.set_active(self._applier_domain.lightmode_enabled)
        self.light_theme_switch.connect("state-set", self.switch_switched)
        self.light_theme_switch.set_valign(Gtk.Align.CENTER)

        action_row.add_suffix(self.light_theme_switch)

        return action_row

    def on_dialog_response(self, widget: Gtk.ColorButton):
        color = widget.get_rgba()
        # get hex value

        hex_color = f"#{int(color.red*255):02X}{int(color.green*255):02X}{int(color.blue*255):02X}"
        color_key = widget.get_title()
        self._applier_domain.scheme[color_key] = hex_color

        print(f"Set color for {widget.get_title()} to {hex_color}")


class GtkApp(Adw.Application):
    def __init__(
        self,
        applier_domain: ApplierDomain,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._applier_domain = applier_domain
        self.connect("activate", self.on_activate)
        self.win: MainWindow = None  # type: ignore

    def on_activate(self, app):
        self.win = MainWindow(
            application=app,
            applier_domain=self._applier_domain,
        )
        self.win.present()
