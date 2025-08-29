from os import name as _name, system as _system, get_terminal_size as _terminal_size
from sys import stdout as _stdout
from time import sleep as _sleep
from threading import Thread as _thread
import math

if _name == 'nt':
    from ctypes import c_int, c_byte, Structure, byref, windll

    class _CursorInfo(Structure):
        _fields_ = [("size", c_int),
                    ("visible", c_byte)]

class System:
    Windows = _name == 'nt'

    def Init():
        _system('')

    def Clear():
        return _system("cls" if System.Windows else "clear")

    def Title(title: str):
        if System.Windows:
            return _system(f"title {title}")

    def Size(x: int, y: int):
        if System.Windows:
            return _system(f"mode {x}, {y}")

    def Command(command: str):
        return _system(command)

class Cursor:
    def HideCursor():
        if _name == 'nt':
            Cursor._cursor(False)
        elif _name == 'posix':
            _stdout.write("\033[?25l")
            _stdout.flush()

    def ShowCursor():
        if _name == 'nt':
            Cursor._cursor(True)
        elif _name == 'posix':
            _stdout.write("\033[?25h")
            _stdout.flush()

    def _cursor(visible: bool):
        ci = _CursorInfo()
        handle = windll.kernel32.GetStdHandle(-11)
        windll.kernel32.GetConsoleCursorInfo(handle, byref(ci))
        ci.visible = visible
        windll.kernel32.SetConsoleCursorInfo(handle, byref(ci))

class _MakeColors:
    def _makeansi(col: str, text: str) -> str:
        return f"\033[38;2;{col}m{text}\033[38;2;255;255;255m"

    def _rmansi(col: str) -> str:
        return col.replace('\033[38;2;', '').replace('m','').replace('50m', '').replace('\x1b[38', '')

    def _makergbcol(var1: list, var2: list) -> list:
        col = list(var1[:12])
        for _col in var2[:12]:
            col.append(_col)
        for _col in reversed(col):
            col.append(_col)
        return col

    def _start(color: str) -> str:
        return f"\033[38;2;{color}m"

    def _end() -> str:
        return "\033[38;2;255;255;255m"

    def _maketext(color: str, text: str, end: bool = False) -> str:
        end = _MakeColors._end() if end else ""
        return color+text+end

    def _getspaces(text: str) -> int:
        return len(text) - len(text.lstrip())

    def _makerainbow(*colors) -> list:
        colors = [color[:24] for color in colors]
        rainbow = []
        for color in colors:
            for col in color:
                rainbow.append(col)
        return rainbow
    
    def _reverse(colors: list) -> list:
        _colors = list(colors)
        for col in reversed(_colors):
            colors.append(col)
        return colors
    
    def _mixcolors(col1: str, col2: str, _reverse: bool = True) -> list:
        col1, col2 = _MakeColors._rmansi(col=col1), _MakeColors._rmansi(col=col2)
        fade1 = Colors.StaticMIX([col1, col2], _start=False)      
        fade2 = Colors.StaticMIX([fade1, col2], _start=False)
        fade3 = Colors.StaticMIX([fade1, col1], _start=False)
        fade4 = Colors.StaticMIX([fade2, col2], _start=False)
        fade5 = Colors.StaticMIX([fade1, fade3], _start=False)    
        fade6 = Colors.StaticMIX([fade3, col1], _start=False)
        fade7 = Colors.StaticMIX([fade1, fade2], _start=False)
        mixed = [col1, fade6, fade3, fade5, fade1, fade7, fade2, fade4, col2]
        return _MakeColors._reverse(colors=mixed) if _reverse else mixed 

