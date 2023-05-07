import colorsys
from typing import Tuple


class ColorTransformer:
    @staticmethod
    def rgb_to_hex(rgb: int) -> str:
        return "%02x%02x%02x" % rgb

    @staticmethod
    def hex_to_rgb(hexa: str):
        return tuple(int(hexa[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def dec_to_rgb(decimal_value: int) -> Tuple[int, int, int]:
        red = (decimal_value >> 16) & 255
        green = (decimal_value >> 8) & 255
        blue = decimal_value & 255

        return red, green, blue

    @classmethod
    def hex_to_hls(cls, hexa: str) -> Tuple[int, int, int]:
        hue, light, saturation = colorsys.rgb_to_hls(*cls.hex_to_rgb(hexa))
        return int(hue * 360), int(light), int(saturation)
