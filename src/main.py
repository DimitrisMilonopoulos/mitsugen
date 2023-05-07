import os

from rich.console import Console

from models import MaterialColors
from src.util import Config, Scheme, Theme, parse_arguments, reload_apps, set_wallpaper


def get_scheme(args):
    scheme = Scheme(Theme.get(args.wallpaper), args.lightmode)
    return scheme.to_hex()


def print_scheme(scheme: MaterialColors):
    console = Console()
    print("Scheme info:")
    for key, value in scheme.items():
        console.print(f"{key}: {value}", style=f"{value}")


def main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    args = parse_arguments()
    lightmode_enabled: bool = args.lightmode
    scheme = get_scheme(args)
    conf = Config.read(f"{parent_dir}/example/config.ini")
    if not conf:
        raise Exception("Could not find config file")

    print_scheme(scheme)

    Config.generate(scheme, conf, args.wallpaper, lightmode_enabled, parent_dir)
    reload_apps(lightmode_enabled, scheme=scheme)
    set_wallpaper(args.wallpaper)


if __name__ == "__main__":
    main()
