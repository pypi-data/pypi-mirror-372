from aspose.page.eps import device
from aspose.page.eps import xmp
import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class FontConstants:
    '''This class defines a set of constants for saving fonts.'''
    
    embed_fonts_as_list: list[str]
    
    EMBED_FONTS: str
    
    EMBED_FONTS_AS: str
    
    EMBED_FONTS_TYPE1: str
    
    EMBED_FONTS_TYPE3: str
    
    EMBED_FONTS_TRUETYPE: str
    
    ...

class GradientBrush:
    '''This class is used for encapsulating LinearGradientBrush and PathGradientBrush with possibility to set wrap mode to clamp.
    Native gradient brushes always throw an exception when someone tries to set WrapMode property to WrapMode.Clamp.'''
    
    def __init__(self, native_brush: aspose.pydrawing.Brush):
        '''Creates new instance of GradientBrush.'''
        ...
    
    @property
    def wrap_mode(self) -> aspose.pydrawing.Drawing2D.WrapMode:
        '''Returns or specifies wrap mode for this gradient brush. It can be WrapMode.Clamp, that results in throwing exception in  native gradient brushes.'''
        ...
    
    @wrap_mode.setter
    def wrap_mode(self, value: aspose.pydrawing.Drawing2D.WrapMode):
        ...
    
    @property
    def native_brush(self) -> aspose.pydrawing.Brush:
        '''Returns native gradient brush.'''
        ...
    
    @property
    def bounds(self) -> aspose.pydrawing.RectangleF:
        '''Returns or specifies bounds for this gradient brushes.'''
        ...
    
    @bounds.setter
    def bounds(self, value: aspose.pydrawing.RectangleF):
        ...
    
    ...

class LoadOptions:
    '''Basic class for document loading options.'''
    
    ...

class PageConstants:
    '''This class defines a set of constants which describe a page.
    Convenience objects are provided for various margins, orientations,
    rescaling, and standard page sizes.'''
    
    @overload
    @staticmethod
    def get_size(self, size: str) -> aspose.page.drawing.Size:
        '''Calculates page size in "Portrait" page orientation'''
        ...
    
    @overload
    @staticmethod
    def get_size(self, size: str, orientation: str) -> aspose.page.drawing.Size:
        '''Calculates page size in given page orientation'''
        ...
    
    @overload
    @staticmethod
    def get_size(self, size: aspose.page.drawing.Size, orientation: str) -> aspose.page.drawing.Size:
        '''Calculates page size in given page orientation'''
        ...
    
    @overload
    @staticmethod
    def get_margins(self, margins_size: str) -> aspose.page.Margins:
        '''Gets page margins values'''
        ...
    
    @overload
    @staticmethod
    def get_margins(self, margins: aspose.page.Margins, orientation: str) -> aspose.page.Margins:
        '''Calculate page margins мфдгуы in specified orientation'''
        ...
    
    orientation_list: list[str]
    
    size_list: list[str]
    
    ORIENTATION: str
    
    VIEWING_ORIENTATION: str
    
    ORIENTATION_PORTRAIT: str
    
    ORIENTATION_LANDSCAPE: str
    
    ORIENTATION_BEST_FIT: str
    
    PAGE_SIZE: str
    
    SIZE_INTERNATIONAL: str
    
    SIZE_A3: str
    
    SIZE_A4: str
    
    SIZE_A5: str
    
    SIZE_A6: str
    
    SIZE_LETTER: str
    
    SIZE_LEGAL: str
    
    SIZE_EXECUTIVE: str
    
    SIZE_LEDGER: str
    
    PAGE_MARGINS: str
    
    MARGINS_ZERO: str
    
    MARGINS_SMALL: str
    
    MARGINS_MEDIUM: str
    
    MARGINS_LARGE: str
    
    FIT_TO_PAGE: str
    
    TRANSPARENT: str
    
    BACKGROUND: str
    
    BACKGROUND_COLOR: str
    
    ...

