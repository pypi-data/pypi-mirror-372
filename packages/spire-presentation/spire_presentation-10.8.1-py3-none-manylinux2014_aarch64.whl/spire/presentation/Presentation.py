from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from spire.presentation import _Presentation
from ctypes import *
import abc

class Presentation (_Presentation) :
    """
    Represents a PowerPoint presentation document. Provides comprehensive functionality 
    for creating, loading, manipulating, saving, and presenting slideshow documents.
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new empty Presentation instance.
        """
        GetDllLibPpt().Presentation_CreatePresentation.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_CreatePresentation)
        super(Presentation, self).__init__(intPtr)
    def __del__(self):
        """
        Destructor that releases resources associated with the Presentation instance.
        """
        GetDllLibPpt().Presentation_Dispose.argtypes = [c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_Dispose,self.Ptr)
        super(Presentation, self).__del__()
    
    @property

    def SlideSize(self)->'SlideSize':
        """
        Gets the current slide size configuration.

        Returns:
            SlideSize: Object representing slide dimensions and orientation.
        """
        GetDllLibPpt().Presentation_get_SlideSize.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SlideSize,self.Ptr)
        ret = None if intPtr==None else SlideSize(intPtr)
        return ret


    @property

    def SectionList(self)->'SectionList':
        """
        Gets the collection of sections organizing slides in the presentation.

        Returns:
            SectionList: Collection of presentation sections.
        """
        GetDllLibPpt().Presentation_get_SectionList.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SectionList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SectionList,self.Ptr)
        ret = None if intPtr==None else SectionList(intPtr)
        return ret



    def SetPageSize(self ,w:float,h:float,IsRatio:bool):
        """
        Configures the page/slide dimensions.

        Args:
            w: Width value or width ratio
            h: Height value or height ratio
            IsRatio: True if values represent ratios, False for absolute units
        """
        
        GetDllLibPpt().Presentation_SetPageSize.argtypes=[c_void_p ,c_float,c_float,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetPageSize,self.Ptr, w,h,IsRatio)

    @property
    def StrictFirstAndLastCharacters(self)->bool:
        """
        Gets or sets whether to use strict typography rules for first/last characters.

        This property controls typographic rules regarding line breaks and character positioning.
        """
        GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_StrictFirstAndLastCharacters,self.Ptr)
        return ret

    @StrictFirstAndLastCharacters.setter
    def StrictFirstAndLastCharacters(self, value:bool):
        GetDllLibPpt().Presentation_set_StrictFirstAndLastCharacters.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_StrictFirstAndLastCharacters,self.Ptr, value)

    @property

    def WavAudios(self)->'WavAudioCollection':
        """
        Gets the collection of all embedded audio files in the presentation.

        Returns:
            WavAudioCollection: Collection of audio objects.
        """
        GetDllLibPpt().Presentation_get_WavAudios.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_WavAudios.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_WavAudios,self.Ptr)
        ret = None if intPtr==None else WavAudioCollection(intPtr)
        return ret


    @property

    def Videos(self)->'VideoCollection':
        """
        Gets the collection of all embedded video files in the presentation.

        Returns:
            VideoCollection: Collection of video objects.
        """
        GetDllLibPpt().Presentation_get_Videos.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Videos.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Videos,self.Ptr)
        ret = None if intPtr==None else VideoCollection(intPtr)
        return ret


    @property

    def TagsList(self)->'TagCollection':
        """
        Gets the collection of document tags/metadata.

        Returns:
            TagCollection: Collection of tag objects.
        """
        GetDllLibPpt().Presentation_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Images(self)->'ImageCollection':
        """
        Gets the collection of all images used in the presentation.

        Returns:
            ImageCollection: Collection of image objects.
        """
        GetDllLibPpt().Presentation_get_Images.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Images.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Images,self.Ptr)
        ret = None if intPtr==None else ImageCollection(intPtr)
        return ret


    @property

    def DocumentProperty(self)->'IDocumentProperty':
        """
        Gets standard and custom document properties.

        Returns:
            IDocumentProperty: Interface for accessing document properties.
        """
        GetDllLibPpt().Presentation_get_DocumentProperty.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DocumentProperty.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_DocumentProperty,self.Ptr)
        ret = None if intPtr==None else IDocumentProperty(intPtr)
        return ret


    @property

    def CommentAuthors(self)->'CommentAuthorCollection':
        """
        Gets the collection of comment authors in the presentation.

        Returns:
            CommentAuthorCollection: Collection of comment author objects.
        """
        GetDllLibPpt().Presentation_get_CommentAuthors.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_CommentAuthors.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_CommentAuthors,self.Ptr)
        ret = None if intPtr==None else CommentAuthorCollection(intPtr)
        return ret


    @property
    def DFlag(self)->bool:
        """
        Gets or sets the document flag status (internal use).

        This property is used internally for document state tracking.
        """
        GetDllLibPpt().Presentation_get_DFlag.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DFlag.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_DFlag,self.Ptr)
        return ret

    @DFlag.setter
    def DFlag(self, value:bool):
        GetDllLibPpt().Presentation_set_DFlag.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_DFlag,self.Ptr, value)

    @property

    def FormatAndVersion(self)->'FormatAndVersion':
        """
        Gets the file format and version of the presentation (read-only).

        Returns:
            FormatAndVersion: Enumeration value representing file format and version.
        """
        GetDllLibPpt().Presentation_get_FormatAndVersion.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FormatAndVersion.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FormatAndVersion,self.Ptr)
        objwraped = FormatAndVersion(ret)
        return objwraped

