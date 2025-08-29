from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideColorSchemeCollection (  ICollection, IEnumerable) :
    """
    Represents a collection of additional color schemes.
    
    """
    @property
    def Count(self)->int:
        """
        Gets the number of elements in the collection.

        Returns:
            int: The count of elements.
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'SlideColorScheme':
        """
        Gets a color scheme by index.

        Args:
            index (int): The zero-based index of the scheme.

        Returns:
            SlideColorScheme: The color scheme at the specified index.
        """
        
        GetDllLibPpt().SlideColorSchemeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideColorSchemeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else SlideColorScheme(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Checks equality with another object.

        Args:
            obj (SpireObject): The object to compare.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideColorSchemeCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator to iterate through the collection.

        Returns:
            IEnumerator: An enumerator for the collection.
        """
        GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements of the collection to the specified array.
#    </summary>
#    <param name="array">Target array.</param>
#    <param name="index">Starting index in the array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().SlideColorSchemeCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.

        Returns:
            bool: True if thread-safe, False otherwise.
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object to synchronize access to the collection.

        Returns:
            SpireObject: The synchronization root object.
        """
        GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorSchemeCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


