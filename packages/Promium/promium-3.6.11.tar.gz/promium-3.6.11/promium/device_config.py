import os
from typing import NamedTuple


DEFAULT_USER_AGENT_ANDROID = (
    f"Mozilla/5.0 (Linux; Android 14; SM-G960U) "
    f"AppleWebKit/537.36 (KHTML, like Gecko) "
    f"Chrome/{os.environ.get('GOOGLE_CHROME_VERSION', '131.0.6778.39')} "
    f"Mobile Safari/537.36"
)
DEFAULT_USER_AGENT_IOS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.4.1 Mobile/15E148 Safari/604.1"
)
DEFAULT_USER_AGENT_HUAWEI = (
    f"Mozilla/5.0 (Linux; Android 11; HUAWEI Mate 40 Pro Build/HUAWEIMate40Pro;"
    f" xx-xx) AppleWebKit/537.36 (KHTML, like Gecko) "
    f"Chrome/{os.environ.get('GOOGLE_CHROME_VERSION', '131.0.6778.39')} "
    f"Mobile Safari/537.36"
)


class DesktopDevice(NamedTuple):
    width: int
    height: int
    user_agent: str = ''


class CustomDevice(NamedTuple):
    """
    It is possible to create your own device,
    which is not in the list of known devices in DevTools Emulator panel

    Usage:
        XIAOMI_REDMI_7 = CustomDevice(393, 851)
    """
    width: int
    height: int
    pixel_ratio: float = 1.0
    user_agent: str = DEFAULT_USER_AGENT_ANDROID


CHROME_DESKTOP_1920_1080 = DesktopDevice(1920, 1080)
CHROME_DESKTOP_1024_768 = DesktopDevice(1024, 768)

ANDROID_360_640 = CustomDevice(360, 640, 3.0)
ANDROID_1280_800 = CustomDevice(1280, 800, 3.0)
XIAOMI_REDMI_7 = CustomDevice(393, 851)

HUAWEI_MATE_40_PRO = CustomDevice(768, 850, 3.0, DEFAULT_USER_AGENT_HUAWEI)

IOS_750_1334 = CustomDevice(750, 1334, 2.0, DEFAULT_USER_AGENT_IOS)
IOS_1080_1920 = CustomDevice(1080, 1920, 2.0, DEFAULT_USER_AGENT_IOS)

NEXUS_5 = CustomDevice(412, 732, 2.0)
IPHONE_X = CustomDevice(375, 812, 3.0, DEFAULT_USER_AGENT_IOS)
IPAD_MINI = CustomDevice(768, 1024, 2.0, DEFAULT_USER_AGENT_IOS)
IPAD_PRO = CustomDevice(1024, 1366, 2.0, DEFAULT_USER_AGENT_IOS)
