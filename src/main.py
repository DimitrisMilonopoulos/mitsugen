import os

from applier.domain import ApplierDomain, GenerationOptions
from ui.app import GtkApp
from util import Config, parse_arguments


def main():  # sourcery skip: raise-specific-error
    parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    arguments = parse_arguments()
    lightmode_enabled: bool = arguments.lightmode

    conf = Config.read(f"{parent_dir}/example/config.ini")
    if not conf:
        raise Exception("Could not find config file")

    applier_domain = ApplierDomain(
        conf=conf,
        generation_options=GenerationOptions(
            parent_dir=parent_dir,
            lightmode_enabled=lightmode_enabled,
            wallpaper_path=arguments.wallpaper
            or ApplierDomain.get_current_system_wallpaper_path(),
        ),
    )
    if arguments.ui:
        app = GtkApp(
            application_id="com.picker.Mitsugen", applier_domain=applier_domain
        )
        app.run(None)
        import time

        time.sleep(2000)
    else:
        applier_domain.apply_theme()


if __name__ == "__main__":
    main()
