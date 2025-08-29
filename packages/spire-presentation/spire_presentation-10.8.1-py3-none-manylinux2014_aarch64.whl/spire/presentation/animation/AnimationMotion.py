from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationMotion (  CommonBehavior) :
    """
    Represents motion path animation behavior.

    """
    @property

    def From(self)->'PointF':
        """
        Gets or sets the starting point of the motion animation.
        
        Returns:
            PointF: The starting coordinates of the motion path.
        """
        GetDllLibPpt().AnimationMotion_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_From.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_From,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @From.setter
    def From(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_From.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_From,self.Ptr, value.Ptr)

    @property

    def To(self)->'PointF':
        """
        Gets or sets the ending point of the motion animation.
        
        Returns:
            PointF: The destination coordinates of the motion path.
        """
        GetDllLibPpt().AnimationMotion_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_To,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @To.setter
    def To(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_To,self.Ptr, value.Ptr)

    @property

    def By(self)->'PointF':
        """
        Gets or sets the relative movement offset for the animation.
        
        Returns:
            PointF: The displacement coordinates relative to the starting position.
        """
        GetDllLibPpt().AnimationMotion_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_By.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_By,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @By.setter
    def By(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_By.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_By,self.Ptr, value.Ptr)

    @property

    def RotationCenter(self)->'PointF':
        """
        Gets or sets the rotation center point for the animated object.
        
        Returns:
            PointF: The coordinates of the rotation pivot point.
        """
        GetDllLibPpt().AnimationMotion_get_RotationCenter.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_RotationCenter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_RotationCenter,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @RotationCenter.setter
    def RotationCenter(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_RotationCenter.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_RotationCenter,self.Ptr, value.Ptr)

    @property

    def Origin(self)->'AnimationMotionOrigin':
        """
        Gets or sets the origin point interpretation for the motion path.
        
        Returns:
            AnimationMotionOrigin: The coordinate space used for motion points.
        """
        GetDllLibPpt().AnimationMotion_get_Origin.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_Origin.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_Origin,self.Ptr)
        objwraped = AnimationMotionOrigin(ret)
        return objwraped

    @Origin.setter
    def Origin(self, value:'AnimationMotionOrigin'):
        GetDllLibPpt().AnimationMotion_set_Origin.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_Origin,self.Ptr, value.value)

    @property

    def Path(self)->'MotionPath':
        """
        Gets or sets the custom motion path for the animation.
        
        Returns:
            MotionPath: The collection of points defining the movement trajectory.
        """
        from spire.presentation.animation.MotionPath import MotionPath
        GetDllLibPpt().AnimationMotion_get_Path.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_Path.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_Path,self.Ptr)
        ret = None if intPtr==None else MotionPath(intPtr)
        return ret


    @Path.setter
    def Path(self, value:'MotionPath'):
        GetDllLibPpt().AnimationMotion_set_Path.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_Path,self.Ptr, value.Ptr)

    @property

    def PathEditMode(self)->'AnimationMotionPathEditMode':
        """
        Gets or sets the editing mode for the motion path.
        
        Returns:
            AnimationMotionPathEditMode: The current editing behavior for path points.
        """
        GetDllLibPpt().AnimationMotion_get_PathEditMode.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_PathEditMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_PathEditMode,self.Ptr)
        objwraped = AnimationMotionPathEditMode(ret)
        return objwraped

    @PathEditMode.setter
    def PathEditMode(self, value:'AnimationMotionPathEditMode'):
        GetDllLibPpt().AnimationMotion_set_PathEditMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_PathEditMode,self.Ptr, value.value)

    @property
    def RelativeAngle(self)->float:
        """
        Gets or sets the rotation angle relative to the motion path.
        
        Returns:
            float: The rotation angle in degrees relative to the movement direction.
        """
        GetDllLibPpt().AnimationMotion_get_RelativeAngle.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_RelativeAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_RelativeAngle,self.Ptr)
        return ret

    @RelativeAngle.setter
    def RelativeAngle(self, value:float):
        GetDllLibPpt().AnimationMotion_set_RelativeAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_RelativeAngle,self.Ptr, value)

    @property

    def PointsType(self)->str:
        """
        Gets the point type identifier for the motion path.
        
        Returns:
            str: A string representing the point type classification.
        """
        GetDllLibPpt().AnimationMotion_get_PointsType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_PointsType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationMotion_get_PointsType,self.Ptr))
        return ret