class Colors:
    def StaticRGB(r: int, g: int, b: int) -> str:
        return _MakeColors._start(f"{r};{g};{b}")

    def DynamicRGB(r1: int, g1: int, b1: int, r2: int, g2: int, b2: int) -> list:
        steps = 24
        colors = []
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / (steps - 1))
            g = int(g1 + (g2 - g1) * i / (steps - 1))
            b = int(b1 + (b2 - b1) * i / (steps - 1))
            colors.append(f"{r};{g};{b}")
        return colors

    def StaticMIX(colors: list, _start: bool = True) -> str:
        rgb = []
        for col in colors:
            col = _MakeColors._rmansi(col=col)
            col = col.split(';')
            r = int(int(col[0]))
            g = int(int(col[1]))
            b = int(int(col[2]))
            rgb.append([r, g, b])
        r = round(sum(rgb[0] for rgb in rgb) / len(rgb))
        g = round(sum(rgb[1] for rgb in rgb) / len(rgb))
        b = round(sum(rgb[2] for rgb in rgb) / len(rgb))
        rgb = f'{r};{g};{b}'
        return _MakeColors._start(rgb) if _start else rgb

    def DynamicMIX(colors: list):
        _colors = []
        for color in colors:
            if colors.index(color) == len(colors) - 1:
                break
            _colors.append([color, colors[colors.index(color) + 1]])
        colors = [_MakeColors._mixcolors(col1=color[0], col2=color[1], _reverse=False) for color in _colors]
        final = []
        for col in colors:
            for col in col:
                final.append(col)
        return _MakeColors._reverse(colors=final)

    def Symbol(symbol: str, col: str, col_left_right: str, left: str = '[', right: str = ']') -> str:
        return f"{col_left_right}{left}{col}{symbol}{col_left_right}{right}{Col.reset}"

    black_to_white = ["m;m;m"]
    black_to_red = ["m;0;0"]
    black_to_green = ["0;m;0"]
    black_to_blue = ["0;0;m"]
    white_to_black = ["n;n;n"]
    white_to_red = ["255;n;n"]
    white_to_green = ["n;255;n"]
    white_to_blue = ["n;n;255"]
    red_to_black = ["n;0;0"]
    red_to_white = ["255;m;m"]
    red_to_yellow = ["255;m;0"]
    red_to_purple = ["255;0;m"]
    green_to_black = ["0;n;0"]
    green_to_white = ["m;255;m"]
    green_to_yellow = ["m;255;0"]
    green_to_cyan = ["0;255;m"]
    blue_to_black = ["0;0;n"]
    blue_to_white = ["m;m;255"]
    blue_to_cyan = ["0;m;255"]
    blue_to_purple = ["m;0;255"]
    yellow_to_red = ["255;n;0"]
    yellow_to_green = ["n;255;0"]
    purple_to_red = ["255;0;n"]
    purple_to_blue = ["n;0;255"]
    cyan_to_green = ["0;255;n"]
    cyan_to_blue = ["0;n;255"]
    orange_to_purple = ["255;150;m"]
    pink_to_cyan = ["255;0;n"]
    turquoise_to_yellow = ["0;150;n"]
    gray_to_purple = ["150;150;m"]
    neon_gradient = ["255;20;m"]
    coral_to_lime = ["255;127;m"]
    neon_green_to_purple = ["57;255;m"]
    pink_to_turquoise = ["255;0;n"]
    yellow_to_cyan = ["255;255;m"]
    purple_to_coral = ["255;0;n"]
    blue_to_neon = ["0;0;m"]
    green_to_purple = ["0;255;m"]
    red_to_cyan = ["255;0;m"]
    orange_to_cyan = ["255;150;m"]
    lime_to_purple = ["0;255;m"]
    coral_to_purple = ["255;127;m"]
    turquoise_to_pink = ["0;150;n"]
    gray_to_cyan = ["150;150;m"]
    neon_pink_to_blue = ["255;20;n"]
    yellow_to_neon = ["255;255;m"]
    purple_to_lime = ["255;0;n"]
    cyan_to_purple = ["0;255;m"]
    blue_to_yellow = ["0;0;n"]
    green_to_neon = ["0;255;m"]
    red_to_turquoise = ["255;0;m"]
    orange_to_neon = ["255;150;m"]
    lime_to_cyan = ["0;255;m"]
    coral_to_neon = ["255;127;m"]
    turquoise_to_coral = ["0;150;n"]
    gray_to_neon = ["150;150;m"]
    neon_pink_to_purple = ["255;20;m"]
    yellow_to_purple = ["255;255;m"]
    purple_to_neon = ["255;0;m"]
    cyan_to_neon = ["0;255;m"]
    blue_to_coral = ["0;0;n"]
    green_to_lime = ["0;255;n"]
    red_to_lime = ["255;0;n"]
    orange_to_lime = ["255;150;n"]
    lime_to_neon = ["0;255;m"]
    coral_to_cyan = ["255;127;m"]
    turquoise_to_neon = ["0;150;m"]
    gray_to_lime = ["150;150;n"]
    neon_pink_to_cyan = ["255;20;m"]
    yellow_to_lime = ["255;255;n"]
    purple_to_cyan = ["255;0;m"]
    cyan_to_lime = ["0;255;n"]
    blue_to_lime = ["0;0;n"]
    green_to_coral = ["0;255;n"]
    red_to_neon = ["255;0;m"]
    orange_to_turquoise = ["255;150;n"]
    magenta_to_teal = ["255;0;m"]
    violet_to_gold = ["238;130;n"]
    indigo_to_silver = ["75;0;n"]
    olive_to_khaki = ["128;128;n"]
    maroon_to_crimson = ["128;0;n"]
    navy_to_sapphire = ["0;0;n"]
    gold_to_amber = ["255;215;n"]
    silver_to_lavender = ["192;192;n"]
    bronze_to_sienna = ["205;127;n"]
    mint_to_emerald = ["62;180;n"]
    salmon_to_coral = ["250;128;n"]
    orchid_to_plum = ["218;112;n"]
    aqua_to_cyan = ["0;255;m"]
    ruby_to_magenta = ["224;17;n"]
    topaz_to_amber = ["255;200;n"]
    jade_to_mint = ["0;168;n"]
    amethyst_to_violet = ["153;102;n"]
    teal_to_aqua = ["0;128;m"]
    crimson_to_ruby = ["220;20;n"]
    khaki_to_olive = ["240;230;n"]
    lavender_to_silver = ["230;230;n"]
    emerald_to_jade = ["0;201;n"]
    sapphire_to_navy = ["15;82;n"]
    amber_to_gold = ["255;191;n"]
    plum_to_orchid = ["221;160;n"]
    sienna_to_bronze = ["160;82;n"]
    coral_to_salmon = ["255;127;n"]
    lime_to_mint = ["0;255;n"]
    magenta_to_violet = ["255;0;n"]
    teal_to_turquoise = ["0;128;n"]
    gold_to_topaz = ["255;215;n"]
    silver_to_gray = ["192;192;n"]
    bronze_to_coral = ["205;127;n"]
    lavender_to_purple = ["230;230;m"]
    mint_to_lime = ["62;180;n"]
    salmon_to_pink = ["250;128;n"]
    crimson_to_red = ["220;20;n"]
    orchid_to_magenta = ["218;112;n"]
    plum_to_purple = ["221;160;m"]
    sienna_to_orange = ["160;82;n"]
    khaki_to_yellow = ["240;230;n"]
    aqua_to_turquoise = ["0;255;n"]
    emerald_to_green = ["0;201;n"]
    sapphire_to_blue = ["15;82;n"]
    ruby_to_crimson = ["224;17;n"]
    amber_to_orange = ["255;191;n"]
    topaz_to_yellow = ["255;200;n"]
    jade_to_emerald = ["0;168;n"]
    amethyst_to_purple = ["153;102;m"]

    red_to_blue = ...
    red_to_green = ...
    green_to_blue = ...
    green_to_red = ...
    blue_to_red = ...
    blue_to_green = ...
    rainbow = ...

    red = _MakeColors._start('255;0;0')
    green = _MakeColors._start('0;255;0')
    blue = _MakeColors._start('0;0;255')
    white = _MakeColors._start('255;255;255')
    black = _MakeColors._start('0;0;0')
    gray = _MakeColors._start('150;150;150')
    yellow = _MakeColors._start('255;255;0')
    purple = _MakeColors._start('255;0;255')
    cyan = _MakeColors._start('0;255;255')
    orange = _MakeColors._start('255;150;0')
    pink = _MakeColors._start('255;0;150')
    turquoise = _MakeColors._start('0;150;255')
    light_gray = _MakeColors._start('200;200;200')
    dark_gray = _MakeColors._start('100;100;100')
    light_red = _MakeColors._start('255;100;100')
    light_green = _MakeColors._start('100;255;100')
    light_blue = _MakeColors._start('100;100;255')
    dark_red = _MakeColors._start('100;0;0')
    dark_green = _MakeColors._start('0;100;0')
    dark_blue = _MakeColors._start('0;0;100')
    neon_green = _MakeColors._start('57;255;20')
    neon_pink = _MakeColors._start('255;20;147')
    deep_purple = _MakeColors._start('75;0;130')
    coral = _MakeColors._start('255;127;127')
    lime = _MakeColors._start('0;255;127')
    teal = _MakeColors._start('0;128;128')
    magenta = _MakeColors._start('255;0;255')
    violet = _MakeColors._start('238;130;238')
    indigo = _MakeColors._start('75;0;130')
    olive = _MakeColors._start('128;128;0')
    maroon = _MakeColors._start('128;0;0')
    navy = _MakeColors._start('0;0;128')
    gold = _MakeColors._start('255;215;0')
    silver = _MakeColors._start('192;192;192')
    bronze = _MakeColors._start('205;127;50')
    lavender = _MakeColors._start('230;230;250')
    mint = _MakeColors._start('62;180;137')
    salmon = _MakeColors._start('250;128;114')
    crimson = _MakeColors._start('220;20;60')
    orchid = _MakeColors._start('218;112;214')
    plum = _MakeColors._start('221;160;221')
    sienna = _MakeColors._start('160;82;45')
    khaki = _MakeColors._start('240;230;140')
    aqua = _MakeColors._start('0;255;255')
    emerald = _MakeColors._start('0;201;87')
    sapphire = _MakeColors._start('15;82;186')
    ruby = _MakeColors._start('224;17;95')
    amber = _MakeColors._start('255;191;0')
    topaz = _MakeColors._start('255;200;124')
    jade = _MakeColors._start('0;168;107')
    amethyst = _MakeColors._start('153;102;204')
    reset = white

    col = (list, str)
    dynamic_colors = [
        black_to_white, black_to_red, black_to_green, black_to_blue,
        white_to_black, white_to_red, white_to_green, white_to_blue,
        red_to_black, red_to_white, red_to_yellow, red_to_purple,
        green_to_black, green_to_white, green_to_yellow, green_to_cyan,
        blue_to_black, blue_to_white, blue_to_cyan, blue_to_purple,
        yellow_to_red, yellow_to_green,
        purple_to_red, purple_to_blue,
        cyan_to_green, cyan_to_blue,
        orange_to_purple, pink_to_cyan, turquoise_to_yellow,
        gray_to_purple, neon_gradient,
        coral_to_lime, neon_green_to_purple, pink_to_turquoise,
        yellow_to_cyan, purple_to_coral, blue_to_neon,
        green_to_purple, red_to_cyan, orange_to_cyan,
        lime_to_purple, coral_to_purple, turquoise_to_pink,
        gray_to_cyan, neon_pink_to_blue, yellow_to_neon,
        purple_to_lime, cyan_to_purple, blue_to_yellow,
        green_to_neon, red_to_turquoise, orange_to_neon,
        lime_to_cyan, coral_to_neon, turquoise_to_coral,
        gray_to_neon, neon_pink_to_purple, yellow_to_purple,
        purple_to_neon, cyan_to_neon, blue_to_coral,
        green_to_lime, red_to_lime, orange_to_lime,
        lime_to_neon, coral_to_cyan, turquoise_to_neon,
        gray_to_lime, neon_pink_to_cyan, yellow_to_lime,
        purple_to_cyan, cyan_to_lime, blue_to_lime,
        green_to_coral, red_to_neon, orange_to_turquoise,
        magenta_to_teal, violet_to_gold, indigo_to_silver,
        olive_to_khaki, maroon_to_crimson, navy_to_sapphire,
        gold_to_amber, silver_to_lavender, bronze_to_sienna,
        mint_to_emerald, salmon_to_coral, orchid_to_plum,
        aqua_to_cyan, ruby_to_magenta, topaz_to_amber,
        jade_to_mint, amethyst_to_violet, teal_to_aqua,
        crimson_to_ruby, khaki_to_olive, lavender_to_silver,
        emerald_to_jade, sapphire_to_navy, amber_to_gold,
        plum_to_orchid, sienna_to_bronze, coral_to_salmon,
        lime_to_mint, magenta_to_violet, teal_to_turquoise,
        gold_to_topaz, silver_to_gray, bronze_to_coral,
        lavender_to_purple, mint_to_lime, salmon_to_pink,
        crimson_to_red, orchid_to_magenta, plum_to_purple,
        sienna_to_orange, khaki_to_yellow, aqua_to_turquoise,
        emerald_to_green, sapphire_to_blue, ruby_to_crimson,
        amber_to_orange, topaz_to_yellow, jade_to_emerald,
        amethyst_to_purple
    ]

    for color in dynamic_colors:
        _col = 20
        reversed_col = 220
        dbl_col = 20
        dbl_reversed_col = 220
        content = color[0]
        color.pop(0)
        for _ in range(12):
            if 'm' in content:
                result = content.replace('m', str(_col))
                color.append(result)
            elif 'n' in content:
                result = content.replace('n', str(reversed_col))
                color.append(result)
            _col += 20
            reversed_col -= 20
        for _ in range(12):
            if 'm' in content:
                result = content.replace('m', str(dbl_reversed_col))
                color.append(result)
            elif 'n' in content:
                result = content.replace('n', str(dbl_col))
                color.append(result)
            dbl_col += 20
            dbl_reversed_col -= 20

    red_to_blue = _MakeColors._makergbcol(red_to_purple, purple_to_blue)
    red_to_green = _MakeColors._makergbcol(red_to_yellow, yellow_to_green)
    green_to_blue = _MakeColors._makergbcol(green_to_cyan, cyan_to_blue)
    green_to_red = _MakeColors._makergbcol(green_to_yellow, yellow_to_red)
    blue_to_red = _MakeColors._makergbcol(blue_to_purple, purple_to_red)
    blue_to_green = _MakeColors._makergbcol(blue_to_cyan, cyan_to_green)
    rainbow = _MakeColors._makerainbow(
        red_to_green, green_to_blue, blue_to_red)

    for _col in (
        red_to_blue, red_to_green,
        green_to_blue, green_to_red,
        blue_to_red, blue_to_green
    ): dynamic_colors.append(_col)
    dynamic_colors.append(rainbow)

    static_colors = [
        red, green, blue, white, black, gray,
        yellow, purple, cyan, orange, pink, turquoise,
        light_gray, dark_gray, light_red, light_green, light_blue,
        dark_red, dark_green, dark_blue, neon_green, neon_pink,
        deep_purple, coral, lime, teal, magenta, violet,
        indigo, olive, maroon, navy, gold, silver,
        bronze, lavender, mint, salmon, crimson, orchid,
        plum, sienna, khaki, aqua, emerald, sapphire,
        ruby, amber, topaz, jade, amethyst, reset
    ]

    all_colors = [color for color in dynamic_colors]
    for color in static_colors:
        all_colors.append(color)

