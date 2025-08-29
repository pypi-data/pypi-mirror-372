from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideBackground (  IActiveSlide) :
    """
    Represents the background of a slide.
    
    Attributes:
        Type (BackgroundType): Gets or sets the type of background fill.
        EffectDag (EffectDag): Gets the Effect Dag object.
        Fill (FillFormat): Gets or sets the FillFormat for BackgroundType.OwnBackground fill.
        ThemeColor (ColorFormat): Gets or sets the ColorFormat for themed fill.
        ThemeIndex (UInt16): Gets or sets the index of the theme (0-999, 0 means no fill).
        Slide (ActiveSlide): Gets the parent slide of the shape (read-only).
        Presentation (Presentation): Gets the parent presentation of the slide (read-only).
    """
    @property

    def Type(self)->'BackgroundType':
        """
        Gets or sets the type of background fill.
        """
        GetDllLibPpt().SlideBackground_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideBackground_get_Type,self.Ptr)
        objwraped = BackgroundType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'BackgroundType'):
        GetDllLibPpt().SlideBackground_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlideBackground_set_Type,self.Ptr, value.value)

    @property

    def EffectDag(self)->'EffectDag':
        """
        Gets the Effect Dag.
        """
        GetDllLibPpt().SlideBackground_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Fill(self)->'FillFormat':
        """
        Gets or sets the FillFormat for BackgroundType.OwnBackground fill.
        """
        GetDllLibPpt().SlideBackground_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @Fill.setter
    def Fill(self, value:'FillFormat'):
        GetDllLibPpt().SlideBackground_set_Fill.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_Fill,self.Ptr, value.Ptr)

    @property

    def ThemeColor(self)->'ColorFormat':
        """
        Gets or sets the ColorFormat for themed fill.
        """
        GetDllLibPpt().SlideBackground_get_ThemeColor.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_ThemeColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_ThemeColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ThemeColor.setter
    def ThemeColor(self, value:'ColorFormat'):
        GetDllLibPpt().SlideBackground_set_ThemeColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_ThemeColor,self.Ptr, value.Ptr)

    @property

    def ThemeIndex(self)->'UInt16':
        """
        Gets or sets the index of the theme (0-999, 0 means no fill).
        """
        GetDllLibPpt().SlideBackground_get_ThemeIndex.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_ThemeIndex.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_ThemeIndex,self.Ptr)
        ret = None if intPtr==None else UInt16(intPtr)
        return ret


    @ThemeIndex.setter
    def ThemeIndex(self, value:'UInt16'):
        GetDllLibPpt().SlideBackground_set_ThemeIndex.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().SlideBackground_set_ThemeIndex,self.Ptr, value.Ptr)


    def GetBackgroundFillFormat(self ,slide:'ActiveSlide')->'FillFormat':
        """
        Gets the slide's background fill format.
        
        Args:
            slide (ActiveSlide): The slide with current background.
        
        Returns:
            FillFormat: The fill format of the background.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideBackground_GetBackgroundFillFormat.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideBackground_GetBackgroundFillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_GetBackgroundFillFormat,self.Ptr, intPtrslide)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideBackground_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideBackground_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideBackground_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
        Gets the parent slide of the shape (read-only).
        """
        GetDllLibPpt().SlideBackground_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets the parent presentation of the slide (read-only).
        """
        GetDllLibPpt().SlideBackground_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().SlideBackground_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideBackground_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


