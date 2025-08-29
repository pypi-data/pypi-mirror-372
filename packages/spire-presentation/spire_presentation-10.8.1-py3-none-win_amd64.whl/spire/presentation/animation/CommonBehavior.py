from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommonBehavior (  PptObject) :
    """
    Represents the base class for animation effect behaviors.
    
    Provides common properties for animation behaviors.
    """
    @property
    def Accumulate(self)->'TriState':
        """"
        Gets or sets whether animation behaviors accumulate.
        
        Returns:
            TriState: The accumulation setting
        """
        GetDllLibPpt().CommonBehavior_get_Accumulate.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Accumulate.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_get_Accumulate,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @Accumulate.setter
    def Accumulate(self, value:'TriState'):
        """
        Sets whether animation behaviors accumulate.
        
        Args:
            value: The new accumulation setting
        """
        GetDllLibPpt().CommonBehavior_set_Accumulate.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Accumulate,self.Ptr, value.value)

    @property

    def Additive(self)->'BehaviorAdditiveType':
        """
        Gets or sets how the behavior combines with other animations.
        
        Returns:
            BehaviorAdditiveType: The additive behavior type
        """
        GetDllLibPpt().CommonBehavior_get_Additive.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Additive.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_get_Additive,self.Ptr)
        objwraped = BehaviorAdditiveType(ret)
        return objwraped

    @Additive.setter
    def Additive(self, value:'BehaviorAdditiveType'):
        """
        Sets how the behavior combines with other animations.
        
        Args:
            value: The new additive behavior type
        """
        GetDllLibPpt().CommonBehavior_set_Additive.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Additive,self.Ptr, value.value)

    @property

    def Timing(self)->'Timing':
        """
        Gets or sets the timing properties for the effect behavior.
        
        Returns:
            Timing: The timing configuration object
        """
        GetDllLibPpt().CommonBehavior_get_Timing.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehavior_get_Timing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehavior_get_Timing,self.Ptr)
        ret = None if intPtr==None else Timing(intPtr)
        return ret


    @Timing.setter
    def Timing(self, value:'Timing'):
        """
        Sets the timing properties for the effect behavior.
        
        Args:
            value: The new timing configuration
        """
        GetDllLibPpt().CommonBehavior_set_Timing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehavior_set_Timing,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this object equals the specified object.
        
        Args:
            obj: The object to compare
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CommonBehavior_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehavior_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommonBehavior_Equals,self.Ptr, intPtrobj)
        return ret

