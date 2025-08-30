from aspose.page.xps.presentation import image
from aspose.page.xps.presentation import pdf
import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class IEventBasedModificationOptions:
    '''Defines options relevant to handling event-based modifications during document saving.'''
    
    @property
    def before_page_saving_event_handlers(self) -> None:
        '''The collection of event handlers that performs modifications to an XPS page just before it is saved.'''
        ...
    
    ...

class IPipelineOptions:
    '''Defines conversion options related to pipeline configuration.'''
    
    @property
    def batch_size(self) -> int:
        '''Specifies the size of a portion of pages to pass from node to node.'''
        ...
    
    @batch_size.setter
    def batch_size(self, value: int):
        ...
    
    ...

class IXpsTextConversionOptions:
    '''Defines options for conversion of XPS to other formats.'''
    
    @property
    def preserve_text(self) -> bool:
        '''In XPS, some text elements may contain references to alternate glyph forms
        that do not correspond to any character code in the font.
        If this flag is set to true, the text from such XPS elements is converted to graphic shapes.
        Then the text itself appears transparent on top. This leaves the text of such elements selectable.
        But the side effect is that the output file may be much larger than the original.
        If this flag is set to false, the characters that should be displayed as alternate forms
        are replaced with some other characters that become mapped to the alternate glyph forms.
        Therefore the text, although still selectable, will be modified and likely become unreadable.'''
        ...
    
    @preserve_text.setter
    def preserve_text(self, value: bool):
        ...
    
    ...

class WdpNotSupportedException(RuntimeError):
    '''The exception that is thrown whenever an XPS document containing
    WDP images is being converted in library version for .NET 2.0.'''
    
    def __init__(self):
        '''Creates new instance.'''
        ...
    
    ...

