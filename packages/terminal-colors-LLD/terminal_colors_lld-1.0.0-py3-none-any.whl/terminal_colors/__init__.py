import typing as _typing
import types as _types
if _typing.TYPE_CHECKING:
    from _typeshed import SupportsWrite as _SupportsWrite
import re as _re

# __all__ = (
# "print_color", "print_colored_values", "input_color",
# "color_text", "remove_color", 
# "hex_to_rgb", "custom_color", "hex_color",
# "Foreground", "SystemColors", "Backgrounds", "ColoredExeption",
# "color_pattern", "color_format", "type_color_format",
# "register_color", "register_type_color", 
# "Coloring", "List", "Set", "Tuple", "Dict", 
# "color_text", "color_object", "print_color", 
# "print_colored_values", "input_color", 
# "remove_color", "side_fill_color", 
# )


def _check_valid_color_value(x:_typing.Any):
    return isinstance(x,int) and 256 > x

def hex_to_rgb(hex_code:str):
    """Turns a hex code into RGB"""
    return tuple(int(hex_code[i+1:i+3], 16) for i in (0, 2, 4))

def custom_color(r:int,g:int,b:int,background=False):
    """Make a color based on RGB"""
    assert all(map(_check_valid_color_value,[r,g,b])), f"r, g, b should all be numbers less than under 256 and not {type(r).__name__}"
    return f'\033[{48 if background else 38};2;{r};{g};{b}m'

def hex_color(hex_code:str):
    """Turns a hex code into a color"""
    assert hex_code.startswith("#")
    r,g,b = hex_to_rgb(hex_code)
    return f'\033[38;2;{r};{g};{b}m'

class Foreground:
    BLACK   = '\033[30m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    VIOLET  = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'
    GREY    = '\033[90m'
    RED2    = '\033[91m'
    GREEN2  = '\033[92m'
    YELLOW2 = '\033[93m'
    BLUE2   = '\033[94m'
    VIOLET2 = '\033[95m'
    CYAN2   = '\033[96m'
    WHITE2  = '\033[97m'

class SystemColors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    ITALIC    = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK     = '\033[5m'
    BLINK2    = '\033[6m'
    SELECTED  = '\033[7m'

color_tag_pattern = _re.compile(r"¤[A-Za-z0-9_]+¤|¤[A-Za-z0-9_]+\s|\s[A-Za-z0-9_]+¤",_re.IGNORECASE)
"""Color pattern via regex"""

end_tag_pattern = _re.compile(r"¤end |¤end¤| end¤")

color_pattern = _re.compile(r"\x1b\[[3-4]8;2;[0-9]+;[0-9]+;[0-9]+m|\x1b\[[0-9]+m", _re.IGNORECASE)

class Background:
    BLACKBG   = '\033[40m'
    REDBG     = '\033[41m'
    GREENBG   = '\033[42m'
    YELLOWBG  = '\033[43m'
    BLUEBG    = '\033[44m'
    VIOLETBG  = '\033[45m'
    CYANBG    = '\033[46m'
    WHITEBG   = '\033[47m'
    GREYBG    = '\033[100m'
    REDBG2    = '\033[101m'
    GREENBG2  = '\033[102m'
    YELLOWBG2 = '\033[103m'
    BLUEBG2   = '\033[104m'
    VIOLETBG2 = '\033[105m'
    CYANBG2   = '\033[106m'
    WHITEBG2  = '\033[107m'

