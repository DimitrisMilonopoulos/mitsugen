import logging
import os
import re
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path

from rich.logging import RichHandler
from transformers import ColorTransformer

from src.material_color_utilities_python import Image, themeFromImage
from src.models import MaterialColors


def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument("wallpaper", help="the wallpaper that will be used", type=str)

    parser.add_argument(
        "-l",
        "--lightmode",
        help="specify whether to use light mode",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--ui",
        help="use ui",
        action="store_true",
    )
    args: Namespace = parser.parse_args()
    return args


def setup_logging():
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    log = logging.getLogger("rich")
    return log


log = setup_logging()


def reload_apps(lightmode_enabled: bool, scheme: MaterialColors):
    adw_theme = "adw-gtk3-dark" if not lightmode_enabled else "adw-gtk3"
    postfix = "dark" if not lightmode_enabled else "light"

    log.info(f"Restarting GTK {postfix}")
    os.system(f"gsettings set org.gnome.desktop.interface gtk-theme {adw_theme}")
    os.system(f"gsettings set org.gnome.desktop.interface gtk-theme custom-{postfix}")

    log.info("Restarting Gnome Shell theme")
    os.system(
        f"gsettings set org.gnome.shell.extensions.user-theme name 'Marble-green-{postfix}'"
    )
    os.system(
        f"gsettings set org.gnome.shell.extensions.user-theme name 'Marble-blue-{postfix}'"
    )


def set_wallpaper(path: str):
    log.info("Setting wallpaper with swaybg")
    os.system("gsettings set org.gnome.desktop.background picture-options 'scaled'")
    os.system(f"gsettings set org.gnome.desktop.background picture-uri {path}")


class Config:
    @staticmethod
    def read(filename: str):
        config = ConfigParser()
        try:
            print(config.read(filename))
        except OSError as err:
            logging.exception(f"Could not open {err.filename}")
        else:
            logging.info(f"Loaded {len(config.sections())} templates from config file")
            return config

    @classmethod
    def generate(
        cls,
        scheme: MaterialColors,
        config: ConfigParser,
        wallpaper: str,
        lightmode_enabled: bool,
        parent_dir: str,
    ) -> dict | None:
        """Generate a config file from a template

        Args:
            scheme (MaterialColors): The color scheme to use
            config (ConfigParser): The config file to use
            wallpaper (str): The path to the wallpaper

        Returns:
            dict | None: The generated config file. None if error
        """
        for item in config.sections():
            num = 0
            template_name = config[item].name
            template_path_str = config[item]["template_path"]
            if template_path_str.startswith("."):
                template_path_str = f"{parent_dir}/{template_path_str[1:]}"
            template_path = Path(template_path_str).expanduser()
            # if its a relative path use parent dir as base.
            output_path = Path(config[item]["output_path"]).expanduser()

            if lightmode_enabled and cls._is_dark_theme(template_name):
                continue

            if not lightmode_enabled and not cls._is_dark_theme(template_name):
                continue

            try:
                with open(template_path, "r") as input:  # Template file
                    input_data = input.read()
            except OSError as err:
                logging.exception(f"Could not open {err.filename}")
                num += 1
                return

            output_data = input_data

            for key, value in scheme.items():
                pattern = f"@{{{key}}}"
                pattern_hex = f"@{{{key}.hex}}"
                pattern_rgb = f"@{{{key}.rgb}}"
                pattern_hue = f"@{{{key}.hue}}"
                pattern_sat = f"@{{{key}.sat}}"
                pattern_light = f"@{{{key}.light}}"
                pattern_wallpaper = "@{wallpaper}"

                hex_stripped = value[1:]  # type: ignore
                rgb_value = f"rgb{ColorTransformer.hex_to_rgb(hex_stripped)}"
                hue, light, saturation = ColorTransformer.hex_to_hls(hex_stripped)
                wallpaper_value = os.path.abspath(wallpaper)

                output_data = re.sub(pattern, hex_stripped, output_data)
                output_data = re.sub(pattern_hex, value, output_data)
                output_data = re.sub(pattern_rgb, rgb_value, output_data)
                output_data = re.sub(pattern_wallpaper, wallpaper_value, output_data)
                output_data = re.sub(pattern_hue, f"{hue}", output_data)
                output_data = re.sub(pattern_sat, f"{saturation}", output_data)
                output_data = re.sub(pattern_light, f"{light}", output_data)

                num += 1

            try:
                with open(output_path, "w") as output:
                    output.write(output_data)
            except OSError as err:
                logging.exception(
                    f"Could not write {template_name} template to {err.filename}"
                )
            else:
                log.info(f"Exported {template_name} template to {output_path}")

    @staticmethod
    def _is_dark_theme(name: str) -> bool:
        upper_name = name.upper()
        return upper_name.endswith("DARK")


class Theme:
    @classmethod
    def get(cls, image: str):
        log.info(f"Using image {image}")

        img = cls._get_image_from_file(image)

        return themeFromImage(img)

    @classmethod
    def _get_image_from_file(cls, image: str):
        """Get image from file and resample it"""
        img = Image.open(image)
        basewidth = 64
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        return img.resize((basewidth, hsize), Image.Resampling.LANCZOS)


class Scheme:
    def __init__(self, theme: dict, lightmode: bool):
        if lightmode:
            log.info("Using light scheme")
            self.scheme_dict = theme["schemes"]["light"].props
        else:
            log.info("Using dark scheme")
            self.scheme_dict = theme["schemes"]["dark"].props

    def get(self) -> dict:
        return self.scheme_dict

    def to_rgb(self) -> dict:
        scheme = self.scheme_dict

        for key, value in scheme.items():
            scheme[key] = ColorTransformer.dec_to_rgb(value)
        return scheme

    def to_hex(self) -> MaterialColors:
        scheme = self.scheme_dict

        # Need to convert to rgb first
        self.to_rgb()

        for key, value in scheme.items():
            scheme[key] = "#{value}".format(value=ColorTransformer.rgb_to_hex(value))
        return scheme
