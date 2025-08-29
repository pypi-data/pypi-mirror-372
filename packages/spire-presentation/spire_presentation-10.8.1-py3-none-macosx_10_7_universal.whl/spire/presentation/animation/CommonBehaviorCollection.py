from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class CommonBehaviorCollection (  SpireObject) :
    """
    Represents a collection of behavior effects for animations in a presentation.
    
    This class provides methods to manage and manipulate a collection of animation behaviors.
    """
    @dispatch
    def __getitem__(self, key):
        """
        Gets the behavior at the specified index.
        
        Args:
            key: The zero-based index of the behavior to retrieve.
        
        Returns:
            The behavior at the specified index.
        
        Raises:
            StopIteration: If the index is equal to or greater than Count.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().CommonBehaviorCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommonBehaviorCollection_get_Item.restype=IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Item,self.Ptr, key)
        ret = None if intPtrWithTypeName==None else self._create(intPtrWithTypeName)
        return ret

    @staticmethod
    def _create(intPtrWithTypeName:IntPtrWithTypeName)->'CommonBehavior':
        """
        Creates a specific CommonBehavior subclass instance based on type information.
        
        Args:
            intPtrWithTypeName: Pointer and type name information for behavior creation.
        
        Returns:
            A concrete CommonBehavior subclass instance (e.g., AnimationColorBehavior, 
            AnimationMotion, etc.) based on the provided type information.
        """
        from spire.presentation.animation.AnimationColorBehavior import AnimationColorBehavior
        from spire.presentation.animation.AnimationCommandBehavior import AnimationCommandBehavior
        from spire.presentation.animation.AnimationFilterEffect import AnimationFilterEffect
        from spire.presentation.animation.AnimationMotion import AnimationMotion
        from spire.presentation.animation.AnimationProperty import AnimationProperty
        from spire.presentation.animation.AnimationRotation import AnimationRotation
        from spire.presentation.animation.AnimationScale import AnimationScale
        from spire.presentation.animation.AnimationSet import AnimationSet
        from spire.presentation.animation.CommonBehavior import CommonBehavior

        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'Spire.Presentation.Drawing.Animation.AnimationColorBehavior'):
            ret = AnimationColorBehavior(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationCommandBehavior'):
            ret = AnimationCommandBehavior(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationFilterEffect'):
            ret = AnimationFilterEffect(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationMotion'):
            ret = AnimationMotion(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationProperty'):
            ret = AnimationProperty(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationRotation'):
            ret = AnimationRotation(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationScale'):
            ret = AnimationScale(intPtr)
        elif (strName == 'Spire.Presentation.Drawing.Animation.AnimationSet'):
            ret = AnimationSet(intPtr)
        else:
            ret = CommonBehavior(intPtr)

        return ret

    @property
    def Count(self)->int:
        """
        Gets the number of behaviors in the collection.
        
        Returns:
            The total number of behaviors in the collection.
        """
        GetDllLibPpt().CommonBehaviorCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Count,self.Ptr)
        return ret


    def Append(self ,item:'CommonBehavior')->int:
        """
        Adds a new behavior to the end of the collection.
        
        Args:
            item: The behavior to add to the collection.
        
        Returns:
            The index at which the behavior has been added.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_Append.restype=c_int
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Append,self.Ptr, intPtritem)
        return ret


    def Insert(self ,index:int,item:'CommonBehavior'):
        """
        Inserts a behavior into the collection at the specified index.
        
        Args:
            index: The zero-based index at which to insert the behavior.
            item: The behavior to insert.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Insert,self.Ptr, index,intPtritem)


    def Remove(self ,item:'CommonBehavior'):
        """
        Removes the specified behavior from the collection.
        
        Args:
            item: The behavior to remove.
        """
        intPtritem:c_void_p = item.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Remove,self.Ptr, intPtritem)


    def RemoveAt(self ,index:int):
        """
        Removes the behavior at the specified index.
        
        Args:
            index: The zero-based index of the behavior to remove.
        """
        
        GetDllLibPpt().CommonBehaviorCollection_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_RemoveAt,self.Ptr, index)

    def Clear(self):
        """Removes all behaviors from the collection."""
        GetDllLibPpt().CommonBehaviorCollection_Clear.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Clear,self.Ptr)


    def get_Item(self ,index:int)->'CommonBehavior':
        """
        Retrieves the behavior at the specified index.
        
        Args:
            index: The zero-based index of the behavior to retrieve.
        
        Returns:
            The behavior at the specified index.
        """
        
        GetDllLibPpt().CommonBehaviorCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().CommonBehaviorCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else CommonBehavior(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current object is equal to another object.
        
        Args:
            obj: The object to compare with.
        
        Returns:
            True if the objects are equal; otherwise, False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().CommonBehaviorCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_Equals,self.Ptr, intPtrobj)
        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator for the entire collection.
        
        Returns:
            An enumerator that iterates through the collection.
        """
        GetDllLibPpt().CommonBehaviorCollection_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().CommonBehaviorCollection_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().CommonBehaviorCollection_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


