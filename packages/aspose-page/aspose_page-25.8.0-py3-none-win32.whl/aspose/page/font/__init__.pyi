import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class DrFont:
    '''Use this class instead of GDI+ Font'''
    
    @overload
    def get_text_width_points(self, text: str) -> float:
        '''Gets the text width points.
        
        :param text: The text to calculate.
        :returns: Returns width'''
        ...
    
    @overload
    def get_text_width_points(self, text: str, start_index: int, char_count: int) -> float:
        '''Gets the text width points.
        
        :param text: The text to calculate.
        :param start_index: The start index.
        :param char_count: The char count.
        :returns: Returns width'''
        ...
    
    def replace(self, font: aspose.page.font.DrFont) -> None:
        '''Replace font content
        
        :param font: The source font.'''
        ...
    
    def get_char_width_points(self, c: str) -> float:
        '''Returns width of the character (points).
        
        :param c: The symbol to calculate.
        :returns: Returns width'''
        ...
    
    def get_text_size_points(self, text: str) -> aspose.pydrawing.SizeF:
        '''Returns measurement text box of the text in points.
        
        :param text: The text to calculate.
        :returns: Returns size'''
        ...
    
    def get_char_width_lis(self, c: str) -> int:
        '''Gets the char width lis.
        
        :param c: The symbol to calculate.
        :returns: Returns width'''
        ...
    
    def get_text_width_lis(self, text: str) -> int:
        '''Gets the text width lis.
        
        :param text: The text to calculate.
        :returns: Returns width'''
        ...
    
    @staticmethod
    def is_poorly_rendered_by_gdi_plus(self, font_name: str) -> bool:
        '''Returns True for "Microsoft Sans Serif" font. This one is poorly rendered by GDI+. See Test286 and Gemini-6959.
        
        :param font_name: Name of the font.
        :returns: ``True`` if [is poorly rendered by GDI plus] [the specified font name]; otherwise, ``False``.'''
        ...
    
    @property
    def style(self) -> aspose.pydrawing.FontStyle:
        '''Gets style of this font.'''
        ...
    
    @property
    def is_bold(self) -> bool:
        '''Gets a value indicating whether this instance is bold.'''
        ...
    
    @property
    def is_italic(self) -> bool:
        '''Gets a value indicating whether this instance is italic.'''
        ...
    
    @property
    def small_caps_scale_factor(self) -> float:
        '''Gets the SmallCaps scale factor.'''
        ...
    
    @property
    def family_name(self) -> str:
        '''Gets name of this font.'''
        ...
    
    @property
    def size_points(self) -> float:
        '''Gets size of this font (points).'''
        ...
    
    @size_points.setter
    def size_points(self, value: float):
        ...
    
    @property
    def ascent_points(self) -> float:
        '''Returns the cell ascent in points.'''
        ...
    
    @property
    def descent_points(self) -> float:
        '''Returns the cell descent in points.'''
        ...
    
    @property
    def cell_height_points(self) -> float:
        '''Shortcut for :attr:`DrFont.ascent_points` + :attr:`DrFont.descent_points`.'''
        ...
    
    @property
    def ascent_lis(self) -> int:
        '''Cell ascent of this font (lis).
        This is a vertical distance from cell top to cell baseline.
        
        This value is also called **cell baseline**.'''
        ...
    
    @property
    def descent_lis(self) -> int:
        '''Cell descent of this font (lis).
        This is a vertical distance from cell bottom to cell baseline.'''
        ...
    
    @property
    def cell_height_lis(self) -> int:
        '''Returns cell height of this font (lis).
        This is a shortcut for :attr:`DrFont.ascent_lis` + :attr:`DrFont.descent_lis`.'''
        ...
    
    @property
    def leading_lis(self) -> int:
        '''Returns leading of this font (lis).
        This is a shortcut for :attr:`DrFont.line_spacing_lis` - :attr:`DrFont.cell_height_lis`.'''
        ...
    
    @property
    def leading_points(self) -> float:
        '''Returns leading of this font (lis).
        This is a shortcut for :attr:`DrFont.line_spacing_lis` - :attr:`DrFont.cell_height_lis`.'''
        ...
    
    @property
    def line_spacing_lis(self) -> int:
        '''Returns cell spacing of this font (lis).
        This is a vertical distance between baselines of the two glyphs.'''
        ...
    
    @property
    def line_spacing_points(self) -> float:
        '''Returns cell spacing of this font (points).
        This is a vertical distance between baselines of the two glyphs.'''
        ...
    
    @property
    def style_ex(self) -> int:
        '''This property contains additional information about font's style'''
        ...
    
    @style_ex.setter
    def style_ex(self, value: int):
        ...
    
    ...

