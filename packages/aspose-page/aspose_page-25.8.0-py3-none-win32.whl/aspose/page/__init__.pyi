"""This is a wrapper module for Aspose.Page .NET assembly"""

from aspose.page import drawing
from aspose.page import eps
from aspose.page import font
from aspose.page import plugins
from aspose.page import xps
import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable
from typing import Any

def get_pyinstaller_hook_dirs() -> Any:
  """Function required by PyInstaller. Returns paths to module 
  PyInstaller hooks. Not intended to be called explicitly."""
...

class BuildVersionInfo:
    '''This class provides information about current product build.'''
    
    def __init__(self):
        ...
    
    ASSEMBLY_VERSION: str
    
    PRODUCT: str
    
    FILE_VERSION: str
    
    ...

class Document:
    '''A superclass for all encapsulated documents.'''
    
    ...

class ExternalFontCache:
    '''Use this class to obtain font encapsulation in a form that is accepted by .'''
    
    def __init__(self):
        ...
    
    @staticmethod
    def fetch_dr_font(self, family_name: str, size_points: float, style: aspose.pydrawing.FontStyle) -> aspose.page.font.DrFont:
        '''Fetches :class:`aspose.page.font.DrFont` by font family name, size and style.
        
        :param family_name: Font family name.
        :param size_points: Font size in points (one point is 1/72 of inch).
        :param style: Font style.
        :returns: Returns DrFont'''
        ...
    
    @staticmethod
    def create_font_by_family_name(self, family_name: str, size: float, style: aspose.pydrawing.FontStyle) -> aspose.pydrawing.Font:
        '''Creates  by font family name, style and size.
        
        :param family_name: Font family name.
        :param size: Font size in points (one point is 1/72 of inch).
        :param style: Font style.
        :returns: Returns Font object.'''
        ...
    
    ...

