import os
from util import Theme, Scheme, Config, set_wallpaper, reload_apps, parse_arguments


def get_scheme(args):
    scheme = Scheme(Theme.get(args.wallpaper), args.lightmode)
    return scheme.to_hex()


def main():
    home = os.environ["HOME"]
    args = parse_arguments()
    lightmode_enabled: bool = args.lightmode
    scheme = get_scheme(args)
    conf = Config.read(f"{home}/Desktop/DownloadedPackages/Matugen/example/config.ini")
    import pprint

    pprint.pprint("Scheme: ")
    pprint.pprint(scheme, sort_dicts=False)

    Config.generate(scheme, conf, args.wallpaper, lightmode_enabled)
    reload_apps(lightmode_enabled, scheme=scheme)
    set_wallpaper(args.wallpaper)


if __name__ == "__main__":
    main()
