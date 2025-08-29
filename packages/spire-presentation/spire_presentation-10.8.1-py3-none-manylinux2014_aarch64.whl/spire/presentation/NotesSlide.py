from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class NotesSlide (  ActiveSlide) :
    """
    Represents a notes slide in a presentation.
    
    Inherits from ActiveSlide and provides access to notes-specific content.
    """
    @property

    def NotesTextFrame(self)->'ITextFrameProperties':
        """
        Gets the text frame containing notes text.
        
        Returns:
            ITextFrameProperties: Read-only text frame with notes content. 
            Returns None if no text frame exists.
        """
        GetDllLibPpt().NotesSlide_get_NotesTextFrame.argtypes=[c_void_p]
        GetDllLibPpt().NotesSlide_get_NotesTextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().NotesSlide_get_NotesTextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property

    def Theme(self)->'Theme':
        """
        Gets the theme object inherited from the master slide.
        
        Returns:
            Theme: Theme object associated with the notes slide.
        """
        GetDllLibPpt().NotesSlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().NotesSlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().NotesSlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
        Applies an extra color scheme to the notes slide.
        
        Args:
            scheme: Color scheme to apply to the slide.
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().NotesSlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().NotesSlide_ApplyTheme,self.Ptr, intPtrscheme)

    #@dispatch

    #def GetThumbnail(self ,scaleX:float,scaleY:float)->Bitmap:
    #    """
    #<summary>
    #    Gets a Thumbnail Bitmap object with custom scaling.
    #</summary>
    #<param name="scaleX">The value by which to scale this Thumbnail in the x-axis direction.</param>
    #<param name="scaleY">The value by which to scale this Thumbnail in the y-axis direction.</param>
    #<returns>Bitmap object.</returns>
    #    """
        
    #    GetDllLibPpt().NotesSlide_GetThumbnail.argtypes=[c_void_p ,c_float,c_float]
    #    GetDllLibPpt().NotesSlide_GetThumbnail.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().NotesSlide_GetThumbnail,self.Ptr, scaleX,scaleY)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


    #@dispatch

    #def GetThumbnail(self ,imageSize:Size)->Bitmap:
    #    """
    #<summary>
    #    Gets a Thumbnail Bitmap object with specified size.
    #</summary>
    #<param name="imageSize">Size of the image to create.</param>
    #<returns>Bitmap object.</returns>
    #    """
    #    intPtrimageSize:c_void_p = imageSize.Ptr

    #    GetDllLibPpt().NotesSlide_GetThumbnailI.argtypes=[c_void_p ,c_void_p]
    #    GetDllLibPpt().NotesSlide_GetThumbnailI.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().NotesSlide_GetThumbnailI,self.Ptr, intPtrimageSize)
    #    ret = None if intPtr==None else Bitmap(intPtr)
    #    return ret


