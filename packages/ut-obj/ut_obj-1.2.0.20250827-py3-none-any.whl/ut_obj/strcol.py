# coding=utf-8

TyStr = str

"""
Koskya Utilities Module
contains the Kosakya Utilitiy Classes
"""


class Style:
    reset = '0'
    bold = '1'
    disable = '2'
    negative1 = '3'
    underline = '4'
    negative2 = '5'
    reverse = '7'
    invisible = '8'
    strikethrough = '9'


class Fg:
    black = '30'
    red = '31'
    green = '32'
    yellow = '33'
    blue = '34'
    magenta = '35'
    cyan = '36'
    white = '37'
    reset = '39'


class Bg:
    black = '40'
    red = '41'
    green = '42'
    yellow = '43'
    blue = '44'
    magenta = '45'
    cyan = '46'
    white = '47'
    reset = '49'


class StrCol:
    """Colour Class
    """
    # esc = "\033"
    esc = "\u001b"
    check_mark = u'\u2705'
    heavy_check_mark = u'\u2713'
    heavy_check_mark_ = u'\u2714'

    @classmethod
    def show(
            cls, text: TyStr,
            fg: TyStr, bg: TyStr = Bg.reset,
            style: TyStr = Style.reset, esc: TyStr = esc
    ) -> TyStr:
        return f"{esc}[{style};{fg};{bg}m{text}{esc}[0m"

    @classmethod
    def sh_red(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.red)

    @classmethod
    def sh_green(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.green)

    @classmethod
    def sh_yellow(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.yellow)

    @classmethod
    def sh_blue(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.blue)

    @classmethod
    def sh_magenta(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.magenta)

    @classmethod
    def sh_bold(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.red, style=Style.bold)

    @classmethod
    def sh_bold_red(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.red, style=Style.bold)

    @classmethod
    def sh_bold_green(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.green, style=Style.bold)

    @classmethod
    def sh_bold_light_green(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg='92', style=Style.bold)

    @classmethod
    def sh_bold_yellow(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.yellow, style=Style.bold)

    @classmethod
    def sh_bold_blue(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.blue, style=Style.bold)

    @classmethod
    def sh_bold_magenta(cls, text: TyStr) -> TyStr:
        return cls.show(text, fg=Fg.magenta, style=Style.bold)

    @classmethod
    def sh_bold_cyan(cls, text: TyStr) -> TyStr:
        """light blue
        """
        return cls.show(text, fg=Fg.cyan, style=Style.bold)
