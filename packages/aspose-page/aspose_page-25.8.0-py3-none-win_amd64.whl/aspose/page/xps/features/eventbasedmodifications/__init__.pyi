import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class BeforePageSavingEventHandler:
    '''The base class for before-page-saving event handlers.'''
    
    ...

class IModificationAPI:
    '''The basic interface for any XPS element's modification API.'''
    
    ...

class PageAPI:
    '''The **Page** element modification API.'''
    
    @overload
    def add_canvas(self, canvas: aspose.page.xps.xpsmodel.XpsCanvas) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Adds a canvas.
        
        :param canvas: The canvas to be added.
        :returns: Added canvas.'''
        ...
    
    @overload
    def add_canvas(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Adds a new canvas to the page.
        
        :returns: Added canvas.'''
        ...
    
    @overload
    def add_path(self, path: aspose.page.xps.xpsmodel.XpsPath) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Adds a path element.
        
        :param path: The path to be added.
        :returns: Added path.'''
        ...
    
    @overload
    def add_path(self, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Adds a new path to the page.
        
        :param data: The geometry of the path.
        :returns: Added path.'''
        ...
    
    @overload
    def add_glyphs(self, glyphs: aspose.page.xps.xpsmodel.XpsGlyphs) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Adds a glyphs element.
        
        :param glyphs: The glyphs element to be added.
        :returns: Added glyphs element.'''
        ...
    
    @overload
    def add_glyphs(self, font_family: str, font_rendering_em_size: float, font_style: aspose.pydrawing.FontStyle, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Adds new glyphs to the page.
        
        :param font_family: Font family.
        :param font_rendering_em_size: Font size.
        :param font_style: Font style.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: Added glyphs.'''
        ...
    
    @overload
    def add_glyphs(self, font: aspose.page.xps.xpsmodel.XpsFont, font_rendering_em_size: float, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Adds new glyphs to the page.
        
        :param font: Font resource.
        :param font_rendering_em_size: Font size.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: Added glyphs.'''
        ...
    
    @overload
    def create_glyphs(self, font_family: str, font_rendering_em_size: float, font_style: aspose.pydrawing.FontStyle, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Creates new glyphs.
        
        :param font_family: Font family.
        :param font_rendering_em_size: Font size.
        :param font_style: Font style.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: New glyphs.'''
        ...
    
    @overload
    def create_glyphs(self, font: aspose.page.xps.xpsmodel.XpsFont, font_rendering_em_size: float, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Creates new glyphs.
        
        :param font: Font resource.
        :param font_rendering_em_size: Font size.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: New glyphs.'''
        ...
    
    @overload
    def insert_glyphs(self, index: int, font_family: str, font_size: float, font_style: aspose.pydrawing.FontStyle, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Inserts new glyphs to the page at  position.
        
        :param index: Position at which new glyphs should be inserted.
        :param font_family: Font family.
        :param font_size: Font size.
        :param font_style: Font style.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: Inserted glyphs.'''
        ...
    
    @overload
    def insert_glyphs(self, index: int, font: aspose.page.xps.xpsmodel.XpsFont, font_size: float, origin_x: float, origin_y: float, unicode_string: str) -> aspose.page.xps.xpsmodel.XpsGlyphs:
        '''Inserts new glyphs to the page at  position.
        
        :param index: Position at which new glyphs should be inserted.
        :param font: Font resource.
        :param font_size: Font size.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: Inserted glyphs.'''
        ...
    
    @overload
    def create_path_geometry(self, abbreviated_geometry: str) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a new path geometry specified with abbreviated form.
        
        :param abbreviated_geometry: Abbreviated form of path geometry.
        :returns: New path geometry.'''
        ...
    
    @overload
    def create_path_geometry(self) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a new path geometry.
        
        :returns: New path geometry.'''
        ...
    
    @overload
    def create_path_geometry(self, path_figures) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        ...
    
    @overload
    def create_path_figure(self, start_point: aspose.pydrawing.PointF, is_closed: bool) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        '''Creates a new path figure.
        
        :param start_point: The starting point for the first segment of the path figure.
        :param is_closed: Specifies whether the path is closed. If set to true, the stroke is drawn
                          "closed", that is, the last point in the last segment of the path figure is connected with
                          the point specified in the StartPoint attribute, otherwise the stroke is drawn "open", and
                          the last point is not connected to the start point. Only applicable if the path figure is
                          used in a Path element that specifies a stroke.
        :returns: New path figure.'''
        ...
    
    @overload
    def create_path_figure(self, start_point: aspose.pydrawing.PointF, segments, is_closed: bool) -> aspose.page.xps.xpsmodel.XpsPathFigure:
        ...
    
    @overload
    def create_solid_color_brush(self, color: aspose.page.xps.xpsmodel.XpsColor) -> aspose.page.xps.xpsmodel.XpsSolidColorBrush:
        '''Creates a new solid color brush.
        
        :param color: The color for filled elements.
        :returns: New solid color brush.'''
        ...
    
    @overload
    def create_solid_color_brush(self, color: aspose.pydrawing.Color) -> aspose.page.xps.xpsmodel.XpsSolidColorBrush:
        '''Creates a new solid color brush.
        
        :param color: The color for filled elements.
        :returns: New solid color brush.'''
        ...
    
    @overload
    def create_gradient_stop(self, color: aspose.page.xps.xpsmodel.XpsColor, offset: float) -> aspose.page.xps.xpsmodel.XpsGradientStop:
        '''Creates a new gradient stop.
        
        :param color: The gradient stop color.
        :param offset: The gradient offset.
        :returns: New gradient stop.'''
        ...
    
    @overload
    def create_gradient_stop(self, color: aspose.pydrawing.Color, offset: float) -> aspose.page.xps.xpsmodel.XpsGradientStop:
        '''Creates a new gradient stop.
        
        :param color: The gradient stop color.
        :param offset: The gradient offset.
        :returns: New gradient stop.'''
        ...
    
    @overload
    def create_linear_gradient_brush(self, gradient_stops, start_point: aspose.pydrawing.PointF, end_point: aspose.pydrawing.PointF) -> aspose.page.xps.xpsmodel.XpsLinearGradientBrush:
        ...
    
    @overload
    def create_linear_gradient_brush(self, start_point: aspose.pydrawing.PointF, end_point: aspose.pydrawing.PointF) -> aspose.page.xps.xpsmodel.XpsLinearGradientBrush:
        '''Creates a new linear gradient brush.
        
        :param start_point: The starting point of the linear gradient.
        :param end_point: The end point of the linear gradient.
        :returns: New linear gradient brush.'''
        ...
    
    @overload
    def create_radial_gradient_brush(self, gradient_stops, center: aspose.pydrawing.PointF, gradient_origin: aspose.pydrawing.PointF, radius_x: float, radius_y: float) -> aspose.page.xps.xpsmodel.XpsRadialGradientBrush:
        ...
    
    @overload
    def create_radial_gradient_brush(self, center: aspose.pydrawing.PointF, gradient_origin: aspose.pydrawing.PointF, radius_x: float, radius_y: float) -> aspose.page.xps.xpsmodel.XpsRadialGradientBrush:
        '''Creates a new radial gradient brush.
        
        :param center: The center point of the radial gradient (that is, the center of the ellipse).
        :param gradient_origin: The origin point of the radial gradient.
        :param radius_x: The radius in the x dimension of the ellipse which defines the radial gradient.
        :param radius_y: The radius in the y dimension of the ellipse which defines the radial gradient.
        :returns: New radial gradient brush.'''
        ...
    
    @overload
    def create_image_brush(self, image: aspose.page.xps.xpsmodel.XpsImage, viewbox: aspose.pydrawing.RectangleF, viewport: aspose.pydrawing.RectangleF) -> aspose.page.xps.xpsmodel.XpsImageBrush:
        '''Creates a new image brush.
        
        :param image: An image resource.
        :param viewbox: The position and dimensions of the brush's source content.
        :param viewport: The region in the containing coordinate space of the prime brush
                         tile that is (possibly repeatedly) applied to fill the region to which the brush is applied
        :returns: New image brush.'''
        ...
    
    @overload
    def create_image_brush(self, image_path: str, viewbox: aspose.pydrawing.RectangleF, viewport: aspose.pydrawing.RectangleF) -> aspose.page.xps.xpsmodel.XpsImageBrush:
        '''Creates a new image brush.
        
        :param image_path: The path to the image to take as a brush tile.
        :param viewbox: The position and dimensions of the brush's source content.
        :param viewport: The region in the containing coordinate space of the prime brush
                         tile that is (possibly repeatedly) applied to fill the region to which the brush is applied
        :returns: New image brush.'''
        ...
    
    @overload
    def create_color(self, color: aspose.pydrawing.Color) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color.
        
        :param color: A native color instance for RGB color.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, a: int, r: int, g: int, b: int) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in sRGB color space.
        
        :param a: The alpha color component.
        :param r: The red color component.
        :param g: The green color component.
        :param b: The blue color component.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, r: int, g: int, b: int) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in sRGB color space.
        
        :param r: The red color component.
        :param g: The green color component.
        :param b: The blue color component.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, a: float, r: float, g: float, b: float) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in scRGB color space.
        
        :param a: The alpha color component.
        :param r: The red color component.
        :param g: The green color component.
        :param b: The blue color component.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, r: float, g: float, b: float) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in scRGB color space.
        
        :param r: The red color component.
        :param g: The green color component.
        :param b: The blue color component.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, path: str, components: list[float]) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in ICC based color space.
        
        :param path: The path to the ICC profile.
        :param components: Color components.
        :returns: New color.'''
        ...
    
    @overload
    def create_color(self, icc_profile: aspose.page.xps.xpsmodel.XpsIccProfile, components: list[float]) -> aspose.page.xps.xpsmodel.XpsColor:
        '''Creates a new color in ICC based color space.
        
        :param icc_profile: The ICC profile resource.
        :param components: Color components.
        :returns: New color.'''
        ...
    
    def remove_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        '''Removes an element at  position from the page.
        
        :param index: Position at which element should be removed.
        :returns: Removed element.'''
        ...
    
    def create_canvas(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Creates a new canvas.
        
        :returns: New canvas.'''
        ...
    
    def insert_canvas(self, index: int) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Inserts a new canvas to the page at  position.
        
        :param index: Position at which a new canvas should be inserted.
        :returns: Inserted canvas.'''
        ...
    
    def create_path(self, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Creates a new path.
        
        :param data: The geometry of the path.
        :returns: New  path.'''
        ...
    
    def insert_path(self, index: int, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Inserts a new path to the page at  position.
        
        :param index: Position at which a new path should be inserted.
        :param data: The geometry of the path.
        :returns: Inserted path.'''
        ...
    
    def create_matrix(self, m11: float, m12: float, m21: float, m22: float, m31: float, m32: float) -> aspose.page.xps.xpsmodel.XpsMatrix:
        '''Creates a new affine transformation matrix.
        
        :param m11: Element 11.
        :param m12: Element 12.
        :param m21: Element 21.
        :param m22: Element 22.
        :param m31: Element 31.
        :param m32: Element 32.
        :returns: New affine transformation matrix.'''
        ...
    
    def create_arc_segment(self, point: aspose.pydrawing.PointF, size: aspose.pydrawing.SizeF, rotation_angle: float, is_large_arc: bool, sweep_direction: aspose.page.xps.xpsmodel.XpsSweepDirection, is_stroked: bool) -> aspose.page.xps.xpsmodel.XpsArcSegment:
        '''Creates a new elliptical arc segment.
        
        :param point: The endpoint of the elliptical arc.
        :param size: The x and y radius of the elliptical arc as an x,y pair.
        :param rotation_angle: Indicates how the ellipse is rotated relative to the current coordinate system.
        :param is_large_arc: Determines whether the arc is drawn with a sweep of 180 or greater.
        :param sweep_direction: The direction in which the arc is drawn.
        :param is_stroked: Specifies whether the stroke for this segment of the path is drawn.
        :returns: New elliptical arc segment.'''
        ...
    
    def create_poly_line_segment(self, points: list[aspose.pydrawing.PointF], is_stroked: bool) -> aspose.page.xps.xpsmodel.XpsPolyLineSegment:
        '''Creates a new polygonal drawing containing an arbitrary number of individual vertices.
        
        :param points: A set of coordinates for the multiple segments that define the poly line segment.
        :param is_stroked: Specifies whether the stroke for this segment of the path is drawn.
        :returns: New polygonal drawing segment.'''
        ...
    
    def create_poly_bezier_segment(self, points: list[aspose.pydrawing.PointF], is_stroked: bool) -> aspose.page.xps.xpsmodel.XpsPolyBezierSegment:
        '''Creates a new set of cubic Bézier curves.
        
        :param points: Control points for multiple Bézier segments.
        :param is_stroked: Specifies whether the stroke for this segment of the path is drawn.
        :returns: New cubic Bézier curves segment.'''
        ...
    
    def create_poly_quadratic_bezier_segment(self, points: list[aspose.pydrawing.PointF], is_stroked: bool) -> aspose.page.xps.xpsmodel.XpsPolyQuadraticBezierSegment:
        '''Creates a new set of quadratic Bézier curves from the previous point in the path figure through a set
        of vertices, using specified control points.
        
        :param points: Control points for multiple quadratic Bézier segments.
        :param is_stroked: Specifies whether the stroke for this segment of the path is drawn.
        :returns: New quadratic Bézier curves segment.'''
        ...
    
    def create_visual_brush(self, element: aspose.page.xps.xpsmodel.XpsContentElement, viewbox: aspose.pydrawing.RectangleF, viewport: aspose.pydrawing.RectangleF) -> aspose.page.xps.xpsmodel.XpsVisualBrush:
        '''Creates a new visual brush.
        
        :param element: The XPS element (Canvas, Path or Glyphs) for Visual property od visual brush.
        :param viewbox: The position and dimensions of the brush's source content.
        :param viewport: The region in the containing coordinate space of the prime brush
                         tile that is (possibly repeatedly) applied to fill the region to which the brush is applied
        :returns: New visual brush.'''
        ...
    
    def add_outline_entry(self, description: str, outline_level: int, target_page_number: int) -> None:
        '''Adds an outline entry to the document.
        
        :param description: The entry description.
        :param outline_level: The outline level.
        :param target_page_number: The target page number.'''
        ...
    
    @property
    def utils(self) -> aspose.page.xps.DocumentUtils:
        '''Gets the object that provides utilities beyond the formal XPS manipulation API.'''
        ...
    
    @property
    def total_page_count(self) -> int:
        '''Returns the total number of pages in all documents inside XPS document.'''
        ...
    
    @property
    def page_count(self) -> int:
        '''Returns the number of pages in the active document.'''
        ...
    
    @property
    def height(self) -> float:
        '''Returns/sets the height of the page, expressed as a real number
        in units of the effective coordinate space.'''
        ...
    
    @height.setter
    def height(self, value: float):
        ...
    
    @property
    def width(self) -> float:
        '''Returns/sets the width of the page, expressed as a real number in
        units of the effective coordinate space.'''
        ...
    
    @width.setter
    def width(self, value: float):
        ...
    
    ...