#
#    def AddDigitalSignature(self ,certificate:'X509Certificate2',comments:str,signTime:'DateTime')->'IDigitalSignatures':
#        """
#    <summary>
#        Add a DigitalSignature.
#    </summary>
#    <param name="certificate">Certificate object that was used to sign</param>
#    <param name="comments">Signature Comments</param>
#    <param name="signTime">Sign Time</param>
#    <returns>Collection of DigitalSignature</returns>
#        """
#        intPtrcertificate:c_void_p = certificate.Ptr
#        intPtrsignTime:c_void_p = signTime.Ptr
#
#        GetDllLibPpt().Presentation_AddDigitalSignature.argtypes=[c_void_p ,c_void_p,c_wchar_p,c_void_p]
#        GetDllLibPpt().Presentation_AddDigitalSignature.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().Presentation_AddDigitalSignature,self.Ptr, intPtrcertificate,comments,intPtrsignTime)
#        ret = None if intPtr==None else IDigitalSignatures(intPtr)
#        return ret
#



    def GetDigitalSignatures(self)->'IDigitalSignatures':
        """
        Gets the collection of digital signatures applied to the document.

        Returns:
            IDigitalSignatures: Collection of digital signature objects.
        """
        GetDllLibPpt().Presentation_GetDigitalSignatures.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_GetDigitalSignatures.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_GetDigitalSignatures,self.Ptr)
        ret = None if intPtr==None else IDigitalSignatures(intPtr)
        return ret


    def RemoveAllDigitalSignatures(self):
        """
        Removes all digital signatures from the document.
        """
        GetDllLibPpt().Presentation_RemoveAllDigitalSignatures.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveAllDigitalSignatures,self.Ptr)

    @property
    def IsDigitallySigned(self)->bool:
        """
        Indicates whether the presentation contains digital signatures.

        Returns:
            bool: True if digitally signed, False otherwise.
        """
        GetDllLibPpt().Presentation_get_IsDigitallySigned.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_IsDigitallySigned.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_IsDigitallySigned,self.Ptr)
        return ret


    def SetCustomFontsFolder(self ,fontsFolder:str):
        """
        Sets the folder path for custom fonts used in the presentation.

        Args:
            fontsFolder: Path to the folder containing custom fonts
        """
        
        fontsFolderPtr = StrToPtr(fontsFolder)
        GetDllLibPpt().Presentation_SetCustomFontsFolder.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetCustomFontsFolder,self.Ptr,fontsFolderPtr)

    @dispatch

    def IsPasswordProtected(self ,fileName:str)->bool:
        """
        Determines if a file is password protected.

        Args:
            fileName: Path to the file to check

        Returns:
            bool: True if password protected, False otherwise
        """
        
        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().Presentation_IsPasswordProtected.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().Presentation_IsPasswordProtected.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_IsPasswordProtected,self.Ptr,fileNamePtr)
        return ret

    @dispatch

    def IsPasswordProtected(self ,stream:Stream)->bool:
        """
        Determines if a stream contains a password protected presentation.

        Args:
            stream: Input stream containing presentation data

        Returns:
            bool: True if password protected, False otherwise
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().Presentation_IsPasswordProtectedS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Presentation_IsPasswordProtectedS.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_IsPasswordProtectedS,self.Ptr, intPtrstream)
        return ret

    @property
    def HighQualityImage(self)->bool:
        """
        Gets or sets whether to use high-quality image rendering.

        When True, images will be rendered at higher quality at the cost of performance.
        """
        GetDllLibPpt().Presentation_get_HighQualityImage.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HighQualityImage.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_HighQualityImage,self.Ptr)
        return ret

    @HighQualityImage.setter
    def HighQualityImage(self, value:bool):
        GetDllLibPpt().Presentation_set_HighQualityImage.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_HighQualityImage,self.Ptr, value)

    
    def SlideSizeAutoFit(self, value:bool):
        """
        Enables or disables automatic slide size fitting.

        Args:
            value: True to enable auto-fitting, False to disable
        """
        GetDllLibPpt().Presentation_set_SlideSizeAutoFit.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideSizeAutoFit,self.Ptr, value)

    def Dispose(self):
        """
        Releases all resources used by the Presentation object.
        """
        GetDllLibPpt().Presentation_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_Dispose,self.Ptr)

    @property

    def SaveToPdfOption(self)->'SaveToPdfOption':
        """
        Gets or sets options for saving to PDF format.

        Returns:
            SaveToPdfOption: Configuration object for PDF export.
        """
        GetDllLibPpt().Presentation_get_SaveToPdfOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToPdfOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToPdfOption,self.Ptr)
        ret = None if intPtr==None else SaveToPdfOption(intPtr)
        return ret


    @SaveToPdfOption.setter
    def SaveToPdfOption(self, value:'SaveToPdfOption'):
        GetDllLibPpt().Presentation_set_SaveToPdfOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToPdfOption,self.Ptr, value.Ptr)

    @property

    def SaveToHtmlOption(self)->'SaveToHtmlOption':
        """
        Gets or sets options for saving to HTML format.

        Returns:
            SaveToHtmlOption: Configuration object for HTML export.
        """
        GetDllLibPpt().Presentation_get_SaveToHtmlOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToHtmlOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToHtmlOption,self.Ptr)
        ret = None if intPtr==None else SaveToHtmlOption(intPtr)
        return ret


    @SaveToHtmlOption.setter
    def SaveToHtmlOption(self, value:'SaveToHtmlOption'):
        GetDllLibPpt().Presentation_set_SaveToHtmlOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToHtmlOption,self.Ptr, value.Ptr)

    @property

    def SaveToPptxOption(self)->'SaveToPptxOption':
        """
        Gets or sets options for saving to PPTX format.

        Returns:
            SaveToPptxOption: Configuration object for PPTX export.
        """
        GetDllLibPpt().Presentation_get_SaveToPptxOption.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveToPptxOption.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_SaveToPptxOption,self.Ptr)
        ret = None if intPtr==None else SaveToPptxOption(intPtr)
        return ret


    @SaveToPptxOption.setter
    def SaveToPptxOption(self, value:'SaveToPptxOption'):
        GetDllLibPpt().Presentation_set_SaveToPptxOption.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveToPptxOption,self.Ptr, value.Ptr)


    def FindSlide(self ,id:int)->'ISlide':
        """
        Finds a slide by its unique identifier.

        Args:
            id: Slide identifier to locate

        Returns:
            ISlide: Found slide object or None if not found
        """
        
        GetDllLibPpt().Presentation_FindSlide.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().Presentation_FindSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_FindSlide,self.Ptr, id)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


#
#    def GetBytes(self)->List['Byte']:
#        """
#    <summary>
#        Converts the document to an array of bytes. 
#    </summary>
#    <returns>An array of bytes.</returns>
#        """
#        GetDllLibPpt().Presentation_GetBytes.argtypes=[c_void_p]
#        GetDllLibPpt().Presentation_GetBytes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().Presentation_GetBytes,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret



    def GetStream(self)->'Stream':
        """
        Gets the presentation content as a readable stream.

        Returns:
            Stream: Readable stream containing presentation data
        """
        GetDllLibPpt().Presentation_GetStream.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat):
        """
        Loads presentation content from a stream.

        Args:
            stream: Stream containing presentation data
            fileFormat: Format of the presentation data
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt().Presentation_LoadFromStream.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromStream,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat,password:str):
        """
        Loads password-protected presentation content from a stream.

        Args:
            stream: Stream containing presentation data
            fileFormat: Format of the presentation data
            password: Password to unlock the presentation
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromStreamSFP.argtypes=[c_void_p ,c_void_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromStreamSFP,self.Ptr, intPtrstream,enumfileFormat,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str):
        """
        Loads presentation content from a file.

        Args:
            file: Path to the presentation file
        """
        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_LoadFromFile.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFile,self.Ptr,filePtr)

    @dispatch

    def LoadFromFile(self ,file:str,password:str):
        """
        Loads password-protected presentation content from a file.

        Args:
            file: Path to the presentation file
            password: Password to unlock the presentation
        """
        
        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromFileFP.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFP,self.Ptr,filePtr,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat):
        """
        Loads presentation content from a file with specific format.

        Args:
            file: Path to the presentation file
            fileFormat: Format of the presentation file
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_LoadFromFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFF,self.Ptr,filePtr,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat,password:str):
        """
        Loads password-protected presentation content from a file with specific format.

        Args:
            file: Path to the presentation file
            fileFormat: Format of the presentation file
            password: Password to unlock the presentation
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_LoadFromFileFFP.argtypes=[c_void_p ,c_char_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_LoadFromFileFFP,self.Ptr,filePtr,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,stream:Stream,fileFormat:FileFormat):
        """
        Saves the presentation to a stream.

        Args:
            stream: Output stream to write presentation data
            fileFormat: Format to save the presentation in
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt().Presentation_SaveToFile.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_SaveToFile,self.Ptr, intPtrstream,enumfileFormat)


    def SaveToSVG(self)->List[Stream]:
       """
        Saves the presentation as SVG images (one per slide).

        Returns:
            List[Stream]: Collection of streams containing SVG data for each slide
        """
       GetDllLibPpt().Presentation_SaveToSVG.argtypes=[c_void_p]
       GetDllLibPpt().Presentation_SaveToSVG.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().Presentation_SaveToSVG,self.Ptr)
       ret = GetObjVectorFromArray(intPtrArray,Stream)
       return ret




    def OnlineSaveToFile(self ,file:str,fileFormat:'FileFormat')->bool:
        """
        Saves the presentation for online/cloud use.

        Args:
            file: Output file path
            fileFormat: Format to save the presentation in

        Returns:
            bool: True if save succeeded, False otherwise
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_OnlineSaveToFile.argtypes=[c_void_p ,c_char_p,c_int]
        GetDllLibPpt().Presentation_OnlineSaveToFile.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_OnlineSaveToFile,self.Ptr,filePtr,enumfileFormat)
        return ret

    @dispatch

    def SaveToFile(self ,file:str,fileFormat:FileFormat):
        """
        Saves the presentation to a file.

        Args:
            file: Output file path
            fileFormat: Format to save the presentation in
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().Presentation_SaveToFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().Presentation_SaveToFileFF,self.Ptr,filePtr,enumfileFormat)

#    @dispatch
#
#    def SaveToHttpResponse(self ,FileName:str,fileFormat:FileFormat,response:'HttpResponse'):
#        """
#    <summary>
#        Save Presation to the http response.
#    </summary>
#    <param name="FileName">File Name</param>
#    <param name="response">Http response</param>
#    <param name="saveType">Save type : attachment or inline mode</param>
#        """
#        enumfileFormat:c_int = fileFormat.value
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibPpt().Presentation_SaveToHttpResponse.argtypes=[c_void_p ,c_wchar_p,c_int,c_void_p]
#        CallCFunction(GetDllLibPpt().Presentation_SaveToHttpResponse,self.Ptr, FileName,enumfileFormat,intPtrresponse)


