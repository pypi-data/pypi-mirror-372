from aspose.page.drawing import drawing2d
from aspose.page.drawing import imaging
import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class Color:
    '''Represents an ARGB (alpha, red, green, blue) color.'''
    
    def __init__(self):
        ...
    
    @overload
    @staticmethod
    def from_argb(self, argb: int) -> aspose.page.drawing.Color:
        '''Creates a :class:`Color` structure from a 32-bit ARGB value.
        
        :returns: The :class:`Color` structure that this method creates.
        
        :param argb: A value specifying the 32-bit ARGB value.'''
        ...
    
    @overload
    @staticmethod
    def from_argb(self, alpha: int, red: int, green: int, blue: int) -> aspose.page.drawing.Color:
        '''Creates a :class:`Color` structure from the four ARGB component (alpha, red, green, and blue) values. Although this method allows a 32-bit value to be passed for each component, the value of each component is limited to 8 bits.
        
        :returns: The :class:`Color` that this method creates.
        
        :param alpha: The alpha component. Valid values are 0 through 255.
        :param red: The red component. Valid values are 0 through 255.
        :param green: The green component. Valid values are 0 through 255.
        :param blue: The blue component. Valid values are 0 through 255.
        :raises System.ArgumentException: ,,, or is less than 0 or greater than 255.'''
        ...
    
    @overload
    @staticmethod
    def from_argb(self, alpha: int, base_color: aspose.page.drawing.Color) -> aspose.page.drawing.Color:
        '''Creates a :class:`Color` structure from the specified :class:`Color` structure, but with the new specified alpha value. Although this method allows a 32-bit value to be passed for the alpha value, the value is limited to 8 bits.
        
        :returns: The :class:`Color` that this method creates.
        
        :param alpha: The alpha value for the new :class:`Color`. Valid values are 0 through 255.
        :param base_color: The :class:`Color` from which to create the new :class:`Color`.
        :raises System.ArgumentException: is less than 0 or greater than 255.'''
        ...
    
    @overload
    @staticmethod
    def from_argb(self, red: int, green: int, blue: int) -> aspose.page.drawing.Color:
        '''Creates a :class:`Color` structure from the specified 8-bit color values (red, green, and blue). The alpha value is implicitly 255 (fully opaque). Although this method allows a 32-bit value to be passed for each color component, the value of each component is limited to 8 bits.
        
        :returns: The :class:`Color` that this method creates.
        
        :param red: The red component value for the new :class:`Color`. Valid values are 0 through 255.
        :param green: The green component value for the new :class:`Color`. Valid values are 0 through 255.
        :param blue: The blue component value for the new :class:`Color`. Valid values are 0 through 255.
        :raises System.ArgumentException: ,, or is less than 0 or greater than 255.'''
        ...
    
    @staticmethod
    def from_name(self, name: str) -> aspose.page.drawing.Color:
        '''Creates a :class:`Color` structure from the specified name of a predefined color.
        
        :returns: The :class:`Color` that this method creates.
        
        :param name: A string that is the name of a predefined color. Valid names are the same as the names of the elements of the  enumeration.'''
        ...
    
    def get_brightness(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) brightness value for this :class:`Color` structure.
        
        :returns: The brightness of this :class:`Color`. The brightness ranges from 0.0 through 1.0, where 0.0 represents black and 1.0 represents white.'''
        ...
    
    def get_hue(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) hue value, in degrees, for this :class:`Color` structure.
        
        :returns: The hue, in degrees, of this :class:`Color`. The hue is measured in degrees, ranging from 0.0 through 360.0, in HSB color space.'''
        ...
    
    def get_saturation(self) -> float:
        '''Gets the hue-saturation-brightness (HSB) saturation value for this :class:`Color` structure.
        
        :returns: The saturation of this :class:`Color`. The saturation ranges from 0.0 through 1.0, where 0.0 is grayscale and 1.0 is the most saturated.'''
        ...
    
    def to_argb(self) -> int:
        '''Gets the 32-bit ARGB value of this :class:`Color` structure.
        
        :returns: The 32-bit ARGB value of this :class:`Color`.'''
        ...
    
    def clone(self) -> object:
        '''Clones this Aspose.Page.Drawing.Color.'''
        ...
    
    transparent: aspose.page.drawing.Color
    
    alice_blue: aspose.page.drawing.Color
    
    antique_white: aspose.page.drawing.Color
    
    aqua: aspose.page.drawing.Color
    
    aquamarine: aspose.page.drawing.Color
    
    azure: aspose.page.drawing.Color
    
    beige: aspose.page.drawing.Color
    
    bisque: aspose.page.drawing.Color
    
    black: aspose.page.drawing.Color
    
    blanched_almond: aspose.page.drawing.Color
    
    blue: aspose.page.drawing.Color
    
    blue_violet: aspose.page.drawing.Color
    
    brown: aspose.page.drawing.Color
    
    burly_wood: aspose.page.drawing.Color
    
    cadet_blue: aspose.page.drawing.Color
    
    chartreuse: aspose.page.drawing.Color
    
    chocolate: aspose.page.drawing.Color
    
    coral: aspose.page.drawing.Color
    
    cornflower_blue: aspose.page.drawing.Color
    
    cornsilk: aspose.page.drawing.Color
    
    crimson: aspose.page.drawing.Color
    
    cyan: aspose.page.drawing.Color
    
    dark_blue: aspose.page.drawing.Color
    
    dark_cyan: aspose.page.drawing.Color
    
    dark_goldenrod: aspose.page.drawing.Color
    
    dark_gray: aspose.page.drawing.Color
    
    dark_green: aspose.page.drawing.Color
    
    dark_khaki: aspose.page.drawing.Color
    
    dark_magenta: aspose.page.drawing.Color
    
    dark_olive_green: aspose.page.drawing.Color
    
    dark_orange: aspose.page.drawing.Color
    
    dark_orchid: aspose.page.drawing.Color
    
    dark_red: aspose.page.drawing.Color
    
    dark_salmon: aspose.page.drawing.Color
    
    dark_sea_green: aspose.page.drawing.Color
    
    dark_slate_blue: aspose.page.drawing.Color
    
    dark_slate_gray: aspose.page.drawing.Color
    
    dark_turquoise: aspose.page.drawing.Color
    
    dark_violet: aspose.page.drawing.Color
    
    deep_pink: aspose.page.drawing.Color
    
    deep_sky_blue: aspose.page.drawing.Color
    
    dim_gray: aspose.page.drawing.Color
    
    dodger_blue: aspose.page.drawing.Color
    
    firebrick: aspose.page.drawing.Color
    
    floral_white: aspose.page.drawing.Color
    
    forest_green: aspose.page.drawing.Color
    
    fuchsia: aspose.page.drawing.Color
    
    gainsboro: aspose.page.drawing.Color
    
    ghost_white: aspose.page.drawing.Color
    
    gold: aspose.page.drawing.Color
    
    goldenrod: aspose.page.drawing.Color
    
    gray: aspose.page.drawing.Color
    
    green: aspose.page.drawing.Color
    
    green_yellow: aspose.page.drawing.Color
    
    honeydew: aspose.page.drawing.Color
    
    hot_pink: aspose.page.drawing.Color
    
    indian_red: aspose.page.drawing.Color
    
    indigo: aspose.page.drawing.Color
    
    ivory: aspose.page.drawing.Color
    
    khaki: aspose.page.drawing.Color
    
    lavender: aspose.page.drawing.Color
    
    lavender_blush: aspose.page.drawing.Color
    
    lawn_green: aspose.page.drawing.Color
    
    lemon_chiffon: aspose.page.drawing.Color
    
    light_blue: aspose.page.drawing.Color
    
    light_coral: aspose.page.drawing.Color
    
    light_cyan: aspose.page.drawing.Color
    
    light_goldenrod_yellow: aspose.page.drawing.Color
    
    light_green: aspose.page.drawing.Color
    
    light_gray: aspose.page.drawing.Color
    
    light_pink: aspose.page.drawing.Color
    
    light_salmon: aspose.page.drawing.Color
    
    light_sea_green: aspose.page.drawing.Color
    
    light_sky_blue: aspose.page.drawing.Color
    
    light_slate_gray: aspose.page.drawing.Color
    
    light_steel_blue: aspose.page.drawing.Color
    
    light_yellow: aspose.page.drawing.Color
    
    lime: aspose.page.drawing.Color
    
    lime_green: aspose.page.drawing.Color
    
    linen: aspose.page.drawing.Color
    
    magenta: aspose.page.drawing.Color
    
    maroon: aspose.page.drawing.Color
    
    medium_aquamarine: aspose.page.drawing.Color
    
    medium_blue: aspose.page.drawing.Color
    
    medium_orchid: aspose.page.drawing.Color
    
    medium_purple: aspose.page.drawing.Color
    
    medium_sea_green: aspose.page.drawing.Color
    
    medium_slate_blue: aspose.page.drawing.Color
    
    medium_spring_green: aspose.page.drawing.Color
    
    medium_turquoise: aspose.page.drawing.Color
    
    medium_violet_red: aspose.page.drawing.Color
    
    midnight_blue: aspose.page.drawing.Color
    
    mint_cream: aspose.page.drawing.Color
    
    misty_rose: aspose.page.drawing.Color
    
    moccasin: aspose.page.drawing.Color
    
    navajo_white: aspose.page.drawing.Color
    
    navy: aspose.page.drawing.Color
    
    old_lace: aspose.page.drawing.Color
    
    olive: aspose.page.drawing.Color
    
    olive_drab: aspose.page.drawing.Color
    
    orange: aspose.page.drawing.Color
    
    orange_red: aspose.page.drawing.Color
    
    orchid: aspose.page.drawing.Color
    
    pale_goldenrod: aspose.page.drawing.Color
    
    pale_green: aspose.page.drawing.Color
    
    pale_turquoise: aspose.page.drawing.Color
    
    pale_violet_red: aspose.page.drawing.Color
    
    papaya_whip: aspose.page.drawing.Color
    
    peach_puff: aspose.page.drawing.Color
    
    peru: aspose.page.drawing.Color
    
    pink: aspose.page.drawing.Color
    
    plum: aspose.page.drawing.Color
    
    powder_blue: aspose.page.drawing.Color
    
    purple: aspose.page.drawing.Color
    
    red: aspose.page.drawing.Color
    
    rosy_brown: aspose.page.drawing.Color
    
    royal_blue: aspose.page.drawing.Color
    
    saddle_brown: aspose.page.drawing.Color
    
    salmon: aspose.page.drawing.Color
    
    sandy_brown: aspose.page.drawing.Color
    
    sea_green: aspose.page.drawing.Color
    
    sea_shell: aspose.page.drawing.Color
    
    sienna: aspose.page.drawing.Color
    
    silver: aspose.page.drawing.Color
    
    sky_blue: aspose.page.drawing.Color
    
    slate_blue: aspose.page.drawing.Color
    
    slate_gray: aspose.page.drawing.Color
    
    snow: aspose.page.drawing.Color
    
    spring_green: aspose.page.drawing.Color
    
    steel_blue: aspose.page.drawing.Color
    
    tan: aspose.page.drawing.Color
    
    teal: aspose.page.drawing.Color
    
    thistle: aspose.page.drawing.Color
    
    tomato: aspose.page.drawing.Color
    
    turquoise: aspose.page.drawing.Color
    
    violet: aspose.page.drawing.Color
    
    wheat: aspose.page.drawing.Color
    
    white: aspose.page.drawing.Color
    
    white_smoke: aspose.page.drawing.Color
    
    yellow: aspose.page.drawing.Color
    
    yellow_green: aspose.page.drawing.Color
    
    @property
    def r(self) -> int:
        '''Gets the red component value of this :class:`Color` structure.
        
        :returns: The red component value of this :class:`Color`.'''
        ...
    
    @property
    def g(self) -> int:
        '''Gets the green component value of this :class:`Color` structure.
        
        :returns: The green component value of this :class:`Color`.'''
        ...
    
    @property
    def b(self) -> int:
        '''Gets the blue component value of this :class:`Color` structure.
        
        :returns: The blue component value of this :class:`Color`.'''
        ...
    
    @property
    def a(self) -> int:
        '''Gets the alpha component value of this :class:`Color` structure.
        
        :returns: The alpha component value of this :class:`Color`.'''
        ...
    
    @property
    def is_empty(self) -> bool:
        '''Specifies whether this :class:`Color` structure is uninitialized.
        
        :returns: This property returns true if this color is uninitialized; otherwise, false.'''
        ...
    
    @property
    def is_named_color(self) -> bool:
        '''Gets a value indicating whether this :class:`Color` structure is a named color or a member of the  enumeration.
        
        :returns: true if this :class:`Color` was created by using either the :meth:`Color.from_name` method; otherwise, false.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of this :class:`Color`.
        
        :returns: The name of this :class:`Color`.'''
        ...
    
    EMPTY: aspose.page.drawing.Color
    
    ...

