from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnimation (  PptObject) :
    """
    Represents text animation effects in a presentation.
    """
    @property

    def ShapeRef(self)->'Shape':
        """
        Gets the shape associated with the text animation.
        
        Returns:
            Shape: The associated shape object.
        """
        GetDllLibPpt().TextAnimation_get_ShapeRef.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_ShapeRef.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimation_get_ShapeRef,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def ParagraphBuildType(self)->'ParagraphBuildType':
        """
        Gets or sets the paragraph build type for text animation.
        """
        GetDllLibPpt().TextAnimation_get_ParagraphBuildType.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_ParagraphBuildType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextAnimation_get_ParagraphBuildType,self.Ptr)
        objwraped = ParagraphBuildType(ret)
        return objwraped

    @ParagraphBuildType.setter
    def ParagraphBuildType(self, value:'ParagraphBuildType'):
        GetDllLibPpt().TextAnimation_set_ParagraphBuildType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextAnimation_set_ParagraphBuildType,self.Ptr, value.value)

    @property

    def Background(self)->'AnimationEffect':
        """
        Gets or sets the shape background animation effect.
        """
        GetDllLibPpt().TextAnimation_get_Background.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_Background.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimation_get_Background,self.Ptr)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret


    @Background.setter
    def Background(self, value:'AnimationEffect'):
        GetDllLibPpt().TextAnimation_set_Background.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextAnimation_set_Background,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the current object is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextAnimation_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextAnimation_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimation_Equals,self.Ptr, intPtrobj)
        return ret