#    @dispatch
#
#    def SaveToHttpResponse(self ,FileName:str,fileFormat:FileFormat,response:'HttpResponse',isInlineMode:bool):
#        """
#    <summary>
#        Save Presation to the http response.
#    </summary>
#    <param name="FileName">File name</param>
#    <param name="response">Http response.</param>
#    <param name="isInlineMode">True - inline mode, False - Attachment mode.</param>
#        """
#        enumfileFormat:c_int = fileFormat.value
#        intPtrresponse:c_void_p = response.Ptr
#
#        GetDllLibPpt().Presentation_SaveToHttpResponseFFRI.argtypes=[c_void_p ,c_wchar_p,c_int,c_void_p,c_bool]
#        CallCFunction(GetDllLibPpt().Presentation_SaveToHttpResponseFFRI,self.Ptr, FileName,enumfileFormat,intPtrresponse,isInlineMode)



    def Encrypt(self ,password:str):
        """
        Encrypts the presentation with a password.

        Args:
            password: Encryption password
        """
        
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_Encrypt.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_Encrypt,self.Ptr,passwordPtr)

    def RemoveEncryption(self):
        """
        Removes encryption from the presentation.
        """
        GetDllLibPpt().Presentation_RemoveEncryption.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveEncryption,self.Ptr)


    def Protect(self ,password:str):
        """
        Protects the presentation from modification.

        Args:
            password: Protection password
        """
        passwordPtr = StrToPtr(password)
        GetDllLibPpt().Presentation_Protect.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_Protect,self.Ptr,passwordPtr)

    def RemoveProtect(self):
        """
        Removes protection from the presentation.
        """
        GetDllLibPpt().Presentation_RemoveProtect.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_RemoveProtect,self.Ptr)

    #@dispatch

    #def Print(self ,presentationPrintDocument:PresentationPrintDocument):
    #    """

    #    """
    #    intPtrpresentationPrintDocument:c_void_p = presentationPrintDocument.Ptr

    #    GetDllLibPpt().Presentation_Print.argtypes=[c_void_p ,c_void_p]
    #    CallCFunction(GetDllLibPpt().Presentation_Print,self.Ptr, intPtrpresentationPrintDocument)

