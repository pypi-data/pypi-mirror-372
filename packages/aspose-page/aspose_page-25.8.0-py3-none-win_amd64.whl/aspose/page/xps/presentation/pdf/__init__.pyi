import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class PdfEncryptionDetails:
    '''Contains details for a pdf encryption.'''
    
    def __init__(self, user_password: str, owner_password: str, permissions: int, encryption_algorithm: aspose.page.xps.presentation.pdf.PdfEncryptionAlgorithm):
        '''Initializes a new instance of the  class.
        
        :param user_password: The user password.
        :param owner_password: The owner password.
        :param permissions: The permissions.
        :param encryption_algorithm: The encryption algorithm.'''
        ...
    
    @property
    def user_password(self) -> str:
        '''Gets or sets the User password.
        
        Opening the document with the correct user password (or opening a document
        that does not have a user password) allows additional operations to be
        performed according to the user access permissions specified in the document’s
        encryption dictionary.'''
        ...
    
    @user_password.setter
    def user_password(self, value: str):
        ...
    
    @property
    def owner_password(self) -> str:
        '''Gets or sets the Owner password.
        
        Opening the document with the correct owner password (assuming it is not the
        same as the user password) allows full (owner) access to the document. This
        unlimited access includes the ability to change the document’s passwords and
        access permissions.'''
        ...
    
    @owner_password.setter
    def owner_password(self, value: str):
        ...
    
    @property
    def permissions(self) -> int:
        '''Gets or sets the permissions.'''
        ...
    
    @permissions.setter
    def permissions(self, value: int):
        ...
    
    @property
    def encryption_algorithm(self) -> aspose.page.xps.presentation.pdf.PdfEncryptionAlgorithm:
        '''Gets or sets the encryption mode.'''
        ...
    
    @encryption_algorithm.setter
    def encryption_algorithm(self, value: aspose.page.xps.presentation.pdf.PdfEncryptionAlgorithm):
        ...
    
    ...

class PdfSaveOptions(aspose.page.SaveOptions):
    '''Class for XPS-as-PDF saving options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        '''Gets/sets the array of numbers of pages to convert.'''
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def outline_tree_height(self) -> int:
        '''Specifies the height of the document outline tree to save.
        0 - the outline tree will not be converted,
        1 - only the first level outline items will be converted,
        ans so on.
        Default is 10.'''
        ...
    
    @outline_tree_height.setter
    def outline_tree_height(self, value: int):
        ...
    
    @property
    def outline_tree_expansion_level(self) -> int:
        '''Specifies up to what level the document outline should be expanded when the PDF file is opened in a viewer.
        1 - only the first level outline items are shown,
        2 - only the first and second level outline items are shown,
        and so on.
        Default is 1.'''
        ...
    
    @outline_tree_expansion_level.setter
    def outline_tree_expansion_level(self, value: int):
        ...
    
    @property
    def text_compression(self) -> aspose.page.xps.presentation.pdf.PdfTextCompression:
        '''Specifies compression type to be used for all content streams except images.
        Default is :attr:`PdfTextCompression.FLATE`.'''
        ...
    
    @text_compression.setter
    def text_compression(self, value: aspose.page.xps.presentation.pdf.PdfTextCompression):
        ...
    
    @property
    def image_compression(self) -> aspose.page.xps.presentation.pdf.PdfImageCompression:
        '''Specifies compression type to be used for all images in the document.
        Default is :attr:`PdfImageCompression.AUTO`.'''
        ...
    
    @image_compression.setter
    def image_compression(self, value: aspose.page.xps.presentation.pdf.PdfImageCompression):
        ...
    
    @property
    def encryption_details(self) -> aspose.page.xps.presentation.pdf.PdfEncryptionDetails:
        '''Gets or sets a encryption details. If not set, then no encryption will be performed.'''
        ...
    
    @encryption_details.setter
    def encryption_details(self, value: aspose.page.xps.presentation.pdf.PdfEncryptionDetails):
        ...
    
    @property
    def preserve_text(self) -> bool:
        '''In XPS, some text elements may contain references to alternate glyph forms
        that do not correspond to any character code in the font.
        If this flag is set to true, the text from such XPS elements is converted to graphic shapes.
        Then the text itself appears transparent on top. This leaves the text of such elements selectable.
        But the side effect is that the output file may be much larger than the original.
        If this flag is set to false, the characters that should be displayed as alternate forms
        are replaced with some other characters that become mapped to the alternate glyph forms.
        Therefore the text, although still selectable, will be modified and likely become unreadable.
        Default is false.'''
        ...
    
    @preserve_text.setter
    def preserve_text(self, value: bool):
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

class PdfEncryptionAlgorithm:
    '''Encryption mode enum. Describe using algorithm and key length.
    This enum is extended in order to be able to further increase functionality.
    This enum implements "Base-to-Core" pattern.'''
    
    RC4_40: int
    RC4_128: int

class PdfImageCompression:
    '''Specifies the type of compression applied to images in the PDF file.'''
    
    AUTO: int
    NONE: int
    RLE: int
    FLATE: int
    LZW_BASELINE_PREDICTOR: int
    LZW_OPTIMIZED_PREDICTOR: int
    JPEG: int

class PdfTextCompression:
    '''Specifies a type of compression applied to all contents in the PDF file except images.'''
    
    NONE: int
    RLE: int
    LZW: int
    FLATE: int

