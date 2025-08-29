from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationCommandBehavior (  CommonBehavior) :
    """
    Represents a command effect for an animation behavior.
    
    """
    @property

    def Type(self)->'AnimationCommandType':
        """
        Gets the type of command behavior.
        
        Returns:
            AnimationCommandType: The command type.
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Type,self.Ptr)
        objwraped = AnimationCommandType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'AnimationCommandType'):
        """
        Sets the type of command behavior.
        
        Args:
            value: The command type to set.
        """
        GetDllLibPpt().AnimationCommandBehavior_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationCommandBehavior_set_Type,self.Ptr, value.value)

    @property

    def Value(self)->str:
        """
        Gets the command value.
        
        Returns:
            str: The command value.
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Value.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Value.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Value,self.Ptr))
        return ret


    @Value.setter
    def Value(self, value:str):
        """
        Sets the command value.
        
        Args:
            value: The command value to set.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().AnimationCommandBehavior_set_Value.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().AnimationCommandBehavior_set_Value,self.Ptr,valuePtr)

    @property

    def Target(self)->'IShape':
        """
        Gets the target shape for the command.
        
        Returns:
            IShape: The target shape.
        """
        GetDllLibPpt().AnimationCommandBehavior_get_Target.argtypes=[c_void_p]
        GetDllLibPpt().AnimationCommandBehavior_get_Target.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationCommandBehavior_get_Target,self.Ptr)
        ret = None if intPtr==None else IShape(intPtr)
        return ret


