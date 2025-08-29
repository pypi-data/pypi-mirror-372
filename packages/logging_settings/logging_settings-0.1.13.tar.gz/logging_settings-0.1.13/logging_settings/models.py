from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING

from colorama import Fore, Style

__all__ = ("LOG_LINE_FORMATS",)


LOG_LINE_FORMATS = {
    NOTSET: Style.DIM + Fore.WHITE,
    DEBUG: Style.NORMAL + Fore.WHITE,
    INFO: Style.BRIGHT + Fore.WHITE,
    WARNING: Style.NORMAL + Fore.YELLOW,
    ERROR: Style.NORMAL + Fore.RED,
    CRITICAL: Style.BRIGHT + Fore.RED,
}