class GraphicsFactory:
    '''This class statically creates common graphics objects.'''
    
    def __init__(self):
        ...
    
    @staticmethod
    def create_pen_by_color(self, color: aspose.pydrawing.Color) -> aspose.pydrawing.Pen:
        '''Creates a pen by color.
        
        :param color: The pen color.'''
        ...
    
    @staticmethod
    def create_pen_by_color_and_width(self, color: aspose.pydrawing.Color, width: float) -> aspose.pydrawing.Pen:
        ...
    
    @staticmethod
    def create_pen_by_brush(self, brush: aspose.pydrawing.Brush) -> aspose.pydrawing.Pen:
        '''Creates a pen by brush.
        
        :param brush: The pen brush.'''
        ...
    
    @staticmethod
    def create_pen_by_brush_and_width(self, brush: aspose.pydrawing.Brush, width: float) -> aspose.pydrawing.Pen:
        '''Creates a pen by brush and width.
        
        :param brush: The pen brush.
        :param width: The Pen width.'''
        ...
    
    @staticmethod
    def create_linear_gradient_brush_by_points(self, start: aspose.pydrawing.PointF, end: aspose.pydrawing.PointF, start_color: aspose.pydrawing.Color, end_color: aspose.pydrawing.Color) -> aspose.pydrawing.Drawing2D.LinearGradientBrush:
        '''Creates a linear gradient brush by points.
        
        :param start: The start point of the gradient.
        :param end: The end point of the gradient.
        :param start_color: The start color of the gradient.
        :param end_color: The end color of the gradient.'''
        ...
    
    @staticmethod
    def create_linear_gradient_brush_by_rect_and_mode(self, rect: aspose.pydrawing.RectangleF, start_color: aspose.pydrawing.Color, end_color: aspose.pydrawing.Color, mode: aspose.pydrawing.Drawing2D.LinearGradientMode) -> aspose.pydrawing.Drawing2D.LinearGradientBrush:
        '''Creates a linear gradient brush by rectangle and LinearGradientMode.
        
        :param rect: The bounding rectangle of the gradient.
        :param start_color: The start color of the gradient.
        :param end_color: The end color of the gradient.
        :param mode: The linear gradient mode.'''
        ...
    
    @staticmethod
    def create_linear_gradient_brush_by_rect_and_angle(self, rect: aspose.pydrawing.RectangleF, start_color: aspose.pydrawing.Color, end_color: aspose.pydrawing.Color, angle: float) -> aspose.pydrawing.Drawing2D.LinearGradientBrush:
        '''Creates a linear gradient brush by rectangle and an angle of rotation.
        
        :param rect: The bounding rectangle of the gradient.
        :param start_color: The start color of the gradient.
        :param end_color: The end color of the gradient.
        :param angle: The angle of the rotation of the gradient.'''
        ...
    
    @staticmethod
    def create_path_gradient_brush_by_points(self, points: list[aspose.pydrawing.PointF], wrap_mode: aspose.pydrawing.Drawing2D.WrapMode) -> aspose.pydrawing.Drawing2D.PathGradientBrush:
        '''Creates a path gradient brush by points and WrapMode.
        
        :param points: The points of the gradient.
        :param wrap_mode: The wrap mode of the gradient.'''
        ...
    
    @staticmethod
    def create_path_gradient_brush_by_path(self, path: aspose.pydrawing.Drawing2D.GraphicsPath) -> aspose.pydrawing.Drawing2D.PathGradientBrush:
        '''Creates a path gradient brush by an object of GraphicsPath and WrapMode.
        
        :param path: The path of the gradient.'''
        ...
    
    @staticmethod
    def create_hatch_brush_by_style_and_color(self, style: aspose.pydrawing.Drawing2D.HatchStyle, color: aspose.pydrawing.Color) -> aspose.pydrawing.Drawing2D.HatchBrush:
        '''Creates a hatch brush by hatch style and a color.
        
        :param style: The hatch style.
        :param color: The foreground color of the brush.'''
        ...
    
    @staticmethod
    def create_hatch_brush_by_style_and_colors(self, style: aspose.pydrawing.Drawing2D.HatchStyle, fore_color: aspose.pydrawing.Color, back_color: aspose.pydrawing.Color) -> aspose.pydrawing.Drawing2D.HatchBrush:
        '''Creates a hatch brush by hatch style and two colors.
        
        :param style: The hatch style.
        :param fore_color: The foreground color of the brush.
        :param back_color: The background color of the brush.'''
        ...
    
    ...

class IGlyph:
    '''This interface give access to main parameters of glyphs.'''
    
    @property
    def advance_width(self) -> float:
        '''Returns advanced width of the glyph.'''
        ...
    
    @property
    def char_code(self) -> str:
        '''Returns char code of the glyph.'''
        ...
    
    @property
    def left_side_bearing(self) -> float:
        '''Returns left side bearing of the glyph.'''
        ...
    
    ...

class License:
    '''Provides methods to license the component.'''
    
    def __init__(self):
        '''Initializes a new instance of this class.'''
        ...
    
    @overload
    def set_license(self, license_name: str) -> None:
        '''Licenses the component.
        
        Tries to find the license in the following locations:
        
        1. Explicit path.'''
        ...
    
    @overload
    def set_license(self, stream: io.BytesIO) -> None:
        '''Licenses the component.
        
        :param stream: A stream that contains the license.
        
        Use this method to load a license from a stream.'''
        ...
    
    @property
    def embedded(self) -> bool:
        '''License number was added as embedded resource.'''
        ...
    
    @embedded.setter
    def embedded(self, value: bool):
        ...
    
    ...

class Margins:
    '''This class encapsulates top, left, bottom and right margins.'''
    
    def __init__(self, top: int, left: int, bottom: int, right: int):
        '''Initializes an instance of Margin class.
        
        :param top: Top margin.
        :param left: Left margin.
        :param bottom: Bottom margin.
        :param right: Right margin.'''
        ...
    
    def set(self, top: int, left: int, bottom: int, right: int) -> None:
        '''Specifies margins values.
        
        :param top: Top margin.
        :param left: Left margin.
        :param bottom: Bottom margin.
        :param right: Right margin.'''
        ...
    
    @property
    def top(self) -> int:
        '''Top margin.'''
        ...
    
    @top.setter
    def top(self, value: int):
        ...
    
    @property
    def left(self) -> int:
        '''Left margin.'''
        ...
    
    @left.setter
    def left(self, value: int):
        ...
    
    @property
    def bottom(self) -> int:
        '''Bottom margin.'''
        ...
    
    @bottom.setter
    def bottom(self, value: int):
        ...
    
    @property
    def right(self) -> int:
        '''Right margin.'''
        ...
    
    @right.setter
    def right(self, value: int):
        ...
    
    ...

