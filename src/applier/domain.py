import os
import subprocess
from configparser import ConfigParser

from pydantic import BaseModel
from rich.console import Console

from material_color_utilities_python.closest_folder_color.domain import (
    ClosestFolderColorDomain,
)
from models import MaterialColors
from util import Config, Scheme, Theme, reload_apps, set_wallpaper


class GenerationOptions(BaseModel):
    parent_dir: str
    lightmode_enabled: bool = False
    scheme: MaterialColors | None = None
    wallpaper_path: str | None = None


def print_scheme(scheme: MaterialColors):
    console = Console()
    print("Scheme info:")
    for key, value in scheme.items():
        console.print(f"{key}: {value}", style=f"{value}")


class ApplierDomain:
    def __init__(
        self, conf: ConfigParser, generation_options: GenerationOptions
    ) -> None:
        self._generation_options = generation_options
        self._conf = conf
        self._closest_folder_color_domain = ClosestFolderColorDomain()
        self._top_colors: list[str] = []

    def set_wallpaper_path(self, path: str) -> None:
        self._generation_options.wallpaper_path = path

    def set_lightmode_enabled(self, enabled: bool) -> None:
        self._generation_options.lightmode_enabled = enabled

    def set_scheme_color_based_on_key(self, key: str, color: str) -> None:
        if self._generation_options.scheme is None:
            raise ValueError("Scheme is None")
        self._generation_options.scheme[key] = color

    def reset_scheme(self, color: str | None = None) -> None:
        self._generation_options.scheme = self._get_scheme(color)

    @property
    def lightmode_enabled(self) -> bool:
        return self._generation_options.lightmode_enabled

    @property
    def scheme(self) -> MaterialColors:
        if self._generation_options.scheme is None:
            self._generation_options.scheme = self._get_scheme()
        return self._generation_options.scheme

    def apply_theme(self) -> None:
        if self._generation_options.wallpaper_path is None:
            raise ValueError("Wallpaper path is None")

        scheme = self._generation_options.scheme or self._get_scheme()
        Config.generate(
            scheme=scheme,
            config=self._conf,
            wallpaper=self._generation_options.wallpaper_path,
            lightmode_enabled=self._generation_options.lightmode_enabled,
            parent_dir=self._generation_options.parent_dir,
        )
        primary_color = scheme["primary"]
        folder_color = self._closest_folder_color_domain.get_closest_color(
            primary_color
        )

        self._set_papirus_icon_theme(folder_color)
        self._reload_apps()

    def _set_papirus_icon_theme(self, folder_color: str) -> None:
        print(f"Applying Papirus {folder_color}.")
        # Set current directory to home directory. No need for sudo then
        os.system("export PWD=$HOME")
        os.system(f"papirus-folders -C {folder_color}")

        # get a key from the config that contains SPOTIFY in it

        lightmode_enabled = self._generation_options.lightmode_enabled

        if self._has_config_key("SPOTIFY" if lightmode_enabled else "SPOTIFY-DARK"):
            print("Setting up spotify theme")
            os.system("spicetify config current_theme Matte")
            os.system("spicetify config color_scheme mitsugen")
            os.system("spicetify apply")

        if lightmode_enabled:
            os.system(
                "gsettings set org.gnome.desktop.interface icon-theme Papirus-Light"
            )
        else:
            os.system(
                "gsettings set org.gnome.desktop.interface icon-theme Papirus-Dark"
            )

    def _has_config_key(self, key: str) -> bool:
        return any(key in self._conf[section].name for section in self._conf.sections())

    def _reload_apps(self) -> None:
        if self._generation_options.wallpaper_path is None:
            raise ValueError("Wallpaper path is None")
        reload_apps(
            self._generation_options.lightmode_enabled, scheme=self._get_scheme()
        )
        set_wallpaper(self._generation_options.wallpaper_path)
        os.system("notify-send 'Theme applied! Enjoy!'")

    def _get_scheme(self, color: str | None = None) -> MaterialColors:
        if not color:
            if self._generation_options.wallpaper_path is None:
                raise ValueError("Wallpaper path is None")
            theme, top_colors = Theme.get(self._generation_options.wallpaper_path)
            self._top_colors = top_colors
        else:
            theme = Theme.get_theme_from_color(color)

        return self._get_scheme_from_theme(theme)

    @property
    def top_colors(self) -> list[str]:
        if not self._top_colors:
            self._get_scheme()
        return self._top_colors

    def _get_scheme_from_theme(self, theme: dict) -> MaterialColors:
        scheme = Scheme(
            theme=theme,
            lightmode=self._generation_options.lightmode_enabled,
        )
        colors = scheme.to_hex()
        print_scheme(colors)
        return colors

    @staticmethod
    def get_current_system_wallpaper_path() -> str:
        command = "gsettings get org.gnome.desktop.background picture-uri"
        output = subprocess.check_output(command, shell=True, text=True)

        # Remove leading/trailing whitespace and newline characters from the output
        output = output.strip()
        output = output.replace("'", "")
        # Remove file:// from the output. If exists
        output = output.replace("file://", "")
        return output
