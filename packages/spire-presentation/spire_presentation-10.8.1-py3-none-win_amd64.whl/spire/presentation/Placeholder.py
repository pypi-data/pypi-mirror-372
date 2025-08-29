from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Placeholder (  PptObject) :
    """
    Represents a placeholder area on a slide that can hold specific types of content.
    """
    @property

    def Orientation(self)->'Direction':
        """
        Gets the text orientation within the placeholder.
        
        Read-only property that indicates the text flow direction.
        
        Returns:
            Direction: Enumeration value representing text orientation
        """
        GetDllLibPpt().Placeholder_get_Orientation.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Orientation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Orientation,self.Ptr)
        objwraped = Direction(ret)
        return objwraped

    @property

    def Size(self)->'PlaceholderSize':
        """
        Gets the relative size category of the placeholder.
        
        Read-only property indicating the size category (Full, Half, Quarter).
        
        Returns:
            PlaceholderSize: Enumeration value representing size category
        """
        GetDllLibPpt().Placeholder_get_Size.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Size.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Size,self.Ptr)
        objwraped = PlaceholderSize(ret)
        return objwraped

    @property

    def Type(self)->'PlaceholderType':
        """
        Gets the content type the placeholder is designed to hold.
        
        Read-only property indicating the placeholder's purpose (Title, Body, Chart, etc.).
        
        Returns:
            PlaceholderType: Enumeration value representing content type
        """
        GetDllLibPpt().Placeholder_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Type,self.Ptr)
        objwraped = PlaceholderType(ret)
        return objwraped

    @property

    def Index(self)->'UInt32':
        """
        Gets the position index of the placeholder within its parent slide.
        
        Read-only property that identifies the placeholder's order on the slide.
        
        Returns:
            UInt32: Numerical index of the placeholder
        """
        GetDllLibPpt().Placeholder_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Index.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Placeholder_get_Index,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if the specified object is equivalent to this placeholder.
        
        Compares the current placeholder with another object to check equality.
        
        Args:
            obj (SpireObject): The object to compare with the current placeholder
            
        Returns:
            bool: True if objects are equivalent, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Placeholder_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Placeholder_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Placeholder_Equals,self.Ptr, intPtrobj)
        return ret