Col = Colors

class Colorate:
    def Color(color: str, text: str, end: bool = True) -> str:
        return _MakeColors._maketext(color=color, text=text, end=end)

    def Error(text: str, color: str = Colors.red, end: bool = False, spaces: bool = 1, enter: bool = True, wait: int = False) -> str:
        content = _MakeColors._maketext(
            color=color, text="\n" * spaces + text, end=end)
        if enter:
            var = input(content)
        else:
            print(content)
            var = None
        if wait is True:
            exit()
        elif wait is not False:
            _sleep(wait)
        return var

    def Vertical(color: list, text: str, speed: int = 1, start: int = 0, stop: int = 0, cut: int = 0, fill: bool = False) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""
        nstart = 0
        color_n = 0
        for lin in lines:
            colorR = color[color_n]
            if fill:
                result += " " * \
                    _MakeColors._getspaces(
                        lin) + "".join(_MakeColors._makeansi(colorR, x) for x in lin.strip()) + "\n"
            else:
                result += " " * \
                    _MakeColors._getspaces(
                        lin) + _MakeColors._makeansi(colorR, lin.strip()) + "\n"  
            if nstart != start:
                nstart += 1
                continue
            if lin.rstrip():
                if (
                    stop == 0
                    and color_n + speed < len(color)
                    or stop != 0
                    and color_n + speed < stop
                ):
                    color_n += speed
                elif stop == 0:
                    color_n = 0
                else:
                    color_n = stop
        return result.rstrip()

    def Horizontal(color: list, text: str, speed: int = 1, cut: int = 0) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""
        for lin in lines:
            carac = list(lin)
            color_n = 0
            for car in carac:
                colorR = color[color_n]
                result += " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip())
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 0
            result += "\n"
        return result.rstrip()

    def Diagonal(color: list, text: str, speed: int = 1, cut: int = 0) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""
        color_n = 0
        for lin in lines:
            carac = list(lin)
            for car in carac:
                colorR = color[color_n]
                result += " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip())
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 1
            result += "\n"
        return result.rstrip()

    def DiagonalBackwards(color: list, text: str, speed: int = 1, cut: int = 0) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""
        resultL = ''
        color_n = 0
        for lin in lines:
            carac = list(lin)
            carac.reverse()
            resultL = ''
            for car in carac:
                colorR = color[color_n]
                resultL = " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip()) + resultL
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 0
            result = result + '\n' + resultL
        return result.strip()

    def Format(text: str, second_chars: list, mode, principal_col: list, second_col: str):
        if mode == Colorate.Vertical:
            ctext = mode(principal_col, text, fill=True)
        else:
            ctext = mode(principal_col, text)
        ntext = ""
        for x in ctext:
            if x in second_chars:
                x = Colorate.Color(second_col, x)
            ntext += x
        return ntext

    def GradientText(text: str, color: list, intensity: float = 1.0) -> str:
        lines = text.splitlines()
        result = ""
        color = color[:]
        if len(color) < len(lines):
            color = color * (len(lines) // len(color) + 1)
        for i, line in enumerate(lines):
            t = math.sin(i / len(lines) * math.pi * intensity)
            color_idx = int(t * (len(color) - 1))
            result += _MakeColors._makeansi(color[color_idx], line) + "\n"
        return result.rstrip()

class Anime:
    def Fade(text: str, color: list, mode, time=True, interval=0.05, hide_cursor: bool = True, enter: bool = False):
        if hide_cursor:
            Cursor.HideCursor()
        if type(time) == int:
            time *= 15
        global passed
        passed = False
        if enter:
            th = _thread(target=Anime._input)
            th.start()
        if time is True:
            while True:
                if passed is not False:
                    break
                Anime._anime(text, color, mode, interval)
                ncolor = color[1:]
                ncolor.append(color[0])
                color = ncolor
        else:
            for _ in range(time):
                if passed is not False:
                    break
                Anime._anime(text, color, mode, interval)
                ncolor = color[1:]
                ncolor.append(color[0])
                color = ncolor
        if hide_cursor:
            Cursor.ShowCursor()

    def Move(text: str, color: list, time=True, interval=0.01, hide_cursor: bool = True, enter: bool = False):
        if hide_cursor:
            Cursor.HideCursor()
        if type(time) == int:
            time *= 15
        global passed
        passed = False
        columns = _terminal_size().columns
        if enter:
            th = _thread(target=Anime._input)
            th.start()
        count = 0
        mode = 1
        if time is True:
            while not passed:
                if mode == 1:
                    if count >= (columns - (max(len(txt) for txt in text.splitlines()) + 1)):
                        mode = 2
                    count += 1
                elif mode == 2:
                    if count <= 0:
                        mode = 1
                    count -= 1
                Anime._anime('\n'.join((' ' * count) + line for line in text.splitlines()), color or [], lambda a, b: b, interval)
        else:
            for _ in range(time):
                if passed:
                    break
                if mode == 1:
                    if count >= (columns - (max(len(txt) for txt in text.splitlines()) + 1)):
                        mode = 2
                elif mode == 2:
                    if count <= 0:
                        mode = 1
                Anime._anime('\n'.join((' ' * count) + line for line in text.splitlines()), color or [], lambda a, b: b, interval)
                count += 1
        if hide_cursor:
            Cursor.ShowCursor()

    def Bar(length, carac_0: str = '[ ]', carac_1: str = '[0]', color: list = Colors.white, mode=Colorate.Horizontal, interval: int = 0.5, hide_cursor: bool = True, enter: bool = False, center: bool = False):
        if hide_cursor:
            Cursor.HideCursor()
        if type(color) == list:
            while not length <= len(color):
                ncolor = list(color)
                for col in ncolor:
                    color.append(col)
        global passed
        passed = False
        if enter:
            th = _thread(target=Anime._input)
            th.start()
        for i in range(length + 1):
            bar = carac_1 * i + carac_0 * (length - i)
            if passed:
                break
            if type(color) == list:
                if center:
                    print(Center.XCenter(mode(color, bar)))
                else:
                    print(mode(color, bar))
            else:
                if center:
                    print(Center.XCenter(color + bar))
                else:
                    print(color + bar)
            _sleep(interval)
            System.Clear()
        if hide_cursor:
            Cursor.ShowCursor()

    def Pulse(text: str, color: list, time=True, interval=0.1, hide_cursor: bool = True, enter: bool = False):
        if hide_cursor:
            Cursor.HideCursor()
        if type(time) == int:
            time *= 15
        global passed
        passed = False
        if enter:
            th = _thread(target=Anime._input)
            th.start()
        if time is True:
            while not passed:
                for i in range(10):
                    scale = 1 + 0.1 * math.sin(i * math.pi / 5)
                    scaled_text = '\n'.join(' ' * int((1 - scale) * len(line) / 2) + line for line in text.splitlines())
                    Anime._anime(Center.XCenter(scaled_text), color, Colorate.Horizontal, interval)
                    ncolor = color[1:]
                    ncolor.append(color[0])
                    color = ncolor
        else:
            for _ in range(time):
                if passed:
                    break
                for i in range(10):
                    scale = 1 + 0.1 * math.sin(i * math.pi / 5)
                    scaled_text = '\n'.join(' ' * int((1 - scale) * len(line) / 2) + line for line in text.splitlines())
                    Anime._anime(Center.XCenter(scaled_text), color, Colorate.Horizontal, interval)
                    ncolor = color[1:]
                    ncolor.append(color[0])
                    color = ncolor
        if hide_cursor:
            Cursor.ShowCursor()

    def Anime() -> None: ...

    def _anime(text: str, color: list, mode, interval: int):
        _stdout.write(mode(color, text))
        _stdout.flush()
        _sleep(interval)
        System.Clear()

    def _input() -> str:
        global passed
        passed = input()
        return passed

class Write:
    def Print(text: str, color: list, interval=0.05, hide_cursor: bool = True, end: str = Colors.reset) -> None:
        if hide_cursor:
            Cursor.HideCursor()
        Write._write(text=text, color=color, interval=interval)
        _stdout.write(end)
        _stdout.flush()
        if hide_cursor:
            Cursor.ShowCursor()

    def Input(text: str, color: list, interval=0.05, hide_cursor: bool = True, input_color: str = Colors.reset, end: str = Colors.reset, func=input) -> str:
        if hide_cursor:
            Cursor.HideCursor()
        Write._write(text=text, color=color, interval=interval)
        valor = func(input_color)
        _stdout.write(end)
        _stdout.flush()
        if hide_cursor:
            Cursor.ShowCursor()
        return valor

    def _write(text: str, color, interval: int):
        lines = list(text)
        if type(color) == list:
            while not len(lines) <= len(color):
                ncolor = list(color)
                for col in ncolor:
                    color.append(col)
        n = 0
        for line in lines:
            if type(color) == list:
                _stdout.write(_MakeColors._makeansi(color[n], line))
            else:
                _stdout.write(color + line)
            _stdout.flush()
            _sleep(interval)
            if line.strip():
                n += 1

class Center:
    center = 'CENTER'
    left = 'LEFT'
    right = 'RIGHT'

    def XCenter(text: str, spaces: int = None, icon: str = " "):
        if spaces is None:
            spaces = Center._xspaces(text=text)
        return "\n".join((icon * spaces) + text for text in text.splitlines())

    def YCenter(text: str, spaces: int = None, icon: str = "\n"):
        if spaces is None:
            spaces = Center._yspaces(text=text)
        return icon * spaces + "\n".join(text.splitlines())

    def Center(text: str, xspaces: int = None, yspaces: int = None, xicon: str = " ", yicon: str = "\n") -> str:
        if xspaces is None:
            xspaces = Center._xspaces(text=text)
        if yspaces is None:
            yspaces = Center._yspaces(text=text)
        text = yicon * yspaces + "\n".join(text.splitlines())
        return "\n".join((xicon * xspaces) + text for text in text.splitlines())

    def GroupAlign(text: str, align: str = center):
        align = align.upper()
        if align == Center.center:
            return Center.XCenter(text)
        elif align == Center.left:
            return text
        elif align == Center.right:
            length = _terminal_size().columns
            maxLineSize = max(len(line) for line in text.splitlines())
            return '\n'.join((' ' * (length - maxLineSize)) + line for line in text.splitlines())
        else:
            raise Center.BadAlignment()
    
    def TextAlign(text: str, align: str = center):
        align = align.upper()
        mlen = max(len(i) for i in text.splitlines())
        if align == Center.center:
            return "\n".join((' ' * int(mlen/2 - len(lin)/2)) + lin for lin in text.splitlines())
        elif align == Center.left:
            return text
        elif align == Center.right:
            ntext = '\n'.join(' ' * (mlen - len(lin)) + lin for lin in text.splitlines())
            return ntext
        else:
            raise Center.BadAlignment()

    def _xspaces(text: str):
        try:
            col = _terminal_size().columns
        except OSError:
            return 0
        textl = text.splitlines()
        ntextl = max((len(v) for v in textl if v.strip()), default=0)
        return int((col - ntextl) / 2)

    def _yspaces(text: str):
        try:
            lin = _terminal_size().lines
        except OSError:
            return 0
        textl = text.splitlines()
        ntextl = len(textl)
        return int((lin - ntextl) / 2)

    class BadAlignment(Exception):
        def __init__(self):
            super().__init__("Choose a correct alignment: Center.center / Center.left / Center.right")

class Add:
    def Add(banner1, banner2, spaces=0, center=False):
        if center:
            split1 = len(banner1.splitlines())
            split2 = len(banner2.splitlines())
            if split1 > split2:
                spaces = (split1 - split2) // 2
            elif split2 > split1:
                spaces = (split2 - split1) // 2
            else:
                spaces = 0
        if spaces > max(len(banner1.splitlines()), len(banner2.splitlines())):
            spaces = max(len(banner1.splitlines()), len(banner2.splitlines()))
        ban1 = banner1.splitlines()
        ban2 = banner2.splitlines()
        ban1count = len(ban1)
        ban2count = len(ban2)
        size = Add._length(ban1)
        ban1 = Add._edit(ban1, size)
        ban1line = 0
        ban2line = 0
        text = ''
        for _ in range(spaces):
            if ban1count >= ban2count:
                ban1data = ban1[ban1line]
                ban2data = ''
                ban1line += 1
            else:
                ban1data = " " * size
                ban2data = ban2[ban2line]
                ban2line += 1
            text = text + ban1data + ban2data + '\n'
        while ban1line < ban1count or ban2line < ban2count:
            ban1data = ban1[ban1line] if ban1line < ban1count else " " * size
            ban2data = ban2[ban2line] if ban2line < ban2count else ""
            text = text + ban1data + ban2data + '\n'
            ban1line += 1
            ban2line += 1
        return text

    class MaximumSpaces(Exception):
        def __init__(self, spaces: str):
            super().__init__(f"Too much spaces [{spaces}].")

    def _length(ban1):
        bigestline = 0
        for line in ban1:
            if len(line) > bigestline:
                bigestline = len(line)
        return bigestline

    def _edit(ban1, size):
        return [line + (size - len(line)) * " " for line in ban1]

class Banner:
    def Box(content: str, up_left: str, up_right: str, down_left: str, down_right: str, left_line: str, up_line: str, right_line: str, down_line: str) -> str:
        l = 0
        lines = content.splitlines()
        for a in lines:
            if len(a) > l:
                l = len(a)
        if l % 2 == 1:
            l += 1
        box = up_left + (up_line * l) + up_right + "\n"
        for line in lines:
            box += left_line + " " + line + (" " * int((l - len(line)))) + " " + right_line + "\n"
        box += down_left + (down_line * l) + down_right + "\n"
        return box

    def SimpleCube(content: str) -> str:
        l = 0
        lines = content.splitlines()
        for a in lines:
            if len(a) > l:
                l = len(a)
        if l % 2 == 1:
            l += 1
        box = "__" + ("_" * l) + "__\n"
        box += "| " + (" " * int(l / 2)) + (" " * int(l / 2)) + " |\n"
        for line in lines:
            box += "| " + line + (" " * int((l - len(line)))) + " |\n"
        box += "|_" + ("_" * l) + "_|\n"
        return box

    def DoubleCube(content: str) -> str:
        return Banner.Box(content, "╔═", "═╗", "╚═", "═╝", "║", "═", "║", "═")

    def RoundedBox(content: str) -> str:
        l = 0
        lines = content.splitlines()
        for a in lines:
            if len(a) > l:
                l = len(a)
        if l % 2 == 1:
            l += 1
        box = "╭" + ("─" * l) + "╮\n"
        for line in lines:
            box += "│ " + line + (" " * int((l - len(line)))) + " │\n"
        box += "╰" + ("─" * l) + "╯\n"
        return box

    def Lines(content: str, color=None, mode=Colorate.Horizontal, line='═', pepite='ቐ') -> str:
        l = 1
        for c in content.splitlines():
            if len(c) > l:
                l = len(c)
        mode = Colorate.Horizontal if color is not None else (lambda **kw: kw['text'])
        box = mode(text=f"─{line*l}{pepite * 2}{line*l}─", color=color)
        assembly = box + "\n" + content + "\n" + box
        final = ''
        for lines in assembly.splitlines():
            final += Center.XCenter(lines) + "\n"
        return final
    
    def Arrow(icon: str = 'a', size: int = 2, number: int = 2, direction='right') -> str:
        spaces = ' ' * (size + 1)
        _arrow = ''
        structure = (size + 2, [size * 2, size * 2])
        count = 0
        if direction == 'right':
            for i in range(structure[1][0]):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count += 2
            for i in range(structure[1][0] + 1):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count -= 2
        elif direction == 'left':
            for i in range(structure[1][0]):
                count += 2
            for i in range(structure[1][0]):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count -= 2
            for i in range(structure[1][0] + 1):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count += 2
        return _arrow

Box = Banner
System.Init()