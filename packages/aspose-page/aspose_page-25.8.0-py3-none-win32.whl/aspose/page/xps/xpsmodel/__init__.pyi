import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class XpsArcSegment(aspose.page.xps.xpsmodel.XpsPathSegment):
    '''Class incapsulating ArcSegment element features.
    This element describes an elliptical arc.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsArcSegment:
        '''Clones this arc segment.
        
        :returns: Clone of this arc segment.'''
        ...
    
    @property
    def point(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the endpoint of the elliptical arc.'''
        ...
    
    @point.setter
    def point(self, value: aspose.pydrawing.PointF):
        ...
    
    @property
    def size(self) -> aspose.pydrawing.SizeF:
        '''Returns/sets the x and y radius of the elliptical arc as an x,y pair.'''
        ...
    
    @size.setter
    def size(self, value: aspose.pydrawing.SizeF):
        ...
    
    @property
    def rotation_angle(self) -> float:
        '''Returns/sets value indicating how the ellipse is rotated relative to the current coordinate system.'''
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value: float):
        ...
    
    @property
    def is_large_arc(self) -> bool:
        '''Returns/sets value determining whether the arc is drawn with a sweep of 180 or greater.'''
        ...
    
    @is_large_arc.setter
    def is_large_arc(self, value: bool):
        ...
    
    @property
    def sweep_direction(self) -> aspose.page.xps.xpsmodel.XpsSweepDirection:
        '''Returns/sets value specifying the direction in which the arc is drawn.'''
        ...
    
    @sweep_direction.setter
    def sweep_direction(self, value: aspose.page.xps.xpsmodel.XpsSweepDirection):
        ...
    
    ...

