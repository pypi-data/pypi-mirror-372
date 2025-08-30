import aspose.page
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class Collate(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`DocumentCollate` and :class:`JobCollateAllDocuments` features classes.'''
    
    ...

class CompositePrintTicketElement(aspose.page.xps.xpsmetadata.PrintTicketElement):
    '''The base class for classes that may be composite Print Schema elements (i.e. containing other elements).'''
    
    ...

class DecimalValue(aspose.page.xps.xpsmetadata.Value):
    '''The class that incapsulates a Decimal value in a PrintTicket document.'''
    
    def __init__(self, value: decimal.Decimal):
        '''Creates a new instance.
        
        :param value: A decimal value.'''
        ...
    
    ...

class DocumentBannerSheet(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the banner sheet to be output for a particular document. The banner sheet should be output on the default
    :class:`PageMediaSize` and using the default :class:`PageMediaType`. The banner sheet should
    be also isolated from the remainder of the job. This means that any finishing or processing options (such as
    :class:`DocumentDuplex`, :class:`DocumentStaple`, or :class:`DocumentBinding`)
    should not include the banner sheet. The banner sheet may or may not be isolated from the remainder of the job.
    This means that any job finishing or processing options, may include the document banner sheet.
    The banner sheet should occur as the first sheet of the document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentbannersheet'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.DocumentBannerSheet.BannerSheetOption]):
        ...
    
    ...

class DocumentBannerSheetSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom banner sheet.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentbannersheetsource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentBinding(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the method of binding. Each document is bound separately.
    DocumentBinding and JobBindAllDocuments are mutually exclusive.
    It is up to the driver to determine constraint handling between keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentbinding'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption]):
        ...
    
    ...

class DocumentBindingGutter(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the width of the binding gutter.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentbindinggutter'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentCollate(aspose.page.xps.xpsmetadata.Collate):
    '''Describes the collating characteristics of the output. All pages in each individual document are collated.
    DocumentCollate and JobCollateAlldocuments are mutually exclusive. The behavior and implementation of whether
    both or only one of these keywords is implemented is left to the driver.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcollate'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Collate.CollateOption]):
        ...
    
    ...

class DocumentCopiesAllPages(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the number of copies of a document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcopiesallpages'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentCoverBack(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the back (ending) cover sheet. Each document will have a separate sheet.
    The cover sheet should be printed on the :class:`PageMediaSize` and :class:`PageMediaType`
    used for the final page of the document. The cover sheet should be integrated into processing options
    (such as :class:`DocumentDuplex`, :class:`DocumentNUp`) as indicated by the Option specified.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcoverback'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption]):
        ...
    
    ...

class DocumentCoverBackSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom back-cover sheet.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcoverbacksource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentCoverFront(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the front (beginning) cover sheet. Each document will have a separate sheet.
    The cover sheet should be printed on the :class:`PageMediaSize` and :class:`PageMediaType`
    used for the first page of the document. The cover sheet should be integrated into processing options
    (such as :class:`DocumentDuplex`, :class:`DocumentNUp`) as indicated by the Option specified.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcoverfront'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption]):
        ...
    
    ...

class DocumentCoverFrontSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom front-cover sheet.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentcoverfrontsource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentDuplex(aspose.page.xps.xpsmetadata.Duplex):
    '''Describes the duplex characteristics of the output. The duplex feature allows for
    printing on both sides of the media. Each document is duplexed separately.
    DocumentDuplex and JobDuplexAllDocumentsContiguously are mutually exclusive.
    It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentduplex'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Duplex.DuplexOption]):
        ...
    
    ...

class DocumentHolePunch(aspose.page.xps.xpsmetadata.HolePunch):
    '''Describes the hole punching characteristics of the output. Each document is punched separately.
    The :class:`JobHolePunch` and :class:`DocumentHolePunch` keywords are mutually exclusive.
    Both should not be specified simultaneously in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentholepunch'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption]):
        ...
    
    ...

class DocumentID(aspose.page.xps.xpsmetadata.IDProperty):
    '''Specifies a unique ID for the document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentid'''
    
    def __init__(self, document_id: str):
        '''Creates a new instance.
        
        :param document_id: The document ID.'''
        ...
    
    ...

class DocumentImpositionColor(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Application content labeled with the specified named color MUST appear on all color separations.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentimpositioncolor'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentInputBin(aspose.page.xps.xpsmetadata.InputBin):
    '''Describes the installed input bin in a device or the full list of supported bins for a device.
    The :class:`JobInputBin`, :class:`DocumentInputBin`, and :class:`PageInputBin`
    keywords are mutually exclusive. Both should not be specified simultaneously in a PrintTicket
    or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentinputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.InputBin.IInputBinItem]):
        ...
    
    ...

class DocumentNUp(aspose.page.xps.xpsmetadata.NUp):
    '''Describes the output and format of multiple logical pages to a single physical sheet.
    Each document is compiled separately.
    DocumentNUp
    
     and:class:`JobNUpAllDocumentsContiguously`
    are mutually exclusive. It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentnup'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.NUp.INUpItem]):
        ...
    
    def add_pages_per_sheet_option(self, value: int) -> aspose.page.xps.xpsmetadata.DocumentNUp:
        '''Adds and option with a
        PagesPerSheet
        
         scored property value.
        Specifies the number of logical pages per physical sheet.
        
        :param value: A
                      PagesPerSheet
                      scored property value.
                      Supported set can be any set of integers E.g. {1,2,4,6,8,9,16}.
        :returns: This feature instance.'''
        ...
    
    ...

class DocumentName(aspose.page.xps.xpsmetadata.NameProperty):
    '''Specifies a descriptive name for the document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentname'''
    
    def __init__(self, document_name: str):
        '''Creates a new instance.
        
        :param document_name: The document name.'''
        ...
    
    ...

class DocumentOutputBin(aspose.page.xps.xpsmetadata.OutputBin):
    '''Describes the full list of supported bins for the device. Allows specification of output
    bin on a per document basis. The :class:`JobOutputBin`, :class:`DocumentOutputBin` and
    :class:`PageOutputBin` keywords are mutually exclusive only one should be specified in
    a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentoutputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.OutputBin.IOutputBinItem]):
        ...
    
    ...

class DocumentPageRanges(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Describes the output range of the document in pages. The parameter value must conform to the following structure:
    - PageRangeText: "PageRange" or "PageRange,PageRange"
    - PageRange: "PageNumber" or "PageNumber-PageNumber"
    - PageNumber: 1 to N, where N is the number of pages in the document.If PageNumber \> N, then PageNumber = N.
    Whitespace in the string should be ignored.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentpageranges'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class DocumentPrintTicket(aspose.page.xps.xpsmetadata.PrintTicket):
    '''The class that incapsulates a document-level print ticket.'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.IDocumentPrintTicketItem]):
        '''Creates a document-level print ticket instance.
        
        :param items: An arbitrary array of :class:`IDocumentPrintTicketItem` instances.
                      Each one can be a :class:`Feature`, a :class:`ParameterInit` or a :class:`Property` instance.'''
        ...
    
    def add(self, items: list[aspose.page.xps.xpsmetadata.IDocumentPrintTicketItem]) -> None:
        '''Adds an array of items to the end of this PrintTicket item list.
        Each one may be a :class:`Feature`, an :class:`Option` or a :class:`Property` instance.
        
        :param items: An array of items to add.'''
        ...
    
    ...

class DocumentRollCut(aspose.page.xps.xpsmetadata.RollCut):
    '''Describes the cutting method for roll paper. Each document is handled separately.
    The specified options describe the different methods for roll cut.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentrollcut'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.RollCut.RollCutOption]):
        ...
    
    ...

class DocumentSeparatorSheet(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the separator sheet usage for a document.
    Separator sheets should appear in the output as indicated by the Option specified below.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentseparatorsheet'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.DocumentSeparatorSheet.DocumentSeparatorSheetOption]):
        ...
    
    ...

class DocumentStaple(aspose.page.xps.xpsmetadata.Staple):
    '''Describes the stapling characteristics of the output. Each document is stapled separately.
    The :class:`JobStapleAllDocuments` and :class:`DocumentStaple` keywords are mutually exclusive.
    It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documentstaple'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Staple.StapleOption]):
        ...
    
    ...

class DocumentURI(aspose.page.xps.xpsmetadata.URIProperty):
    '''Specifies a uniform resource identifier (URI) for the document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/documenturi'''
    
    def __init__(self, document_uri: str):
        '''Creates a new instance.
        
        :param document_uri: The document URI.'''
        ...
    
    ...

class Duplex(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobDuplexAllDocumentsContiguously` and :class:`DocumentDuplex` features classes.'''
    
    ...

class Feature(aspose.page.xps.xpsmetadata.CompositePrintTicketElement):
    '''The class that incapsulates a common Print Schema feature.
    The base class for all schema-defined features.
    A
    Feature
    
     element contains a complete list of the:class:`Option` and :class:`Property`
    elements that fully describe a device attribute, job formatting setting, or other relevant characteristic.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/feature'''
    
    @overload
    def __init__(self, name: str, option: aspose.page.xps.xpsmetadata.Option, items: list[aspose.page.xps.xpsmetadata.IFeatureItem]):
        '''Creates a new PrintTicket feature instance.
        
        :param name: A feature name.
        :param option: Required :class:`Option` instance.
        :param items: An arbitrary array of :class:`IFeatureItem` instances.
                      Each one must be a :class:`Feature`, an :class:`Option`, or a :class:`Property` instance.'''
        ...
    
    @overload
    def __init__(self, name: str, feature: aspose.page.xps.xpsmetadata.Feature, items: list[aspose.page.xps.xpsmetadata.IFeatureItem]):
        '''Creates a new PrintTicket feature instance.
        
        :param name: A feature name.
        :param feature: Required :class:`Feature` instance.
        :param items: An arbitrary array of :class:`IFeatureItem` instances.
                      Each one must be a :class:`Feature`, an :class:`Option`, or a :class:`Property` instance.'''
        ...
    
    def add(self, items: list[aspose.page.xps.xpsmetadata.IFeatureItem]) -> None:
        '''Adds a list of items to the end of this feature's item list.
        Each one must be a :class:`Feature`, an :class:`Option`, or a :class:`Property` instance.
        
        :param items: List of items to add.'''
        ...
    
    ...

class HolePunch(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobHolePunch` and :class:`DocumentHolePunch` features classes.'''
    
    ...

class IDProperty(aspose.page.xps.xpsmetadata.Property):
    '''The base class for :class:`JobID` and :class:`DocumentID` properties classes.'''
    
    ...

class IDocumentPrintTicketItem:
    '''The interface of document-prefixed print ticket items.'''
    
    ...

class IFeatureItem:
    '''The base interface for classes that may be Print Schema :class:`Feature` items.'''
    
    ...

class IJobPrintTicketItem:
    '''The interface of job-prefixed print ticket items.'''
    
    ...

class IOptionItem:
    '''The interface of classes that may be Print Schema :class:`Option` items.'''
    
    ...

class IPagePrintTicketItem:
    '''The interface of page-prefixed print ticket items.'''
    
    ...

class IPrintTicketElementChild:
    '''The base interface of a child element of any Print Schema element.'''
    
    @property
    def name(self) -> str:
        '''The child name.'''
        ...
    
    ...

class IPrintTicketItem:
    '''The base interface for classes that may be :class:`PrintTicket` root element items.
    It is also the base interface for interfaces that define a scoping prefix.'''
    
    ...

class IPropertyItem:
    '''The base interface for classes that may be a PrintTicket :class:`Property` items.'''
    
    ...

class IScoredPropertyItem:
    '''The base interface for classes that may be PrintTicket :class:`ScoredProperty` items.'''
    
    ...

class InputBin(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobInputBin`, :class:`DocumentInputBin`
    and :class:`PageInputBin` features classes.'''
    
    ...

class IntegerParameterInit(aspose.page.xps.xpsmetadata.ParameterInit):
    '''Base class for all integer parameter initializers.'''
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    @property
    def multiple(self) -> int:
        '''For integer- or decimal-valued parameters, the value of the parameter should be a multiple of this number.'''
        ...
    
    ...

class IntegerValue(aspose.page.xps.xpsmetadata.Value):
    '''The class that incapsulates an Integer value in a PrintTicket document.'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: An integer value.'''
        ...
    
    ...

class JobAccountingSheet(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the accounting sheet to be output for the job. The accounting sheet should be output on the default
    :class:`PageMediaSize` and using the default :class:`PageMediaType`. The accounting sheet should to
    be isolated from the remainder of the job. This means that any finishing or processing options (such as
    
    JobDuplex
    
    ,
    JobStaple
    
    , or
    JobBinding
    
    ) should not include the accounting sheet.
    The accounting sheet may occur as the first or last page of the job at the implementer's discretion.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobaccountingsheet'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobAccountingSheet.JobAccountingSheetOption]):
        ...
    
    ...

class JobBindAllDocuments(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the method of binding. All documents in the job are bound together.
    :class:`JobBindAllDocuments` and :class:`DocumentBinding` are mutually exclusive.
    It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobbindalldocuments'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption]):
        ...
    
    ...

class JobBindAllDocumentsGutter(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the width of the binding gutter.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobbindalldocumentsgutter'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobCollateAllDocuments(aspose.page.xps.xpsmetadata.Collate):
    '''Describes the collating characteristics of the output. All documents in each individual job are collated.
    :class:`DocumentCollate` and :class:`JobCollateAllDocuments` are mutually exclusive.
    The behavior and implementation of whether both or only one of these keywords is implemented is left to the driver.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobcollatealldocuments'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Collate.CollateOption]):
        ...
    
    ...

class JobComment(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies a comment associated with the job. Example: "Please deliver to room 1234 when completed".
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobcomment'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobCopiesAllDocuments(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the number of copies of a job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobcopiesalldocuments'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobDeviceLanguage(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the device languages supported for sending data from driver to physical device.
    This is often called "Page Description Language". This keyword defines what page description
    language is supported by the driver and physical device.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobdevicelanguage'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption]):
        ...
    
    ...

class JobDigitalSignatureProcessing(aspose.page.xps.xpsmetadata.Feature):
    '''Describes configuring the digital signature processing for the entire job.
    Applicable only to content that contains digital signatures.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobdigitalsignatureprocessing'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobDigitalSignatureProcessing.JobDigitalSignatureProcessingOption]):
        ...
    
    ...

class JobDuplexAllDocumentsContiguously(aspose.page.xps.xpsmetadata.Duplex):
    '''Describes the duplex characteristics of the output. The duplex feature allows for printing on
    both sides of the media. All Documents in the job are duplexed together contiguously.
    :class:`JobDuplexAllDocumentsContiguously` and :class:`DocumentDuplex` are mutually exclusive.
    It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobduplexalldocumentscontiguously'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Duplex.DuplexOption]):
        ...
    
    ...

class JobErrorSheet(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the error sheet output. The entire job will have a single error sheet. The error sheet
    should be output on the default :class:`PageMediaSize` and using the default :class:`PageMediaType`.
    The error sheet should to be isolated from the remainder of the job. This means that any finishing or
    processing options (such as
    JobDuplex
    
    ,
    JobStaple
    
    , or
    JobBinding
    
    )
    should not include the error sheet. The error sheet should occur as the final sheet of the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joberrorsheet'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.JobErrorSheet.IJobErrorSheetItem]):
        ...
    
    ...

class JobErrorSheetSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom error sheet.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joberrorsheetsource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobHolePunch(aspose.page.xps.xpsmetadata.HolePunch):
    '''Describes the hole punching characteristics of the output. All documents are punched together.
    The :class:`JobHolePunch` and :class:`DocumentHolePunch` keywords are mutually exclusive.
    Both should not be specified simultaneously in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobholepunch'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption]):
        ...
    
    ...

class JobID(aspose.page.xps.xpsmetadata.IDProperty):
    '''Specifies a unique ID for the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobid'''
    
    def __init__(self, job_id: str):
        '''Creates a new instance.
        
        :param job_id: The job ID.'''
        ...
    
    ...

class JobInputBin(aspose.page.xps.xpsmetadata.InputBin):
    '''Describes the installed input bin in a device or the full list of supported bins for a device.
    Allows specification of input bin on a per job basis. The :class:`JobInputBin`, :class:`DocumentInputBin`,
    and :class:`PageInputBin` keywords are mutually exclusive. Both should not be specified simultaneously
    in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobinputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.InputBin.IInputBinItem]):
        ...
    
    ...

class JobNUpAllDocumentsContiguously(aspose.page.xps.xpsmetadata.NUp):
    '''Describes the output of multiple logical pages to a single physical sheet. All documents in the job
    are compiled together contiguously. :class:`JobNUpAllDocumentsContiguously` and :class:`DocumentNUp`
    are mutually exclusive. It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobnupalldocumentscontiguously'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.NUp.INUpItem]):
        ...
    
    def add_pages_per_sheet_option(self, value: int) -> aspose.page.xps.xpsmetadata.JobNUpAllDocumentsContiguously:
        '''Adds and option with a
        PagesPerSheet
        
         scored property value.
        Specifies the number of logical pages per physical sheet.
        
        :param value: A
                      PagesPerSheet
                      scored property value.
                      Supported set can be any set of integers E.g. {1,2,4,6,8,9,16}.
        :returns: This feature instance.'''
        ...
    
    ...

class JobName(aspose.page.xps.xpsmetadata.NameProperty):
    '''Specifies a descriptive name for the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobname'''
    
    def __init__(self, job_name: str):
        '''Creates a new instance.
        
        :param job_name: The job name.'''
        ...
    
    ...

class JobOptimalDestinationColorProfile(aspose.page.xps.xpsmetadata.Property):
    '''Specifies the optimal color profile given the current device configuration.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joboptimaldestinationcolorprofile'''
    
    def __init__(self, profile: aspose.page.xps.xpsmetadata.JobOptimalDestinationColorProfile.Profile, profile_data: str, path: str):
        ...
    
    ...

class JobOutputBin(aspose.page.xps.xpsmetadata.OutputBin):
    '''Describes the installed output bin in a device or the full list of supported bins for a device.
    The :class:`JobOutputBin`, :class:`DocumentOutputBin` and :class:`PageOutputBin` keywords
    are mutually exclusive only one should be specified in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joboutputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.OutputBin.IOutputBinItem]):
        ...
    
    ...

class JobOutputOptimization(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the job processing, intended to optimize the output for particular use scenarios as indicated by the option specified.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joboutputoptimization'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption]):
        ...
    
    ...

class JobPageOrder(aspose.page.xps.xpsmetadata.Feature):
    '''Defines the order of physical pages for the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobpageorder'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobPageOrder.JobPageOrderOption]):
        ...
    
    ...

class JobPrimaryBannerSheet(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the banner sheet to be output for the job. The banner sheet should be output on the default
    :class:`PageMediaSize` and using the default :class:`PageMediaType`. The banner sheet should
    be isolated from the remainder of the job. This means that any finishing or processing options (such as
    :class:`JobDuplexAllDocumentsContiguously`, :class:`JobStapleAllDocuments`, or :class:`JobBindAllDocuments`)
    should not include the banner sheet. The banner sheet should occur as the first sheet of the job.'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobPrimaryBannerSheet.BannerSheetOption]):
        ...
    
    ...

class JobPrimaryBannerSheetSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a primary custom banner sheet for the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobprimarybannersheetsource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobPrimaryCoverBack(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the back (ending) cover sheet. Each job will have a separate primary sheet.
    The cover sheet should be printed on the :class:`PageMediaSize` and :class:`PageMediaType`
    used for the final page of the job. The cover sheet should be integrated into processing options
    (such as :class:`JobDuplexAllDocumentsContiguously`, :class:`JobNUpAllDocumentsContiguously`)
    as indicated by the Option specified.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobprimarycoverback'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption]):
        ...
    
    ...

class JobPrimaryCoverBackSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom back-cover primary sheet for the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobprimarycoverbacksource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobPrimaryCoverFront(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the front (beginning) cover sheet. The entire job will have a single primary sheet.
    The cover sheet should be printed on the :class:`PageMediaSize` and :class:`PageMediaType`
    used for the first page of the job. The cover sheet should be integrated into processing options
    (such as :class:`JobDuplexAllDocumentsContiguously`, :class:`JobNUpAllDocumentsContiguously`)
    as indicated by the Option specified.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobprimarycoverfront'''
    
    ...

class JobPrimaryCoverFrontSource(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for a custom front-cover primary sheet for the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobprimarycoverfrontsource'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class JobPrintTicket(aspose.page.xps.xpsmetadata.PrintTicket):
    '''The class that incapsulates a job-level print ticket.'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.IJobPrintTicketItem]):
        '''Creates a job-level print ticket instance.
        
        :param items: An arbitrary array of :class:`IJobPrintTicketItem` instances.
                      Each one can be a :class:`Feature`, a :class:`ParameterInit` or a :class:`Property` instance.'''
        ...
    
    def add(self, items: list[aspose.page.xps.xpsmetadata.IJobPrintTicketItem]) -> None:
        '''Adds an array of items to the end of this PrintTicket item list.
        Each one may be a :class:`Feature`, an :class:`Option` or a :class:`Property` instance.
        
        :param items: An array of items to add.'''
        ...
    
    ...

class JobRollCutAtEndOfJob(aspose.page.xps.xpsmetadata.RollCut):
    '''Describes the cutting method for roll paper. The roll should be cut at the end of the job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobrollcutatendofjob'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.RollCut.RollCutOption]):
        ...
    
    ...

class JobStapleAllDocuments(aspose.page.xps.xpsmetadata.Staple):
    '''Describes the stapling characteristics of the output. All documents in the job are stapled together.
    The :class:`JobStapleAllDocuments` and :class:`DocumentStaple` keywords are mutually exclusive.
    It is up to the driver to determine constraint handling between these keywords.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/jobstaplealldocuments'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.Staple.StapleOption]):
        ...
    
    ...

class JobURI(aspose.page.xps.xpsmetadata.URIProperty):
    '''Specifies a uniform resource identifier (URI) for the document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/joburi'''
    
    def __init__(self, job_uri: str):
        '''Creates a new instance.
        
        :param job_uri: The job URI.'''
        ...
    
    ...

class NUp(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobNUpAllDocumentsContiguously` and :class:`DocumentNUp`
    features classes.'''
    
    ...

class NameProperty(aspose.page.xps.xpsmetadata.Property):
    '''The base class for :class:`JobName` and :class:`DocumentName` properties classes.'''
    
    ...

class Option(aspose.page.xps.xpsmetadata.CompositePrintTicketElement):
    '''The class that implements a common PrintTicket
    Option
    
    .
    The base class for all schema-defined options.
    An Option element contains all of the:class:`Property` and
    :class:`ScoredProperty` elements associated with this option.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/option'''
    
    @overload
    def __init__(self, name: str, items: list[aspose.page.xps.xpsmetadata.IOptionItem]):
        '''Creates a new PrintTicket option instance.
        
        :param name: An arbitrary option name.
        :param items: An arbitrary array of :class:`IOptionItem` instances.
                      Each one must be a :class:`ScoredProperty` or a :class:`Property` instance.'''
        ...
    
    @overload
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.IOptionItem]):
        '''Creates a new PrintTicket option instance.
        
        :param items: An arbitrary array of :class:`IOptionItem` instances.
                      Each one must be a :class:`ScoredProperty` or a :class:`Property` instance.'''
        ...
    
    @overload
    def __init__(self, option: aspose.page.xps.xpsmetadata.Option):
        '''Creates a clone option instance.
        
        :param option: An option instance to clone.'''
        ...
    
    def add(self, items: list[aspose.page.xps.xpsmetadata.IOptionItem]) -> None:
        '''Adds a list of items to the end of this option's item list.
        Each one must be a :class:`ScoredProperty` or :class:`Property` instance.
        
        :param items: List of items to add.'''
        ...
    
    ...

class OutputBin(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobOutputBin`, :class:`DocumentOutputBin` and :class:`PageOutputBin`
    features classes.'''
    
    ...

class PageBlackGenerationProcessing(aspose.page.xps.xpsmetadata.Feature):
    '''Specifies black generation behavior for CMYK separations.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessing'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageBlackGenerationProcessing.PageBlackGenerationProcessingOption]):
        ...
    
    ...

class PageBlackGenerationProcessingBlackInkLimit(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Application content labeled with the specified named color MUST appear on all color separations.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessingblackinklimit'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingGrayComponentReplacementExtent(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Describes the extented beyond neutrals (into chromatic colors) that GCR applies.
    0% = Uniform component replacement, 100% = Gray component replacement.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessinggraycomponentreplacementextent'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingGrayComponentReplacementLevel(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the percentage of gray component replacement to perform.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessinggraycomponentreplacementlevel'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingGrayComponentReplacementStart(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Describes the point in the "highlight to shadow" range where GCR should start (100% darkest shadow).
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessinggraycomponentreplacementstart'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingTotalInkCoverageLimit(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the maximum allowed sum of the four ink coverage anywhere in an image.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessingtotalinkcoveragelimit'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingUnderColorAdditionLevel(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Describes the amount chromatic ink (in gray component ratios) to add to areas where GCR/UCR has generated
    "BlackInkLimit" (or UCAStart, if specified) in the dark neutrals and near-neutral areas.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessingundercoloradditionlevel'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlackGenerationProcessingUnderColorAdditionStart(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Describes the shadow level below which UCA will be applied.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblackgenerationprocessingundercoloradditionstart'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageBlendColorSpace(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the color space that should be used for blending operations.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblendcolorspace'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageBlendColorSpace.PageBlendColorSpaceOption]):
        ...
    
    ...

class PageBlendColorSpaceICCProfileURI(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies a relative URI reference to an ICC profile defining the color space that SHOULD be used for blending.
    The \<Uri\> is an absolute part_name relative to the package root.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageblendcolorspaceiccprofileuri'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageBorderless(aspose.page.xps.xpsmetadata.Feature):
    '''Describes when image content should be printed to the physical edges of the media.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageborderless'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageBorderless.PageBorderlessOption]):
        ...
    
    ...

class PageColorManagement(aspose.page.xps.xpsmetadata.Feature):
    '''Configures color management for the current page.
    This is considered automatic in SHIM - DM_ICMMethod Add System.
    Describes what component should perform color management (i.e. Driver).
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagecolormanagement'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageColorManagement.PageColorManagementOption]):
        ...
    
    ...

class PageCopies(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the number of copies of a page.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagecopies'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageDestinationColorProfile(aspose.page.xps.xpsmetadata.Feature):
    '''Defines the characteristics of the destination color profile.
    Describes whether the application or driver selects the destination color profile to be used.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedestinationcolorprofile'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageDestinationColorProfile.PageDestinationColorProfileOption]):
        ...
    
    ...

class PageDestinationColorProfileEmbedded(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the embedded destination color profile.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedestinationcolorprofileembedded'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageDestinationColorProfileURI(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies a relative URI reference to an ICC profile contained in an XPS Document.
    The processing of this option depends of the setting of the PageDeviceColorSpaceUsage feature.
    All elements using that profile are assumed to be already in the appropriate device color space,
    and will not be color managed in the driver or device.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedestinationcolorprofileuri'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageDeviceColorSpaceProfileURI(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies a relative URI to the package root to an ICC profile contained in an XPS Document.
    The processing of this option depends of the setting of the PageDeviceColorSpaceUsage feature.
    All elements using that profile are assumed to be already in the appropriate device color space,
    and will not be color managed in the driver or device.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedevicecolorspaceprofileuri'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageDeviceColorSpaceUsage(aspose.page.xps.xpsmetadata.Feature):
    '''In conjunction with the :class:`PageDeviceColorSpaceProfileURI` parameter, this parameter defines
    the rendering behavior for elements presented in a device color space.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedevicecolorspaceusage'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageDeviceColorSpaceUsage.PageDeviceColorSpaceUsageOption]):
        ...
    
    ...

class PageDeviceFontSubstitution(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the enabled/disabled state of device font substitution.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagedevicefontsubstitution'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageDeviceFontSubstitution.PageDeviceFontSubstitutionOption]):
        ...
    
    ...

class PageForceFrontSide(aspose.page.xps.xpsmetadata.Feature):
    '''Forces the output to appear on the front of a media sheet. Relevant to media sheets with different
    surfaces on each side. In cases where this feature interferes with processing options (such as
    :class:`DocumentDuplex`),
    PageForceFrontSide
    
     takes precedence for the specific
    page to which the feature applies.'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageForceFrontSide.PageForceFrontSideOption]):
        ...
    
    ...

class PageICMRenderingIntent(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the rendering intent as defined by the ICC v2 Specification.
    This value should be ignored if an image or graphical element has an embedded profile
    that specifies the Rendering intent.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageicmrenderingintent'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageICMRenderingIntent.PageICMRenderingIntentOption]):
        ...
    
    ...

class PageImageableSize(aspose.page.xps.xpsmetadata.Property):
    '''Describes the imaged canvas for layout and rendering. This will be reported based on
    :class:`PageMediaSize` and :class:`PageOrientation`.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageimageablesize'''
    
    @overload
    def __init__(self, width: int, height: int):
        '''Creates a new instance.
        
        :param width: An
                      ImageableSizeWidth
                      property value.
        :param height: An
                       ImageableSizeHeight
                       property value.'''
        ...
    
    @overload
    def __init__(self, width: int, height: int, origin_width: int, origin_height: int, extent_width: int, extent_height: int):
        '''Creates a new instance.
        
        :param width: An
                      ImageableSizeWidth
                      property value.
        :param height: An
                       ImageableSizeHeight
                       property value.
        :param origin_width: An
                             ImageableArea
                             sub-property's
                             OriginWidth
                             property value.
        :param origin_height: An
                              ImageableArea
                              sub-property's
                              OriginHeight
                              property value.
        :param extent_width: An
                             ImageableArea
                             sub-property's
                             ExtentWidth
                             property value.
        :param extent_height: An
                              ImageableArea
                              sub-property's
                              ExtentHeight
                              property value.'''
        ...
    
    ...

class PageInputBin(aspose.page.xps.xpsmetadata.InputBin):
    '''Describes the installed input bin in a device or the full list of supported bins for a device.
    Allows specification of input bin on a per page basis. The :class:`JobInputBin`, :class:`DocumentInputBin` and
    :class:`PageInputBin` keywords are mutually exclusive. Both should not be specified simultaneously
    in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageinputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.InputBin.IInputBinItem]):
        ...
    
    ...

class PageMediaColor(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the Media Color options and the characteristics of each option.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediacolor'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption]):
        ...
    
    ...

class PageMediaSize(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the physical media dimensions used for the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasize'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageMediaSize.IPageMediaSizeItem]):
        ...
    
    ...

class PageMediaSizeMediaSizeHeight(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the dimension
    MediaSizeWidth
    
     direction for the Custom
    MediaSize
    
     option.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizemediasizeheight'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaSizeMediaSizeWidth(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the dimension
    MediaSizeHeight
    
     direction for the Custom
    MediaSize
    
     option.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizemediasizewidth'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaSizePSHeight(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the height of the page, parallel to the feed-orientation direction.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizepsheight'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaSizePSHeightOffset(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the offset, parallel to the feed-orientation direction.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizepsheightoffset'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaSizePSOrientation(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the orientation relative to the feed-orientation direction
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizepsorientation'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class PageMediaSizePSWidth(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the width of the page perpendicular to the feed-orientation direction.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizepswidth'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaSizePSWidthOffset(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the offset perpendicular to the feed-orientation direction.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediasizepswidthoffset'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageMediaType(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the
    MediaType
    
     options and the characteristics of each option.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemediatype'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.PageMediaType.IPageMediaTypeItem]):
        ...
    
    ...

class PageMirrorImage(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the mirroring setting of the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagemirrorimage'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageMirrorImage.PageMirrorImageOption]):
        ...
    
    ...

class PageNegativeImage(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the negative setting of the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagenegativeimage'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageNegativeImage.PageNegativeImageOption]):
        ...
    
    ...

class PageOrientation(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the orientation of the physical media sheet.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageorientation'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageOrientation.PageOrientationOption]):
        ...
    
    ...

class PageOutputBin(aspose.page.xps.xpsmetadata.OutputBin):
    '''Describes the full list of supported bins for the device. Allows specification of output bin on a per page basis.
    The :class:`JobOutputBin`, :class:`DocumentOutputBin` and :class:`PageOutputBin` keywords are
    mutually exclusive only one should be specified in a PrintTicket or Print Capabilities document.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageoutputbin'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.OutputBin.IOutputBinItem]):
        ...
    
    ...

class PageOutputColor(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the characteristics of the color settings for the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageoutputcolor'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.PageOutputColor.IPageOutputColorItem]):
        ...
    
    ...

class PageOutputQuality(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the negative setting of the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageoutputquality'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption]):
        ...
    
    ...

class PagePhotoPrintingIntent(aspose.page.xps.xpsmetadata.Feature):
    '''Indicates a high-level intent to the driver for population of photo printing settings.
    These settings deal with the expected output quality a user may specify when printing photos.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagephotoprintingintent'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PagePhotoPrintingIntent.PagePhotoPrintingIntentOption]):
        ...
    
    ...

class PagePoster(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the output of a single page to multiple physical media sheets.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageposter'''
    
    def __init__(self):
        '''Creates a new instance.'''
        ...
    
    def add_pages_per_sheet_option(self, value: int) -> aspose.page.xps.xpsmetadata.PagePoster:
        '''Adds and option with a
        PagesPerSheet
        
         scored property value.
        Specifies the number of physical sheets per logical page.
        
        :param value: A
                      PagesPerSheet
                      scored property value.
        :returns: This feature instance.'''
        ...
    
    ...

class PagePrintTicket(aspose.page.xps.xpsmetadata.PrintTicket):
    '''The class that incapsulates a page-level print ticket.'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.IPagePrintTicketItem]):
        '''Creates a page-level print ticket instance.
        
        :param items: An arbitrary array of :class:`IPagePrintTicketItem` instances.
                      Each one can be a :class:`Feature`, a :class:`ParameterInit` or a :class:`Property` instance.'''
        ...
    
    def add(self, items: list[aspose.page.xps.xpsmetadata.IPagePrintTicketItem]) -> None:
        '''Adds an array of items to the end of this PrintTicket item list.
        Each one may be a :class:`Feature`, an :class:`Option` or a :class:`Property` instance.
        
        :param items: An array of items to add.'''
        ...
    
    ...

class PageResolution(aspose.page.xps.xpsmetadata.Feature):
    '''Defines the page resolution of printed output as either a qualitative value or as dots per inch, or both.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pageresolution'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.PageResolution.IPageResolutionItem]):
        ...
    
    ...

class PageScaling(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the scaling characteristics of the output.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescaling'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.PageScaling.IPageScalingItem]):
        ...
    
    ...

class PageScalingOffsetHeight(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the scaling offset in the
    ImageableSizeWidth
    
     direction for custom scaling.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescalingoffsetheight'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageScalingOffsetWidth(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the scaling offset in the
    ImageableSizeWidth
    
     direction for custom scaling.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescalingoffsetwidth'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageScalingScale(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the scaling factor for custom square scaling.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescalingscale'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageScalingScaleHeight(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the scaling factor in the
    ImageableSizeHeight
    
     direction for custom scaling.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescalingscaleheight'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageScalingScaleWidth(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the scaling factor in the
    ImageableSizeWidth
    
     direction for custom scaling.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagescalingscalewidth'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageSourceColorProfile(aspose.page.xps.xpsmetadata.Feature):
    '''Defines the characteristics of the source color profile.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagesourcecolorprofile'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageSourceColorProfile.PageSourceColorProfileOption]):
        ...
    
    ...

class PageSourceColorProfileEmbedded(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the embedded source color profile.'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageSourceColorProfileURI(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the source for color profile.'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageTrueTypeFontMode(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the method of TrueType font handling to be used.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagetruetypefontmode'''
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption]):
        ...
    
    ...

class PageWatermark(aspose.page.xps.xpsmetadata.Feature):
    '''Describes the watermark setting of the output and the watermark characteristics. Watermarks apply
    to the logical page, not the physical page. For example, if :class:`DocumentDuplex` is enabled,
    a watermark will appear on each
    NUp
    
     page on each sheet. If:class:`DocumentDuplex`,
    
    PagesPerSheet
    
    =2, then each sheet will have 2 watermarks.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermark'''
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.PageWatermark.IPageWatermarkItem]):
        ...
    
    ...

class PageWatermarkOriginHeight(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the origin of a watermark relative to the origin of the
    PageImageableSize
    
    .
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarkoriginheight'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkOriginWidth(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the origin of a watermark relative to the origin of the
    PageImageableSize
    
    .
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarkoriginwidth'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkTextAngle(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the angle of the watermark text relative to the
    PageImageableSizeWidth
    
     direction.
    The angle is measured in the counter-clockwise direction.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarktextangle'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkTextColor(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Defines the sRGB color for the watermark text. Format is ARGB: #AARRGGBB.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarktextcolor'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkTextFontSize(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Defines the available font sizes for the watermark text.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarktextfontsize'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkTextText(aspose.page.xps.xpsmetadata.StringParameterInit):
    '''Specifies the text of the watermark.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarktexttext'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    ...

class PageWatermarkTransparency(aspose.page.xps.xpsmetadata.IntegerParameterInit):
    '''Specifies the transparency for the watermark. Fully opaque would have a value of 0.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/pagewatermarktransparency'''
    
    def __init__(self, value: int):
        '''Creates a new instance.
        
        :param value: The parameter value.'''
        ...
    
    @property
    def min_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the smallest allowed value.'''
        ...
    
    @property
    def max_value(self) -> int:
        '''For integer- or decimal-valued parameters, defines the largest allowed value.'''
        ...
    
    ...

class ParameterInit(aspose.page.xps.xpsmetadata.PrintTicketElement):
    '''The class that implements a common PrintTicket parameter initializer.
    The base class for all schema-defined parameter initializers.
    Defines a value for an instance of a
    ParameterDef
    
     element.
    A
    ParameterInit
    
     element is the target of the reference made by a:class:`ParameterRef` element.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/parameterinit'''
    
    def __init__(self, name: str, value: aspose.page.xps.xpsmetadata.Value):
        '''Creates a new instance.
        
        :param name: A parameter name.
        :param value: A parameter value.'''
        ...
    
    ...

class ParameterRef(aspose.page.xps.xpsmetadata.PrintTicketElement):
    '''The class that implements a common PrintTicket parameter reference.
    A
    ParameterRef
    
     element defines a reference to a:class:`ParameterInit` element.
    A :class:`ScoredProperty` element that contains a ParameterRef element does not have
    an explicitly-set :class:`Value` element. Instead, the :class:`ScoredProperty` element
    receives its value from the :class:`ParameterInit` element referenced by a
    ParameterRef
    
     element.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/parameterref'''
    
    def __init__(self, name: str):
        '''Creates a new instance.
        
        :param name: A parameter name.'''
        ...
    
    ...

class PrintTicket:
    '''The class that implements a common PrintTicket of any scope.
    The base class for job-, document- and page-level print tickets.
    A
    PrintTicket
    
     element is the root element of the PrintTicket document.
    A
    PrintTicket
    
     element contains all job formatting information required to output a job.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/printticket'''
    
    def remove(self, names: list[str]) -> None:
        '''Removes an item from this PrintTicket item list.
        
        :param names: An array of item names.'''
        ...
    
    ...

class PrintTicketElement:
    '''The base class for classes that may be Print Schema elements.'''
    
    @property
    def name(self) -> str:
        '''Gets the element name.'''
        ...
    
    ...

class Property(aspose.page.xps.xpsmetadata.CompositePrintTicketElement):
    '''The class that implements a common PrintTicket
    Property
    
    .
    The base class for all schema-defined properties.
    A
    Property
    
     element declares a device, job formatting, or other relevant property
    whose name is given by its name attribute. A:class:`Value` element is used to assign
    a value to the
    Property
    
    .
    A
    Property
    
     can be complex, possibly containing multiple subproperties.
    Subproperties are also represented by
    Property
    
     elements.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/property'''
    
    @overload
    def __init__(self, name: str, property: aspose.page.xps.xpsmetadata.Property, items: list[aspose.page.xps.xpsmetadata.IPropertyItem]):
        '''Creates a new instance.
        
        :param name: A property name.
        :param property: A mandatory :class:`Property` instance.
        :param items: An arbitrary array of :class:`IPropertyItem` instances.
                      Each one must be a :class:`Property` or a :class:`Value` instance.'''
        ...
    
    @overload
    def __init__(self, name: str, value: aspose.page.xps.xpsmetadata.Value, items: list[aspose.page.xps.xpsmetadata.IPropertyItem]):
        '''Creates a new instance.
        
        :param name: A property name.
        :param value: A mandatory :class:`Value` instance.
        :param items: An arbitrary array of :class:`IPropertyItem` instances.
                      Each one must be a :class:`Property` or a :class:`Value` instance.'''
        ...
    
    ...

class QNameValue(aspose.page.xps.xpsmetadata.Value):
    '''The class that incapsulates a QName value in a PrintTicket document.'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: A QName value.'''
        ...
    
    ...

class RollCut(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobRollCutAtEndOfJob` and :class:`DocumentRollCut` features classes.'''
    
    ...

class ScoredProperty(aspose.page.xps.xpsmetadata.CompositePrintTicketElement):
    '''The class that implements a common PrintTicket
    ScoredProperty
    
    .
    The base class for all schema-defined scored properties.
    A
    ScoredProperty
    
     element declares a property that is intrinsic to an:class:`Option` definition. Such properties should be compared when evaluating
    how closely a requested :class:`Option` matches a device-supported :class:`Option`.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/scoredproperty'''
    
    @overload
    def __init__(self, name: str, parameter_ref: aspose.page.xps.xpsmetadata.ParameterRef):
        '''Creates a new instance.
        
        :param name: A property name.
        :param parameter_ref: A :class:`ParameterRef` instance.'''
        ...
    
    @overload
    def __init__(self, name: str, value: aspose.page.xps.xpsmetadata.Value, items: list[aspose.page.xps.xpsmetadata.IScoredPropertyItem]):
        '''Creates a new instance.
        
        :param name: A property name.
        :param value: A property value.
        :param items: An arbitrary array of :class:`IScoredPropertyItem` instances.
                      Each one must be a :class:`ScoredProperty`, a :class:`Property` or a :class:`Value` instance.'''
        ...
    
    ...

class SelectionType(aspose.page.xps.xpsmetadata.Property):
    '''The convenience class for SelectionType PrintTicket property.'''
    
    PICK_ONE: aspose.page.xps.xpsmetadata.SelectionType
    
    PICK_MANY: aspose.page.xps.xpsmetadata.SelectionType
    
    ...

class Staple(aspose.page.xps.xpsmetadata.Feature):
    '''The base class for :class:`JobStapleAllDocuments` and :class:`DocumentStaple` features classes.'''
    
    ...

class StringParameterInit(aspose.page.xps.xpsmetadata.ParameterInit):
    '''Base class for all string parameter initializers.'''
    
    @property
    def min_length(self) -> int:
        '''For string values, defines the shortest allowed string.'''
        ...
    
    @property
    def max_length(self) -> int:
        '''For string values, defines the longest allowed string.'''
        ...
    
    ...

class StringValue(aspose.page.xps.xpsmetadata.Value):
    '''The class that incapsulates a String value in a PrintTicket document.'''
    
    def __init__(self, value: str):
        '''Creates a new instance.
        
        :param value: A string value.'''
        ...
    
    ...

class URIProperty(aspose.page.xps.xpsmetadata.Property):
    '''The base class for :class:`JobURI` and :class:`DocumentURI` properties classes.'''
    
    ...

class Value(aspose.page.xps.xpsmetadata.PrintTicketElement):
    '''The base class that incapsulates a :class:`Property` or a :class:`ScoredProperty`
    value in a PrintTicket document.
    A Value element associates a literal with a type.
    https://docs.microsoft.com/en-us/windows/win32/printdocs/value'''
    
    @property
    def value_string(self) -> str:
        '''Gets the value as string.'''
        ...
    
    ...

class CollateOption(aspose.page.xps.xpsmetadata.Option):
    
    collated: aspose.page.xps.xpsmetadata.Collate.CollateOption
    
    uncollated: aspose.page.xps.xpsmetadata.Collate.CollateOption
    
    ...

class BannerSheetOption(aspose.page.xps.xpsmetadata.Option):
    
    none: aspose.page.xps.xpsmetadata.DocumentBannerSheet.BannerSheetOption
    
    standard: aspose.page.xps.xpsmetadata.DocumentBannerSheet.BannerSheetOption
    
    custom: aspose.page.xps.xpsmetadata.DocumentBannerSheet.BannerSheetOption
    
    ...

class BindingGutter(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    def __init__(self, value: int):
        ...
    
    document_binding_gutter: aspose.page.xps.xpsmetadata.DocumentBinding.BindingGutter
    
    ...

class BindingOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, name: str, items: list[aspose.page.xps.xpsmetadata.DocumentBinding.IBindingOptionItem]):
        ...
    
    bale: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    bind_bottom: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    bind_left: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    bind_right: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    bind_top: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    booklet: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    edge_stitch_bottom: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    edge_stitch_left: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    edge_stitch_right: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    edge_stitch_top: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    fold: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    jog_offset: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    trim: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    none: aspose.page.xps.xpsmetadata.DocumentBinding.BindingOption
    
    ...

class IBindingOptionItem:
    
    ...

class CoverBackOption(aspose.page.xps.xpsmetadata.Option):
    
    no_cover: aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption
    
    print_back: aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption
    
    print_both: aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption
    
    print_front: aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption
    
    blank_cover: aspose.page.xps.xpsmetadata.DocumentCoverBack.CoverBackOption
    
    ...

class CoverFrontOption(aspose.page.xps.xpsmetadata.Option):
    
    no_cover: aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption
    
    print_back: aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption
    
    print_both: aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption
    
    print_front: aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption
    
    blank_cover: aspose.page.xps.xpsmetadata.DocumentCoverFront.CoverFrontOption
    
    ...

class DocumentSeparatorSheetOption(aspose.page.xps.xpsmetadata.Option):
    
    both_sheets: aspose.page.xps.xpsmetadata.DocumentSeparatorSheet.DocumentSeparatorSheetOption
    
    end_sheet: aspose.page.xps.xpsmetadata.DocumentSeparatorSheet.DocumentSeparatorSheetOption
    
    none: aspose.page.xps.xpsmetadata.DocumentSeparatorSheet.DocumentSeparatorSheetOption
    
    start_sheet: aspose.page.xps.xpsmetadata.DocumentSeparatorSheet.DocumentSeparatorSheetOption
    
    ...

class DuplexMode(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    AUTOMATIC: aspose.page.xps.xpsmetadata.Duplex.DuplexMode
    
    MANUAL: aspose.page.xps.xpsmetadata.Duplex.DuplexMode
    
    ...

class DuplexOption(aspose.page.xps.xpsmetadata.Option):
    
    @staticmethod
    def two_sided_short_edge(self, duplex_mode: aspose.page.xps.xpsmetadata.Duplex.DuplexMode) -> aspose.page.xps.xpsmetadata.Duplex.DuplexOption:
        ...
    
    @staticmethod
    def two_sided_long_edge(self, duplex_mode: aspose.page.xps.xpsmetadata.Duplex.DuplexMode) -> aspose.page.xps.xpsmetadata.Duplex.DuplexOption:
        ...
    
    ONE_SIDED: aspose.page.xps.xpsmetadata.Duplex.DuplexOption
    
    ...

class HolePunchOption(aspose.page.xps.xpsmetadata.Option):
    
    bottom_edge: aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption
    
    left_edge: aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption
    
    none: aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption
    
    right_edge: aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption
    
    top_edge: aspose.page.xps.xpsmetadata.HolePunch.HolePunchOption
    
    ...

class BinType(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    CONTINUOUS_FEED: aspose.page.xps.xpsmetadata.InputBin.BinType
    
    SHEET_FEED: aspose.page.xps.xpsmetadata.InputBin.BinType
    
    ...

class FeedDirection(aspose.page.xps.xpsmetadata.Property):
    
    LONG_EDGE_FIRST: aspose.page.xps.xpsmetadata.InputBin.FeedDirection
    
    SHORT_EDGE_FIRST: aspose.page.xps.xpsmetadata.InputBin.FeedDirection
    
    ...

class FeedFace(aspose.page.xps.xpsmetadata.Property):
    
    FACE_UP: aspose.page.xps.xpsmetadata.InputBin.FeedFace
    
    FACE_DOWN: aspose.page.xps.xpsmetadata.InputBin.FeedFace
    
    ...

class FeedType(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    AUTOMATIC: aspose.page.xps.xpsmetadata.InputBin.FeedType
    
    MANUAL: aspose.page.xps.xpsmetadata.InputBin.FeedType
    
    ...

class IInputBinItem:
    
    ...

class IInputBinOptionItem:
    
    ...

class InputBinOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.InputBin.IInputBinOptionItem]):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.InputBin.IInputBinOptionItem]) -> aspose.page.xps.xpsmetadata.InputBin.InputBinOption:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmetadata.InputBin.InputBinOption:
        ...
    
    AUTO_SELECT: aspose.page.xps.xpsmetadata.InputBin.InputBinOption
    
    MANUAL: aspose.page.xps.xpsmetadata.InputBin.InputBinOption
    
    CASSETTE: aspose.page.xps.xpsmetadata.InputBin.InputBinOption
    
    TRACTOR: aspose.page.xps.xpsmetadata.InputBin.InputBinOption
    
    AUTO_SHEET_FEEDER: aspose.page.xps.xpsmetadata.InputBin.InputBinOption
    
    ...

class MediaCapacity(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    HIGH: aspose.page.xps.xpsmetadata.InputBin.MediaCapacity
    
    STANDARD: aspose.page.xps.xpsmetadata.InputBin.MediaCapacity
    
    ...

class MediaPath(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    STRAIGHT: aspose.page.xps.xpsmetadata.InputBin.MediaPath
    
    SERPENTINE: aspose.page.xps.xpsmetadata.InputBin.MediaPath
    
    ...

class MediaSheetCapacity(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    def __init__(self, media_sheet_capacity: int):
        ...
    
    ...

class MediaSizeAutoSense(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    SUPPORTED: aspose.page.xps.xpsmetadata.InputBin.MediaSizeAutoSense
    
    NONE: aspose.page.xps.xpsmetadata.InputBin.MediaSizeAutoSense
    
    ...

class MediaTypeAutoSense(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    SUPPORTED: aspose.page.xps.xpsmetadata.InputBin.MediaTypeAutoSense
    
    NONE: aspose.page.xps.xpsmetadata.InputBin.MediaTypeAutoSense
    
    ...

class JobAccountingSheetOption(aspose.page.xps.xpsmetadata.Option):
    
    NONE: aspose.page.xps.xpsmetadata.JobAccountingSheet.JobAccountingSheetOption
    
    STANDARD: aspose.page.xps.xpsmetadata.JobAccountingSheet.JobAccountingSheetOption
    
    ...

class BindingGutter(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    def __init__(self, value: int):
        ...
    
    JOB_BIND_ALL_DOCUMENTS_GUTTER: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingGutter
    
    ...

class BindingOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, name: str, items: list[aspose.page.xps.xpsmetadata.JobBindAllDocuments.IBindingOptionItem]):
        ...
    
    BALE: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    BIND_BOTTOM: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    BIND_LEFT: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    BIND_RIGHT: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    BIND_TOP: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    BOOKLET: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    EDGE_STITCH_BOTTOM: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    EDGE_STITCH_LEFT: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    EDGE_STITCH_RIGHT: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    EDGE_STITCH_TOP: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    FOLD: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    JOG_OFFSET: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    TRIM: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    NONE: aspose.page.xps.xpsmetadata.JobBindAllDocuments.BindingOption
    
    ...

class IBindingOptionItem:
    
    ...

class IJobDeviceLanguageOptionItem:
    
    ...

class JobDeviceLanguageOption(aspose.page.xps.xpsmetadata.Option):
    
    @overload
    def __init__(self, name: str, items: list[aspose.page.xps.xpsmetadata.JobDeviceLanguage.IJobDeviceLanguageOptionItem]):
        ...
    
    @overload
    def __init__(self, option: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.JobDeviceLanguage.IJobDeviceLanguageOptionItem]) -> aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption:
        ...
    
    def set_language_level(self, language_level: str) -> aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption:
        ...
    
    def set_language_encoding(self, language_encoding: str) -> aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption:
        ...
    
    def set_language_version(self, language_version: str) -> aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption:
        ...
    
    XPS: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    _201PL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    ART: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    ASCII: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    CA_PSL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    ESCP2: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    ESC_PAGE: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    HPGL2: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    KPDL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    KS: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    KSSM: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    PCL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    PCL5C: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    PCL5E: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    PCLXL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    POST_SCRIPT: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    PPDS: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    RPDL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    RTL: aspose.page.xps.xpsmetadata.JobDeviceLanguage.JobDeviceLanguageOption
    
    ...

class JobDigitalSignatureProcessingOption(aspose.page.xps.xpsmetadata.Option):
    
    PRINT_INVALID_SIGNATURES: aspose.page.xps.xpsmetadata.JobDigitalSignatureProcessing.JobDigitalSignatureProcessingOption
    
    PRINT_INVALID_SIGNATURES_WITH_ERROR_REPORT: aspose.page.xps.xpsmetadata.JobDigitalSignatureProcessing.JobDigitalSignatureProcessingOption
    
    PRINT_ONLY_VALID_SIGNATURES: aspose.page.xps.xpsmetadata.JobDigitalSignatureProcessing.JobDigitalSignatureProcessingOption
    
    ...

class ErrorSheetOption(aspose.page.xps.xpsmetadata.Option):
    
    CUSTOM: aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetOption
    
    NONE: aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetOption
    
    STANDARD: aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetOption
    
    ...

class ErrorSheetWhen(aspose.page.xps.xpsmetadata.Feature):
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetWhen.ErrorSheetWhenOption]):
        ...
    
    ...

class ErrorSheetWhenOption(aspose.page.xps.xpsmetadata.Option):
    
    ALWAYS: aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetWhen.ErrorSheetWhenOption
    
    ON_ERROR: aspose.page.xps.xpsmetadata.JobErrorSheet.ErrorSheetWhen.ErrorSheetWhenOption
    
    ...

class IJobErrorSheetItem:
    
    ...

class Profile:
    
    RGB: aspose.page.xps.xpsmetadata.JobOptimalDestinationColorProfile.Profile
    
    ICC: aspose.page.xps.xpsmetadata.JobOptimalDestinationColorProfile.Profile
    
    CMYK: aspose.page.xps.xpsmetadata.JobOptimalDestinationColorProfile.Profile
    
    ...

class JobOutputOptimizationOption(aspose.page.xps.xpsmetadata.Option):
    
    ARCHIVE_FORMAT: aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption
    
    OPTIMIZE_FOR_PORTABILITY: aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption
    
    OPTIMIZE_FOR_QUALITY: aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption
    
    OPTIMIZE_FOR_SPEED: aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption
    
    NONE: aspose.page.xps.xpsmetadata.JobOutputOptimization.JobOutputOptimizationOption
    
    ...

class JobPageOrderOption(aspose.page.xps.xpsmetadata.Option):
    
    STANDARD: aspose.page.xps.xpsmetadata.JobPageOrder.JobPageOrderOption
    
    REVERSE: aspose.page.xps.xpsmetadata.JobPageOrder.JobPageOrderOption
    
    ...

class BannerSheetOption(aspose.page.xps.xpsmetadata.Option):
    
    NONE: aspose.page.xps.xpsmetadata.JobPrimaryBannerSheet.BannerSheetOption
    
    STANDARD: aspose.page.xps.xpsmetadata.JobPrimaryBannerSheet.BannerSheetOption
    
    CUSTOM: aspose.page.xps.xpsmetadata.JobPrimaryBannerSheet.BannerSheetOption
    
    ...

class CoverBackOption(aspose.page.xps.xpsmetadata.Option):
    
    NO_COVER: aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption
    
    PRINT_BACK: aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption
    
    PRINT_BOTH: aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption
    
    PRINT_FRONT: aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption
    
    BLANK_COVER: aspose.page.xps.xpsmetadata.JobPrimaryCoverBack.CoverBackOption
    
    ...

class CoverFrontOption(aspose.page.xps.xpsmetadata.Option):
    
    NO_COVER: aspose.page.xps.xpsmetadata.JobPrimaryCoverFront.CoverFrontOption
    
    PRINT_BACK: aspose.page.xps.xpsmetadata.JobPrimaryCoverFront.CoverFrontOption
    
    PRINT_BOTH: aspose.page.xps.xpsmetadata.JobPrimaryCoverFront.CoverFrontOption
    
    PRINT_FRONT: aspose.page.xps.xpsmetadata.JobPrimaryCoverFront.CoverFrontOption
    
    BLANK_COVER: aspose.page.xps.xpsmetadata.JobPrimaryCoverFront.CoverFrontOption
    
    ...

class INUpItem:
    
    ...

class PresentationDirection(aspose.page.xps.xpsmetadata.Feature):
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption]):
        ...
    
    ...

class PresentationDirectionOption(aspose.page.xps.xpsmetadata.Option):
    
    right_bottom: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    bottom_right: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    left_bottom: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    bottom_left: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    right_top: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    top_right: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    left_top: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    top_left: aspose.page.xps.xpsmetadata.NUp.PresentationDirection.PresentationDirectionOption
    
    ...

class BinType(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    MAIL_BOX: aspose.page.xps.xpsmetadata.OutputBin.BinType
    
    SORTER: aspose.page.xps.xpsmetadata.OutputBin.BinType
    
    STACKER: aspose.page.xps.xpsmetadata.OutputBin.BinType
    
    FINISHER: aspose.page.xps.xpsmetadata.OutputBin.BinType
    
    NONE: aspose.page.xps.xpsmetadata.OutputBin.BinType
    
    ...

class IOutputBinItem:
    
    ...

class IOutputBinOptionItem:
    
    ...

class MediaSheetCapacity(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    def __init__(self, media_sheet_capacity: int):
        ...
    
    ...

class OutputBinOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, items: list[aspose.page.xps.xpsmetadata.OutputBin.IOutputBinOptionItem]):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.OutputBin.IOutputBinOptionItem]) -> aspose.page.xps.xpsmetadata.OutputBin.OutputBinOption:
        ...
    
    ...

class PageBlackGenerationProcessingOption(aspose.page.xps.xpsmetadata.Option):
    
    automatic: aspose.page.xps.xpsmetadata.PageBlackGenerationProcessing.PageBlackGenerationProcessingOption
    
    custom: aspose.page.xps.xpsmetadata.PageBlackGenerationProcessing.PageBlackGenerationProcessingOption
    
    ...

class PageBlendColorSpaceOption(aspose.page.xps.xpsmetadata.Option):
    
    s_rgb: aspose.page.xps.xpsmetadata.PageBlendColorSpace.PageBlendColorSpaceOption
    
    sc_rgb: aspose.page.xps.xpsmetadata.PageBlendColorSpace.PageBlendColorSpaceOption
    
    icc_profile: aspose.page.xps.xpsmetadata.PageBlendColorSpace.PageBlendColorSpaceOption
    
    ...

class PageBorderlessOption(aspose.page.xps.xpsmetadata.Option):
    
    borderless: aspose.page.xps.xpsmetadata.PageBorderless.PageBorderlessOption
    
    none: aspose.page.xps.xpsmetadata.PageBorderless.PageBorderlessOption
    
    ...

class PageColorManagementOption(aspose.page.xps.xpsmetadata.Option):
    
    none: aspose.page.xps.xpsmetadata.PageColorManagement.PageColorManagementOption
    
    device: aspose.page.xps.xpsmetadata.PageColorManagement.PageColorManagementOption
    
    driver: aspose.page.xps.xpsmetadata.PageColorManagement.PageColorManagementOption
    
    system: aspose.page.xps.xpsmetadata.PageColorManagement.PageColorManagementOption
    
    ...

class PageDestinationColorProfileOption(aspose.page.xps.xpsmetadata.Option):
    
    application: aspose.page.xps.xpsmetadata.PageDestinationColorProfile.PageDestinationColorProfileOption
    
    driver_configuration: aspose.page.xps.xpsmetadata.PageDestinationColorProfile.PageDestinationColorProfileOption
    
    ...

class PageDeviceColorSpaceUsageOption(aspose.page.xps.xpsmetadata.Option):
    
    match_to_default: aspose.page.xps.xpsmetadata.PageDeviceColorSpaceUsage.PageDeviceColorSpaceUsageOption
    
    override_device_default: aspose.page.xps.xpsmetadata.PageDeviceColorSpaceUsage.PageDeviceColorSpaceUsageOption
    
    ...

class PageDeviceFontSubstitutionOption(aspose.page.xps.xpsmetadata.Option):
    
    off: aspose.page.xps.xpsmetadata.PageDeviceFontSubstitution.PageDeviceFontSubstitutionOption
    
    on: aspose.page.xps.xpsmetadata.PageDeviceFontSubstitution.PageDeviceFontSubstitutionOption
    
    ...

class PageForceFrontSideOption(aspose.page.xps.xpsmetadata.Option):
    
    force_front_side: aspose.page.xps.xpsmetadata.PageForceFrontSide.PageForceFrontSideOption
    
    none: aspose.page.xps.xpsmetadata.PageForceFrontSide.PageForceFrontSideOption
    
    ...

class PageICMRenderingIntentOption(aspose.page.xps.xpsmetadata.Option):
    
    absolute_colorimetric: aspose.page.xps.xpsmetadata.PageICMRenderingIntent.PageICMRenderingIntentOption
    
    relative_colorimetric: aspose.page.xps.xpsmetadata.PageICMRenderingIntent.PageICMRenderingIntentOption
    
    photographs: aspose.page.xps.xpsmetadata.PageICMRenderingIntent.PageICMRenderingIntentOption
    
    business_graphics: aspose.page.xps.xpsmetadata.PageICMRenderingIntent.PageICMRenderingIntentOption
    
    ...

class PageMediaColorOption(aspose.page.xps.xpsmetadata.Option):
    
    @staticmethod
    def custom(self, media_colors_rgb: str) -> aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption:
        ...
    
    black: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    blue: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    brown: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    gold: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    golden_rod: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    gray: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    green: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    ivory: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    no_color: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    orange: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    pink: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    red: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    silver: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    turquoise: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    violet: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    white: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    yellow: aspose.page.xps.xpsmetadata.PageMediaColor.PageMediaColorOption
    
    ...

class IPageMediaSizeItem:
    
    ...

class IPageMediaSizeOptionItem:
    
    ...

class PageMediaSizeOption(aspose.page.xps.xpsmetadata.Option):
    
    @overload
    def __init__(self, name: str, items: list[aspose.page.xps.xpsmetadata.PageMediaSize.IPageMediaSizeOptionItem]):
        ...
    
    @overload
    def __init__(self, option: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.PageMediaSize.IPageMediaSizeOptionItem]) -> aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption:
        ...
    
    def set_media_size_width(self, media_size_width: int) -> aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption:
        ...
    
    def set_media_size_height(self, media_size_height: int) -> aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption:
        ...
    
    custom_media_size: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    ps_custom_media_size: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa0: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa1: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa10: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa2: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa3: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa3_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa3_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa4: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa4_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa4_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa5: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa5_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa5_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa6: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa6_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa7: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa8: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoa9: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob0: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob1: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob10: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob2: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob3: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob4: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob4_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob5_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob5_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob7: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob8: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isob9: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc0: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc1: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc10: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc2: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc3: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc3_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc4: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc4_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc5: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc5_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc6: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc6_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc6c5_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc7: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc8: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isoc9: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isodl_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isodl_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    isosra3: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_quadruple_hagaki_postcard: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb0: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb1: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb10: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb2: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb3: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb4: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb4_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb5: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb5_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb6: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb6_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb7: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb8: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    jisb9: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_chou_3_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_chou_3_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_chou_4_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_chou_4_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_hagaki_postcard: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_hagaki_postcard_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_kaku_2_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_kaku_2_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_kaku_3_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_kaku_3_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_4_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_10x11: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_10x14: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_11x17: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_9x11: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_architecture_a_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_architecture_b_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_architecture_c_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_architecture_d_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_architecture_e_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_c_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_d_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_e_sheet: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_executive: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_german_legal_fanfold: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_german_standard_fanfold: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_legal: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_legal_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_letter: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_letter_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_letter_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_letter_plus: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_monarch_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_note: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_10_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_10_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_9_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_11_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_12_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_number_14_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_personal_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_quarto: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_statement: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_super_a: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_super_b: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_tabloid: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_tabloid_extra: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    other_metric_a4_plus: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    other_metric_a3_plus: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    other_metric_folio: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    other_metric_invite_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    other_metric_italian_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc1_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc1_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc10_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc10_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc16k: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc16k_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc2_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc2_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc32k: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc32k_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc32k_big: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc3_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc3_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc4_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc4_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc5_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc5_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc6_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc6_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc7_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc7_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc8_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc8_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc9_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    prc9_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_06_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_08_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_12_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_15_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_18_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_22_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_24_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_30_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_36_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    roll_54_inch: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_double_hagaki_postcard: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_double_hagaki_postcard_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_l_photo: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_2l_photo: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_1_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_2_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_3_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_4_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_6_envelope: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    japan_you_6_envelope_rotated: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_4x6: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_4x8: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_5x7: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_8x10: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_10x12: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    north_america_14x17: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    business_card: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    credit_card: aspose.page.xps.xpsmetadata.PageMediaSize.PageMediaSizeOption
    
    ...

class BackCoating(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    glossy: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    high_gloss: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    matte: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    satin: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    semi_gloss: aspose.page.xps.xpsmetadata.PageMediaType.BackCoating
    
    ...

class FrontCoating(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    glossy: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    high_gloss: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    matte: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    satin: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    semi_gloss: aspose.page.xps.xpsmetadata.PageMediaType.FrontCoating
    
    ...

class IPageMediaTypeItem:
    
    ...

class IPageMediaTypeOptionItem:
    
    ...

class Material(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    aluminum: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    display: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    dry_film: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    paper: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    polyester: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    transparency: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    wet_film: aspose.page.xps.xpsmetadata.PageMediaType.Material
    
    ...

class PageMediaTypeOption(aspose.page.xps.xpsmetadata.Option):
    
    @overload
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.PageMediaType.IPageMediaTypeOptionItem]):
        ...
    
    @overload
    def __init__(self, option: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.PageMediaType.IPageMediaTypeOptionItem]) -> aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption:
        ...
    
    def set_weight(self, weight: int) -> aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption:
        ...
    
    auto_select: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    archival: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    back_print_film: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    bond: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    card_stock: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    continous: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    envelope_plain: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    envelope_window: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    fabric: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    high_resolution: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    label: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    multi_layer_form: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    multi_part_form: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_film: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_glossy: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_high_gloss: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_matte: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_satin: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    photographic_semi_gloss: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    plain: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    screen: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    screen_paged: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    stationary: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    tab_stock_full: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    tab_stock_pre_cut: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    transparency: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    t_shirt_transfer: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.PageMediaTypeOption
    
    ...

class PrePrinted(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.PrePrinted
    
    pre_printed_value: aspose.page.xps.xpsmetadata.PageMediaType.PrePrinted
    
    letterhead: aspose.page.xps.xpsmetadata.PageMediaType.PrePrinted
    
    ...

class PrePunched(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.PrePunched
    
    pre_punched_value: aspose.page.xps.xpsmetadata.PageMediaType.PrePunched
    
    ...

class Recycled(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    none: aspose.page.xps.xpsmetadata.PageMediaType.Recycled
    
    standard: aspose.page.xps.xpsmetadata.PageMediaType.Recycled
    
    ...

class PageMirrorImageOption(aspose.page.xps.xpsmetadata.Option):
    
    mirror_image_width: aspose.page.xps.xpsmetadata.PageMirrorImage.PageMirrorImageOption
    
    mirror_image_height: aspose.page.xps.xpsmetadata.PageMirrorImage.PageMirrorImageOption
    
    none: aspose.page.xps.xpsmetadata.PageMirrorImage.PageMirrorImageOption
    
    ...

class PageNegativeImageOption(aspose.page.xps.xpsmetadata.Option):
    
    negative: aspose.page.xps.xpsmetadata.PageNegativeImage.PageNegativeImageOption
    
    none: aspose.page.xps.xpsmetadata.PageNegativeImage.PageNegativeImageOption
    
    ...

class PageOrientationOption(aspose.page.xps.xpsmetadata.Option):
    
    LANDSCAPE: aspose.page.xps.xpsmetadata.PageOrientation.PageOrientationOption
    
    PORTRAIT: aspose.page.xps.xpsmetadata.PageOrientation.PageOrientationOption
    
    REVERSE_LANDSCAPE: aspose.page.xps.xpsmetadata.PageOrientation.PageOrientationOption
    
    REVERSE_PORTRAIT: aspose.page.xps.xpsmetadata.PageOrientation.PageOrientationOption
    
    ...

class IPageOutputColorItem:
    
    ...

class IPageOutputColorOptionItem:
    
    ...

class PageOutputColorOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.PageOutputColor.IPageOutputColorOptionItem]):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.PageOutputColor.IPageOutputColorOptionItem]) -> aspose.page.xps.xpsmetadata.PageOutputColor.PageOutputColorOption:
        ...
    
    @staticmethod
    def color(self, device_bits_per_pixel: int, driver_bits_per_pixel: int) -> aspose.page.xps.xpsmetadata.PageOutputColor.PageOutputColorOption:
        ...
    
    @staticmethod
    def grayscale(self, device_bits_per_pixel: int, driver_bits_per_pixel: int) -> aspose.page.xps.xpsmetadata.PageOutputColor.PageOutputColorOption:
        ...
    
    @staticmethod
    def monochrome(self, device_bits_per_pixel: int, driver_bits_per_pixel: int) -> aspose.page.xps.xpsmetadata.PageOutputColor.PageOutputColorOption:
        ...
    
    ...

class PageOutputQualityOption(aspose.page.xps.xpsmetadata.Option):
    
    automatic: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    draft: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    fax: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    high: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    normal: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    photographic: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    text: aspose.page.xps.xpsmetadata.PageOutputQuality.PageOutputQualityOption
    
    ...

class PagePhotoPrintingIntentOption(aspose.page.xps.xpsmetadata.Option):
    
    none: aspose.page.xps.xpsmetadata.PagePhotoPrintingIntent.PagePhotoPrintingIntentOption
    
    photo_best: aspose.page.xps.xpsmetadata.PagePhotoPrintingIntent.PagePhotoPrintingIntentOption
    
    photo_draft: aspose.page.xps.xpsmetadata.PagePhotoPrintingIntent.PagePhotoPrintingIntentOption
    
    photo_standard: aspose.page.xps.xpsmetadata.PagePhotoPrintingIntent.PagePhotoPrintingIntentOption
    
    ...

class IPageResolutionItem:
    
    ...

class IPageResolutionOptionItem:
    
    ...

class PageResolutionOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.PageResolution.IPageResolutionOptionItem]):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.PageResolution.IPageResolutionOptionItem]) -> aspose.page.xps.xpsmetadata.PageResolution.PageResolutionOption:
        ...
    
    def set_resolution_x(self, resolution_x: int) -> aspose.page.xps.xpsmetadata.PageResolution.PageResolutionOption:
        ...
    
    def set_resolution_y(self, resolution_y: int) -> aspose.page.xps.xpsmetadata.PageResolution.PageResolutionOption:
        ...
    
    ...

class QualitativeResolution(aspose.page.xps.xpsmetadata.ScoredProperty):
    
    default: aspose.page.xps.xpsmetadata.PageResolution.QualitativeResolution
    
    draft: aspose.page.xps.xpsmetadata.PageResolution.QualitativeResolution
    
    high: aspose.page.xps.xpsmetadata.PageResolution.QualitativeResolution
    
    normal: aspose.page.xps.xpsmetadata.PageResolution.QualitativeResolution
    
    other: aspose.page.xps.xpsmetadata.PageResolution.QualitativeResolution
    
    ...

class IPageScalingItem:
    
    ...

class PageScalingOption(aspose.page.xps.xpsmetadata.Option):
    
    custom: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    custom_square: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    fit_application_bleed_size_to_page_imageable_size: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    fit_application_content_size_to_page_imageable_size: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    fit_application_media_size_to_page_imageable_size: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    fit_application_media_size_to_page_media_size: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    none: aspose.page.xps.xpsmetadata.PageScaling.PageScalingOption
    
    ...

class ScaleOffsetAlignment(aspose.page.xps.xpsmetadata.Feature):
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption]):
        ...
    
    ...

class ScaleOffsetAlignmentOption(aspose.page.xps.xpsmetadata.Option):
    
    bottom_center: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    bottom_left: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    bottom_right: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    center: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    left_center: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    right_center: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    top_center: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    top_left: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    top_right: aspose.page.xps.xpsmetadata.PageScaling.ScaleOffsetAlignmentOption
    
    ...

class PageSourceColorProfileOption(aspose.page.xps.xpsmetadata.Option):
    
    rgb: aspose.page.xps.xpsmetadata.PageSourceColorProfile.PageSourceColorProfileOption
    
    cmyk: aspose.page.xps.xpsmetadata.PageSourceColorProfile.PageSourceColorProfileOption
    
    none: aspose.page.xps.xpsmetadata.PageSourceColorProfile.PageSourceColorProfileOption
    
    ...

class PageTrueTypeFontModeOption(aspose.page.xps.xpsmetadata.Option):
    
    automatic: aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption
    
    download_as_outline_font: aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption
    
    download_as_raster_font: aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption
    
    download_as_native_true_type_font: aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption
    
    render_as_bitmap: aspose.page.xps.xpsmetadata.PageTrueTypeFontMode.PageTrueTypeFontModeOption
    
    ...

class IPageWatermarkItem:
    
    ...

class IPageWatermarkOptionItem:
    
    ...

class Layering(aspose.page.xps.xpsmetadata.Feature):
    
    def __init__(self, options: list[aspose.page.xps.xpsmetadata.PageWatermark.LayeringOption]):
        ...
    
    ...

class LayeringOption(aspose.page.xps.xpsmetadata.Option):
    
    overlay: aspose.page.xps.xpsmetadata.PageWatermark.LayeringOption
    
    underlay: aspose.page.xps.xpsmetadata.PageWatermark.LayeringOption
    
    ...

class PageWatermarkOption(aspose.page.xps.xpsmetadata.Option):
    
    @overload
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.PageWatermark.IPageWatermarkOptionItem]):
        ...
    
    @overload
    def __init__(self, option: aspose.page.xps.xpsmetadata.PageWatermark.PageWatermarkOption):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.PageWatermark.IPageWatermarkOptionItem]) -> aspose.page.xps.xpsmetadata.PageWatermark.PageWatermarkOption:
        ...
    
    def clone(self) -> aspose.page.xps.xpsmetadata.PageWatermark.PageWatermarkOption:
        ...
    
    text: aspose.page.xps.xpsmetadata.PageWatermark.PageWatermarkOption
    
    ...

class RollCutOption(aspose.page.xps.xpsmetadata.Option):
    
    banner: aspose.page.xps.xpsmetadata.RollCut.RollCutOption
    
    cut_sheet_at_image_edge: aspose.page.xps.xpsmetadata.RollCut.RollCutOption
    
    cut_sheet_at_standard_media_size: aspose.page.xps.xpsmetadata.RollCut.RollCutOption
    
    none: aspose.page.xps.xpsmetadata.RollCut.RollCutOption
    
    ...

class IStapleOptionItem:
    
    ...

class StapleOption(aspose.page.xps.xpsmetadata.Option):
    
    def __init__(self, option_name: str, items: list[aspose.page.xps.xpsmetadata.Staple.IStapleOptionItem]):
        ...
    
    @overload
    def add(self, items: list[aspose.page.xps.xpsmetadata.Staple.IStapleOptionItem]) -> aspose.page.xps.xpsmetadata.Staple.StapleOption:
        ...
    
    def set_angle(self, angle: int) -> aspose.page.xps.xpsmetadata.Staple.StapleOption:
        ...
    
    def set_sheet_capacity(self, sheet_capacity: int) -> aspose.page.xps.xpsmetadata.Staple.StapleOption:
        ...
    
    SADDLE_STITCH: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_BOTTOM_LEFT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_BOTTOM_RIGHT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_DUAL_BOTTOM: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_DUAL_LEFT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_DUAL_RIGHT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_DUAL_TOP: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    NONE: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_TOP_LEFT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    STAPLE_TOP_RIGHT: aspose.page.xps.xpsmetadata.Staple.StapleOption
    
    ...