color_format = {
    # System colors
    "header":    SystemColors.HEADER,
    "ok_b":      SystemColors.OKBLUE,
    "ok_c":      SystemColors.OKCYAN,
    "ok_g":      SystemColors.OKGREEN,
    "warning":   SystemColors.WARNING,
    "fail":      SystemColors.FAIL,
    "end":       SystemColors.ENDC,
    "bold":      SystemColors.BOLD,
    "underline": SystemColors.UNDERLINE,
    "italic":    SystemColors.ITALIC,
    "blink":     SystemColors.BLINK,
    "blink2":    SystemColors.BLINK2,
    "selected":  SystemColors.SELECTED,

    # Standard Colors
    "black":   Foreground.BLACK,
    "red":     Foreground.RED,
    "green":   Foreground.GREEN,
    "yellow":  Foreground.YELLOW,
    "blue":    Foreground.BLUE,
    "violet":  Foreground.VIOLET,
    "cyan":    Foreground.CYAN,
    "white":   Foreground.WHITE,
    "grey":    Foreground.GREY,
    "red2":    Foreground.RED2,
    "green2":  Foreground.GREEN2,
    "yellow2": Foreground.YELLOW2,
    "blue2":   Foreground.BLUE2,
    "violet2": Foreground.VIOLET2,
    "cyan2":   Foreground.CYAN2,
    "white2":  Foreground.WHITE2,

    # Backgrounds
    "bg_black":   Background.BLACKBG,
    "bg_white":   Background.WHITEBG,
    "bg_white2":  Background.WHITEBG2,
    "bg_red":     Background.REDBG,
    "bg_green":   Background.GREENBG,
    "bg_yellow":  Background.YELLOWBG,
    "bg_blue":    Background.BLUEBG,
    "bg_violet":  Background.VIOLETBG,
    "bg_cyan":    Background.CYANBG,
    "bg_grey":    Background.GREYBG,
    "bg_red2":    Background.REDBG2,
    "bg_green2":  Background.GREENBG2,
    "bg_yellow2": Background.YELLOWBG2,
    "bg_blue2":   Background.BLUEBG2,
    "bg_voilet2": Background.VIOLETBG2,
    "bg_cyan2":   Background.CYANBG2,
}

type_color_format = {
    int:hex_color("#B5CEA8"),
    float:hex_color("#B5CEA8"),
    str:hex_color("#CE9178"),
    bool:hex_color("#569CD6"),
    type:hex_color("#4EC9B0"),
    _types.FunctionType:hex_color("#D0DCAA"),
    _types.BuiltinFunctionType:hex_color("#D0DCAA"),
    _types.NoneType:hex_color("#569CD6"),
    _types.ModuleType:hex_color("#4EC9B0"),
}

module_color_format:dict[_types.ModuleType,_types.FunctionType] = {}

custom_colored_repr:dict[type,_types.FunctionType] = {}

def replace_default_repr_for_types():
    """
    This currently adds custom repr for bool, str and bytes
    """
    
    def custom_str_repr(string:str):
        patterns:list[str] = end_tag_pattern.findall(string)
        for pattern in patterns:
            string = string.replace(pattern,"¤end¤¤str¤")
        return color_text(f"¤str '{string}¤str ' end¤")

    register_custom_repr(bytes,lambda b: color_text(f"¤bool b str¤'{str(b).removeprefix("b'").removesuffix("'")}' end¤"))
    register_custom_repr(str, custom_str_repr)
    register_custom_repr(bool,lambda bool: hex_color("#0077ff" if bool else "#ff510c")+str(bool)+SystemColors.ENDC)


# Functions for registering things
def register_color(name:str,color:str):
    """Registers a color with the ¤ format
    Args:
        name (`str`): The name of the tag that corresponds wit the color`
        color (`str`): The color the tag represents.
    """
    if not isinstance(name,str):
        raise _TypeError(f"{color_object(name)} ¤warning is not a module")
    color_format[name] = color_text(color,add_end=False)

def register_type_color(type_:type,color:str):
    """Registers a color for the specified type
    Args:
        type (`str`): The type that should be colored
        color (`str`): The color of the type.
    """
    if type_ in _compatible_type_tuple:
        raise _TypeError(f"{color_object(type_)} ¤warning has a custom pre defined color and cannot be set")
    if type_.__class__ != type:
        raise _TypeError(f"{color_object(type_)} ¤warning is not a class")
    type_color_format[type_] = color_text(color,add_end=False)

