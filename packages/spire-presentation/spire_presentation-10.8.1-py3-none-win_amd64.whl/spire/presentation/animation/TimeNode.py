from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNode (SpireObject) :
    """
     Represents a node in the animation timeline hierarchy.
    """
    @property

    def ChildNodes(self)->'TimeNodes':
        """
        Gets the direct child nodes of this time node.
        
        Returns:
            TimeNodes: A collection of direct child time nodes
        """
        GetDllLibPpt().TimeNode_get_ChildNodes.argtypes=[c_void_p]
        GetDllLibPpt().TimeNode_get_ChildNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNode_get_ChildNodes,self.Ptr)
        ret = None if intPtr==None else TimeNodes(intPtr)
        return ret


    @property

    def SubNodes(self)->'TimeNodes':
        """
        Gets the subordinated nodes associated with this time node.
        
        Returns:
            TimeNodes: A collection of subordinate time nodes
        """
        GetDllLibPpt().TimeNode_get_SubNodes.argtypes=[c_void_p]
        GetDllLibPpt().TimeNode_get_SubNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeNode_get_SubNodes,self.Ptr)
        ret = None if intPtr==None else TimeNodes(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current time node.
        
        Args:
            obj (SpireObject): The object to compare with the current time node
            
        Returns:
            bool: True if the specified object is equal to the current time node; otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNode_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNode_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNode_Equals,self.Ptr, intPtrobj)
        return ret