class PsConverterException(RuntimeError):
    '''This class contains information about an error that is
    thrown while PS file is converted to PDF document.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`PsConverterException` class.'''
        ...
    
    @overload
    def __init__(self, error_str: str):
        '''Initializes a new instance of the :class:`PsConverterException` class.
        
        :param error_str: The string that describes a reason of coversion error.'''
        ...
    
    ...

class PsDocument(aspose.page.Document):
    '''This class encapsulates PS/EPS documents.'''
    
    @overload
    def __init__(self):
        '''Initializes empty :class:`PsDocument`. This constructor is used only for additional operations that are not related to PostScript files,
        for example, converting fonts.'''
        ...
    
    @overload
    def __init__(self, out_ps_file_path: str, options: aspose.page.eps.device.PsSaveOptions):
        '''Initializes empty :class:`PsDocument` with initialized page.
        
        :param out_ps_file_path: The output PS/EPS file path.
        :param options: A set of parameters controlling saving of PostScript file.'''
        ...
    
    @overload
    def __init__(self, out_ps_stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions):
        '''Initializes empty :class:`PsDocument` with initialized page.
        
        :param out_ps_stream: Stream where to save PS/EPS file.
        :param options: A set of parameters controlling saving of PostScript file.'''
        ...
    
    @overload
    def __init__(self, out_ps_file_path: str, options: aspose.page.eps.device.PsSaveOptions, multipaged: bool):
        '''Initializes empty :class:`PsDocument`.
        
        :param out_ps_file_path: The output PS/EPS file path.
        :param options: A set of parameters controlling saving of PostScript file.
        :param multipaged: If false page will not be initialized. In this case page initialization should be performed via explicit "openPage(width, height) call.'''
        ...
    
    @overload
    def __init__(self, out_ps_stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions, multipaged: bool):
        '''Initializes empty :class:`PsDocument`.
        
        :param out_ps_stream: Stream where to save PS/EPS file.
        :param options: A set of parameters controlling saving of PostScript file.
        :param multipaged: If false page will not be initialized. In this case page initialization should be performed via explicit "openPage(width, height) call.'''
        ...
    
    @overload
    def __init__(self, out_ps_file_path: str, options: aspose.page.eps.device.PsSaveOptions, number_of_pages: int):
        '''Initializes empty :class:`PsDocument` when the number of Postscript document pages is known in advance.
        
        :param out_ps_file_path: The output PS/EPS file path.
        :param options: A set of parameters controlling saving of PostScript file.
        :param number_of_pages: The number of pages in the PostScript document.'''
        ...
    
    @overload
    def __init__(self, out_ps_stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions, number_of_pages: int):
        '''Initializes empty :class:`PsDocument` when the number of Postscript document pages is known in advance.
        
        :param out_ps_stream: Stream where to save PS/EPS file.
        :param options: A set of parameters controlling saving of PostScript file.
        :param number_of_pages: The number of pages in the PostScript document.'''
        ...
    
    @overload
    def __init__(self, ps_file_path: str):
        '''Initializes :class:`PsDocument` with an input PS/EPS file.
        
        :param ps_file_path: PS/EPS file path.'''
        ...
    
    @overload
    def __init__(self, in_ps_stream: io.BytesIO):
        '''Initializes :class:`PsDocument` with a stream of PS/EPS file.
        
        :param in_ps_stream: Input stream of PS/EPS file.'''
        ...
    
    @overload
    def save_as_pdf(self, out_pdf_file_path: str, options: aspose.page.eps.device.PdfSaveOptions) -> None:
        '''Saves PS/EPS file to PDF file.
        
        :param out_pdf_file_path: An output PDF file path.
        :param options: Contains flags that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    def save_as_pdf(self, pdf_stream: io.BytesIO, options: aspose.page.eps.device.PdfSaveOptions) -> None:
        '''Saves PS/EPS file to PDF stream.
        
        :param pdf_stream: An output PDF stream.
        :param options: Contains flags that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    def save_as_image(self, options: aspose.page.eps.device.ImageSaveOptions) -> None:
        '''Saves PS/EPS file to image file. The output directory and the file name will be the same as from input PS file.
        The file extension will correspond to image format in "option" param.'''
        ...
    
    @overload
    def save_as_image(self, options: aspose.page.eps.device.ImageSaveOptions, out_dir: str, file_name_template: str) -> None:
        ...
    
    @overload
    def save(self, eps_stream: io.BytesIO) -> None:
        '''Saves given :class:`PsDocument` as EPS file. This method is used only after updating XMP metadata.
        It saves initial EPS file with updated existing metadata or new one created while calling GetMetadata method.
        In the last case all necessary PostScript code and EPS comments are added.
        
        :param eps_stream: Stream of output EPS file.'''
        ...
    
    @overload
    def save(self) -> None:
        '''Saves given :class:`PsDocument` as EPS file. This method is used only when PsDocument was created from scratch.'''
        ...
    
    @overload
    def resize_eps(self, out_eps_file_path: str, new_size_in_units: aspose.pydrawing.SizeF, units: aspose.page.Units) -> None:
        '''Resizes given :class:`PsDocument` as EPS file. This method is used only after extracting EPS size.
        It saves initial EPS file with updated existing %%BoundingBox or new one will be created. Page transformation matrix also will be set.
        
        :param out_eps_file_path: The output EPS file path.
        :param new_size_in_units: New size of EPS image in assigned units.
        :param units: The units of the new size. Can be points, inches, millimeters, centimeters and percents of initial size.'''
        ...
    
    @overload
    def resize_eps(self, eps_stream: io.BytesIO, new_size_in_units: aspose.pydrawing.SizeF, units: aspose.page.Units) -> None:
        '''Resizes given :class:`PsDocument` as EPS file. This method is used only after extracting EPS size.
        It saves initial EPS file with updated existing %%BoundingBox or new one will be created. Page transformation matrix also will be set.
        
        :param eps_stream: Stream of output EPS file.
        :param new_size_in_units: New size of EPS image in assigned units.
        :param units: The units of the new size. Can be points, inches, millimeters, centimeters and percents of initial size.'''
        ...
    
    @overload
    def crop_eps(self, out_eps_file_path: str, crop_box: list[float]) -> None:
        '''Crops given :class:`PsDocument` as EPS file.
        It saves initial EPS file with updated existing %%BoundingBox or new one will be created.
        
        :param out_eps_file_path: The output EPS file path.
        :param crop_box: The crop box (x0, y0, x, y).'''
        ...
    
    @overload
    def crop_eps(self, eps_stream: io.BytesIO, crop_box: list[float]) -> None:
        '''Crops given :class:`PsDocument` as EPS file.
        It saves initial EPS file with updated existing %%BoundingBox or new one will be created.
        
        :param eps_stream: Stream of output EPS file.
        :param crop_box: The crop box (x0, y0, x, y).'''
        ...
    
    @overload
    @staticmethod
    def save_image_as_eps(self, image_stream: io.BytesIO, eps_stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves PNG/JPEG/TIFF/BMP/GIF/EMF image from input stream to EPS output stream.
        
        :param image_stream: Image input stream.
        :param eps_stream: EPS output stream.
        :param options: Contains parameters that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    @staticmethod
    def save_image_as_eps(self, image_file_path: str, eps_file_path: str, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves PNG/JPEG/TIFF/BMP/GIF/EMF image from file to EPS file.
        
        :param image_file_path: The image file path.
        :param eps_file_path: EPS file path.
        :param options: Contains parameters that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    @staticmethod
    def save_image_as_eps(self, image: aspose.pydrawing.Bitmap, eps_file_path: str, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves Bitmap object to EPS file.
        
        :param image: The image.
        :param eps_file_path: EPS file path.
        :param options: Contains parameters that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    @staticmethod
    def save_image_as_eps(self, image: aspose.pydrawing.Bitmap, eps_stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves Bitmap object to EPS output stream.
        
        :param image: The image.
        :param eps_stream: EPS output stream.
        :param options: Contains parameters that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    def convert_type_3_font_to_ttf(self, type_3_font_file_path: str, output_dir: str) -> None:
        '''Converts Type 3 font to TrueType.
        The name of the converted TTF font will be the same as input Type 3 font file with ".ttf" extension.
        TTF file will be saved to assigned output directory.
        
        :param type_3_font_file_path: The Type 3 font file path.
        :param output_dir: Output dir where to save resulting TrueType font.'''
        ...
    
    @overload
    def convert_type_3_font_to_ttf(self, type_3_font_file_path: str, output_stream: io.BytesIO) -> None:
        '''Converts Type 3 font to TrueType stream.
        
        :param type_3_font_file_path: The Type 3 font file path.
        :param output_stream: Output stream where to save resulting TrueType font.'''
        ...
    
    @overload
    def open_page(self, width: float, height: float) -> None:
        '''Creates new page and make it current one.
        
        :param width: The width of new page.
        :param height: The height of new page.'''
        ...
    
    @overload
    def open_page(self, page_name: str) -> None:
        '''Creates new page with document's size and make it current one.
        
        :param page_name: The name of new page. If it is null the name o the page will be an order number of the page.'''
        ...
    
    @overload
    def rotate(self, angle_radians: float) -> None:
        '''Adds rotation counterclockwise about the origin to current graphics state (rotate current matrix).
        
        :param angle_radians: The angle of rotation in radians.'''
        ...
    
    @overload
    def rotate(self, angle_degrees: int) -> None:
        '''Adds rotation counterclockwise about the origin to current graphics state (rotate current matrix).
        
        :param angle_degrees: The angle of rotation in degrees.'''
        ...
    
    @overload
    def fill_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def fill_text(self, text: str, advances: list[float], font: aspose.pydrawing.Font, x: float, y: float) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param font: The font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def fill_text(self, text: str, dr_font: aspose.page.font.DrFont, x: float, y: float) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def fill_text(self, text: str, advances: list[float], dr_font: aspose.page.font.DrFont, x: float, y: float) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def fill_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float, fill: aspose.pydrawing.Brush) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill: The fill used for painting glyphs.'''
        ...
    
    @overload
    def fill_text(self, text: str, advances: list[float], font: aspose.pydrawing.Font, x: float, y: float, fill: aspose.pydrawing.Brush) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill: The fill used for painting glyphs.'''
        ...
    
    @overload
    def fill_text(self, text: str, dr_font: aspose.page.font.DrFont, x: float, y: float, fill: aspose.pydrawing.Brush) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill: The fill used for painting glyphs.'''
        ...
    
    @overload
    def fill_text(self, text: str, advances: list[float], dr_font: aspose.page.font.DrFont, x: float, y: float, fill: aspose.pydrawing.Brush) -> None:
        '''Adds a text string by filling interrior of glyphs.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill: The fill used for painting glyphs.'''
        ...
    
    @overload
    def outline_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def outline_text(self, text: str, advances: list[float], font: aspose.pydrawing.Font, x: float, y: float) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param font: The font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def outline_text(self, text: str, dr_font: aspose.page.font.DrFont, x: float, y: float) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def outline_text(self, text: str, advances: list[float], dr_font: aspose.page.font.DrFont, x: float, y: float) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.'''
        ...
    
    @overload
    def outline_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param stroke: The stroke used for drawing glyphs outlines.'''
        ...
    
    @overload
    def outline_text(self, text: str, advances: list[float], font: aspose.pydrawing.Font, x: float, y: float, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param stroke: The stroke used for drawing glyphs outlines.'''
        ...
    
    @overload
    def outline_text(self, text: str, dr_font: aspose.page.font.DrFont, x: float, y: float, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param stroke: The stroke used for drawing glyphs outlines.'''
        ...
    
    @overload
    def outline_text(self, text: str, advances: list[float], dr_font: aspose.page.font.DrFont, x: float, y: float, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param stroke: The stroke used for drawing glyphs outlines.'''
        ...
    
    @overload
    def fill_and_stroke_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float, fill_paint: aspose.pydrawing.Brush, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by filling interrior of glyphs and drawing glyphs contours.
        
        :param text: The text to add.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill_paint: The fill used for painting glyphs interior.
        :param stroke: The stroke used for drawing glyphs contours.'''
        ...
    
    @overload
    def fill_and_stroke_text(self, text: str, advances: list[float], font: aspose.pydrawing.Font, x: float, y: float, fill_paint: aspose.pydrawing.Brush, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by filling interrior of glyphs and drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param font: System font that will be used to draw text.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill_paint: The fill used for painting glyphs interior.
        :param stroke: The stroke used for drawing glyphs contours.'''
        ...
    
    @overload
    def fill_and_stroke_text(self, text: str, dr_font: aspose.page.font.DrFont, x: float, y: float, fill_paint: aspose.pydrawing.Brush, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by filling interrior of glyphs and drawing glyphs contours.
        
        :param text: The text to add.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill_paint: The fill used for painting glyphs interior.
        :param stroke: The stroke used for drawing glyphs contours.'''
        ...
    
    @overload
    def fill_and_stroke_text(self, text: str, advances: list[float], dr_font: aspose.page.font.DrFont, x: float, y: float, fill_paint: aspose.pydrawing.Brush, stroke: aspose.pydrawing.Pen) -> None:
        '''Adds a text string by filling interrior of glyphs and drawing glyphs contours.
        
        :param text: The text to add.
        :param advances: An array of glyphs width. It's length must comply with the number of glyphs in the string.
        :param dr_font: that will be used to draw text. It can be used with custom font that is located in custom folder.
        :param x: X coordinate for text origin.
        :param y: Y coordinate for text origin.
        :param fill_paint: The fill used for painting glyphs interior.
        :param stroke: The stroke used for drawing glyphs contours.'''
        ...
    
    @overload
    def draw_polyline(self, x_points: list[int], y_points: list[int], n_points: int) -> None:
        '''Draws a polyline.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def draw_polyline(self, x_points: list[float], y_points: list[float], n_points: int) -> None:
        '''Draws a polyline.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def draw_polygon(self, x_points: list[int], y_points: list[int], n_points: int) -> None:
        '''Draws a polygon.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def draw_polygon(self, x_points: list[float], y_points: list[float], n_points: int) -> None:
        '''Draws a poligone.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def fill_polygon(self, x_points: list[int], y_points: list[int], n_points: int) -> None:
        '''Fills a poligone.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def fill_polygon(self, x_points: list[float], y_points: list[float], n_points: int) -> None:
        '''Fills a poligone.
        
        :param x_points: X coordinates of points.
        :param y_points: Y coordinate of points.
        :param n_points: The number of points.'''
        ...
    
    @overload
    def draw_image(self, image: aspose.pydrawing.Bitmap) -> None:
        '''Draw image.
        
        :param image: The image to draw.'''
        ...
    
    @overload
    def draw_image(self, image: aspose.pydrawing.Bitmap, transform: aspose.pydrawing.Drawing2D.Matrix, bkg: aspose.pydrawing.Color) -> None:
        '''Draw transformed image with background.
        
        :param image: The image to draw.
        :param transform: The matrix to transform image.
        :param bkg: Background for image.'''
        ...
    
    @overload
    def merge_to_pdf(self, out_pdf_file_path: str, files_for_merge: list[str], options: aspose.page.SaveOptions) -> None:
        '''Merges PS/EPS files to a device.
        
        :param files_for_merge: PS/EPS files for merging with this file to an output device.
        :param out_pdf_file_path: An output PDF file path.
        :param options: Contains flags that specify output of errors thrown during conversion.'''
        ...
    
    @overload
    def merge_to_pdf(self, pdf_stream: io.BytesIO, files_for_merge: list[str], options: aspose.page.SaveOptions) -> None:
        '''Merges PS/EPS files to a device.
        
        :param files_for_merge: PS/EPS files for merging with this file to an output device.
        :param pdf_stream: An output PDF stream.
        :param options: Contains flags that specify output of errors thrown during conversion.'''
        ...
    
    def save_as_images_bytes(self, options: aspose.page.eps.device.ImageSaveOptions) -> list[bytes]:
        '''Saves PS/EPS file to images bytes arrays.
        
        :param options: Contains necessary parameters for saving image and flags that specify output of errors thrown during conversion.
        :returns: Images bytes. One byte array for one page.'''
        ...
    
    def get_xmp_metadata(self) -> aspose.page.eps.xmp.XmpMetadata:
        '''Reads PS/EPS file and extracts XmpMetdata if it already exists or add new one if it doesn't exist.
        
        :returns: Existing or new instance of XMP metadata.'''
        ...
    
    def extract_text(self, options: aspose.page.SaveOptions, start_page: int, end_page: int) -> str:
        '''Extract text from PS file. The text can be extracted only if it is written with Type 42 (TrueType) font or Type 0 font with Type 42 fonts in its Vector Map.
        
        :param options: The save options.
        :param start_page: The page from which to begin to extract text. This parameter is usefull for multi-paged documents.
        :param end_page: The page till which to finish to extract text. This parameter is usefull for multi-paged documents.
        :returns: The extracted text.'''
        ...
    
    def extract_eps_size(self) -> aspose.pydrawing.Size:
        '''Reads EPS file and extracts a size of EPS image from %%BoundingBox comment or default page size (595, 842) if it doesn't exist.
        
        :returns: The size of the EPS image.'''
        ...
    
    def extract_eps_bounding_box(self) -> list[int]:
        '''Reads EPS file and extracts bounding box of EPS image from %%BoundingBox comment or bounds for default page size (0, 0, 595, 842) if it doesn't exist.
        
        :returns: The bounding box of the EPS image.'''
        ...
    
    def convert_type_1_font_to_ttf(self, type_1_font_file_path: str, output_dir: str) -> None:
        '''Converts Type 1 font to TrueType.
        The name of the converted TTF font will be the same as input Type 1 font with ".ttf" extension.
        TTF file will be saved to assigned output directory.
        
        :param type_1_font_file_path: The Type 1 font file path.
        :param output_dir: Output dir where to save resulting TrueType font.'''
        ...
    
    def set_page_size(self, width: float, height: float) -> None:
        '''Sets page size. To create pages with different sizes in one document use
        method just after this method.
        
        :param width: The width of page in resulting PostScript file.
        :param height: The height of page in resulting PostScript file.'''
        ...
    
    def close_page(self) -> None:
        '''Complete current page.'''
        ...
    
    def write_graphics_save(self) -> None:
        '''Writes saving of the current graphics state (See PostScript specification on operator "gsave").'''
        ...
    
    def write_graphics_restore(self) -> None:
        '''Writes restoring of the current graphics state (See PostScript specification on operator "grestore").'''
        ...
    
    def set_transform(self, matrix: aspose.pydrawing.Drawing2D.Matrix) -> None:
        '''Set current transformation to this one.
        
        :param matrix: The transformation.'''
        ...
    
    def transform(self, matrix: aspose.pydrawing.Drawing2D.Matrix) -> None:
        '''Adds transformation to current graphics state (concatenates this matrix with current one).
        
        :param matrix: The transformation.'''
        ...
    
    def translate(self, x: float, y: float) -> None:
        '''Adds translation to current graphics state (translates current matrix).
        
        :param x: The translation in X direction.
        :param y: The translation in Y direction.'''
        ...
    
    def scale(self, x_scale: float, y_scale: float) -> None:
        '''Adds scale to current graphics state (scale current matrix).
        
        :param x_scale: The scale in X axis.
        :param y_scale: The translation in Y axis.'''
        ...
    
    def shear(self, shx: float, shy: float) -> None:
        '''Adds shear transformation to current graphics state (shear current matrix).
        
        :param shx: The shear in X axis.
        :param shy: The shear in Y axis.'''
        ...
    
    def clip(self, s: aspose.pydrawing.Drawing2D.GraphicsPath) -> None:
        '''Adds clip to current graphics state.
        
        :param s: The clipping path.'''
        ...
    
    def clip_text(self, text: str, font: aspose.pydrawing.Font, x: float, y: float) -> None:
        '''Adds clip from an outline of given text in given font.
        
        :param text: The text.
        :param font: The font.
        :param x: An X coordinate of the text position.
        :param y: An Y coordinate of the text position.'''
        ...
    
    def clip_rectangle(self, rect: aspose.pydrawing.RectangleF) -> None:
        '''Adds clipping rectangle to current graphics state.
        
        :param rect: The clipping rectangle.'''
        ...
    
    def clip_and_new_path(self, s: aspose.pydrawing.Drawing2D.GraphicsPath) -> None:
        '''Adds clip to current graphics state and than writes "newpath" operator. It is necessary to do to escape
        of confluence of this clipping path and some subsequent pathes such as glyphs outlined with "charpath" operator.
        
        :param s: The clipping path.'''
        ...
    
    def set_paint(self, paint: aspose.pydrawing.Brush) -> None:
        '''Sets paint in current graphics state.
        
        :param paint: The paint. It can be any subclass of  class existed in .NET platform.'''
        ...
    
    def get_paint(self) -> aspose.pydrawing.Brush:
        '''Gets paint of current graphics state.'''
        ...
    
    def set_stroke(self, stroke: aspose.pydrawing.Pen) -> None:
        '''Sets stroke in current graphics state.
        
        :param stroke: The stroke.'''
        ...
    
    def get_stroke(self) -> aspose.pydrawing.Pen:
        '''Gets stroke of current graphics state.'''
        ...
    
    def fill(self, shape: aspose.pydrawing.Drawing2D.GraphicsPath) -> None:
        '''Fill an arbitrary path.
        
        :param shape: The path to fill.'''
        ...
    
    def draw(self, shape: aspose.pydrawing.Drawing2D.GraphicsPath) -> None:
        '''Draw an arbitrary path.
        
        :param shape: The path to draw.'''
        ...
    
    def draw_arc(self, x: float, y: float, width: float, height: float, start_angle: float, arc_angle: float) -> None:
        '''Draws an arc.
        
        :param x: X coordinate of center of the arc.
        :param y: Y coordinate of center of the arc.
        :param width: A width of circumscribed rectangle.
        :param height: A height of circumscribed rectangle.
        :param start_angle: A start angle of the arc.
        :param arc_angle: An angle of the arc.'''
        ...
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float) -> None:
        '''Draws a line segment.
        
        :param x1: X coordinate of the beginning of segment.
        :param y1: Y coordinate of the beginning of segment.
        :param x2: X coordinate of the end of segment.
        :param y2: Y coordinate of the end of segment.'''
        ...
    
    def draw_oval(self, x: float, y: float, width: float, height: float) -> None:
        '''Draws an oval.
        
        :param x: X coordinate of center of the oval.
        :param y: Y coordinate of center of the oval.
        :param width: A width of circumscribed rectangle.
        :param height: A height of circumscribed rectangle.'''
        ...
    
    def draw_rect(self, x: float, y: float, width: float, height: float) -> None:
        '''Draws a rectangle.
        
        :param x: X coordinate of upper left corner of the rectangle.
        :param y: Y coordinate of upper left corner of the rectangle.
        :param width: A width of the rectangle.
        :param height: A height of the rectangle.'''
        ...
    
    def draw_round_rect(self, x: float, y: float, width: float, height: float, arc_width: float, arc_height: float) -> None:
        '''Draws a round rectangle.
        
        :param x: X coordinate of upper left corner of the rectangle.
        :param y: Y coordinate of upper left corner of the rectangle.
        :param width: A width of the rectangle.
        :param height: A height of the rectangle.
        :param arc_width: A width of circumscribed rectangle of the arc that rounds an angle of the rectangle.
        :param arc_height: A height of circumscribed rectangle of the arc that rounds an angle of the rectangle.'''
        ...
    
    def fill_arc(self, x: float, y: float, width: float, height: float, start_angle: float, arc_angle: float) -> None:
        '''Fills an arc.
        
        :param x: X coordinate of center of the arc.
        :param y: Y coordinate of center of the arc.
        :param width: A width of circumscribed rectangle.
        :param height: A height of circumscribed rectangle.
        :param start_angle: A start angle of the arc.
        :param arc_angle: An angle of the arc.'''
        ...
    
    def fill_oval(self, x: float, y: float, width: float, height: float) -> None:
        '''Fills an oval.
        
        :param x: X coordinate of center of the oval.
        :param y: Y coordinate of center of the oval.
        :param width: A width of circumscribed rectangle.
        :param height: A height of circumscribed rectangle.'''
        ...
    
    def fill_rect(self, x: float, y: float, width: float, height: float) -> None:
        '''Fills a rectangle.
        
        :param x: X coordinate of upper left corner of the rectangle.
        :param y: Y coordinate of upper left corner of the rectangle.
        :param width: A width of the rectangle.
        :param height: A height of the rectangle.'''
        ...
    
    def fill_round_rect(self, x: float, y: float, width: float, height: float, arc_width: float, arc_height: float) -> None:
        '''Fills a round rectangle.
        
        :param x: X coordinate of upper left corner of the rectangle.
        :param y: Y coordinate of upper left corner of the rectangle.
        :param width: A width of the rectangle.
        :param height: A height of the rectangle.
        :param arc_width: A width of circumscribed rectangle of the arc that rounds an angle of the rectangle.
        :param arc_height: A height of circumscribed rectangle of the arc that rounds an angle of the rectangle.'''
        ...
    
    def draw_transparent_image(self, image: aspose.pydrawing.Bitmap, transform: aspose.pydrawing.Drawing2D.Matrix, transparency_threshold: int) -> None:
        '''Draw transformed transparent image. If image doesn't have Alpha channel it will be drawn as opaque image
        
        :param image: The image to draw.
        :param transform: The matrix to transform image.
        :param transparency_threshold: A threshold that defines from which value of transparency pixel will be interpreted as fully transparent. All values below this threshold will be interpreted as fully opaque.'''
        ...
    
    def draw_explicit_image_mask(self, image_24bpp: aspose.pydrawing.Bitmap, alpha_mask_1bpp: aspose.pydrawing.Bitmap, transform: aspose.pydrawing.Drawing2D.Matrix) -> None:
        '''Draw masked image.
        
        :param image_24bpp: The image to draw. Must be in 24bpp RGB image format
        :param alpha_mask_1bpp: The image mask. Must be in 1bpp image format.
        :param transform: The matrix to transform image.'''
        ...
    
    @property
    def input_stream(self) -> io.BytesIO:
        '''Gets or sets an input stream of PS/EPS file.'''
        ...
    
    @input_stream.setter
    def input_stream(self, value: io.BytesIO):
        ...
    
    @property
    def number_of_pages(self) -> int:
        '''Returns the number of pages in resulting PDF document.'''
        ...
    
    ...

class PsDocumentException(RuntimeError):
    '''This class contains information about an error that is
    thrown while PostScript file is created, edited and saved.'''
    
    def __init__(self, error_str: str):
        '''Initializes a new instance of the :class:`PsDocumentException` class.
        
        :param error_str: The string that describes a reason of error.'''
        ...
    
    ...

class PsLoadOptions(aspose.page.eps.LoadOptions):
    '''PS document loading options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    ...