def register_module_color(module:_types.ModuleType,color:str):
    """Registers a color for types from the specified module"""
    if not isinstance(module,_types.ModuleType):
        raise _TypeError(f"{color_object(module)} ¤warning is not a module")
    module_color_format[module.__name__] = color_text(color,add_end=False)

def register_custom_repr(_type:type,func:_types.FunctionType):
    if type(_type) != type:
        raise _TypeError(f"{_type} ¤warning is not a type")
    custom_colored_repr[_type] = func
    
        

class Coloring:
    def color_function(color:Foreground|Background|SystemColors):
        def decorator(func:_typing.Any) -> _typing.Callable[[str],None]:
            def colored(*values:str,**kwargs) -> None:
                print_color(*map(lambda text :color_text(f"{color}{text}"),values),**kwargs)
            return colored
        return decorator

    @color_function(Foreground.RED)
    def red():...
    @color_function(Foreground.BLUE)
    def blue():...
    @color_function(Foreground.GREEN)
    def green():...
    color_function(Foreground.YELLOW)
    def yellow():...
    @color_function(Foreground.VIOLET)
    def violet():...
    @color_function(Foreground.CYAN)
    def cyan():...
    @color_function(Foreground.GREY)
    def grey():...

_compatible_type_tuple = (list,dict,tuple,set)
_iterable_container_color_sequence = [hex_color("#FFD70A"),hex_color("#DA70D6"),hex_color("#179FFF")]

def _get_registered_colors():
    return color_format | {k.__name__:v for k,v in type_color_format.items()} | {f"iter{index+1}":color for index,color in enumerate(_iterable_container_color_sequence)}

def _get_step_color(number:int):
    return _iterable_container_color_sequence[number % len(_iterable_container_color_sequence)]

def _color_iterable(item:_typing.Any, step = -1):
    if isinstance(item,list):
        return List.__str__(item, step+1)
    if isinstance(item,dict):
        return Dict.__str__(item,step+1)
    if isinstance(item,set):
        return Set.__str__(item,step+1)
    if isinstance(item,tuple):
        return Tuple.__str__(item,step+1)

def _base__str__(self:_typing.Iterable,symbol:str, step=0):
    built = f"{_get_step_color(step)}{symbol[0]}{SystemColors.ENDC}"
    for index,item in enumerate(self):
        if index != 0:
            built += ", "
        item_class = item.__class__
        
        if hasattr(item,"__color_repr__"):
            built += item.__color_repr__(type_color_format.get(item_class))
            continue

        if isinstance(item, _compatible_type_tuple):
            built += _color_iterable(item,step)
            continue

        built += color_object(item)
    built += f"{_get_step_color(step)}{symbol[1]}{SystemColors.ENDC}"
    return built

class List(list):
    """A colored version of list. Can be used with regular print"""
    def __str__(self,step=0):
        return _base__str__(self,"[]",step)

class Set(set):
    """A colored version of set. Can be used with regular print"""
    def __str__(self,step=0):
        return _base__str__(self,"{}",step)

class Tuple(tuple):
    """A colored version of tuple. Can be used with regular print"""
    def __str__(self,step=0):
        return _base__str__(self,"()",step)
    
class Dict(dict):
    """A colored version of Dict. Can be used with regular print"""
    def __str__(self,step=0):
        built = f"{_get_step_color(step)}{"{"}{SystemColors.ENDC}"
        for index,(key,value) in enumerate(self.items()):
            if index != 0:
                built += ", "
            
            built += color_object(key) + ": "

            if isinstance(value, _compatible_type_tuple):
                built += _color_iterable(value,step)
                continue
            built += color_object(value)
            
        built += f"{_get_step_color(step)}{"}"}{SystemColors.ENDC}"
        return built


