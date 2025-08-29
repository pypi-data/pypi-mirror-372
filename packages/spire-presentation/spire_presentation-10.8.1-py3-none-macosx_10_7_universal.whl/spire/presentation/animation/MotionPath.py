from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionPath ( SpireObject ) :
    """
    Represents a complete animation motion path composed of command segments.
    
    """

    @dispatch
    def __init__(self):
        """
        Initializes a new empty MotionPath instance.
        """
        GetDllLibPpt().MotionPath_CreateMotionPath.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_CreateMotionPath)
        super(MotionPath, self).__init__(intPtr)
    """

    """
    @dispatch
    def __getitem__(self, key):
        """
        Gets the path command segment at the specified index.
        
        Args:
            key (int): Segment index
            
        Returns:
            MotionCmdPath: Path command segment
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().MotionPath_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MotionPath_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_get_Item,self.Ptr, key)
        ret = None if intPtr==None else MotionCmdPath(intPtr)
        return ret

    def Add(self ,pathType:'MotionCommandPathType',pts:'PointF[]',ptsType:'MotionPathPointsType',bRelativeCoord:bool)->int:
        """
        Adds a new command segment to the motion path.
        
        Args:
            pathType (MotionCommandPathType): Type of path command
            pts (List[PointF]): Control points for the segment
            ptsType (MotionPathPointsType): Interpretation method for points
            bRelativeCoord (bool): Whether coordinates are relative
            
        Returns:
            int: Index of the newly added command segment
        """
        enumtype:c_int = pathType.value
        #arraypts:ArrayTypepts = ""
        countpts = len(pts)
        ArrayTypepts = c_void_p * countpts
        arraypts = ArrayTypepts()
        for i in range(0, countpts):
            arraypts[i] = pts[i].Ptr

        enumptsType:c_int = ptsType.value

        GetDllLibPpt().MotionPath_Add.argtypes=[c_void_p ,c_int,ArrayTypepts,c_int,c_int,c_bool]
        GetDllLibPpt().MotionPath_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionPath_Add,self.Ptr, enumtype,arraypts,countpts,enumptsType,bRelativeCoord)
        return ret


    @property
    def Count(self)->int:
        """
        Gets the number of command segments in the motion path.
        
        Returns:
            int: Total segment count
        """
        GetDllLibPpt().MotionPath_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().MotionPath_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionPath_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'MotionCmdPath':
        """
        Retrieves a specific path command segment by index.
        
        Args:
            index (int): Zero-based segment index
            
        Returns:
            MotionCmdPath: Path command segment object
        """
        
        GetDllLibPpt().MotionPath_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MotionPath_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_get_Item,self.Ptr, index)
        ret = None if intPtr==None else MotionCmdPath(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an iterator for traversing all command segments.
        
        Returns:
            IEnumerator: Enumerator object for path segments
        """
        GetDllLibPpt().MotionPath_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().MotionPath_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