class PointF:
    '''Represents an ordered pair of floating-point x- and y-coordinates that defines a point in a two-dimensional plane.'''
    
    @overload
    def __init__(self, x: float, y: float):
        '''Initializes a new instance of the :class:`PointF` class with the specified coordinates.
        
        :param x: The horizontal position of the point.
        :param y: The vertical position of the point.'''
        ...
    
    @overload
    def __init__(self):
        ...
    
    def clone(self) -> object:
        '''Clones this Aspose.Page.Drawing.PointF.'''
        ...
    
    @property
    def is_empty(self) -> bool:
        '''Gets a value indicating whether this :class:`PointF` is empty.
        
        :returns: true if both :attr:`PointF.x` and :attr:`PointF.y` are 0; otherwise, false.'''
        ...
    
    @property
    def x(self) -> float:
        '''Gets or sets the x-coordinate of this :class:`PointF`.
        
        :returns: The x-coordinate of this :class:`PointF`.'''
        ...
    
    @x.setter
    def x(self, value: float):
        ...
    
    @property
    def y(self) -> float:
        '''Gets or sets the y-coordinate of this :class:`PointF`.
        
        :returns: The y-coordinate of this :class:`PointF`.'''
        ...
    
    @y.setter
    def y(self, value: float):
        ...
    
    EMPTY: aspose.page.drawing.PointF
    
    ...

