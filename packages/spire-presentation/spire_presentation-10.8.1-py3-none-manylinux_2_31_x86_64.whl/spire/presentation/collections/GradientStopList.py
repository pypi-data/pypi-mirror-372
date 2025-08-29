from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopList ( IActiveSlide) :
    """
    Represnts a collection of gradient stops.
    
    """

    @dispatch
    def __getitem__(self, index):
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().GradientStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStop(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
        Gets the number of gradient stops in a collection.
          
        """
        GetDllLibPpt().GradientStopList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'GradientStop':
        """
        Gets the gradient stop by index.
    
        """
        
        GetDllLibPpt().GradientStopList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GradientStopList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GradientStop(intPtr)
        return ret


    def AppendByColor(self ,position:float,color:Color)->int:
        """
        Creates a new gradient stop with the specified color.
        Args:
            position: Stop position (0.0 to 1.0)
            color: Stop color
        Returns:
            Index of the new gradient stop
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPpt().GradientStopList_Append.argtypes=[c_void_p ,c_float,c_void_p]
        GetDllLibPpt().GradientStopList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_Append,self.Ptr, position,intPtrcolor)
        return ret

    def AppendByKnownColors(self ,position:float,knownColor:KnownColors)->int:
        """
        Creates a new gradient stop with a predefined color.
        Args:
            position: Stop position (0.0 to 1.0)
            knownColor: Predefined color value
        Returns:
            Index of the new gradient stop
        """
        enumknownColor:c_int = knownColor.value

        GetDllLibPpt().GradientStopList_AppendPK.argtypes=[c_void_p ,c_float,c_int]
        GetDllLibPpt().GradientStopList_AppendPK.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_AppendPK,self.Ptr, position,enumknownColor)
        return ret


    def AppendBySchemeColor(self ,position:float,schemeColor:SchemeColor)->int:
        """
        Creates a new gradient stop with a scheme color.
        Args:
            position: Stop position (0.0 to 1.0)
            schemeColor: Color scheme value
        Returns:
            Index of the new gradient stop
        """
        enumschemeColor:c_int = schemeColor.value

        GetDllLibPpt().GradientStopList_AppendPS.argtypes=[c_void_p ,c_float,c_int]
        GetDllLibPpt().GradientStopList_AppendPS.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientStopList_AppendPS,self.Ptr, position,enumschemeColor)
        return ret

  
    def InsertByColor(self ,index:int,position:float,color:Color):
        """
        Inserts a new gradient stop at the specified index.
        Args:
            index: Insertion position
            position: Stop position (0.0 to 1.0)
            color: Stop color
        """
        intPtrcolor:c_void_p = color.Ptr

        GetDllLibPpt().GradientStopList_Insert.argtypes=[c_void_p ,c_int,c_float,c_void_p]
        CallCFunction(GetDllLibPpt().GradientStopList_Insert,self.Ptr, index,position,intPtrcolor)

   
    def InsertByKnownColors(self ,index:int,position:float,knownColor:KnownColors):
        """
        Creates a new gradient stop with a predefined color.
        Args:
            index: Insertion position
            position: Stop position (0.0 to 1.0)
            knownColor: Predefined color value.
        """
        enumknownColor:c_int = knownColor.value

        GetDllLibPpt().GradientStopList_InsertIPK.argtypes=[c_void_p ,c_int,c_float,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_InsertIPK,self.Ptr, index,position,enumknownColor)

    
    def InsertBySchemeColor(self ,index:int,position:float,schemeColor:SchemeColor):
        """
        Creates a new gradient stop with a scheme color.
        Args:
            index: Insertion position
            position: Stop position (0.0 to 1.0)
            schemeColor: Color scheme value.
        """
        enumschemeColor:c_int = schemeColor.value

        GetDllLibPpt().GradientStopList_InsertIPS.argtypes=[c_void_p ,c_int,c_float,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_InsertIPS,self.Ptr, index,position,enumschemeColor)


    def RemoveAt(self ,index:int):
        """
        Removes the gradient stop at the specified index.
        """
        
        GetDllLibPpt().GradientStopList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().GradientStopList_RemoveAt,self.Ptr, index)

    def RemoveAll(self):
        """
        Removes all gradient stops from a collection.
   
        """
        GetDllLibPpt().GradientStopList_RemoveAll.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().GradientStopList_RemoveAll,self.Ptr)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the entire collection.
        Returns:
            IEnumerator for the entire collection.
        """
        GetDllLibPpt().GradientStopList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


