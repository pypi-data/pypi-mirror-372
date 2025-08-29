from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TagList (SpireObject) :
    """
    Represents the collection of tags
    
    """
    @property
    def Count(self)->int:
        """
        Gets the number of tags in the collection.

        Returns:
            int: The number of tags in the collection
        """
        GetDllLibPpt().TagList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TagList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_get_Count,self.Ptr)
        return ret


    def Append(self ,name:str,value:str)->int:
        """
        Adds a new tag to collection.

        Args:
            name: The name of the tag
            value: The value of the tag

        Returns:
            int: The index of the added tag
        """
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TagList_Append.argtypes=[c_void_p ,c_char_p,c_char_p]
        GetDllLibPpt().TagList_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_Append,self.Ptr,namePtr,valuePtr)
        return ret


    def Remove(self ,name:str):
        """
        Removes the tag with a specified name from the collection.

        Args:
            name: The name of tag to remove
        """
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_Remove.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().TagList_Remove,self.Ptr,namePtr)


    def IndexOfKey(self ,name:str)->int:
        """
        Gets the zero-based index of the specified key in the collection.

        Args:
            name: The name to locate in the collection

        Returns:
            int: The zero-based index if found, otherwise -1
        """
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_IndexOfKey.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_IndexOfKey.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TagList_IndexOfKey,self.Ptr,namePtr)
        return ret


    def Contains(self ,name:str)->bool:
        """
        Indicates whether the collection contains a specific name.

        Args:
            name: The key to locate

        Returns:
            bool: True if the key exists, False otherwise
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_Contains.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_Contains.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TagList_Contains,self.Ptr,namePtr)
        return ret


    def RemoveAt(self ,index:int):
        """
        Removes the tag at the specified index.

        Args:
            index: The zero-based index of the tag to remove
        """
        GetDllLibPpt().TagList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().TagList_RemoveAt,self.Ptr, index)

    def Clear(self):
        """Removes all tags from the collection."""
        GetDllLibPpt().TagList_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().TagList_Clear,self.Ptr)


    def GetByInd(self ,index:int)->str:
        """
        Gets value of a tag at the specified index.

        Args:
            index: Index of the tag to retrieve

        Returns:
            str: Value of the specified tag
        """
        GetDllLibPpt().TagList_GetByInd.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TagList_GetByInd.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_GetByInd,self.Ptr, index))
        return ret



    def GetKey(self ,index:int)->str:
        """
        Gets key of a tag at the specified index.

        Args:
            index: Index of the tag to retrieve

        Returns:
            str: Key of the specified tag
        """
        GetDllLibPpt().TagList_GetKey.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TagList_GetKey.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_GetKey,self.Ptr, index))
        return ret



    def get_Item(self ,name:str)->str:
        """
        Gets the value associated with the specified tag name.

        Args:
            name: Key of the tag

        Returns:
            str: Value associated with the tag
        """
        namePtr = StrToPtr(name)
        GetDllLibPpt().TagList_get_Item.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().TagList_get_Item.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TagList_get_Item,self.Ptr, name))
        return ret



    def set_Item(self ,name:str,value:str):
        """
        Sets the value associated with the specified tag name.

        Args:
            name: Key of the tag
            value: New value for the tag
        """
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TagList_set_Item.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().TagList_set_Item,self.Ptr,namePtr,valuePtr)