class Size:
    '''Stores an ordered pair of integers, typically the width and height of a rectangle.'''
    
    @overload
    def __init__(self, width: int, height: int):
        '''Initializes a new instance of the :class:`Size` class from the specified dimensions.
        
        :param width: The width component of the new :class:`Size`.
        :param height: The height component of the new :class:`Size`.'''
        ...
    
    @overload
    def __init__(self):
        ...
    
    def clone(self) -> object:
        '''Clones this Aspose.Page.Drawing.Size.'''
        ...
    
    def equals(self, obj: object) -> bool:
        '''Tests to see whether the specified object is a :class:`Size` with the same dimensions as this :class:`Size`.
        
        :returns: true if  is a:class:`Size` and has the same width and height as this :class:`Size`; otherwise, false.
        
        :param obj: The  to test.'''
        ...
    
    def get_hash_code(self) -> int:
        '''Returns a hash code for this :class:`Size` structure.
        
        :returns: An integer value that specifies a hash value for this :class:`Size` structure.'''
        ...
    
    def to_string(self) -> str:
        '''Creates a human-readable string that represents this :class:`Size`.
        
        :returns: A string that represents this :class:`Size`.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets or sets the vertical component of this :class:`Size`.
        
        :returns: The vertical component of this :class:`Size`, typically measured in pixels.'''
        ...
    
    @height.setter
    def height(self, value: int):
        ...
    
    @property
    def width(self) -> int:
        '''Gets or sets the horizontal component of this :class:`Size`.
        
        :returns: The horizontal component of this :class:`Size`, typically measured in pixels.'''
        ...
    
    @width.setter
    def width(self, value: int):
        ...
    
    @property
    def is_empty(self) -> bool:
        '''Tests whether this :class:`Size` has width and height of 0.
        
        :returns: This property returns true when this :class:`Size` has both a width and height of 0; otherwise, false.'''
        ...
    
    EMPTY: aspose.page.drawing.Size
    
    ...

