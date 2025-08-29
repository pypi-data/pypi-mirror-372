from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISmartArtNodeCollection (  SpireObject) :
    """
    Represents a collection of nodes within a SmartArt diagram.
    Provides methods to add, remove, and manage hierarchical nodes.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of nodes in the collection.

        Returns:
            int: Total count of nodes.
        """
        GetDllLibPpt().ISmartArtNodeCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, key):
        """
        Retrieves a node by index position.

        Args:
            key (int): Index of the node to retrieve.

        Returns:
            ISmartArtNode: The node at the specified index.

        Raises:
            StopIteration: If index is out of bounds.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Item,self.Ptr, key)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret

    def get_Item(self ,index:int)->'ISmartArtNode':
        """
        Retrieves a node by index position.

        Args:
            index (int): Index of the node to retrieve.

        Returns:
            ISmartArtNode: The node at the specified index.
        """
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret



    def AddNode(self)->'ISmartArtNode':
        """
        Adds a new node to the end of the collection.

        Returns:
            ISmartArtNode: The newly created node.
        """
        GetDllLibPpt().ISmartArtNodeCollection_AddNode.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_AddNode.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_AddNode,self.Ptr)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret


    def RemoveNodeByIndex(self ,index:int):
        """
        Removes a node by its index position.

        Args:
            index (int): Index of the node to remove.
        """

        GetDllLibPpt().ISmartArtNodeCollection_RemoveNode.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNode,self.Ptr, index)


    def RemoveNode(self ,node:'ISmartArtNode'):
        """
        Removes a specific node object from the collection.

        Args:
            node (ISmartArtNode): The node instance to remove.
        """
        intPtrnode:c_void_p = node.Ptr

        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeN.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeN,self.Ptr, intPtrnode)


    def GetNodeByPosition(self ,position:int)->'ISmartArtNode':
        """
        Retrieves a node by its display position index.

        Args:
            position (int): Display position index of the node.

        Returns:
            ISmartArtNode: The node at the specified position.
        """
        
        GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition,self.Ptr, position)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret



    def RemoveNodeByPosition(self ,position:int)->bool:
        """
        Removes a node by its display position index.

        Args:
            position (int): Display position index to remove.

        Returns:
            bool: True if removal succeeded, False otherwise.
        """
        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition,self.Ptr, position)
        return ret


    def AddNodeByPosition(self ,position:int)->'ISmartArtNode':
        """
        Inserts a new node at a specific display position.

        Args:
            position (int): Display position index to insert at.

        Returns:
            ISmartArtNode: The newly created node.
        """
        GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition,self.Ptr, position)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().ISmartArtNodeCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
        Indicates whether access to the collection is thread-safe.

        Returns:
            bool: True if synchronized, False otherwise.
        """
        GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
        Gets an object that can be used to synchronize access to the collection.

        Returns:
            SpireObject: The synchronization root object.
        """
        GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


