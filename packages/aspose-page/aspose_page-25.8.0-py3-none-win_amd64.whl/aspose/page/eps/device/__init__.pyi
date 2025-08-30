import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class ImageSaveOptions(aspose.page.SaveOptions):
    '''This class contains options necessary for managing image saving process.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`ImageSaveOptions` class with default values
        for flags  (true) and  (false).'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified image format.
        
        :param image_format: The format of the image.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified size of the image.
        
        :param size: The image size.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size, image_format: aspose.page.drawing.imaging.ImageFormat):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified size of the image and image format.
        
        :param size: The image size.
        :param image_format: The format of the image.'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat, supress_errors: bool):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified image format.
        
        :param image_format: The format of the image.
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size, supress_errors: bool):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified size.
        
        :param size: The image size.
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size, image_format: aspose.page.drawing.imaging.ImageFormat, supress_errors: bool):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        with specified size of the image and image format.
        
        :param size: The image size.
        :param image_format: The format of the image.
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool):
        '''Initializes a new instance of the :class:`ImageSaveOptions` with
        default value for flag  (false).
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @property
    def smoothing_mode(self) -> None:
        '''Gets/sets the smoothing mode for rendering image.'''
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value: None):
        ...
    
    @property
    def resolution(self) -> float:
        '''Gets/sets the image resolution.'''
        ...
    
    @resolution.setter
    def resolution(self, value: float):
        ...
    
    @property
    def image_format(self) -> aspose.page.drawing.imaging.ImageFormat:
        '''Gets/sets an image format for resulting image.'''
        ...
    
    @image_format.setter
    def image_format(self, value: aspose.page.drawing.imaging.ImageFormat):
        ...
    
    @property
    def try_join_image_fragments(self) -> bool:
        '''The flag for combining image fragments into one picture.'''
        ...
    
    @try_join_image_fragments.setter
    def try_join_image_fragments(self, value: bool):
        ...
    
    ...

class PdfSaveOptions(aspose.page.SaveOptions):
    '''This class contains input and output streams and other options necessary for managing conversion process.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`PdfSaveOptions` class with default values
        for flags  (true) and  (false).'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool):
        '''Initializes a new instance of the :class:`PdfSaveOptions` class with default values for flag  (false).
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size):
        '''Initializes a new instance of the :class:`PdfSaveOptions` with
        with specified size of the page.
        
        :param size: The page size.'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool, size: aspose.page.drawing.Size):
        '''Initializes a new instance of the :class:`PdfSaveOptions` class with default values for flag  (false) and with specified size of the page.
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.
        :param size: The page size.'''
        ...
    
    ...

class PsSaveOptions(aspose.page.SaveOptions):
    '''This class contains options necessary for managing process of converting document to PostScript (PS) or Encapsulated PostScript (EPS) file.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the :class:`PsSaveOptions` class with default values
        for flags  (true) and  (false).'''
        ...
    
    @overload
    def __init__(self, supress_errors: bool):
        '''Initializes a new instance of the :class:`PsSaveOptions` class with default values for flag  (false).
        
        :param supress_errors: Specifies whether errors must be suppressed or not.
                               If true suppressed errors are added to  list.'''
        ...
    
    @property
    def save_format(self) -> aspose.page.eps.device.PsSaveFormat:
        '''The save format of resulting file.'''
        ...
    
    @save_format.setter
    def save_format(self, value: aspose.page.eps.device.PsSaveFormat):
        ...
    
    @property
    def page_size(self) -> aspose.page.drawing.Size:
        '''The size of the page.'''
        ...
    
    @page_size.setter
    def page_size(self, value: aspose.page.drawing.Size):
        ...
    
    @property
    def margins(self) -> aspose.page.Margins:
        '''The margins of the page.'''
        ...
    
    @margins.setter
    def margins(self, value: aspose.page.Margins):
        ...
    
    @property
    def background_color(self) -> None:
        '''The background color.'''
        ...
    
    @background_color.setter
    def background_color(self, value: None):
        ...
    
    @property
    def transparent(self) -> bool:
        '''Indicates if background is transparent.'''
        ...
    
    @transparent.setter
    def transparent(self, value: bool):
        ...
    
    @property
    def embed_fonts(self) -> bool:
        '''Indicates whether to embed used fonts in PS document.'''
        ...
    
    @embed_fonts.setter
    def embed_fonts(self, value: bool):
        ...
    
    @property
    def embed_fonts_as(self) -> str:
        '''A type of font in which to embed fonts in PS document.'''
        ...
    
    @embed_fonts_as.setter
    def embed_fonts_as(self, value: str):
        ...
    
    ...

class PsSaveFormat:
    '''This enumeration contains available options of saving format. It can be PS or EPS.
    EPS is used for only 1-paged documents while PS file can contain any number of pages.'''
    
    PS: int
    EPS: int

