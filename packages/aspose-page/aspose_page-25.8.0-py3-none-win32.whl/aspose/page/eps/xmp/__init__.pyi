import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class XmpField:
    '''Represents XMP field.'''
    
    def to_structure(self) -> list[aspose.page.eps.xmp.XmpField]:
        '''Gets value as a structure.
        
        :returns: The tructure.'''
        ...
    
    def to_array(self) -> list[aspose.page.eps.xmp.XmpValue]:
        '''Gets value as an array.
        
        :returns: The array.'''
        ...
    
    empty: aspose.page.eps.xmp.XmpField
    
    lang: aspose.page.eps.xmp.XmpField
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @prefix.setter
    def prefix(self, value: str):
        ...
    
    @property
    def namespace_uri(self) -> str:
        '''Gets the namespace URI.'''
        ...
    
    @namespace_uri.setter
    def namespace_uri(self, value: str):
        ...
    
    @property
    def local_name(self) -> str:
        '''Gets or sets the name of the local.'''
        ...
    
    @local_name.setter
    def local_name(self, value: str):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @property
    def value(self) -> aspose.page.eps.xmp.XmpValue:
        '''Gets the value.'''
        ...
    
    @property
    def field_type(self) -> aspose.page.eps.xmp.XmpFieldType:
        '''Gets the type of the field.'''
        ...
    
    @property
    def is_empty(self) -> bool:
        '''Gets a value indicating whether this instance is empty.'''
        ...
    
    ...

