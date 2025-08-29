from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SequenceCollection (  IEnumerable) :
    """
    Manages interactive animation sequences for presentation objects.
    """
    @property
    def Count(self)->int:
        """
        Gets the total number of animation sequences.
        
        Returns:
            int: Count of animation sequences.
        """
        GetDllLibPpt().SequenceCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SequenceCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SequenceCollection_get_Count,self.Ptr)
        return ret


    def Add(self ,shape:'IShape')->'AnimationEffectCollection':
        """
        Creates a new animation sequence for a shape.
        
        Args:
            shape: Target shape to animate.
            
        Returns:
            AnimationEffectCollection: New animation sequence container.
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().SequenceCollection_Add.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SequenceCollection_Add.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_Add,self.Ptr, intPtrshape)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret



    def Remove(self ,item:'AnimationEffectCollection'):
        """
        Deletes a specific animation sequence.
        
        Args:
            item: Animation sequence to remove.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().SequenceCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().SequenceCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
        Deletes an animation sequence by position index.
        
        Args:
            index: Zero-based sequence index.
        """
        
        GetDllLibPpt().SequenceCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SequenceCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """
        Removes all animation sequences from the collection.
        """
        GetDllLibPpt().SequenceCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SequenceCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'AnimationEffectCollection':
        """
        Retrieves an animation sequence by index.
        
        Args:
            index: Zero-based sequence index.
            
        Returns:
            AnimationEffectCollection: Animation sequence object.
        """
        
        GetDllLibPpt().SequenceCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SequenceCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator to traverse the sequence collection.
        
        Returns:
            IEnumerator: Iterator object.
        """
        GetDllLibPpt().SequenceCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SequenceCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SequenceCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