def color_text(text:str | object, add_end=True) -> str:
    """Colors strings based on the ¤ color format
    Args:
        text (`str` | `object`): The text that should be colored. If an object is passed it will be colored with `color_object()`
        add (`bool`): Decides if the color ends after coloring.
    Returns:
        str: A colored version of the string without the ¤ tags.
    """
    if not isinstance(text,str): return color_object(text)
    text = str(text)

    found:list[str] = color_tag_pattern.findall(text)
    if len(found) != 0:
        registered_colors = _get_registered_colors()
    
    for pattern_key in found:
        key = pattern_key.replace("¤","").replace(" ","")
        color = registered_colors.get(key.lower())
        if color:
            text = text.replace(pattern_key,color)

    if add_end:
        text += SystemColors.ENDC
    return text

def color_object(obj:object,color:str=None):
    """Returns a colored representation of the object"""
    
    if color == None:
        if type(obj) in custom_colored_repr:
            return custom_colored_repr[type(obj)](obj)

        if obj.__class__ != type and hasattr(obj,"__color_repr__"):
            return obj.__color_repr__(type_color_format.get(obj.__class__))
        
        # Colored iterables
        if isinstance(obj,list):
            return List.__str__(obj)
        if isinstance(obj,dict):
            return Dict.__str__(obj)
        if isinstance(obj,set):
            return Set.__str__(obj)
        if isinstance(obj,tuple):
            return Tuple.__str__(obj)
        
        # Registered colors
        if obj.__class__ in type_color_format:
            return color_object(obj,type_color_format[obj.__class__])
        if hasattr(obj,"__module__") and obj.__module__ in module_color_format:
            return color_object(obj,module_color_format[obj.__module__])
        
        return f"{SystemColors.ENDC}{repr(obj)}{SystemColors.ENDC}"
    return f"{color_text(color,add_end=False)}{repr(obj)}{SystemColors.ENDC}"

def highlight(text_or_object:str|object,highlight_text:str,highlight_color = Background.REDBG2):
    colored = color_text(text_or_object)
    return colored.replace(highlight_text,highlight_color+highlight_text+SystemColors.ENDC)

def print_color(*values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: "_SupportsWrite[str] | None" = None,
    flush: _typing.Literal[False] = False):
    """Print text based on the ¤ color format. Set color names with register_color()"""
    print(*map(color_text,values), sep=sep, end=end, file=file, flush=flush)

def print_colored_values(*values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: "_SupportsWrite[str] | None" = None,
    flush: _typing.Literal[False] = False):
    """Prints values with colors. Set colors for types with register_type_color()"""
    print(*map(color_object,values), sep=sep, end=end, file=file, flush=flush)

def input_color(prompt: object = "",input_color_type = SystemColors.WARNING):
    """Colors input prompt and input. Does not put color on returning text"""
    result = input(color_text(prompt) + input_color_type)
    print(SystemColors.ENDC,end="")
    return result

def remove_color(text:str):
    """Removes any REGISTERED color from text. Be aware that this is both the ¤ format and any colored strings that come from a REGISTERED COLOR. Any unregistered colors can leak through if you're not carefull."""
    found:list[str] = color_pattern.findall(text) + color_tag_pattern.findall(text)
    for color_or_tag in found:
        text = text.replace(color_or_tag,"")
    return text

def side_fill_color(text:str, fill_length:int, fill_color=SystemColors.ENDC, fill_symbol="-",equal_sides = True):
    """Centers text with color"""
    uncolored_text = remove_color(text)
    text_length = fill_length if (len(uncolored_text) / 2).is_integer() or not equal_sides else fill_length + 1
    spaced_text = f"{fill_color}{uncolored_text:{fill_symbol}^{text_length}}"
    colored_text = spaced_text.replace(uncolored_text, SystemColors.ENDC + text + SystemColors.ENDC + fill_color) + SystemColors.ENDC
    return color_text(colored_text)

class ColoredExeption(Exception):
    """Want to show a frustrating error with 𝓈𝓉𝓎𝓁𝑒? Well here you go. Uses the ¤ format"""
    def __init__(self, *args):
        super().__init__(*map(color_text,args))