class SizeF:
    '''Stores an ordered pair of floating-point numbers, typically the width and height of a rectangle.'''
    
    @overload
    def __init__(self, size: aspose.page.drawing.SizeF):
        '''Initializes a new instance of the :class:`SizeF` structure from the specified existing :class:`SizeF` structure.
        
        :param size: The :class:`SizeF` structure from which to create the new :class:`SizeF` structure.'''
        ...
    
    @overload
    def __init__(self, width: float, height: float):
        '''Initializes a new instance of the :class:`SizeF` structure from the specified dimensions.
        
        :param width: The width component of the new :class:`SizeF` structure.
        :param height: The height component of the new :class:`SizeF` structure.'''
        ...
    
    @overload
    def __init__(self):
        ...
    
    def clone(self) -> object:
        '''Clones this Aspose.Page.Drawing.SizeF.'''
        ...
    
    @property
    def is_empty(self) -> bool:
        '''Gets a value that indicates whether this :class:`SizeF` structure has zero width and height.
        
        :returns: This property returns true when this :class:`SizeF` structure has both a width and height of zero; otherwise, false.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets or sets the horizontal component of this :class:`SizeF` structure.
        
        :returns: The horizontal component of this :class:`SizeF` structure, typically measured in pixels.'''
        ...
    
    @width.setter
    def width(self, value: float):
        ...
    
    @property
    def height(self) -> float:
        '''Gets or sets the vertical component of this :class:`SizeF` structure.
        
        :returns: The vertical component of this :class:`SizeF` structure, typically measured in pixels.'''
        ...
    
    @height.setter
    def height(self, value: float):
        ...
    
    EMPTY: aspose.page.drawing.SizeF
    
    ...