class XmpMetadata:
    '''Provides access to XMP metadata stream.'''
    
    @overload
    def register_namespace_uri(self, prefix: str, namespace_uri: str) -> None:
        '''Registers namespace URI.
        
        :param prefix: The value of prefix.
        :param namespace_uri: The value of namespace URI.'''
        ...
    
    @overload
    def register_namespace_uri(self, prefix: str, namespace_uri: str, schema_description: str) -> None:
        '''Registers namespace URI.
        
        :param prefix: The value of prefix.
        :param namespace_uri: The value of namespace URI.
        :param schema_description: The value of schema description.'''
        ...
    
    @overload
    def add(self, key: str, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Adds value to metadata.
        
        :param key: The key to add.
        :param value: Value which will be added.'''
        ...
    
    @overload
    def add(self, key: str, value: object) -> None:
        '''Adds value to metadata.
        
        :param key: The key to add.
        :param value: Value which will be added.'''
        ...
    
    @overload
    def add_array_item(self, array_key: str, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Adds value into an array. The value will be added at the end of the array.
        
        :param array_key: Key of the array to search in the dictionary.
        :param value: Value to add into the array.'''
        ...
    
    @overload
    def add_array_item(self, array_key: str, index: int, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Adds value into an array by specified index.
        
        :param array_key: Key of the array to search in the dictionary.
        :param index: Index of new value in the array.
        :param value: Value to add into the array.'''
        ...
    
    def get_namespace_uri_by_prefix(self, prefix: str) -> str:
        '''Returns  namespace URI by prefix.
        
        :param prefix: The value of prefix.
        :returns: The value of namespace URI.'''
        ...
    
    def get_prefix_by_namespace_uri(self, namespace_uri: str) -> str:
        '''Returns prefix by namespace URI.
        
        :param namespace_uri: Namespace URI.
        :returns: The value of prefix.'''
        ...
    
    def clear(self) -> None:
        '''Clears metadata.'''
        ...
    
    def contains(self, key: str) -> bool:
        '''Checks does key is contained in metadata.
        
        :param key: The key of entry to find.
        :returns: True if key is contained in the metadata.'''
        ...
    
    def remove(self, key: str) -> bool:
        '''Removes entry from metadata.
        
        :param key: The key of entry to remove.
        :returns: True - if key removed; otherwise, false.'''
        ...
    
    def get_value(self, key: str) -> aspose.page.eps.xmp.XmpValue:
        '''Gets data from metadata.
        
        :param key: The key name.
        :returns: XmpValue object.'''
        ...
    
    def set_value(self, key: str, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Sets data to metadata.
        
        :param key: The key name.
        :param value: The value.'''
        ...
    
    def contains_key(self, key: str) -> bool:
        '''Determines does this dictionary contasins specified key.
        
        :param key: Key to search in the dictionary.
        :returns: true if key is found.'''
        ...
    
    def try_get_value(self, key: str, value: aspose.page.eps.xmp.XmpValue) -> bool:
        ...
    
    def set_array_item(self, array_key: str, index: int, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Sets value in an array. Previous value will be replaced with new one.
        
        :param array_key: Key of the array to search in the dictionary.
        :param index: Index of new value in the array.
        :param value: Value to set in the array.'''
        ...
    
    def add_named_value(self, structure_key: str, value_key: str, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Adds named value into a structure.
        
        :param structure_key: Key of the structure to search in the dictionary.
        :param value_key: Name of the value to add into the struture.
        :param value: Value to add into the struture.'''
        ...
    
    def set_named_value(self, structure_key: str, value_key: str, value: aspose.page.eps.xmp.XmpValue) -> None:
        '''Sets named value into a structure. Previous named value, if already exists, will be replaced with new one.
        
        :param structure_key: Key of the structure to search in the dictionary.
        :param value_key: Name of the value to set into the struture.
        :param value: Value to set into the struture.'''
        ...
    
    @property
    def is_fixed_size(self) -> bool:
        '''Checks if colleciton has fixed size.'''
        ...
    
    @property
    def is_read_only(self) -> bool:
        '''Checks if collection is read-only.'''
        ...
    
    @property
    def keys(self) -> None:
        '''Gets collection of metadata keys.'''
        ...
    
    @property
    def values(self) -> None:
        '''Gets values in the metadata.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets count of elements in the collection.'''
        ...
    
    @property
    def is_synchronized(self) -> bool:
        '''Checks if collection is synchronized.'''
        ...
    
    @property
    def sync_root(self) -> object:
        '''Gets collection synchronization object.'''
        ...
    
    ...

class XmpValue:
    '''Represents XMP value'''
    
    @overload
    def __init__(self, value: str):
        '''Constructor for string value.
        
        :param value: String value.'''
        ...
    
    @overload
    def __init__(self, value: int):
        '''Consructor for integer value.
        
        :param value: Integer value.'''
        ...
    
    @overload
    def __init__(self, value: float):
        '''Constructor for floating point Value.
        
        :param value: Double value.'''
        ...
    
    @overload
    def __init__(self, value: datetime.datetime):
        '''Constructor for date time value.
        
        :param value: Date time value.'''
        ...
    
    @overload
    def __init__(self, array: list[aspose.page.eps.xmp.XmpValue]):
        '''Constructor for array value.
        
        :param array: Array value.'''
        ...
    
    def to_string_value(self) -> str:
        '''Converts to string.
        
        :returns: String value.'''
        ...
    
    def to_integer(self) -> int:
        '''Converts to integer.
        
        :returns: Integer value.'''
        ...
    
    def to_double(self) -> float:
        '''Converts to double.
        
        :returns: Double value.'''
        ...
    
    def to_date_time(self) -> datetime.datetime:
        '''Converts to date time.
        
        :returns: DateTime value.'''
        ...
    
    def to_array(self) -> list[aspose.page.eps.xmp.XmpValue]:
        '''Returns array.
        
        :returns: Array value'''
        ...
    
    def to_structure(self) -> list[aspose.page.eps.xmp.XmpField]:
        '''Returns XMP value as structure (set of fields).
        
        :returns: Structure value.'''
        ...
    
    def to_field(self) -> aspose.page.eps.xmp.XmpField:
        '''Returns XMP value as XMP field.
        
        :returns: Field value.'''
        ...
    
    @property
    def is_string(self) -> bool:
        '''Returns true if value is string.'''
        ...
    
    @property
    def is_integer(self) -> bool:
        '''Returns true if value is integer.'''
        ...
    
    @property
    def is_double(self) -> bool:
        '''Returns true if value is floating point value.'''
        ...
    
    @property
    def is_date_time(self) -> bool:
        '''Returns true if value is DateTime.'''
        ...
    
    @property
    def is_field(self) -> bool:
        '''Returns true if XmpValue is field.'''
        ...
    
    @property
    def is_named_value(self) -> bool:
        '''Returns true if XmpValue is named value.'''
        ...
    
    @property
    def is_raw(self) -> bool:
        '''Value is unsupported/unknown and raw XML code is provided.
        
        :returns: True if value returned as raw data.'''
        ...
    
    @property
    def is_named_values(self) -> bool:
        '''Returns true is XmpValue represents named values.'''
        ...
    
    @property
    def is_structure(self) -> bool:
        '''Returns true is XmpValue represents structure.'''
        ...
    
    @property
    def is_array(self) -> bool:
        '''Returns true is XmpValue is array.'''
        ...
    
    ...

class XmpFieldType:
    '''This enum represents types of a XMP field.'''
    
    STRUCT: int
    ARRAY: int
    PROPERTY: int
    PACKET: int
    UNKNOWN: int