class _KeyError(ColoredExeption):...
class _TypeError(ColoredExeption):...


def _generate_examples(text:str):
    """Saves 5 minutes. Took 50 minutes to create"""
    built_text = ""
    current_build = ""
    is_building = False
    for char in text:
        if char == "§":
            is_building = True
            continue
        if is_building:
            if char == "\n":
                evaluated = eval(current_build.replace("¤ \b", "¤"))
                length = len(evaluated) if isinstance(evaluated,str) else len(repr(evaluated))
                colored_evaluated = color_text(evaluated).replace("¤", "¤ \b")
                built_text += f"¤violet2 ¤bold >>> end¤ ¤bold {current_build} ¤cyan ->{"\n\t" if length > 40 else ""} end¤ {colored_evaluated}\n"
                current_build = ""
                is_building = False
                continue
            current_build += char
            continue
        if char == "\n":
            built_text += SystemColors.ENDC
        built_text += char
    return built_text

def color_help():
    """Call if you need help with the color format or how to use this module"""
    callables = [v for v in globals().values() if callable(v)] + [print,list,dict,tuple,set]
    callables.sort(key=lambda function_like:function_like.__name__,reverse=True)
    old_orange = color_format.get("orange")
    old_dict_items = type_color_format.get(type({}.items()))

    
    help_text = """
    This module uses the ¤bold ¤ end¤ format in ¤str strings end¤ to give color to text
    This format accepts ¤bold ¤COLOR_OF_CHOICE, ¤COLOR_OF_CHOICE¤ and COLOR_OF_CHOICE¤ end¤ as valid patterns for coloring
    To color text use color_text() or print_color()
    color_text() works with regular print
    Please format your strings ¤bold ¤underline before coloring them.
                
    To give a text color just put a ¤ infront or after a color
        >>> "¤ \bgreen hello there"
    
    You can also use the color ¤type classes end¤ like Foreground, Background and SystemColors to make a colored string
        >>> Foreground.RED+"hi there "+SystemColors.ENDC+"friend"
                
    You can also use ¤ \bend to end all colors and modifiers
        >>> "¤ \bgreen we want this part to be green ¤ \bbold this to be bold ¤ \bend but this part will be normal"

    The Coloring class can be used to fill text with one color check output
        >>> Coloring.red("this will be  \bprinted in red")

    
    You can also give text a background by using ¤bold bg_COLOR_OF_CHOICE
        >>> "¤ \bbg_red hello there"

    Colored text has more characters than a normal string
        >>> len("normal length is 19")
        >>> len("¤red normal length is 19 end¤")
    
    list, dict, tuple and set will color their values when used in print_color or print_colored_values
        >>> [1, 2, 3]
    You can also use their color equivilents List, Dict, Tuple and Set to have colored versions that work in regular print
        >>> Set((1,2,3,4,5))

    If you wish to use the color of a class you can use the name of the class instead of the color
        >>> "normal string untill i use int ¤ \bint 1 ¤ \bstr or str to copy the color"

    If you want to register your own colors you can use register_color to register a color
        >>> "¤ \borange this is an invalid orange string"
        >>> register_color("orange",hex_color("#FFA500"))
        >>> "¤ \borange this is now an orange string"
    
    You can do the same for types or your own classes
        >>> {"a":"b"}.items()
        >>> register_type_color(type({}.items()),hex_color("#FFC0CB"))
        >>> {"a":"b"}.items()
        
    """.replace(">>> ","§")
    
    for function_like in callables:
        if function_like.__name__ in help_text:
            help_text = help_text.replace(f" {function_like.__name__}",f" {type_color_format[function_like.__class__]}{function_like.__name__}¤end¤")
    print_color(_generate_examples(help_text))
    if old_orange:
        color_format["orange"] = old_orange
    else:
        del color_format["orange"]
    if old_dict_items:
        type_color_format[type({}.items())] = old_dict_items
    else:
        del type_color_format[type({}.items())]