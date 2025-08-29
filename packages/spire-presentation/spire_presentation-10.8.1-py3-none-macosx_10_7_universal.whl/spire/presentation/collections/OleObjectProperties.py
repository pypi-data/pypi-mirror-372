from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class OleObjectProperties (  ICollection, IEnumerable) :
    """
    Represents a collection of properties associated with an OLE object.
    This collection stores key-value pairs that define various attributes of an OLE object.
    
    """

    def Add(self ,name:str,value:str):
        """
        Adds a new property to the collection with the specified name and value.
        
        Args:
            name (str): The name of the property to add.
            value (str): The value of the property to add.
        """
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().OleObjectProperties_Add.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Add,self.Ptr,namePtr,valuePtr)


    def Remove(self ,name:str):
        """
        Removes the property with the specified name from the collection.
        
        Args:
            name (str): The name of the property to remove.
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().OleObjectProperties_Remove.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Remove,self.Ptr,namePtr)



    def get_Item(self ,name:str)->str:
        """
        Gets the value of the property with the specified name.
        
        Args:
            name (str): The name of the property to retrieve.
        
        Returns:
            str: The value associated with the specified property name.
        """
        
        namePtr = StrToPtr(name)
        GetDllLibPpt().OleObjectProperties_get_Item.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().OleObjectProperties_get_Item.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().OleObjectProperties_get_Item,self.Ptr, namePtr))
        return ret

    def Keys(self)->List[str]:
        """
        Gets all property names in the collection.
        
        Returns:
            List[str]: A list of all property names in the collection.
        """
        GetDllLibPpt().OleObjectProperties_get_Keys.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_Keys.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().OleObjectProperties_get_Keys,self.Ptr)
        ret = GetStringPtrArray(intPtrArray)
        return ret



    def set_Item(self ,name:str,value:str):
        """
        Sets the value of the property with the specified name.
        
        Args:
            name (str): The name of the property to set.
            value (str): The value to assign to the specified property.
        """
        
        namePtr = StrToPtr(name)
        valuePtr = StrToPtr(value)
        GetDllLibPpt().OleObjectProperties_set_Item.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_set_Item,self.Ptr,namePtr,valuePtr)

    def Clear(self):
        """
        Removes all properties from the collection.
        """
        GetDllLibPpt().OleObjectProperties_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().OleObjectProperties_Clear,self.Ptr)


    @property
    def Count(self)->int:
        """
        Gets the number of properties contained in the collection.
        
        Returns:
            int: The total number of properties in the collection.
        """
        GetDllLibPpt().OleObjectProperties_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().OleObjectProperties_get_Count,self.Ptr)
        return ret

    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is synchronized (thread-safe).
        
        Returns:
            bool: True if access is thread-safe; otherwise, False.
        """
        GetDllLibPpt().OleObjectProperties_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().OleObjectProperties_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.
        
        Returns:
            SpireObject: An object that can be used to synchronize access to the collection.
        """
        GetDllLibPpt().OleObjectProperties_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectProperties_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Returns an enumerator that iterates through the collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection.
        """
        GetDllLibPpt().OleObjectProperties_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().OleObjectProperties_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().OleObjectProperties_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


