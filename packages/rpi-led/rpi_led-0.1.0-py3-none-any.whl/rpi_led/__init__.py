from os import PathLike


def set_value(path: PathLike[str] | str, value: str) -> None:
    try:
        with open(path, "w") as f:
            f.write(value)
    except PermissionError:
        raise PermissionError("The module \"rpi-led\" requires root privileges to run.")


def get_value(path: PathLike[str] | str) -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except PermissionError:
        raise PermissionError("The module \"rpi-led\" requires root privileges to run.")


class BUILT_IN_LED:
    LED_DIR = "ACT"

    @classmethod
    def set_brightness(cls, value: int) -> None:
        cls.set_trigger("none")
        set_value(f"/sys/class/leds/{cls.LED_DIR}/brightness", str(value))

    @classmethod
    def set_trigger(cls, value: str) -> None:
        set_value(f"/sys/class/leds/{cls.LED_DIR}/trigger", value)

    @classmethod
    def get_brightness(cls) -> int:
        return int(get_value(f"/sys/class/leds/{cls.LED_DIR}/brightness"))

    @classmethod
    def get_trigger(cls) -> str:
        return get_value(f"/sys/class/leds/{cls.LED_DIR}/trigger")

    @classmethod
    def toggle(cls) -> None:
        current_brightness = cls.get_brightness()
        new_brightness = int(not current_brightness)
        cls.set_brightness(new_brightness)

    @classmethod
    def on(cls):
        cls.set_brightness(1)

    @classmethod
    def off(cls):
        cls.set_brightness(0)

    @classmethod
    def blink(cls, delay: int = 500, delay_on: int = None, delay_off: int = None) -> None:
        if delay_on is None:
            delay_on = delay
        if delay_off is None:
            delay_off = delay
        cls.set_trigger("timer")
        set_value(f"/sys/class/leds/{cls.LED_DIR}/delay_on", str(delay_on))
        set_value(f"/sys/class/leds/{cls.LED_DIR}/delay_off", str(delay_off))


class RED_LED(BUILT_IN_LED):
    LED_DIR = "PWR"


class GREEN_LED(BUILT_IN_LED):
    LED_DIR = "ACT"