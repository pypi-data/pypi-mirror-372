from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnimationCollection (  SpireObject ) :
    """
    Represent collection of text animations.
    
    Provides methods to access and manage text animation elements.
    """
    @dispatch
    def __getitem__(self, index):
        """
        Gets the element at the specified index.
        
        Args:
            index: Zero-based index of the element to retrieve
            
        Returns:
            TextAnimation: The animation element at the specified position
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().TextAnimationCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextAnimationCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret

    @property
    def Count(self)->int:
        """
        Gets the number of elements in the collection.
        
        Returns:
            int: Total count of animation elements
        """
        GetDllLibPpt().TextAnimationCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Count,self.Ptr)
        return ret

    @dispatch

    def get_Item(self ,index:int)->TextAnimation:
        """
        Gets element by index.
        
        Args:
            index: Zero-based index of the element to retrieve
            
        Returns:
            TextAnimation: The animation element at the specified position
        """
        
        GetDllLibPpt().TextAnimationCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextAnimationCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret


#    @dispatch
#
#    def get_Item(self ,shape:IShape)->List[TextAnimation]:
#        """
#    <summary>
#        Gets all elements 
#    </summary>
#    <param name="shape"></param>
#    <returns></returns>
#        """
#        intPtrshape:c_void_p = shape.Ptr
#
#        GetDllLibPpt().TextAnimationCollection_get_ItemS.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().TextAnimationCollection_get_ItemS.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_ItemS,self.Ptr, intPtrshape)
#        ret = GetObjVectorFromArray(intPtrArray, TextAnimation)
#        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if objects are equal.
        
        Args:
            obj: Object to compare with
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextAnimationCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextAnimationCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator for the collection.
        
        Returns:
            IEnumerator: Iterator object for collection traversal
        """
        GetDllLibPpt().TextAnimationCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection into the specified array.
#    </summary>
#    <param name="array">Array to fill.</param>
#    <param name="index">Starting position in target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().TextAnimationCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().TextAnimationCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether collection access is thread-safe.
        
        Returns:
            bool: True if access is synchronized, False otherwise
        """
        GetDllLibPpt().TextAnimationCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets the synchronization root object.
        
        Returns:
            SpireObject: Object used for synchronization
        """
        GetDllLibPpt().TextAnimationCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimationCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimationCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


