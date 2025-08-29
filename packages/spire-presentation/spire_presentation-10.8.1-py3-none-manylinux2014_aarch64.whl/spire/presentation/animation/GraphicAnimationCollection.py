from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicAnimationCollection (  ICollection, IEnumerable) :
    """
    Represent collection of graphic animations.

    """
    @property
    def Count(self)->int:
        """
        Gets a number of elements in the collection.
        """
        GetDllLibPpt().GraphicAnimationCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimationCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_get_Count,self.Ptr)
        return ret

    @dispatch

    def get_Item(self ,index:int)->GraphicAnimation:
        """
        Gets element by index.
        
        Args:
            index (int): The index of the element.
            
        Returns:
            GraphicAnimation: The animation at the specified index.
        """
        
        GetDllLibPpt().GraphicAnimationCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().GraphicAnimationCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else GraphicAnimation(intPtr)
        return ret


#    @dispatch
#
#    def get_Item(self ,shape:IShape)->List[GraphicAnimation]:
#        """
#    <summary>
#        Gets all elements 
#    </summary>
#    <param name="shape"></param>
#    <returns></returns>
#        """
#        intPtrshape:c_void_p = shape.Ptr
#
#        GetDllLibPpt().GraphicAnimationCollection_get_ItemS.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().GraphicAnimationCollection_get_ItemS.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_get_ItemS,self.Ptr, intPtrshape)
#        ret = GetObjVectorFromArray(intPtrArray, GraphicAnimation)
#        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current collection is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GraphicAnimationCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GraphicAnimationCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator for the collection.
        
        Returns:
            IEnumerator: An iterator object.
        """
        GetDllLibPpt().GraphicAnimationCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimationCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_GetEnumerator,self.Ptr)
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
#        GetDllLibPpt().GraphicAnimationCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().GraphicAnimationCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
        """
        GetDllLibPpt().GraphicAnimationCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimationCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets a synchronization root.
        Readonly.
        """
        GetDllLibPpt().GraphicAnimationCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimationCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicAnimationCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


