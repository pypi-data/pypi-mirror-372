from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionCmdPath (SpireObject) :
    """
    Represents a single command segment within an animation motion path.
    """
    @property

    def Points(self)->List['PointF']:
        """
        Gets the collection of points defining the path segment.
        
        Returns:
            List[PointF]: Array of point coordinates
        """
        GetDllLibPpt().MotionCmdPath_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().MotionCmdPath_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret


#    @Points.setter
#    def Points(self, value:List['PointF']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibPpt().MotionCmdPath_set_Points.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibPpt().MotionCmdPath_set_Points,self.Ptr, vArray, vCount)


    @property

    def CommandType(self)->'MotionCommandPathType':
        """
        Gets or sets the command type for this path segment.
        
        Returns:
            MotionCommandPathType: Current command type
        """
        GetDllLibPpt().MotionCmdPath_get_CommandType.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_CommandType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_CommandType,self.Ptr)
        objwraped = MotionCommandPathType(ret)
        return objwraped

    @CommandType.setter
    def CommandType(self, value:'MotionCommandPathType'):
        """
        Sets the command type for this path segment.
        
        Args:
            value (MotionCommandPathType): New command type
        """
        GetDllLibPpt().MotionCmdPath_set_CommandType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_CommandType,self.Ptr, value.value)

    @property
    def IsRelative(self)->bool:
        """
        Determines if path coordinates are relative to starting position.
        
        Returns:
            bool: True if coordinates are relative
        """
        GetDllLibPpt().MotionCmdPath_get_IsRelative.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_IsRelative.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_IsRelative,self.Ptr)
        return ret

    @IsRelative.setter
    def IsRelative(self, value:bool):
        """
        Sets whether path coordinates are relative to starting position.
        
        Args:
            value (bool): True for relative coordinates
        """
        GetDllLibPpt().MotionCmdPath_set_IsRelative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_IsRelative,self.Ptr, value)

    @property

    def PointsType(self)->'MotionPathPointsType':
        """
        Gets or sets the interpretation method for path points.
        
        Returns:
            MotionPathPointsType: Current points interpretation
        """
        GetDllLibPpt().MotionCmdPath_get_PointsType.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_PointsType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_PointsType,self.Ptr)
        objwraped = MotionPathPointsType(ret)
        return objwraped

    @PointsType.setter
    def PointsType(self, value:'MotionPathPointsType'):
        """
        Sets the interpretation method for path points.
        
        Args:
            value (MotionPathPointsType): New points interpretation
        """
        GetDllLibPpt().MotionCmdPath_set_PointsType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_PointsType,self.Ptr, value.value)

