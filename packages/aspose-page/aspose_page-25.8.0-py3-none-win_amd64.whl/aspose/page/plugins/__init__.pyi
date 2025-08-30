import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class ByteArrayDataSource:
    '''Represents byte array data source for save operations of a plugin.'''
    
    def __init__(self):
        '''Initializes new byte array data source.
        
        :param data: A byte array.'''
        ...
    
    @property
    def data_type(self) -> aspose.page.plugins.DataType:
        '''Type of data source (byte array).'''
        ...
    
    ...

class ByteArrayResult:
    '''Represents operation result in the form of the bytes array.'''
    
    def to_file(self) -> str:
        '''Tries to convert the result to a file.
        
        :returns: A string representing the path to the output file if the result is file; otherwise ``None``.'''
        ...
    
    def to_stream(self) -> io.BytesIO:
        '''Tries to convert the result to a stream object.
        
        :returns: A stream object representing the output data if the result is stream; otherwise ``None``.'''
        ...
    
    @property
    def is_file(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a file; otherwise ``False``.'''
        ...
    
    @property
    def is_stream(self) -> bool:
        '''Indicates whether the result is an output stream.
        
        :returns: ``True`` if the result is a stream object; otherwise ``False``.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Indicates whether the result is a text string.
        
        :returns: ``True`` if the result is a string; otherwise ``False``.'''
        ...
    
    @property
    def is_byte_array(self) -> bool:
        '''Indicates whether the result is a byte array.
        
        :returns: ``True`` if the result is a byte array; otherwise ``False``.'''
        ...
    
    @property
    def data(self) -> object:
        '''Gets raw data.
        
        :returns: An ``object`` representing output data.'''
        ...
    
    ...

class FileDataSource:
    '''Represents file data source for load and save operations of a plugin.'''
    
    def __init__(self, path: str):
        '''Initializes new file data source with the specified path.
        
        :param path: A string representing the path to the source file.'''
        ...
    
    @property
    def data_type(self) -> aspose.page.plugins.DataType:
        '''Type of data source (file).'''
        ...
    
    @property
    def path(self) -> str:
        '''Gets the path to the file of the current data source.'''
        ...
    
    ...

class FileResult:
    '''Represents operation result in the form of string path to file.'''
    
    def to_file(self) -> str:
        '''Tries to convert the result to a file.
        
        :returns: A string representing the path to the output file if the result is file; otherwise ``None``.'''
        ...
    
    def to_stream(self) -> io.BytesIO:
        '''Tries to convert the result to a stream object.
        
        :returns: A stream object representing the output data if the result is stream; otherwise ``None``.'''
        ...
    
    @property
    def is_file(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a file; otherwise ``False``.'''
        ...
    
    @property
    def is_stream(self) -> bool:
        '''Indicates whether the result is an output stream.
        
        :returns: ``True`` if the result is a stream object; otherwise ``False``.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Indicates whether the result is a text string.
        
        :returns: ``True`` if the result is a string; otherwise ``False``.'''
        ...
    
    @property
    def is_byte_array(self) -> bool:
        '''Indicates whether the result is a byte array.
        
        :returns: ``True`` if the result is a byte array; otherwise ``False``.'''
        ...
    
    @property
    def data(self) -> object:
        '''Gets raw data.
        
        :returns: An ``object`` representing output data.'''
        ...
    
    ...

class IDataSource:
    '''General data source interface that defines common members that concrete data sources should implement.'''
    
    @property
    def data_type(self) -> aspose.page.plugins.DataType:
        '''Type of data source (file or stream).'''
        ...
    
    ...

class IOperationResult:
    '''General operation result interface that defines common methods that concrete plugin operation result should implement.'''
    
    def to_file(self) -> str:
        '''Tries to convert the result to the file.
        
        :returns: A string representing the path to the output file if the result is file; otherwise ``None``.'''
        ...
    
    def to_stream(self) -> io.BytesIO:
        '''Tries to convert the result to the stream object.
        
        :returns: A stream object representing the output data if the result is stream; otherwise ``None``.'''
        ...
    
    @property
    def is_file(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a file; otherwise ``False``.'''
        ...
    
    @property
    def is_stream(self) -> bool:
        '''Indicates whether the result is an output stream.
        
        :returns: ``True`` if the result is a stream object; otherwise ``False``.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Indicates whether the result is a text string.
        
        :returns: ``True`` if the result is a string; otherwise ``False``.'''
        ...
    
    @property
    def is_byte_array(self) -> bool:
        '''Indicates whether the result is a byte array.
        
        :returns: ``True`` if the result is a byte array; otherwise ``False``.'''
        ...
    
    @property
    def data(self) -> object:
        '''Gets raw data.
        
        :returns: An ``object`` representing output data.'''
        ...
    
    ...

class IPlugin:
    '''General plugin interface that defines common methods that concrete plugin should implement.'''
    
    def process(self, options: aspose.page.plugins.IPluginOptions) -> aspose.page.plugins.ResultContainer:
        '''Charges a plugin to process with defined options
        
        :param options: An options object containing instructions for the plugin
        :returns: An ResultContainer object containing the result of the processing'''
        ...
    
    ...

class IPluginOptions:
    '''General plugin option interface that defines common methods that concrete plugin option should implement.'''
    
    ...

class PsConverter:
    
    def __init__(self):
        ...
    
    def process(self, options: aspose.page.plugins.IPluginOptions) -> aspose.page.plugins.ResultContainer:
        '''Starts the PsConverter processing with the specified parameters.
        
        :param options: An options object containing instructions for the PsConverter.
        :returns: An ResultContainer object containing the result of the operation.
        
        :raises System.NotSupportedException:'''
        ...
    
    ...

class PsConverterOptions:
    '''Represents options for  plugin.'''
    
    def add_data_source(self, data_source: aspose.page.plugins.IDataSource) -> None:
        '''Adds new data source to the PsConverter plugin data collection.
        
        :param data_source: Data source to add.'''
        ...
    
    def add_save_data_source(self, save_data_source: aspose.page.plugins.IDataSource) -> None:
        '''Adds new data source to the PsConverterOptions plugin data collection.
        
        :param save_data_source: Data source (file or stream) for saving operation results.
        :raises System.NotImplementedException:'''
        ...
    
    @property
    def data_collection(self) -> None:
        '''Returns PsConverterOptions plugin data collection.'''
        ...
    
    @property
    def save_targets_collection(self) -> None:
        '''Gets collection of added targets for saving operation results.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
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
    def debug(self) -> bool:
        '''Specifies whether debug information must be printed to standard output stream or not.'''
        ...
    
    @debug.setter
    def debug(self, value: bool):
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

class PsConverterToImageOptions(aspose.page.plugins.PsConverterOptions):
    '''Represents PS/EPS to Image converter options for  plugin.'''
    
    @overload
    def __init__(self):
        '''Initializes new instance of the :class:`PsConverterToImageOptions` object with default options.'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat):
        '''Initializes new instance of the :class:`PsConverterToImageOptions` object with image format.
        
        :param image_format: A format of resulting image.'''
        ...
    
    @overload
    def __init__(self, size: aspose.page.drawing.Size):
        '''Initializes new instance of the :class:`PsConverterToImageOptions` object with a size of the resulting image.
        
        :param size: A size the resulting image.'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat, size: aspose.page.drawing.Size):
        '''Initializes new instance of the :class:`PsConverterToImageOptions` object with image format and a size of the resulting image.
        
        :param image_format: A format of resulting image.
        :param size: A size the resulting image.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
        ...
    
    @property
    def image_format(self) -> aspose.page.drawing.imaging.ImageFormat:
        '''Gets/sets the image type.'''
        ...
    
    @image_format.setter
    def image_format(self, value: aspose.page.drawing.imaging.ImageFormat):
        ...
    
    @property
    def size(self) -> aspose.page.drawing.Size:
        '''Gets/sets the size of the resulting image.'''
        ...
    
    @size.setter
    def size(self, value: aspose.page.drawing.Size):
        ...
    
    @property
    def resolution(self) -> float:
        '''Gets/sets the image resolution.'''
        ...
    
    @resolution.setter
    def resolution(self, value: float):
        ...
    
    @property
    def smoothing_mode(self) -> None:
        '''Gets/sets the smoothing mode for rendering image.'''
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value: None):
        ...
    
    ...

class PsConverterToPdfOptions(aspose.page.plugins.PsConverterOptions):
    '''Represents PS/EPS to PDF converter options for  plugin.'''
    
    def __init__(self):
        '''Initializes new instance of the :class:`PsConverterToPdfOptions` object with default options.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
        ...
    
    ...

class ResultContainer:
    '''Represents container that contains the result collection of processing the plugin.'''
    
    @property
    def result_collection(self) -> None:
        '''Gets collection of the operation results'''
        ...
    
    ...

class StreamDataSource:
    '''Represents stream data source for load and save operations of a plugin.'''
    
    def __init__(self, data: io.BytesIO):
        '''Initializes new stream data source with the specified stream object.
        
        :param data: Stream object'''
        ...
    
    @property
    def data_type(self) -> aspose.page.plugins.DataType:
        '''Type of data source (stream).'''
        ...
    
    @property
    def data(self) -> io.BytesIO:
        '''Gets the stream object of the current data source.'''
        ...
    
    ...

class StreamResult:
    '''Represents operation result in the form of Stream.'''
    
    def to_file(self) -> str:
        '''Tries to convert the result to a file.
        
        :returns: A string representing the path to the output file if the result is file; otherwise ``None``.'''
        ...
    
    def to_stream(self) -> io.BytesIO:
        '''Tries to convert the result to a stream object.
        
        :returns: A stream object representing the output data if the result is stream; otherwise ``None``.'''
        ...
    
    @property
    def is_file(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a file; otherwise ``False``.'''
        ...
    
    @property
    def is_stream(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a stream object; otherwise ``False``.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Indicates whether the result is a string.
        
        :returns: ``True`` if the result is a string; otherwise ``False``.'''
        ...
    
    @property
    def is_byte_array(self) -> bool:
        '''Indicates whether the result is a byte array.
        
        :returns: ``True`` if the result is a byte array; otherwise ``False``.'''
        ...
    
    @property
    def data(self) -> object:
        '''Gets raw data.
        
        :returns: An ``object`` representing output data.'''
        ...
    
    ...

class StringResult:
    '''Represents operation result in the form of string.'''
    
    def to_file(self) -> str:
        '''Tries to convert the result to a file.
        
        :returns: A string representing the path to the output file if the result is file; otherwise ``None``.'''
        ...
    
    def to_stream(self) -> io.BytesIO:
        '''Tries to convert the result to a stream object.
        
        :returns: A stream object representing the output data if the result is stream; otherwise ``None``.'''
        ...
    
    @property
    def is_file(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a file; otherwise ``False``.'''
        ...
    
    @property
    def is_stream(self) -> bool:
        '''Indicates whether the result is a path to an output file.
        
        :returns: ``True`` if the result is a stream object; otherwise ``False``.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Indicates whether the result is a string.
        
        :returns: ``True`` if the result is a string; otherwise ``False``.'''
        ...
    
    @property
    def is_byte_array(self) -> bool:
        '''Indicates whether the result is a byte array.
        
        :returns: ``True`` if the result is a byte array; otherwise ``False``.'''
        ...
    
    @property
    def data(self) -> object:
        '''Gets raw data.
        
        :returns: An ``object`` representing output data.'''
        ...
    
    @property
    def text(self) -> str:
        '''Returns string representation of the result.'''
        ...
    
    ...

class XpsConverter:
    
    def __init__(self):
        ...
    
    def process(self, options: aspose.page.plugins.IPluginOptions) -> aspose.page.plugins.ResultContainer:
        '''Starts the XpsConverter processing with the specified parameters.
        
        :param options: An options object containing instructions for the XpsConverter.
        :returns: An ResultContainer object containing the result of the operation.
        
        :raises System.NotSupportedException:'''
        ...
    
    ...

class XpsConverterOptions:
    '''Represents options for  plugin.'''
    
    def add_data_source(self, data_source: aspose.page.plugins.IDataSource) -> None:
        '''Adds new data source to the XpsConverter plugin data collection.
        
        :param data_source: Data source to add.'''
        ...
    
    def add_save_data_source(self, save_data_source: aspose.page.plugins.IDataSource) -> None:
        '''Adds new data source to the XpsConverterOptions plugin data collection.
        
        :param save_data_source: Data source (file or stream) for saving operation results.
        :raises System.NotImplementedException:'''
        ...
    
    @property
    def data_collection(self) -> None:
        '''Returns XpsConverterOptions plugin data collection.'''
        ...
    
    @property
    def save_targets_collection(self) -> None:
        '''Gets collection of added targets for saving operation results.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
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

class XpsConverterToImageOptions(aspose.page.plugins.XpsConverterOptions):
    '''Represents XPS to Image converter options for  plugin.'''
    
    @overload
    def __init__(self):
        '''Initializes new instance of the :class:`XpsConverterToImageOptions` object with default options.'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat):
        '''Initializes new instance of the :class:`XpsConverterToImageOptions` object with image format.
        
        :param image_format: A format of resulting image.'''
        ...
    
    @overload
    def __init__(self, size: aspose.pydrawing.Size):
        '''Initializes new instance of the :class:`XpsConverterToImageOptions` object with a size of the resulting image.
        
        :param size: A size the resulting image.'''
        ...
    
    @overload
    def __init__(self, image_format: aspose.page.drawing.imaging.ImageFormat, size: aspose.pydrawing.Size):
        '''Initializes new instance of the :class:`XpsConverterToImageOptions` object with image format and a size of the resulting image.
        
        :param image_format: A format of resulting image.
        :param size: A size the resulting image.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        '''Gets/sets the array of numbers of pages in XPS document to convert. If not set all pages will be converted.'''
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    @property
    def image_format(self) -> aspose.page.drawing.imaging.ImageFormat:
        '''Gets/sets the image type.'''
        ...
    
    @image_format.setter
    def image_format(self, value: aspose.page.drawing.imaging.ImageFormat):
        ...
    
    @property
    def size(self) -> aspose.pydrawing.Size:
        '''Gets/sets the size of the resulting image.'''
        ...
    
    @size.setter
    def size(self, value: aspose.pydrawing.Size):
        ...
    
    @property
    def resolution(self) -> float:
        '''Gets/sets the image resolution.'''
        ...
    
    @resolution.setter
    def resolution(self, value: float):
        ...
    
    @property
    def smoothing_mode(self) -> None:
        '''Gets/sets the smoothing mode for rendering image.'''
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value: None):
        ...
    
    ...

class XpsConverterToPdfOptions(aspose.page.plugins.XpsConverterOptions):
    '''Represents XPS to PDF converter options for  plugin.'''
    
    def __init__(self):
        '''Initializes new instance of the :class:`XpsConverterToPdfOptions` object with default options.'''
        ...
    
    @property
    def operation_name(self) -> str:
        '''Returns operation name.'''
        ...
    
    @property
    def page_numbers(self) -> list[int]:
        '''Gets/sets the array of numbers of pages in XPS document to convert. If not set all pages will be converted.'''
        ...
    
    @page_numbers.setter
    def page_numbers(self, value: list[int]):
        ...
    
    ...

class DataType:
    '''Represents possible types of data for plugin processing.'''
    
    FILE: int
    STREAM: int
    BYTE_ARRAY: int

