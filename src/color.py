class Color:
    PRIMARY = (217, 4, 41)
    SECONDARY = (239, 35, 60)
    TERTIARY = (43, 45, 66)

    @staticmethod
    def rgb_to_bgr(color):
        return color[::-1]