class XpsBrush(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating common features of all brush elements.'''
    
    @property
    def opacity(self) -> float:
        '''Returns/sets value defining the uniform transparency of the brush fill.'''
        ...
    
    @opacity.setter
    def opacity(self, value: float):
        ...
    
    ...

class XpsCanvas(aspose.page.xps.xpsmodel.XpsContentElement):
    '''Class incapsulating Canvas element features.
    This element groups elements together. For example, Glyphs and Path elements
    can be grouped in a canvas in order to be identified as a unit (as a hyperlink destination) or
    to apply a composed property value to each child and ancestor element.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    def add_canvas(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Adds a new canvas to this canvas's child list.
        
        :returns: Added canvas.'''
        ...
    
    def insert_canvas(self, index: int) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Inserts a new canvas to this canvas's child list at  position.
        
        :param index: Position at which a new canvas should be inserted.
        :returns: Inserted canvas.'''
        ...
    
    def add_path(self, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Adds a new path to this canvas's child list.
        
        :param data: The geometry of the path.
        :returns: Added path.'''
        ...
    
    def insert_path(self, index: int, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Inserts a new path to this canvas's child list at  position.
        
        :param index: Position at which a new path should be inserted.
        :param data: The geometry of the path.
        :returns: Inserted path.'''
        ...
    
    def add_glyphs(self, font_family: str, font_size: float, font_style: aspose.pydrawing.FontStyle, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Adds new glyphs to this canvas's child list.
        
        :param font_family: Font family.
        :param font_size: Font size.
        :param font_style: Font style.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin T coordinate.
        :param unicode_string: String to be printed.
        :returns: Added glyphs.'''
        ...
    
    def insert_glyphs(self, index: int, font_family: str, font_size: float, font_style: aspose.pydrawing.FontStyle, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Inserts new glyphs to this canvas's child list at  position.
        
        :param index: Position at which new glyphs should be inserted.
        :param font_family: Font family.
        :param font_size: Font size.
        :param font_style: Font style.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin T coordinate.
        :param unicode_string: String to be printed.
        :returns: Added glyphs.'''
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Clones this canvas.
        
        :returns: Clone of this canvas.'''
        ...
    
    @property
    def edge_mode(self) -> aspose.page.xps.xpsmodel.XpsEdgeMode:
        '''Returns/sets the value that controls how edges of paths within the canvas are rendered.'''
        ...
    
    @edge_mode.setter
    def edge_mode(self, value: aspose.page.xps.xpsmodel.XpsEdgeMode):
        ...
    
    ...

class XpsColor:
    '''The base class incapsulating common color features.'''
    
    def to_color(self) -> aspose.pydrawing.Color:
        '''Convenience method for getting .NET native representation of any color/
        
        :returns:  structure'''
        ...
    
    ...

class XpsContentElement(aspose.page.xps.xpsmodel.XpsHyperlinkElement):
    '''Incapsulates features of XPS content elements: Canvas, Path and Glyphs.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    @property
    def render_transform(self) -> aspose.page.xps.xpsmodel.XpsMatrix:
        '''Returns/sets the affine transformation matrix establishing a new coordinate frame
        for all attributes of the element and for all child elements (if any).'''
        ...
    
    @render_transform.setter
    def render_transform(self, value: aspose.page.xps.xpsmodel.XpsMatrix):
        ...
    
    @property
    def clip(self) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Returns/sets the path geometry instance limiting the rendered region of the element.'''
        ...
    
    @clip.setter
    def clip(self, value: aspose.page.xps.xpsmodel.XpsPathGeometry):
        ...
    
    @property
    def opacity(self) -> float:
        '''Returns/sets the value defining the uniform transparency of the element.'''
        ...
    
    @opacity.setter
    def opacity(self, value: float):
        ...
    
    @property
    def opacity_mask(self) -> aspose.page.xps.xpsmodel.XpsBrush:
        '''Returns/sets the brush specifying a mask of alpha values
        that is applied to the element in the same fashion as the Opacity attribute,
        but allowing different alpha values for different areas of the element.'''
        ...
    
    @opacity_mask.setter
    def opacity_mask(self, value: aspose.page.xps.xpsmodel.XpsBrush):
        ...
    
    ...

class XpsElement(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating common XPS element features.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        '''Provides access to element's children by index .
        
        :param index: Index of child element.
        :returns: Child element at  position.'''
        ...
    
    @property
    def count(self) -> int:
        '''Returns number of child elements.'''
        ...
    
    ...

class XpsElementLinkTarget(aspose.page.xps.xpsmodel.XpsHyperlinkTarget):
    '''Class incapsulating the relative named-address hyperlink target.'''
    
    @overload
    def __init__(self, target_page: aspose.page.xps.xpsmodel.XpsPage):
        '''Creates the new instance.
        
        :param target_page: The page element within the active fixed document.'''
        ...
    
    @overload
    def __init__(self, target_canvas: aspose.page.xps.xpsmodel.XpsCanvas):
        '''Creates the new instance.
        
        :param target_canvas: The canvas element within the active fixed document.'''
        ...
    
    @overload
    def __init__(self, target_path: aspose.page.xps.xpsmodel.XpsPath):
        '''Creates the new instance.
        
        :param target_path: The path element within the active fixed document.'''
        ...
    
    @overload
    def __init__(self, target_glyphs: aspose.page.xps.xpsmodel.XpsGlyphs):
        '''Creates the new instance.
        
        :param target_glyphs: The glyphs element within the active fixed document.'''
        ...
    
    ...

class XpsExternalLinkTarget(aspose.page.xps.xpsmodel.XpsHyperlinkTarget):
    '''Class incapsulating the external hyperlink target.'''
    
    def __init__(self, target_uri: str):
        '''Creates the new instance.
        
        :param target_uri: The external target URI.'''
        ...
    
    @property
    def target_uri(self) -> str:
        '''Gets the target URI.'''
        ...
    
    ...

class XpsFileResource:
    '''Class incapsulating common features of all file resources.'''
    
    ...

class XpsFont(aspose.page.xps.xpsmodel.XpsFileResource):
    '''Class incapsulating a TrueType font resource.'''
    
    ...

class XpsGlyphs(aspose.page.xps.xpsmodel.XpsContentElement):
    '''Class incapsulating Glyphs element features.
    This element represents a run of uniformly-formatted text from a single font.
    It provides information necessary for accurate rendering and supports search
    and selection features in viewing consumers.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Clone this glyphs.
        
        :returns: Clone of this glyphs.'''
        ...
    
    @property
    def bidi_level(self) -> int:
        '''Returns/sets the value specifying the Unicode algorithm bidirectional nesting level.
        Even values imply left-to-right layout, odd values imply right-to-left layout.
        Right-to-left layout places the run origin at the right side of the first glyph,
        with positive advance widths (representing advances to the left) placing subsequent
        glyphs to the left of the previous glyph.'''
        ...
    
    @bidi_level.setter
    def bidi_level(self, value: int):
        ...
    
    @property
    def fill(self) -> aspose.page.xps.xpsmodel.XpsBrush:
        '''Returns/sets the brush used to fill the shape of the rendered glyphs.'''
        ...
    
    @fill.setter
    def fill(self, value: aspose.page.xps.xpsmodel.XpsBrush):
        ...
    
    @property
    def font(self) -> aspose.page.xps.xpsmodel.XpsFont:
        '''Returns font resource for the TrueType font used to typeset elements text.'''
        ...
    
    @property
    def font_rendering_em_size(self) -> float:
        '''Returns/sets the font size in drawing surface units, expressed as a float
        in units of the effective coordinate space.'''
        ...
    
    @font_rendering_em_size.setter
    def font_rendering_em_size(self, value: float):
        ...
    
    @property
    def origin_x(self) -> float:
        '''Returns/sets the x coordinate of the first glyph in the run,
        in units of the effective coordinate space.'''
        ...
    
    @origin_x.setter
    def origin_x(self, value: float):
        ...
    
    @property
    def origin_y(self) -> float:
        '''Returns/sets the y coordinate of the first glyph in the run,
        in units of the effective coordinate space.'''
        ...
    
    @origin_y.setter
    def origin_y(self, value: float):
        ...
    
    @property
    def is_sideways(self) -> bool:
        '''Returns/sets the value indicating that a glyph is turned on its side,
        with the origin being defined as the top center of the unturned glyph.'''
        ...
    
    @is_sideways.setter
    def is_sideways(self, value: bool):
        ...
    
    @property
    def unicode_string(self) -> str:
        '''Returns/sets the string of text rendered by the Glyphs element.
        The text is specified as Unicode code points.'''
        ...
    
    @unicode_string.setter
    def unicode_string(self, value: str):
        ...
    
    @property
    def style_simulations(self) -> aspose.page.xps.xpsmodel.XpsStyleSimulations:
        '''Returns/sets the value specifying a style simulation.'''
        ...
    
    @style_simulations.setter
    def style_simulations(self, value: aspose.page.xps.xpsmodel.XpsStyleSimulations):
        ...
    
    ...

class XpsGradientBrush(aspose.page.xps.xpsmodel.XpsTransformableBrush):
    '''Class incapsulating common features of LinerGradientBrush and RadialGradientBrush elements.'''
    
    @property
    def gradient_stops(self) -> None:
        '''Returns/sets list of gradient stops that comprise the gradient.'''
        ...
    
    @gradient_stops.setter
    def gradient_stops(self, value: None):
        ...
    
    @property
    def color_interpolation_mode(self) -> aspose.page.xps.xpsmodel.XpsColorInterpolationMode:
        '''Returns/sets value specifying the gamma function for color interpolation. The gamma adjustment
        should not be applied to the alpha component, if specified.'''
        ...
    
    @color_interpolation_mode.setter
    def color_interpolation_mode(self, value: aspose.page.xps.xpsmodel.XpsColorInterpolationMode):
        ...
    
    @property
    def spread_method(self) -> aspose.page.xps.xpsmodel.XpsSpreadMethod:
        '''Returns/sets value describing how the brush should fill the content area outside of the primary,
        initial gradient area.'''
        ...
    
    @spread_method.setter
    def spread_method(self, value: aspose.page.xps.xpsmodel.XpsSpreadMethod):
        ...
    
    ...

class XpsGradientStop(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating GradientStop element features.
    This  element is used by both the LinearGradientBrush and RadialGradientBrush elements to define
    the location and range of color progression for rendering a gradient.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsGradientStop:
        '''Clones this gradient stop.
        
        :returns: Clone of this gradient stop.'''
        ...
    
    @property
    def color(self) -> aspose.page.xps.xpsmodel.XpsColor:
        '''The gradient stop color.'''
        ...
    
    @property
    def offset(self) -> float:
        '''Returns/sets the gradient offset. The offset indicates a point along the progression of
        the gradient at which a color is specified. Colors between gradient offsets in
        the progression are interpolated.'''
        ...
    
    ...

class XpsHyperlinkElement(aspose.page.xps.xpsmodel.XpsElement):
    '''Incapsulates common features of XPS elements that can be a hyperlink.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    @property
    def hyperlink_target(self) -> aspose.page.xps.xpsmodel.XpsHyperlinkTarget:
        '''Returns/sets hyperlink target object.'''
        ...
    
    @hyperlink_target.setter
    def hyperlink_target(self, value: aspose.page.xps.xpsmodel.XpsHyperlinkTarget):
        ...
    
    ...

class XpsHyperlinkTarget:
    '''Base class for a hyperlink target.'''
    
    ...

class XpsIccBasedColor(aspose.page.xps.xpsmodel.XpsColor):
    '''Incapsulates ICC based color.'''
    
    def to_color(self) -> aspose.pydrawing.Color:
        '''Convenience method for getting .NET native representation of ICC based color.
        
        :returns:  structure.'''
        ...
    
    @property
    def icc_profile(self) -> aspose.page.xps.xpsmodel.XpsIccProfile:
        '''Returns ICC profile resource the color based on.'''
        ...
    
    ...

class XpsIccProfile(aspose.page.xps.xpsmodel.XpsFileResource):
    '''Class incapsulating an ICC profile resource.'''
    
    ...

class XpsImage(aspose.page.xps.xpsmodel.XpsFileResource):
    '''Class incapsulating an image resource.'''
    
    ...

class XpsImageBrush(aspose.page.xps.xpsmodel.XpsTilingBrush):
    '''Class incapsulating ImageBrush property element features.
    This element is used to fill a region with an image.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsImageBrush:
        '''Clones this image brush.
        
        :returns: Clone of this image brush.'''
        ...
    
    @property
    def image_source(self) -> str:
        '''Returns the URI of an image resource.'''
        ...
    
    @property
    def image(self) -> aspose.page.xps.xpsmodel.XpsImage:
        '''Returns image resource used to for the brush.'''
        ...
    
    ...

class XpsLinearGradientBrush(aspose.page.xps.xpsmodel.XpsGradientBrush):
    '''Class incapsulating LinearGradientBrush property element features.
    This element is used to specify a linear gradient brush along a vector.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsLinearGradientBrush:
        '''Clones this linear gradient brush.
        
        :returns: Clone of this linear gradient brush.'''
        ...
    
    @property
    def start_point(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the starting point of the linear gradient.'''
        ...
    
    @start_point.setter
    def start_point(self, value: aspose.pydrawing.PointF):
        ...
    
    @property
    def end_point(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the end point of the linear gradient.'''
        ...
    
    @end_point.setter
    def end_point(self, value: aspose.pydrawing.PointF):
        ...
    
    ...

class XpsMatrix(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating MatrixTransform property element features.
    This element defines an arbitrary affine matrix transformation used to manipulate the coordinate
    systems of elements.'''
    
    @overload
    def transform_points(self, points: list[aspose.pydrawing.PointF], start_index: int, number_of_points: int) -> None:
        '''Applies the affine transformation represented by this Matrix to a specified part of array of points.
        
        :param points: The points.
        :param start_index: The start index.
        :param number_of_points: The number of points.'''
        ...
    
    @overload
    def transform_points(self, points: list[aspose.pydrawing.PointF]) -> None:
        '''Applies the affine transformation represented by this Matrix to a specified array of points.
        
        :param points: The points.'''
        ...
    
    @overload
    def scale(self, scale_x: float, scale_y: float, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Applies the specified scale vector (scaleX and scaleY) to this Matrix in order
        specified by .
        
        :param scale_x: The scale X.
        :param scale_y: The scale Y.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def scale(self, scale_x: float, scale_y: float) -> None:
        '''Applies the specified scale vector (scaleX and scaleY) to this Matrix in default (Prepend) order.
        
        :param scale_x: The scale x.
        :param scale_y: The scale y.'''
        ...
    
    @overload
    def translate(self, offset_x: float, offset_y: float, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Applies the specified translation vector to this Matrix in order specified by .
        
        :param offset_x: The offset X.
        :param offset_y: The offset Y.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def translate(self, offset_x: float, offset_y: float) -> None:
        '''Applies the specified translation vector to this Matrix.
        
        :param offset_x: The offset X.
        :param offset_y: The offset Y.'''
        ...
    
    @overload
    def multiply(self, matrix: aspose.pydrawing.Drawing2D.Matrix, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Multiplies this matrix by the matrix specified by the
        in order specified by.
        
        :param matrix: The matrix.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def multiply(self, matrix: aspose.pydrawing.Drawing2D.Matrix) -> None:
        '''Multiplies this matrix by the matrix specified by the
        in default (Prepend) order.
        
        :param matrix: The matrix.'''
        ...
    
    @overload
    def multiply(self, matrix: aspose.page.xps.xpsmodel.XpsMatrix, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Multiplies this matrix by the matrix specified by the
        in order specified by.
        
        :param matrix: The matrix.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def multiply(self, matrix: aspose.page.xps.xpsmodel.XpsMatrix) -> None:
        '''Multiplies this matrix by the matrix specified by the
        in default (Prepend) order.
        
        :param matrix: The matrix.'''
        ...
    
    @overload
    def rotate(self, angle: float, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Applies clockwise rotation by  to this Matrix in order
        specified by.
        
        :param angle: The angle.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def rotate(self, angle: float) -> None:
        '''Applies clockwise rotation by  to this Matrix in default (Prepend) order.
        
        :param angle: The angle.'''
        ...
    
    @overload
    def rotate_around(self, angle: float, pivot: aspose.pydrawing.PointF, matrix_order: aspose.pydrawing.Drawing2D.MatrixOrder) -> None:
        '''Applies clockwise rotation by  around the
        to this Matrix in order specified by.
        
        :param angle: The angle.
        :param pivot: The pivot point.
        :param matrix_order: The order.'''
        ...
    
    @overload
    def rotate_around(self, angle: float, pivot: aspose.pydrawing.PointF) -> None:
        '''Applies clockwise rotation by  around the
        to this Matrix in default (Prepend) order.
        
        :param angle: The angle.
        :param pivot: The pivot point.'''
        ...
    
    def transform_point(self, point: aspose.pydrawing.PointF) -> aspose.pydrawing.PointF:
        '''Applies the affine transformation represented by this Matrix to a specified point.
        
        :param point: The point.
        :returns: Transformed point'''
        ...
    
    def transform(self, rect: aspose.pydrawing.RectangleF) -> aspose.pydrawing.RectangleF:
        '''Applies the affine transformation represented by this Matrix to a specified rectangle.
        
        :param rect: The rectangle.
        :returns: Transformed rectangle'''
        ...
    
    def skew(self, skew_x: float, skew_y: float) -> None:
        '''Applies specified skew transformation to this Matrix.
        
        :param skew_x: The skew x.
        :param skew_y: The skew y.'''
        ...
    
    def reset(self) -> None:
        '''Resets this Matrix to identity matrix.'''
        ...
    
    @staticmethod
    def equals(self, a: aspose.page.xps.xpsmodel.XpsMatrix, b: aspose.page.xps.xpsmodel.XpsMatrix) -> bool:
        '''The actual implementation.
        
        :param a: The first matrix.
        :param b: The second matrix.
        :returns: [true] if martrix are equals'''
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsMatrix:
        '''Clones this transformation matrix.
        
        :returns: Clone of this transformation matrix.'''
        ...
    
    @property
    def m11(self) -> float:
        '''Gets the M11 element.'''
        ...
    
    @property
    def m12(self) -> float:
        '''Gets the M12 element.'''
        ...
    
    @property
    def m21(self) -> float:
        '''Gets the M21 element.'''
        ...
    
    @property
    def m22(self) -> float:
        '''Gets the M22 element.'''
        ...
    
    @property
    def m31(self) -> float:
        '''Gets the M31 element.'''
        ...
    
    @property
    def m32(self) -> float:
        '''Gets the M32 element.'''
        ...
    
    @property
    def is_identity(self) -> bool:
        '''Gets a value indicating whether this instance is identity matrix.'''
        ...
    
    ...

class XpsObject:
    '''Class incapsulating common XPS model object features.'''
    
    ...

class XpsPage(aspose.page.xps.xpsmodel.XpsElement):
    '''Class incapsulating FixedPage element features.
    This element contains the contents of a page and is the root element of a FixedPage part.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Clones this page.
        
        :returns: Clone of this page.'''
        ...
    
    @property
    def height(self) -> float:
        '''Returns/sets height of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @height.setter
    def height(self, value: float):
        ...
    
    @property
    def width(self) -> float:
        '''Returns/sets width of the page, expressed as a real number in
        units of the effective coordinate space.'''
        ...
    
    @width.setter
    def width(self, value: float):
        ...
    
    @property
    def xml_lang(self) -> str:
        '''Returns/sets value specifying the default language used for
        the current element and for any child or descendant elements.'''
        ...
    
    @xml_lang.setter
    def xml_lang(self, value: str):
        ...
    
    ...

class XpsPageLinkTarget(aspose.page.xps.xpsmodel.XpsHyperlinkTarget):
    '''Class incapsulating the page hyperlink target.'''
    
    def __init__(self, target_page_number: int):
        '''Creates the new instance.
        
        :param target_page_number: The absolute page number within
                                   the whole XPS document (fixed document sequence).'''
        ...
    
    @property
    def target_page_number(self) -> int:
        '''Gets the page number that the parent XPS element refers to.'''
        ...
    
    ...

class XpsPath(aspose.page.xps.xpsmodel.XpsContentElement):
    '''Class incapsulating Path element features.
    This element is the sole means of adding vector graphics and images to a fixed page.
    It defines a single vector graphic to be rendered on a page.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Clones this path.
        
        :returns: Clone this path.'''
        ...
    
    @property
    def fill(self) -> aspose.page.xps.xpsmodel.XpsBrush:
        '''Returns/sets the brush used to paint the geometry specified
        by the Data property of the path.'''
        ...
    
    @fill.setter
    def fill(self, value: aspose.page.xps.xpsmodel.XpsBrush):
        ...
    
    @property
    def data(self) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Returns/sets the geometry of the path.'''
        ...
    
    @data.setter
    def data(self, value: aspose.page.xps.xpsmodel.XpsPathGeometry):
        ...
    
    @property
    def stroke(self) -> aspose.page.xps.xpsmodel.XpsBrush:
        '''Returns/sets the brush used to draw the stroke.'''
        ...
    
    @stroke.setter
    def stroke(self, value: aspose.page.xps.xpsmodel.XpsBrush):
        ...
    
    @property
    def stroke_dash_array(self) -> list[float]:
        '''Returns/sets the array specifying the length of dashes and gaps of the outline stroke.'''
        ...
    
    @stroke_dash_array.setter
    def stroke_dash_array(self, value: list[float]):
        ...
    
    @property
    def stroke_dash_cap(self) -> aspose.page.xps.xpsmodel.XpsDashCap:
        '''Returns/sets the value specifying how the ends of each dash are drawn.'''
        ...
    
    @stroke_dash_cap.setter
    def stroke_dash_cap(self, value: aspose.page.xps.xpsmodel.XpsDashCap):
        ...
    
    @property
    def stroke_dash_offset(self) -> float:
        '''Returns/sets the start point for repeating the dash array pattern.
        If this value is omitted, the dash array aligns with the origin of the stroke.'''
        ...
    
    @stroke_dash_offset.setter
    def stroke_dash_offset(self, value: float):
        ...
    
    @property
    def stroke_start_line_cap(self) -> aspose.page.xps.xpsmodel.XpsLineCap:
        '''Returns/sets the value defining the shape of the beginning of the first dash in a stroke.'''
        ...
    
    @stroke_start_line_cap.setter
    def stroke_start_line_cap(self, value: aspose.page.xps.xpsmodel.XpsLineCap):
        ...
    
    @property
    def stroke_end_line_cap(self) -> aspose.page.xps.xpsmodel.XpsLineCap:
        '''Returns/sets the value defining the shape of the end of the last dash in a stroke.'''
        ...
    
    @stroke_end_line_cap.setter
    def stroke_end_line_cap(self, value: aspose.page.xps.xpsmodel.XpsLineCap):
        ...
    
    @property
    def stroke_line_join(self) -> aspose.page.xps.xpsmodel.XpsLineJoin:
        '''Returns/sets the value defining the shape of the beginning of the first dash in a stroke.'''
        ...
    
    @stroke_line_join.setter
    def stroke_line_join(self, value: aspose.page.xps.xpsmodel.XpsLineJoin):
        ...
    
    @property
    def stroke_miter_limit(self) -> float:
        '''Returns/sets the ratio between the maximum miter length and half of the stroke thickness.
        This value is significant only if the ``StrokeLineJoin`` attribute specifies ``Miter``.'''
        ...
    
    @stroke_miter_limit.setter
    def stroke_miter_limit(self, value: float):
        ...
    
    @property
    def stroke_thickness(self) -> float:
        '''Returns/sets the thickness of a stroke, in units of
        the effective coordinate space (includes the path's render transform).
        The stroke is drawn on top of the boundary of the geometry specified
        by the Path element’s Data property. Half of the StrokeThickness extends
        outside of the geometry specified by the Data property and the other half
        extends inside of the geometry.'''
        ...
    
    @stroke_thickness.setter
    def stroke_thickness(self, value: float):
        ...
    
    ...

class XpsPathFigure(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating PathFigure element features.
    This element is composed of a set of one or more line or curve segments.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        '''Clones this path figure.
        
        :returns: Clone of this path figure.'''
        ...
    
    def add(self, obj: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        ...
    
    def remove(self, obj: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        ...
    
    def insert(self, index: int, obj: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        ...
    
    def remove_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        ...
    
    @property
    def segments(self) -> None:
        '''Return list of child path segments.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        '''Returns/sets the value indicating whether the path figure is closed.'''
        ...
    
    @is_closed.setter
    def is_closed(self, value: bool):
        ...
    
    @property
    def start_point(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the starting point for the first segment of the path figure.'''
        ...
    
    @start_point.setter
    def start_point(self, value: aspose.pydrawing.PointF):
        ...
    
    @property
    def is_filled(self) -> bool:
        '''Returns/sets value indicating whether the path figure is used in computing
        the area of the containing path geometry.'''
        ...
    
    @is_filled.setter
    def is_filled(self, value: bool):
        ...
    
    @property
    def count(self) -> int:
        ...
    
    ...

class XpsPathGeometry(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating PathGeometry property element features.
    This element contains a set of path figures specified either with the Figures attribute or
    with a child PathFigure element.'''
    
    def __getitem__(self, index: int) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    def add_segment(self, segment: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        '''Adds a path segment to the list of child segments of the last pah figure.
        
        :param segment: The path segment to be added.
        :returns: Added path segment.'''
        ...
    
    def insert_segment(self, index: int, segment: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        '''Inserts a path segment to the list of child segments of
        the last path figure at  position.
        
        :param index: Position at which a segment should be inserted.
        :param segment: A path segment to be inserted.
        :returns: Inserted path segment.'''
        ...
    
    def remove_segment(self, segment: aspose.page.xps.xpsmodel.XpsPathSegment) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        '''Removes a path segment from the list of child segments of the last path figure.
        
        :param segment: The path segment to be removed.
        :returns: Removed path segment.'''
        ...
    
    def remove_segment_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsPathSegment:
        '''Removes a path segment from the list of child segments of
        the last path figure at  position.
        
        :param index: Position at which a path segment should be removed.
        :returns: Removed path segment.'''
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Clones this path geometry.
        
        :returns: Clone of this path geometry.'''
        ...
    
    def add(self, obj: aspose.page.xps.xpsmodel.XpsPathFigure) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    def remove(self, obj: aspose.page.xps.xpsmodel.XpsPathFigure) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    def insert(self, index: int, obj: aspose.page.xps.xpsmodel.XpsPathFigure) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    def remove_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    @property
    def fill_rule(self) -> aspose.page.xps.xpsmodel.XpsFillRule:
        '''Returns/sets the value specifying how the intersecting areas of geometric
        shapes are combined to form a region.'''
        ...
    
    @fill_rule.setter
    def fill_rule(self, value: aspose.page.xps.xpsmodel.XpsFillRule):
        ...
    
    @property
    def transform(self) -> aspose.page.xps.xpsmodel.XpsMatrix:
        '''Returns/sets the affine transformation matrix establishing the local matrix transformation
        that is applied to all child and descendant elements of the path geometry before it is used
        for filling, clipping, or stroking.'''
        ...
    
    @transform.setter
    def transform(self, value: aspose.page.xps.xpsmodel.XpsMatrix):
        ...
    
    @property
    def path_figures(self) -> None:
        '''Returns list of child path figures.'''
        ...
    
    @property
    def count(self) -> int:
        ...
    
    ...

class XpsPathPolySegment(aspose.page.xps.xpsmodel.XpsPathSegment):
    '''Class incapsulating common features of PolyLineSegment, PolyBézierSegment and
    PolyQuadraticBézierSegment elements.'''
    
    ...

class XpsPathSegment(aspose.page.xps.xpsmodel.XpsObject):
    '''Class incapsulating common features of all path segment elements.'''
    
    @property
    def is_stroked(self) -> bool:
        '''Returns/sets the value specifying whether the stroke for this segment of the path is drawn.'''
        ...
    
    @is_stroked.setter
    def is_stroked(self, value: bool):
        ...
    
    ...

class XpsPolyBezierSegment(aspose.page.xps.xpsmodel.XpsPathPolySegment):
    '''Class incapsulating PolyBezierSegment element features.
    This element describes a set of cubic Bézier curves.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPolyBezierSegment:
        '''Clones this set of cubic Bézier curves.
        
        :returns: Clone of this set of cubic Bézier curves.'''
        ...
    
    ...

class XpsPolyLineSegment(aspose.page.xps.xpsmodel.XpsPathPolySegment):
    '''Class incapsulating PolyLineSegment element features.
    This element describes a polygonal drawing containing an arbitrary number of individual vertices.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPolyLineSegment:
        '''Clones this polygon.
        
        :returns: Clone of this polygon.'''
        ...
    
    ...

class XpsPolyQuadraticBezierSegment(aspose.page.xps.xpsmodel.XpsPathPolySegment):
    '''Class incapsulating PolyQuadraticBezierSegment element features.
    This element describes a set of quadratic Bézier curves from the previous point in
    the path figure through a set of vertices, using specified control points.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsPolyQuadraticBezierSegment:
        '''Clones this set of quadratic Bézier curves.
        
        :returns: Clone of this set of quadratic Bézier curves.'''
        ...
    
    ...

class XpsRadialGradientBrush(aspose.page.xps.xpsmodel.XpsGradientBrush):
    '''Class incapsulating RadialGradientBrush property element features.
    This element is used to specify a radial gradient brush.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsRadialGradientBrush:
        '''Clones this radial graduent brush.
        
        :returns: Clone of this radial graduent brush.'''
        ...
    
    @property
    def center(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the center point of the radial
        gradient (that is, the center of the ellipse).'''
        ...
    
    @center.setter
    def center(self, value: aspose.pydrawing.PointF):
        ...
    
    @property
    def gradient_origin(self) -> aspose.pydrawing.PointF:
        '''Returns/sets the origin point of the radial gradient.'''
        ...
    
    @gradient_origin.setter
    def gradient_origin(self, value: aspose.pydrawing.PointF):
        ...
    
    @property
    def radius_x(self) -> float:
        '''Returns/sets the radius in the x dimension of the ellipse which defines the radial gradient.'''
        ...
    
    @radius_x.setter
    def radius_x(self, value: float):
        ...
    
    @property
    def radius_y(self) -> float:
        '''Returns/sets the radius in the y dimension of the ellipse which defines the radial gradient.'''
        ...
    
    @radius_y.setter
    def radius_y(self, value: float):
        ...
    
    ...

class XpsRgbColor(aspose.page.xps.xpsmodel.XpsColor):
    '''Incapsulates RGB color of any color space (sRGB or scRGB).'''
    
    def to_color(self) -> aspose.pydrawing.Color:
        '''Convenience method for getting .NET native representation of RGB color.
        
        :returns:  structure.'''
        ...
    
    ...

class XpsSolidColorBrush(aspose.page.xps.xpsmodel.XpsBrush):
    '''Class incapsulating SolidColorBrush property element features.
    This element is used to fill defined geometric regions with a solid color.'''
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsSolidColorBrush:
        '''Clones this solid color brush.
        
        :returns: Clone of this solid color brush.'''
        ...
    
    @property
    def color(self) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Returns/sets the color for filled elements.'''
        ...
    
    @color.setter
    def color(self, value: aspose.page.xps.xpsmodel.XpsColor):
        ...
    
    ...

class XpsTilingBrush(aspose.page.xps.xpsmodel.XpsTransformableBrush):
    '''Class incapsulating common features of tiling brushes elements (VisualBrush and ImageBrush).'''
    
    @property
    def viewbox(self) -> aspose.pydrawing.RectangleF:
        '''Returns/sets the region of the source content of the brush that is to be mapped to the viewport.'''
        ...
    
    @viewbox.setter
    def viewbox(self, value: aspose.pydrawing.RectangleF):
        ...
    
    @property
    def viewport(self) -> aspose.pydrawing.RectangleF:
        '''Returns/sets the position and dimensions of the first brush tile. Subsequent tiles are positioned
        relative to this tile, as specified by the tile mode.'''
        ...
    
    @viewport.setter
    def viewport(self, value: aspose.pydrawing.RectangleF):
        ...
    
    @property
    def tile_mode(self) -> aspose.page.xps.xpsmodel.XpsTileMode:
        '''Returns/sets value specifying how tiling is performed in the filled geometry.'''
        ...
    
    @tile_mode.setter
    def tile_mode(self, value: aspose.page.xps.xpsmodel.XpsTileMode):
        ...
    
    ...

class XpsTransformableBrush(aspose.page.xps.xpsmodel.XpsBrush):
    '''Class incapsulating common features of transformable brushes elements (all except SolidColorBrush).'''
    
    @property
    def transform(self) -> aspose.page.xps.xpsmodel.XpsMatrix:
        '''Returns/sets the matrix transformation applied to the coordinate space of the brush.
        The Transform property is concatenated with the current effective render transform
        to yield an effective render transform local to the brush. The viewport for the brush
        is transformed using the local effective render transform.'''
        ...
    
    @transform.setter
    def transform(self, value: aspose.page.xps.xpsmodel.XpsMatrix):
        ...
    
    ...

class XpsVisualBrush(aspose.page.xps.xpsmodel.XpsTilingBrush):
    '''Class incapsulating VisualBrush property element features.
    This element is used to fill a region with a drawing.'''
    
    def set_visual(self, visual: aspose.page.xps.xpsmodel.XpsContentElement) -> None:
        '''Sets  as Visual element of visual brush.
        
        :param visual: The element.'''
        ...
    
    def clone(self) -> aspose.page.xps.xpsmodel.XpsVisualBrush:
        '''Clones this visual brush.
        
        :returns: Clone of this visual brush.'''
        ...
    
    @property
    def visual(self) -> aspose.page.xps.xpsmodel.XpsContentElement:
        '''Returns/sets a Path, Glyphs, or Canvas element used to draw the brush’s source content.'''
        ...
    
    ...

class XpsColorInterpolationMode:
    '''Valid values of gradient brushes' ColorInterpolationMode property.'''
    
    S_RGB_LINEAR_INTERPOLATION: int
    SC_RGB_LINEAR_INTERPOLATION: int

class XpsDashCap:
    '''Valid values of Path element's StrokeDashCap property.'''
    
    FLAT: int
    ROUND: int
    SQUARE: int
    TRIANGLE: int

class XpsEdgeMode:
    '''Valid values of Canvas element's RenderOptions.EdgeMode property.'''
    
    NONE: int
    ALIASED: int

class XpsFillRule:
    '''Valid values of PathGeometry element's FillRule property.'''
    
    EVEN_ODD: int
    NON_ZERO: int

class XpsLineCap:
    '''Valid values of Path element's StrokeStartLineCap and StrokeEndLineCap properties.'''
    
    FLAT: int
    ROUND: int
    SQUARE: int
    TRIANGLE: int

class XpsLineJoin:
    '''Valid values of Path element's StrokeLineJoin property.'''
    
    MITER: int
    BEVEL: int
    ROUND: int

class XpsSpreadMethod:
    '''Valid values of gradient brushes' SpreadMethod property.'''
    
    PAD: int
    REFLECT: int
    REPEAT: int

class XpsStyleSimulations:
    '''Valid values of Glyphs element's StyleSimulations property.'''
    
    NONE: int
    ITALIC_SIMULATION: int
    BOLD_SIMULATION: int
    BOLD_ITALIC_SIMULATION: int

class XpsSweepDirection:
    '''Valid values of ArcSegment element's SweepDirection property.'''
    
    COUNTERCLOCKWISE: int
    CLOCKWISE: int

class XpsTileMode:
    '''Valid values of tiling brushes' TileMode property.'''
    
    NONE: int
    TILE: int
    FLIP_X: int
    FLIP_Y: int
    FLIP_XY: int