#    @dispatch
#
#    def Print(self ,printerSettings:'PrinterSettings'):
#        """
#    <summary>
#        Prints the presentation according to the specified printer settings.
#    </summary>
#    <param name="printerSettings">Printer settings to use.</param>
#        """
#        intPtrprinterSettings:c_void_p = printerSettings.Ptr
#
#        GetDllLibPpt().Presentation_PrintP.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibPpt().Presentation_PrintP,self.Ptr, intPtrprinterSettings)


#    @dispatch
#
#    def Print(self ,printerSettings:'PrinterSettings',presName:str):
#        """
#    <summary>
#        Prints the document according to the specified printer settings, using
#            the standard (no User Interface) print controller and a presentation name.
#    </summary>
#    <param name="printerSettings">The .NET printer settings to use.</param>
#    <param name="presName">The presentation name to display (for example, in a print
#            status dialog box or printer queue) while printing the presentation.</param>
#        """
#        intPtrprinterSettings:c_void_p = printerSettings.Ptr
#
#        GetDllLibPpt().Presentation_PrintPP.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().Presentation_PrintPP,self.Ptr, intPtrprinterSettings,presName)


    #@dispatch

    #def Print(self ,Name:str):
    #    """
    #<summary>
    #    Print the whole presentation to the specified printer.
    #</summary>
    #<param name="Name">The name of the printer.</param>
    #    """
        
    #    GetDllLibPpt().Presentation_PrintN.argtypes=[c_void_p ,c_wchar_p]
    #    CallCFunction(GetDllLibPpt().Presentation_PrintN,self.Ptr, Name)


    def SetFooterText(self ,text:str):
        """
        Sets the footer text for all slides.

        Args:
            text: Footer text to apply
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().Presentation_SetFooterText.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetFooterText,self.Ptr,textPtr)

    @dispatch

    def SetDateTime(self ,dateTime:DateTime):
        """
        Sets the date/time for all slides using default format.

        Args:
            dateTime: DateTime object containing the date/time value
        """
        intPtrdateTime:c_void_p = dateTime.Ptr

        GetDllLibPpt().Presentation_SetDateTime.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTime,self.Ptr, intPtrdateTime)

    @dispatch

    def SetDateTime(self ,dateTime:DateTime,format:str):
        """
        Sets the date/time for all slides with custom formatting.

        Args:
            dateTime: DateTime object containing the date/time value
            format: Custom format string for date/time display
        """
        intPtrdateTime:c_void_p = dateTime.Ptr

        formatPtr = StrToPtr(format)
        GetDllLibPpt().Presentation_SetDateTimeDF.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTimeDF,self.Ptr, intPtrdateTime,formatPtr)


    def SetFooterVisible(self ,visible:bool):
        """
        Shows or hides the footer on all slides.

        Args:
            visible: True to show footer, False to hide
        """
        
        GetDllLibPpt().Presentation_SetFooterVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetFooterVisible,self.Ptr, visible)


    def SetDateTimeVisible(self ,visible:bool):
        """
        Shows or hides the date/time on all slides.

        Args:
            visible: True to show date/time, False to hide
        """
        
        GetDllLibPpt().Presentation_SetDateTimeVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetDateTimeVisible,self.Ptr, visible)


    def SetSlideNoVisible(self ,visible:bool):
        """
        Shows or hides slide numbers on all slides.

        Args:
            visible: True to show slide numbers, False to hide
        """
        
        GetDllLibPpt().Presentation_SetSlideNoVisible.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPpt().Presentation_SetSlideNoVisible,self.Ptr, visible)

    @property
    def SlideNumberVisible(self)->bool:
        """
        Gets or sets whether slide numbers are visible.

        When True, slide numbers will be displayed on slides.
        """
        GetDllLibPpt().Presentation_get_SlideNumberVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideNumberVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideNumberVisible,self.Ptr)
        return ret

    @SlideNumberVisible.setter
    def SlideNumberVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_SlideNumberVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideNumberVisible,self.Ptr, value)

    @property
    def DateTimeVisible(self)->bool:
        """
        Gets or sets whether date/time is visible on slides.

        When True, date/time will be displayed on slides.
        """
        GetDllLibPpt().Presentation_get_DateTimeVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DateTimeVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_DateTimeVisible,self.Ptr)
        return ret

    @DateTimeVisible.setter
    def DateTimeVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_DateTimeVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_DateTimeVisible,self.Ptr, value)

    @property
    def FooterVisible(self)->bool:
        """
        Gets or sets whether footer is visible on slides.

        When True, footer will be displayed on slides.
        """
        GetDllLibPpt().Presentation_get_FooterVisible.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FooterVisible.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FooterVisible,self.Ptr)
        return ret

    @FooterVisible.setter
    def FooterVisible(self, value:bool):
        GetDllLibPpt().Presentation_set_FooterVisible.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_FooterVisible,self.Ptr, value)

    @property
    def AutoCompressPictures(self)->bool:
        """
        Gets or sets automatic picture compression.

        When True, images will be automatically compressed to reduce file size.
        """
        GetDllLibPpt().Presentation_get_AutoCompressPictures.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_AutoCompressPictures.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_AutoCompressPictures,self.Ptr)
        return ret

    @AutoCompressPictures.setter
    def AutoCompressPictures(self, value:bool):
        GetDllLibPpt().Presentation_set_AutoCompressPictures.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_AutoCompressPictures,self.Ptr, value)

    @property
    def BookmarkIdSeed(self)->int:
        """
        Gets or sets the starting ID for bookmarks.

        This value determines the starting point for bookmark ID generation.
        """
        GetDllLibPpt().Presentation_get_BookmarkIdSeed.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_BookmarkIdSeed.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_BookmarkIdSeed,self.Ptr)
        return ret

    @BookmarkIdSeed.setter
    def BookmarkIdSeed(self, value:int):
        GetDllLibPpt().Presentation_set_BookmarkIdSeed.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_BookmarkIdSeed,self.Ptr, value)

    @property

    def DefaultTextStyle(self)->'TextStyle':
        """
        Gets the default text style for the presentation.

        Returns:
            TextStyle: Default text formatting properties
        """
        GetDllLibPpt().Presentation_get_DefaultTextStyle.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_DefaultTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_DefaultTextStyle,self.Ptr)
        ret = None if intPtr==None else TextStyle(intPtr)
        return ret


    @property
    def ShowNarration(self)->bool:
        """
        Gets or sets whether narration is played during slide shows.

        When True, audio narration will play during presentations.
        """
        GetDllLibPpt().Presentation_get_ShowNarration.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowNarration.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowNarration,self.Ptr)
        return ret

    @ShowNarration.setter
    def ShowNarration(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowNarration.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowNarration,self.Ptr, value)

    @property
    def ShowAnimation(self)->bool:
        """
        Gets or sets whether animations are played during slide shows.

        When True, slide animations will play during presentations.
        """
        GetDllLibPpt().Presentation_get_ShowAnimation.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowAnimation.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowAnimation,self.Ptr)
        return ret

    @ShowAnimation.setter
    def ShowAnimation(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowAnimation.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowAnimation,self.Ptr, value)

    @property
    def ShowLoop(self)->bool:
        """
        Gets or sets whether slide shows loop continuously.

        When True, presentations will restart automatically after completion.
        """
        GetDllLibPpt().Presentation_get_ShowLoop.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowLoop.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowLoop,self.Ptr)
        return ret

    @ShowLoop.setter
    def ShowLoop(self, value:bool):
        GetDllLibPpt().Presentation_set_ShowLoop.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowLoop,self.Ptr, value)

    @property
    def HasMacros(self)->bool:
        """
        Indicates whether the presentation contains VBA macros.

        Returns:
            bool: True if macros are present, False otherwise
        """
        GetDllLibPpt().Presentation_get_HasMacros.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HasMacros.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_HasMacros,self.Ptr)
        return ret

    def DeleteMacros(self):
        """
        Deletes all VBA macros from the presentation.
        """
        GetDllLibPpt().Presentation_DeleteMacros.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().Presentation_DeleteMacros,self.Ptr)

    @property

    def ShowType(self)->'SlideShowType':
        """
        Gets or sets the slide show presentation type.

        Returns:
            SlideShowType: Enumeration value representing presentation mode
        """
        GetDllLibPpt().Presentation_get_ShowType.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ShowType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ShowType,self.Ptr)
        objwraped = SlideShowType(ret)
        return objwraped

    @ShowType.setter
    def ShowType(self, value:'SlideShowType'):
        GetDllLibPpt().Presentation_set_ShowType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_ShowType,self.Ptr, value.value)

    @property
    def UseTimings(self)->bool:
        """
        Gets or sets whether slide timings are used during presentations.

        When True, slide transitions will follow preset timing settings.
        """
        GetDllLibPpt().Presentation_get_UseTimings.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_UseTimings.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_UseTimings,self.Ptr)
        return ret

    @UseTimings.setter
    def UseTimings(self, value:bool):
        GetDllLibPpt().Presentation_set_UseTimings.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_UseTimings,self.Ptr, value)

    @property
    def EmbedTrueTypeFonts(self)->bool:
        """
        Gets or sets whether TrueType fonts are embedded in the document.

        When True, fonts will be embedded to ensure consistent rendering.
        """
        GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_EmbedTrueTypeFonts,self.Ptr)
        return ret

    @EmbedTrueTypeFonts.setter
    def EmbedTrueTypeFonts(self, value:bool):
        GetDllLibPpt().Presentation_set_EmbedTrueTypeFonts.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_EmbedTrueTypeFonts,self.Ptr, value)

    @property
    def FirstSlideNumber(self)->int:
        """
        Gets or sets the starting slide number.

        This value determines the number shown on the first slide.
        """
        GetDllLibPpt().Presentation_get_FirstSlideNumber.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_FirstSlideNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_FirstSlideNumber,self.Ptr)
        return ret

    @FirstSlideNumber.setter
    def FirstSlideNumber(self, value:int):
        GetDllLibPpt().Presentation_set_FirstSlideNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_FirstSlideNumber,self.Ptr, value)

    @property

    def HandoutMaster(self)->'INoteMasterSlide':
        """
        Gets the handout master slide.

        Returns:
            INoteMasterSlide: Master slide for handout layouts
        """
        GetDllLibPpt().Presentation_get_HandoutMaster.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_HandoutMaster.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_HandoutMaster,self.Ptr)
        ret = None if intPtr==None else INoteMasterSlide(intPtr)
        return ret


    @property

    def NotesMaster(self)->'INoteMasterSlide':
        """
        Gets the notes master slide.

        Returns:
            INoteMasterSlide: Master slide for speaker notes layouts
        """
        GetDllLibPpt().Presentation_get_NotesMaster.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_NotesMaster.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_NotesMaster,self.Ptr)
        ret = None if intPtr==None else INoteMasterSlide(intPtr)
        return ret


    @property

    def NotesSlideSize(self)->'SizeF':
        """
        Gets the size of notes slides.

        Returns:
            SizeF: Dimensions of notes slides
        """
        GetDllLibPpt().Presentation_get_NotesSlideSize.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_NotesSlideSize.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_NotesSlideSize,self.Ptr)
        ret = None if intPtr==None else SizeF(intPtr)
        return ret


    @property
    def SaveSubsetFonts(self)->bool:
        """
        Gets or sets whether to embed font subsets.

        When True, only used characters from fonts will be embedded.
        """
        GetDllLibPpt().Presentation_get_SaveSubsetFonts.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SaveSubsetFonts.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SaveSubsetFonts,self.Ptr)
        return ret

    @SaveSubsetFonts.setter
    def SaveSubsetFonts(self, value:bool):
        GetDllLibPpt().Presentation_set_SaveSubsetFonts.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SaveSubsetFonts,self.Ptr, value)

    @property
    def ServerZoom(self)->float:
        """
        Gets or sets the server-side zoom level.

        This property affects how the presentation is rendered on servers.
        """
        GetDllLibPpt().Presentation_get_ServerZoom.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_ServerZoom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Presentation_get_ServerZoom,self.Ptr)
        return ret

    @ServerZoom.setter
    def ServerZoom(self, value:float):
        GetDllLibPpt().Presentation_set_ServerZoom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Presentation_set_ServerZoom,self.Ptr, value)

    @property

    def Masters(self)->'MasterSlideCollection':
        """
        Gets the collection of master slides.

        Returns:
            MasterSlideCollection: Collection of master slide objects
        """
        GetDllLibPpt().Presentation_get_Masters.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Masters.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Masters,self.Ptr)
        ret = None if intPtr==None else MasterSlideCollection(intPtr)
        return ret


    @property

    def Slides(self)->'SlideCollection':
        """
        Gets the collection of slides.

        Returns:
            SlideCollection: Collection of slide objects
        """
        GetDllLibPpt().Presentation_get_Slides.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_Slides.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Presentation_get_Slides,self.Ptr)
        ret = None if intPtr==None else SlideCollection(intPtr)
        return ret
    
    @property

    def SlideCountPerPageForPrint(self)->'PageSlideCount':
        """
        Gets or sets the number of slides per printed page.

        Returns:
            PageSlideCount: Enumeration value representing slides per page
        """
        GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideCountPerPageForPrint,self.Ptr)
        objwraped = PageSlideCount(ret)
        return objwraped

    @SlideCountPerPageForPrint.setter
    def SlideCountPerPageForPrint(self, value:'PageSlideCount'):
        GetDllLibPpt().Presentation_set_SlideCountPerPageForPrint.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideCountPerPageForPrint,self.Ptr, value.value)

    def SelectSlidesForPrint(self ,selectSlidesForPrint:List[str]):
        """
        Selects specific slides for printing.

        Args:
            selectSlidesForPrint: List of slide identifiers to print
        """
        #arrayselectSlidesForPrint:ArrayTypeselectSlidesForPrint = ""
        countselectSlidesForPrint = len(selectSlidesForPrint)
        ArrayTypeselectSlidesForPrint = c_wchar_p * countselectSlidesForPrint
        arrayselectSlidesForPrint = ArrayTypeselectSlidesForPrint()
        for i in range(0, countselectSlidesForPrint):
            arrayselectSlidesForPrint[i] = selectSlidesForPrint[i]


        GetDllLibPpt().Presentation_SelectSlidesForPrint.argtypes=[c_void_p ,ArrayTypeselectSlidesForPrint]
        CallCFunction(GetDllLibPpt().Presentation_SelectSlidesForPrint,self.Ptr, arrayselectSlidesForPrint)
        

    @property

    def OrderForPrint(self)->'Order':
        """
        Gets or sets the printing order (horizontal/vertical).

        Returns:
            Order: Enumeration value representing print order
        """
        GetDllLibPpt().Presentation_get_OrderForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_OrderForPrint.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Presentation_get_OrderForPrint,self.Ptr)
        objwraped = Order(ret)
        return objwraped

    @OrderForPrint.setter
    def OrderForPrint(self, value:'Order'):
        GetDllLibPpt().Presentation_set_OrderForPrint.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Presentation_set_OrderForPrint,self.Ptr, value.value)
      
    @property
    def SlideFrameForPrint(self)->bool:
        """
        Gets or sets whether to print slide frames.

        When True, a border will be printed around each slide.
        """
        GetDllLibPpt().Presentation_get_SlideFrameForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_SlideFrameForPrint.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_SlideFrameForPrint,self.Ptr)
        return ret

    @SlideFrameForPrint.setter
    def SlideFrameForPrint(self, value:bool):
        GetDllLibPpt().Presentation_set_SlideFrameForPrint.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_SlideFrameForPrint,self.Ptr, value)
   
    @property
    def GrayLevelForPrint(self)->bool:
        """
        Gets or sets whether to print in grayscale.

        When True, printed output will be in grayscale.
        """
        GetDllLibPpt().Presentation_get_GrayLevelForPrint.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_GrayLevelForPrint.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_GrayLevelForPrint,self.Ptr)
        return ret

    @GrayLevelForPrint.setter
    def GrayLevelForPrint(self, value:bool):
        GetDllLibPpt().Presentation_set_GrayLevelForPrint.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_GrayLevelForPrint,self.Ptr, value)

    @property
    def IsNoteRetained(self)->bool:
        """
        Gets or sets whether speaker notes are retained.

        When True, speaker notes will be preserved during operations.
        """
        GetDllLibPpt().Presentation_get_IsNoteRetained.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_get_IsNoteRetained.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Presentation_get_IsNoteRetained,self.Ptr)
        return ret

    @IsNoteRetained.setter
    def IsNoteRetained(self, value:bool):
        GetDllLibPpt().Presentation_set_IsNoteRetained.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().Presentation_set_IsNoteRetained,self.Ptr, value)



    def AddEmbeddedFont(self,pathName:str)->str:
        """
        Embeds a font file into the presentation.

        Args:
            pathName: Path to the font file

        Returns:
            str: Identifier for the embedded font
        """
        pathNamePtr = StrToPtr(pathName)
        GetDllLibPpt().Presentation_AddEmbeddedFont.argtypes=[c_void_p,c_char_p]
        GetDllLibPpt().Presentation_AddEmbeddedFont.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Presentation_AddEmbeddedFont,self.Ptr,pathNamePtr))
        return ret
    
    
    @staticmethod
    def SetDefaultFontName(value:str):
        """
        Sets the default font name for new presentations.

        Args:
            value: Font name to use as default
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Presentation_set_DefaultFontName.argtypes=[c_char_p]
        GetDllLibPpt().Presentation_set_DefaultFontName.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_set_DefaultFontName,valuePtr)

    @staticmethod   
    def ResetDefaultFontName():
        """
        Resets the default font name to system default.
        """
        GetDllLibPpt().Presentation_Reset_DefaultFontName.argtypes=[c_void_p]
        GetDllLibPpt().Presentation_Reset_DefaultFontName.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_Reset_DefaultFontName)

    @staticmethod
    def SetCustomFontsDirctory(value:str):
        """
        Sets the directory for custom fonts.

        Args:
            value: Path to directory containing custom fonts
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Presentation_set_CustomFontsDirctory.argtypes=[c_char_p]
        GetDllLibPpt().Presentation_set_CustomFontsDirctory.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_set_CustomFontsDirctory,valuePtr)


    def ReplaceAndFormatText(self,value1:str,value2:str,format:DefaultTextRangeProperties):
        """
        Replaces text and applies formatting.

        Args:
            value1: Text to find
            value2: Replacement text
            format: Formatting to apply to the replacement text
        """
        value1Ptr = StrToPtr(value1)
        value2Ptr = StrToPtr(value2)
        GetDllLibPpt().Presentation_ReplaceAndFormatText.argtypes=[c_void_p,c_char_p,c_char_p,c_void_p]
        GetDllLibPpt().Presentation_ReplaceAndFormatText.restype=c_void_p
        CallCFunction(GetDllLibPpt().Presentation_ReplaceAndFormatText,self.Ptr,value1Ptr,value2Ptr,format.Ptr)