class Metered:
    '''Provides methods to set metered key.'''
    
    def __init__(self):
        '''Initializes a new instance of this class.'''
        ...
    
    def set_metered_key(self, public_key: str, private_key: str) -> None:
        '''Sets metered public and private key.
        If you purchase metered license, when start application, this API should be called, normally, this is enough.
        However, if always fail to upload consumption data and exceed 24 hours, the license will be set to evaluation status,
        to avoid such case, you should regularly check the license status, if it is evaluation status, call this API again.
        
        :param public_key: public key
        :param private_key: private key'''
        ...
    
    @staticmethod
    def get_consumption_quantity(self) -> decimal.Decimal:
        '''Gets consumption file size
        
        :returns: consumption quantity'''
        ...
    
    @staticmethod
    def get_consumption_credit(self) -> decimal.Decimal:
        '''Gets consumption credit
        
        :returns: consumption quantity'''
        ...
    
    ...

class SaveOptions:
    '''This class contains options necessary for managing conversion process.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`SaveOptions` class with default values
        for flags  (true) and :attr:`SaveOptions.debug` (false).'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool):
        '''Initializes a new instance of the :class:`SaveOptions` class with default value for flag :attr:`SaveOptions.debug` (false).
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size):
        '''Initializes a new instance of the :class:`SaveOptions` with
        with specified size of the page.
        
        :param size: The page size.'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool, size: aspose.page.drawing.Size):
        '''Initializes a new instance of the :class:`SaveOptions` class with default value for flag :attr:`SaveOptions.debug` (false) and with specified size of the page.
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.
        :param size: The page size.'''
        ...
    
    @property
    def supress_errors(self) -> bool:
        '''Specifies whether errors must be suppressed or not.
        If true suppressed errors are added to  list.
        If false the first error will terminate the program.'''
        ...
    
    @supress_errors.setter
    def supress_errors(self, value: bool):
        ...
    
    @property
    def size(self) -> aspose.page.drawing.Size:
        '''Gets/sets the size of the image.'''
        ...
    
    @size.setter
    def size(self, value: aspose.page.drawing.Size):
        ...
    
    @property
    def debug(self) -> bool:
        '''Specifies whether debug information must be printed to standard output stream or not.'''
        ...
    
    @debug.setter
    def debug(self, value: bool):
        ...
    
    @property
    def convert_fonts_to_ttf(self) -> bool:
        '''Specifies whether to save non-TrueType fonts to TTF.
        It significantly decreases the volume of the resulting document in PS to PDF conversion
        and increases the speed of conversion of PS files with a large quantity of text in non-TrueType fonts
        to any output format. However there is small vertical shift of text when converting PostSctipt file to image.'''
        ...
    
    @convert_fonts_to_ttf.setter
    def convert_fonts_to_ttf(self, value: bool):
        ...
    
    @property
    def additional_fonts_folders(self) -> list[str]:
        '''Specifies additional folders where converter should find fonts for input document.
        Default folder are standard fonts folder where OS finds fonts for internal needs.'''
        ...
    
    @additional_fonts_folders.setter
    def additional_fonts_folders(self, value: list[str]):
        ...
    
    @property
    def jpeg_quality_level(self) -> int:
        '''The Quality category specifies the level of compression for an image.
        Available values are 0 to 100.
        The lower the number specified, the higher the compression and therefore the lower the quality of the image.
        0 value results in lowest quality image, while 100 results in highest.'''
        ...
    
    @jpeg_quality_level.setter
    def jpeg_quality_level(self, value: int):
        ...
    
    ...

class UserProperties:
    '''Special property class which allows typed properties to be set and
    returned. It also allows the hookup of two default property objects
    to be searched if this property object does not contain the property.'''
    
    def __init__(self):
        '''Initializes an empty instance of UserProperties class.'''
        ...
    
    @overload
    def set_property(self, key: str, value: str) -> object:
        '''Sets string property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: list[str]) -> object:
        '''Sets string array property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: aspose.pydrawing.Color) -> object:
        '''Sets color property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: aspose.pydrawing.Rectangle) -> object:
        '''Sets rectangle property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: aspose.page.Margins) -> object:
        '''Sets margins property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: aspose.pydrawing.Size) -> object:
        '''Sets size property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: int) -> object:
        '''Sets integer property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: float) -> object:
        '''Sets double property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: float) -> object:
        '''Sets float property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: bool) -> object:
        '''Sets boolean property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def set_property(self, key: str, value: aspose.pydrawing.Drawing2D.Matrix) -> object:
        '''Sets matrix property value.
        
        :param key: The name of property.
        :param value: The value of property.
        :returns: A property.'''
        ...
    
    @overload
    def get_property(self, key: str) -> str:
        '''Gets string property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property(self, key: str, def_value: str) -> str:
        '''Gets string property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_string_array(self, key: str) -> list[str]:
        '''Gets string array property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_string_array(self, key: str, def_value: list[str]) -> list[str]:
        '''Gets string array property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_color(self, key: str) -> aspose.pydrawing.Color:
        '''Gets color property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_color(self, key: str, def_value: aspose.pydrawing.Color) -> aspose.pydrawing.Color:
        '''Gets color property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_rectangle(self, key: str) -> aspose.pydrawing.RectangleF:
        '''Gets rectangle property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_rectangle(self, key: str, def_value: aspose.pydrawing.RectangleF) -> aspose.pydrawing.RectangleF:
        '''Gets rectangle property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_margins(self, key: str) -> aspose.page.Margins:
        '''Gets margins property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_margins(self, key: str, def_value: aspose.page.Margins) -> aspose.page.Margins:
        '''Gets margins property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_size(self, key: str) -> aspose.pydrawing.Size:
        '''Gets size property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_size(self, key: str, def_value: aspose.pydrawing.Size) -> aspose.pydrawing.Size:
        '''Gets size property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_int(self, key: str) -> int:
        '''Gets integer property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_int(self, key: str, def_value: int) -> int:
        '''Gets integer property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_double(self, key: str) -> float:
        '''Gets double property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_double(self, key: str, def_value: float) -> float:
        '''Gets double property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_float(self, key: str) -> float:
        '''Gets float property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_float(self, key: str, def_value: float) -> float:
        '''Gets float property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_matrix(self, key: str) -> aspose.pydrawing.Drawing2D.Matrix:
        '''Gets matrix property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def get_property_matrix(self, key: str, def_value: aspose.pydrawing.Drawing2D.Matrix) -> aspose.pydrawing.Drawing2D.Matrix:
        '''Gets matrix property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    @overload
    def is_property(self, key: str) -> bool:
        '''Gets boolean property value.
        
        :param key: The name of property.
        :returns: Property value.'''
        ...
    
    @overload
    def is_property(self, key: str, def_value: bool) -> bool:
        '''Gets boolean property value. If requested property is absent, returns provided default value.
        
        :param key: The name of property.
        :param def_value: Default value of property.
        :returns: Property value.'''
        ...
    
    def property_names(self) -> None:
        '''Returns properties names.
        
        :returns: Enumerator of properties names.'''
        ...
    
    def print_properties(self) -> None:
        ...
    
    ...

class TextRenderingMode:
    '''This enum contains possible values for text rendering mode.'''
    
    FILL: int
    STROKE: int
    FILL_AND_STROKE: int
    NO: int

class Units:
    '''This enum contains possible values for size units.'''
    
    POINTS: int
    INCHES: int
    MILLIMETERS: int
    CENTIMETERS: int
    PERCENTS: int

