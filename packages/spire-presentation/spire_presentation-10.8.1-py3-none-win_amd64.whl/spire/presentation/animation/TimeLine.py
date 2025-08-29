from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeLine (  PptObject) :
    """
    Represents the timeline of animations in a presentation slide.
    """
    @property

    def InteractiveSequences(self)->'SequenceCollection':
        """
        Gets the collection of interactive animation sequences.
        
        Returns:
            SequenceCollection: A collection of interactive animation sequences
        """
        GetDllLibPpt().TimeLine_get_InteractiveSequences.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_InteractiveSequences.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_InteractiveSequences,self.Ptr)
        ret = None if intPtr==None else SequenceCollection(intPtr)
        return ret


    @property

    def MainSequence(self)->'AnimationEffectCollection':
        """
        Gets the main animation sequence of the timeline.
        
        Returns:
            AnimationEffectCollection: The collection of main animation effects
        """
        GetDllLibPpt().TimeLine_get_MainSequence.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_MainSequence.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_MainSequence,self.Ptr)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret


    @property

    def TextAnimations(self)->'TextAnimationCollection':
        """
        Gets the collection of text-specific animations.
        
        Returns:
            TextAnimationCollection: A collection of text-specific animations
        """
        GetDllLibPpt().TimeLine_get_TextAnimations.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_TextAnimations.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_TextAnimations,self.Ptr)
        ret = None if intPtr==None else TextAnimationCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current timeline.
        
        Args:
            obj (SpireObject): The object to compare with the current timeline
            
        Returns:
            bool: True if the specified object is equal to the current timeline; otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeLine_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeLine_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeLine_Equals,self.Ptr, intPtrobj)
        return ret

