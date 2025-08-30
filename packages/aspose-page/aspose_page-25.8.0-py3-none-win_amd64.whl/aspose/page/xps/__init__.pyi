from aspose.page.xps import features
from aspose.page.xps import presentation
from aspose.page.xps import xpsmetadata
from aspose.page.xps import xpsmodel
import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class DocumentUtils:
    '''This class provides utilities beyond the formal XPS manipulation API.'''
    
    def create_rectangle(self, rectangle: aspose.pydrawing.RectangleF) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a rectangle.
        
        :param rectangle: The rectangle.
        :returns: The XPS path geometry.'''
        ...
    
    def create_ellipse(self, center: aspose.pydrawing.PointF, radius_x: float, radius_y: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing an ellipse.
        
        :param center: The center point of the ellipse.
        :param radius_x: The horizontal radius of the ellipse.
        :param radius_y: The vertical radius of the ellipse.
        :returns: The XPS path geometry.'''
        ...
    
    def create_circle(self, center: aspose.pydrawing.PointF, radius: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a circle.
        
        :param center: The center point of the circle.
        :param radius: The radius of the circle.
        :returns: The XPS path geometry.'''
        ...
    
    def create_regular_inscribed_n_gon(self, n: int, center: aspose.pydrawing.PointF, radius: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a regular n-gon inscribed in a circle.
        
        :param n: The number of vertices.
        :param center: The center of the circle.
        :param radius: The radius of the circle.
        :returns: The XPS path geometry.'''
        ...
    
    def create_regular_circumscribed_n_gon(self, n: int, center: aspose.pydrawing.PointF, radius: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a regular n-gon circumscribed around a circle.
        
        :param n: The number of vertices.
        :param center: The center of the circle.
        :param radius: The radius of the circle.
        :returns: The XPS path geometry.'''
        ...
    
    def create_pie_slice(self, center: aspose.pydrawing.PointF, radius: float, start_angle: float, end_angle: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a circle slice between two radial rays.
        
        :param center: The center of the circle.
        :param radius: The radius of the circle.
        :param start_angle: The angle of the starting ray.
        :param end_angle: The angle of the ending ray.
        :returns: The XPS path geometry.'''
        ...
    
    def create_circular_segment(self, center: aspose.pydrawing.PointF, radius: float, start_angle: float, end_angle: float) -> aspose.page.xps.xpsmodel.XpsPathGeometry:
        '''Creates a path geometry representing a circular segment between two angles.
        
        :param center: The center of the circle.
        :param radius: The radius of the circle.
        :param start_angle: The starting angle.
        :param end_angle: The ending angle.
        :returns: The XPS path geometry.'''
        ...
    
    def create_image(self, file_name: str, image_box: aspose.pydrawing.RectangleF, mode: aspose.page.xps.ImageMode) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Creates a rectangular path filled with an image.
        
        :param file_name: The name of the image file.
        :param image_box: The image box to fill with the image.
        :param mode: Image fit mode.
        :returns: The XPS path.'''
        ...
    
    ...

class LoadOptions:
    '''Basic class for document loading options.'''
    
    ...

class XpsDocument(aspose.page.Document):
    '''Class incapsulating the main entity of XPS document that provides manipulation
    methods for any XPS element.'''
    
    @overload
    def __init__(self):
        '''Creates empty XPS document with default page size.'''
        ...
    
    @overload
    def __init__(self, path: str):
        '''Opens an existing XPS document located at the .
        
        :param path: Location of the document.'''
        ...
    
    @overload
    def __init__(self, path: str, options: aspose.page.xps.LoadOptions):
        '''Opens an existing document located at the  as XPS document.
        
        :param path: Location of the document.
        :param options: Document loading options.'''
        ...
    
    @overload
    def __init__(self, stream: io.BytesIO, options: aspose.page.xps.LoadOptions):
        '''Loads an existing document stored in the  as XPS document.
        
        :param stream: Document stream.
        :param options: Document loading options.'''
        ...
    
    @overload
    def save(self, path: str) -> None:
        '''Saves XPS document to XPS file located at the .
        
        :param path: Location of the document.'''
        ...
    
    @overload
    def save(self, stream: io.BytesIO) -> None:
        '''Saves XPS document to stream.
        
        :param stream: Stream XPS document to be saved into.'''
        ...
    
    @overload
    def save_as_pdf(self, out_pdf_file_path: str, options: aspose.page.xps.presentation.pdf.PdfSaveOptions) -> None:
        '''Saves the document in PDF format.
        
        :param out_pdf_file_path: An output PDF file path.
        :param options: Options for saving the document in PDF format.'''
        ...
    
    @overload
    def save_as_pdf(self, stream: io.BytesIO, options: aspose.page.xps.presentation.pdf.PdfSaveOptions) -> None:
        '''Saves the document in PDF format.
        
        :param stream: The stream to write the output PDF file to.
        :param options: Options for saving the document in PDF format.'''
        ...
    
    @overload
    def save_as_ps(self, out_ps_file_path: str, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves the document in PS format.
        
        :param out_ps_file_path: An output PS file path.
        :param options: Options for saving the document in PS format.'''
        ...
    
    @overload
    def save_as_ps(self, stream: io.BytesIO, options: aspose.page.eps.device.PsSaveOptions) -> None:
        '''Saves the document in PS format.
        
        :param stream: The stream to write the output PS file to.
        :param options: Options for saving the document in PS format.'''
        ...
    
    @overload
    def merge_to_pdf(self, files_for_merge: list[str], out_pdf_file_path: str, options: aspose.page.xps.presentation.pdf.PdfSaveOptions) -> None:
        '''Merging XPS documents to PDF using the  instance.
        
        :param files_for_merge: XPS files for merging with this document to an output device.
        :param out_pdf_file_path: An output PDF file path.
        :param options: Document saving options.'''
        ...
    
    @overload
    def merge_to_pdf(self, files_for_merge: list[str], pdf_stream: io.BytesIO, options: aspose.page.xps.presentation.pdf.PdfSaveOptions) -> None:
        '''Merging XPS documents to PDF using the  instance.
        
        :param files_for_merge: XPS files for merging with this document to an output device.
        :param pdf_stream: An output PDF stream.
        :param options: Document saving options.'''
        ...
    
    @overload
    def merge(self, files_for_merge: list[str], out_xps_file_path: str) -> None:
        '''Merging several XPS files to one XPS document.
        
        :param files_for_merge: XPS files for merging with this document.
        :param out_xps_file_path: An output Xps file path.'''
        ...
    
    @overload
    def merge(self, files_for_merge: list[str], out_stream: io.BytesIO) -> None:
        '''Merging several XPS files to one XPS document.
        
        :param files_for_merge: XPS files for merging with this document.
        :param out_stream: The output stream where to save merged XPS documents.'''
        ...
    
    @overload
    def add_canvas(self, canvas: aspose.page.xps.xpsmodel.XpsCanvas) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Adds a canvas.
        
        :param canvas: The canvas to be added.
        :returns: Added canvas.'''
        ...
    
    @overload
    def add_canvas(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Adds a new canvas to the active page.
        
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
        '''Adds a new path to the active page.
        
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
        '''Adds new glyphs to the active page.
        
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
        '''Adds new glyphs to the active page.
        
        :param font: Font resource.
        :param font_rendering_em_size: Font size.
        :param origin_x: Glyphs origin X coordinate.
        :param origin_y: Glyphs origin Y coordinate.
        :param unicode_string: String to be printed.
        :returns: Added glyphs.'''
        ...
    
    @overload
    def add_document(self, activate: bool) -> None:
        '''Adds an empty document with default page size.
        
        :param activate: Flag indicating whether to select added document as active.'''
        ...
    
    @overload
    def add_document(self, width: float, height: float, activate: bool) -> None:
        '''Adds an empty document with the first page dimensions
         and.
        
        :param width: Width of the first page.
        :param height: Height of the first page.
        :param activate: Flag indicating whether to select added document as active.'''
        ...
    
    @overload
    def insert_document(self, index: int, activate: bool) -> None:
        '''Inserts an empty document with default page size
        at  position.
        
        :param index: Position at which a document should be inserted.
        :param activate: Flag indicating whether to select inserted document as active.'''
        ...
    
    @overload
    def insert_document(self, index: int, width: float, height: float, activate: bool) -> None:
        '''Inserts an empty document with the first page dimensions
         and at position.
        
        :param index: Position at which a document should be inserted.
        :param width: Width of the first page.
        :param height: Height of the first page.
        :param activate: Flag indicating whether to select inserted document as active.'''
        ...
    
    @overload
    def add_page(self, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Adds an empty page to the document with default page size.
        
        :param activate: Flag indicating whether to select added page as active.
        :returns: Added page.'''
        ...
    
    @overload
    def add_page(self, width: float, height: float, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Adds an empty page to the document with specified
         and.
        
        :param width: Width of a new page.
        :param height: Height of a new page.
        :param activate: Flag indicating whether to select added page as active.
        :returns: Added page.'''
        ...
    
    @overload
    def add_page(self, page: aspose.page.xps.xpsmodel.XpsPage, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Adds a page to the document.
        
        :param page: Page to be added.
        :param activate: Flag indicating whether to select added page as active.
        :returns: Added page.'''
        ...
    
    @overload
    def insert_page(self, index: int, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Inserts an empty page to the document with default page size
        at  position.
        
        :param index: Position at which a page should be inserted.
        :param activate: Flag indicating whether to select inserted page as active.
        :returns: Inserted page.'''
        ...
    
    @overload
    def insert_page(self, index: int, width: float, height: float, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Inserts an empty page to the document with specified
         and at position.
        
        :param index: Position at which a page should be inserted.
        :param width: Width of a new page.
        :param height: Height of a new page.
        :param activate: Flag indicating whether to select inserted page as active.
        :returns: Inserted page.'''
        ...
    
    @overload
    def insert_page(self, index: int, page: aspose.page.xps.xpsmodel.XpsPage, activate: bool) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Inserts a page to the document at  position.
        
        :param index: Position at which a page should be added.
        :param page: Page to be inserted.
        :param activate: Flag indicating whether to select inserted page as active.
        :returns: Inserted page.'''
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
        '''Inserts new glyphs to the active page at  position.
        
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
        '''Inserts new glyphs to the active page at  position.
        
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
    
    @overload
    def create_image(self, image_path: str) -> aspose.page.xps.xpsmodel.XpsImage:
        '''Creates a new image resource out of image file located at the .
        
        :param image_path: The path to the image to take as a resource.
        :returns: New image resource.'''
        ...
    
    @overload
    def create_image(self, stream: io.BytesIO) -> aspose.page.xps.xpsmodel.XpsImage:
        '''Creates a new image resource out of .
        
        :param stream: The stream containing the image to take as a resource.
        :returns: New image resource.'''
        ...
    
    @overload
    def create_icc_profile(self, icc_profile_path: str) -> aspose.page.xps.xpsmodel.XpsIccProfile:
        '''Creates a new ICC profile resource out of ICC profile file located at the
        .
        
        :param icc_profile_path: The path to the ICC profile to take as a resource.
        :returns: New ICC profile resource.'''
        ...
    
    @overload
    def create_icc_profile(self, stream: io.BytesIO) -> aspose.page.xps.xpsmodel.XpsIccProfile:
        '''Creates a new ICC profile resource out of .
        
        :param stream: The stream containing the ICC profile to take as a resource.
        :returns: New ICC profile resource.'''
        ...
    
    @overload
    def create_font(self, font_family: str, font_style: aspose.pydrawing.FontStyle) -> aspose.page.xps.xpsmodel.XpsFont:
        '''Creates a new TrueType font resource.
        
        :param font_family: The font family.
        :param font_style: The font style.
        :returns: New TrueType font resource.'''
        ...
    
    @overload
    def create_font(self, stream: io.BytesIO) -> aspose.page.xps.xpsmodel.XpsFont:
        '''Creates a new TrueType font resource out of stream.
        
        :param stream: The stream containing the ICC profile to take as a resource.
        :returns: New TrueType font resource.'''
        ...
    
    def select_active_document(self, document_number: int) -> None:
        '''Selects an active document for editing.
        
        :param document_number: A document number.
        :raises System.ArgumentException: Thrown when
                                          is out of bounds.'''
        ...
    
    def select_active_page(self, page_number: int) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Selects an active document page for editing.
        
        :param page_number: A page number.
        :returns: :class:`aspose.page.xps.xpsmodel.XpsPage` instance for active page.
        
        :raises System.ArgumentException: Thrown when
                                          is out of bounds.'''
        ...
    
    def save_as_image(self, options: aspose.page.xps.presentation.image.ImageSaveOptions) -> list[list[bytes]]:
        '''Saves the document in a bitmap image format.
        
        :param options: Options for saving the document in a bitmap image format.
        :returns: The resulting images byte arrays. The first dimension is for inner documents
                  and the second one is for pages within inner documents.'''
        ...
    
    def get_document_print_ticket(self, document_index: int) -> aspose.page.xps.xpsmetadata.DocumentPrintTicket:
        '''Returns the print ticket of the document indexed by .
        
        :param document_index: Index of the document whose print ticket to return.
        :returns: Document's print ticket.'''
        ...
    
    def set_document_print_ticket(self, document_index: int, print_ticket: aspose.page.xps.xpsmetadata.DocumentPrintTicket) -> None:
        '''Links the  to the document indexed by.
        
        :param document_index: Index of the document to link the print ticket to.
        :param print_ticket: The print ticket to link.'''
        ...
    
    def get_page_print_ticket(self, document_index: int, page_index: int) -> aspose.page.xps.xpsmetadata.PagePrintTicket:
        '''Returns the print ticket of the page indexed by
        in the document indexed by.
        
        :param document_index: Index of the document.
        :param page_index: Index of the page whose print ticket to return.
        :returns: Page's print ticket.'''
        ...
    
    def set_page_print_ticket(self, document_index: int, page_index: int, print_ticket: aspose.page.xps.xpsmetadata.PagePrintTicket) -> None:
        '''Links the  to the page indexed by
        in the document indexed by.
        
        :param document_index: Index of the document.
        :param page_index: Index of the page to link the print ticket to.
        :param print_ticket: The print ticket to link.'''
        ...
    
    def remove_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsContentElement:
        '''Removes an element at  position from the active page.
        
        :param index: Position at which element should be removed.
        :returns: Removed element.'''
        ...
    
    def remove_document_at(self, index: int) -> None:
        '''Removes a document at  position.
        
        :param index: Position at which a document should be removed.'''
        ...
    
    def remove_page(self, page: aspose.page.xps.xpsmodel.XpsPage) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Removes a page from the document.
        
        :param page: Page to be removed.
        :returns: Removed page.'''
        ...
    
    def remove_page_at(self, index: int) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Removes a page from the document at  position.
        
        :param index: Position at which a page should be removed.
        :returns: Removed page.'''
        ...
    
    def create_canvas(self) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Creates a new canvas.
        
        :returns: New canvas.'''
        ...
    
    def insert_canvas(self, index: int) -> aspose.page.xps.xpsmodel.XpsCanvas:
        '''Inserts a new canvas to the active page at  position.
        
        :param index: Position at which a new canvas should be inserted.
        :returns: Inserted canvas.'''
        ...
    
    def create_path(self, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Creates a new path.
        
        :param data: The geometry of the path.
        :returns: New  path.'''
        ...
    
    def insert_path(self, index: int, data: aspose.page.xps.xpsmodel.XpsPathGeometry) -> aspose.page.xps.xpsmodel.XpsPath:
        '''Inserts a new path to the active page at  position.
        
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
    
    def add_outline_entry(self, description: str, outline_level: int, target: aspose.page.xps.xpsmodel.XpsHyperlinkTarget) -> None:
        '''Adds an outline entry to the document.
        
        :param description: The entry description.
        :param outline_level: The outline level.
        :param target: The entry target.'''
        ...
    
    @property
    def utils(self) -> aspose.page.xps.DocumentUtils:
        '''Gets the object that provides utilities beyond the formal XPS manipulation API.'''
        ...
    
    @property
    def active_document(self) -> int:
        '''Gets the active document number.'''
        ...
    
    @property
    def active_page(self) -> int:
        '''Gets the active page number within the active document.'''
        ...
    
    @property
    def page(self) -> aspose.page.xps.xpsmodel.XpsPage:
        '''Returns an :class:`aspose.page.xps.xpsmodel.XpsPage` instance for active page.'''
        ...
    
    @property
    def document_count(self) -> int:
        '''Returns the number of documents inside the XPS package.'''
        ...
    
    @property
    def total_page_count(self) -> int:
        '''Returns total number of pages in all documents inside XPS document.'''
        ...
    
    @property
    def page_count(self) -> int:
        '''Returns the number of pages in the active document.'''
        ...
    
    @property
    def job_print_ticket(self) -> aspose.page.xps.xpsmetadata.JobPrintTicket:
        '''Returns/sets document's job print ticket'''
        ...
    
    @job_print_ticket.setter
    def job_print_ticket(self, value: aspose.page.xps.xpsmetadata.JobPrintTicket):
        ...
    
    ...

class XpsLoadOptions(aspose.page.eps.LoadOptions):
    '''XPS document loading options.'''
    
    def __init__(self):
        '''Creates new instance of options.'''
        ...
    
    ...

class ImageMode:
    '''Lists the options of fitting image within a box.'''
    
    FIT_TO_WIDTH: int
    FIT_TO_HEIGHT: int
    FIT_TO_BOX: int

