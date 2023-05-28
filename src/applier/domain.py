from configparser import ConfigParser
import os
import subprocess
from rich.console import Console
from pydantic import BaseModel

from models import MaterialColors
from util import Config, Scheme, Theme, set_wallpaper
from util import reload_apps


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

    def set_wallpaper_path(self, path: str) -> None:
        self._generation_options.wallpaper_path = path

    def set_lightmode_enabled(self, enabled: bool) -> None:
        self._generation_options.lightmode_enabled = enabled

    def set_scheme_color_based_on_key(self, key: str, color: str) -> None:
        if self._generation_options.scheme is None:
            raise ValueError("Scheme is None")
        self._generation_options.scheme[key] = color

    def reset_scheme(self) -> None:
        self._generation_options.scheme = self._get_scheme()

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

        Config.generate(
            scheme=self._generation_options.scheme or self._get_scheme(),
            config=self._conf,
            wallpaper=self._generation_options.wallpaper_path,
            lightmode_enabled=self._generation_options.lightmode_enabled,
            parent_dir=self._generation_options.parent_dir,
        )
        self._reload_apps()

    def _reload_apps(self) -> None:
        if self._generation_options.wallpaper_path is None:
            raise ValueError("Wallpaper path is None")
        reload_apps(
            self._generation_options.lightmode_enabled, scheme=self._get_scheme()
        )
        set_wallpaper(self._generation_options.wallpaper_path)
        os.system("notify-send 'Theme applied! Enjoy!'")

    def _get_scheme(self) -> MaterialColors:
        if self._generation_options.wallpaper_path is None:
            raise ValueError("Wallpaper path is None")
        scheme = Scheme(
            Theme.get(self._generation_options.wallpaper_path),
            self._generation_options.lightmode_enabled,
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
