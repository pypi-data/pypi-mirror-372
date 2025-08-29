from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicAnimation (  PptObject) :
    """
    Represents animation properties for graphical elements.
    Inherits from PptObject to provide animation-specific functionality.
    """
    @property

    def ShapeRef(self)->'Shape':
        """
        Gets the target shape associated with the animation.
        Returns: Reference to the animated Shape object.
        """
        GetDllLibPpt().GraphicAnimation_get_ShapeRef.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimation_get_ShapeRef.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicAnimation_get_ShapeRef,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def BuildType(self)->'GraphicBuildType':
        """
        Gets or sets the animation build type.
        Returns: Current GraphicBuildType enum value.
        """
        GetDllLibPpt().GraphicAnimation_get_BuildType.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimation_get_BuildType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GraphicAnimation_get_BuildType,self.Ptr)
        objwraped = GraphicBuildType(ret)
        return objwraped

    @BuildType.setter
    def BuildType(self, value:'GraphicBuildType'):
        GetDllLibPpt().GraphicAnimation_set_BuildType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GraphicAnimation_set_BuildType,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this animation equals another object.
        Args:
            obj: Target object to compare.
        Returns: True if animations are identical, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GraphicAnimation_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GraphicAnimation_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicAnimation_Equals,self.Ptr, intPtrobj)
        return ret

