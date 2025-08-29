from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffectCollection ( SpireObject) :
    """
    Represents a collection of animation effects.
    
    This class manages a collection of animation effects for a slide.
    """

    @dispatch
    def __getitem__(self, index):
        """
        Gets the animation effect at the specified index.
        
        Args:
            index: The index of the effect.
            
        Returns:
            AnimationEffect: The animation effect at the index.
        """
        if index >= self.Count:
            raise StopIteration
        GetDllLibPpt().AnimationEffectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().AnimationEffectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret
   
    @property
    def Count(self)->int:
        """
        Gets the number of effects in the collection.
        
        Returns:
            int: The number of effects.
        """
        GetDllLibPpt().AnimationEffectCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Count,self.Ptr)
        return ret


    def Remove(self ,item:'AnimationEffect'):
        """
        Removes a specific effect from the collection.
        
        Args:
            item: The effect to remove.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().AnimationEffectCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
        Removes the effect at the specified index.
        
        Args:
            index: The index of the effect to remove.
        """
        
        GetDllLibPpt().AnimationEffectCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """Removes all effects from the collection."""
        GetDllLibPpt().AnimationEffectCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'AnimationEffect':
        """
        Gets the animation effect at the specified index.
        
        Args:
            index: The index of the effect.
            
        Returns:
            AnimationEffect: The animation effect at the index.
        """
        
        GetDllLibPpt().AnimationEffectCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().AnimationEffectCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator for the collection.
        
        Returns:
            IEnumerator: An enumerator for the collection.
        """
        GetDllLibPpt().AnimationEffectCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def TriggerShape(self)->'Shape':
        """
        Gets or sets the trigger shape for the animation.
        
        Returns:
            Shape: The trigger shape.
        """
        GetDllLibPpt().AnimationEffectCollection_get_TriggerShape.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffectCollection_get_TriggerShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_get_TriggerShape,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @TriggerShape.setter
    def TriggerShape(self, value:'Shape'):
        """
        Sets the trigger shape for the animation.
        
        Args:
            value: The trigger shape to set.
        """
        GetDllLibPpt().AnimationEffectCollection_set_TriggerShape.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffectCollection_set_TriggerShape,self.Ptr, value.Ptr)


    def AddEffect(self ,shape:'IShape',animationEffectType:'AnimationEffectType')->'AnimationEffect':
        """
        Adds a new effect to the end of the sequence.
        
        Args:
            shape: The shape to apply the effect to.
            animationEffectType: The type of animation effect.
            
        Returns:
            AnimationEffect: The newly created effect.
        """
        intPtrshape:c_void_p = shape.Ptr
        enumanimationEffectType:c_int = animationEffectType.value

        GetDllLibPpt().AnimationEffectCollection_AddEffect.argtypes=[c_void_p ,c_void_p,c_int]
        GetDllLibPpt().AnimationEffectCollection_AddEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffectCollection_AddEffect,self.Ptr, intPtrshape,enumanimationEffectType)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this object is equal to another.
        
        Args:
            obj: The object to compare with.
            
        Returns:
            bool: True if equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().AnimationEffectCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().AnimationEffectCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().AnimationEffectCollection_Equals,self.Ptr, intPtrobj)
        return ret

