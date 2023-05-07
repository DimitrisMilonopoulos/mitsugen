import os
import pprint
from src.util import Theme, Scheme, Config, set_wallpaper, reload_apps, parse_arguments


def get_scheme(args):
    scheme = Scheme(Theme.get(args.wallpaper), args.lightmode)
    return scheme.to_hex()


def main():
    parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    args = parse_arguments()
    lightmode_enabled: bool = args.lightmode
    scheme = get_scheme(args)
    conf = Config.read(f"{parent_dir}/example/config.ini")
    if not conf:
        raise Exception("Could not find config file")

    pprint.pprint("Scheme: ")
    pprint.pprint(scheme, sort_dicts=False)

    Config.generate(scheme, conf, args.wallpaper, lightmode_enabled, parent_dir)
    reload_apps(lightmode_enabled, scheme=scheme)
    set_wallpaper(args.wallpaper)


if __name__ == "__main__":
    main()
