import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class BmpSaveOptions(aspose.page.eps.device.ImageSaveOptions):
    '''Class for XPS-as-BMP saving options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.Text.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value: aspose.pydrawing.Text.TextRenderingHint):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def image_size(self) -> aspose.pydrawing.Size:
        ...
    
    @image_size.setter
    def image_size(self, value: aspose.pydrawing.Size):
        ...
    
    ...

class ImageSaveOptions(aspose.page.SaveOptions):
    '''Basic class for XPS-as-image saving options.'''
    
    @property
    def page_numbers(self) -> list[int]:
        '''Gets/sets the array of numbers of pages to convert.'''
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def resolution(self) -> float:
        '''Gets/sets the image resolution.'''
        ...
    
    @resolution.setter
    def resolution(self, value: float):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.pydrawing.Drawing2D.SmoothingMode:
        '''Gets/sets the smoothing mode.'''
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value: aspose.pydrawing.Drawing2D.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.Text.TextRenderingHint:
        '''Gets/sets the text rendering hint.'''
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value: aspose.pydrawing.Text.TextRenderingHint):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        '''Gets/sets the interpolation mode.'''
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def image_size(self) -> aspose.pydrawing.Size:
        '''Gets/sets the size of the output images in pixels.'''
        ...
    
    @image_size.setter
    def image_size(self, value: aspose.pydrawing.Size):
        ...
    
    @property
    def batch_size(self) -> int:
        '''Specifies the size of a portion of pages to pass from node to node.'''
        ...
    
    @batch_size.setter
    def batch_size(self, value: int):
        ...
    
    @property
    def before_page_saving_event_handlers(self) -> None:
        '''The collection of event handlers that performs modifications to an XPS page just before it is saved.'''
        ...
    
    ...

class JpegSaveOptions(aspose.page.eps.device.ImageSaveOptions):
    '''Class for XPS-as-JPEG saving options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.Text.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value: aspose.pydrawing.Text.TextRenderingHint):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def image_size(self) -> aspose.pydrawing.Size:
        ...
    
    @image_size.setter
    def image_size(self, value: aspose.pydrawing.Size):
        ...
    
    ...

class PngSaveOptions(aspose.page.eps.device.ImageSaveOptions):
    '''Class for XPS-as-PNG saving options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.Text.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value: aspose.pydrawing.Text.TextRenderingHint):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def image_size(self) -> aspose.pydrawing.Size:
        ...
    
    @image_size.setter
    def image_size(self, value: aspose.pydrawing.Size):
        ...
    
    ...

class TiffSaveOptions(aspose.page.eps.device.ImageSaveOptions):
    '''Class for XPS-as-TIFF saving options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.Text.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value: aspose.pydrawing.Text.TextRenderingHint):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.pydrawing.Drawing2D.InterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value: aspose.pydrawing.Drawing2D.InterpolationMode):
        ...
    
    @property
    def image_size(self) -> aspose.pydrawing.Size:
        ...
    
    @image_size.setter
    def image_size(self, value: aspose.pydrawing.Size):
        ...
    
    @property
    def multipage(self) -> bool:
        '''Gets/sets the flag that defines if multiple images
        should be saved in a single multipage TIFF file.'''
        ...
    
    @multipage.setter
    def multipage(self, value: bool):
        ...
    
    ...

