from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeNode (  Shape) :
    """
    Represents a node shape in a presentation.

    This class provides access to the styling, type, adjustment points, 
    and geometric properties of a node-based shape.
    """
    @property

    def ShapeStyle(self)->'ShapeStyle':
        """
        Gets the style object for the shape.

        Returns:
            ShapeStyle: The style object defining visual properties of the shape.
        """
        GetDllLibPpt().ShapeNode_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeNode_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """
        Gets or sets the geometric type of the shape.

        Returns:
            ShapeType: Enum value representing the shape's geometry type.
        """
        GetDllLibPpt().ShapeNode_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeNode_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().ShapeNode_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeNode_set_ShapeType,self.Ptr, value.value)

    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """
        Gets the collection of shape adjustment points.

        Returns:
            ShapeAdjustCollection: Collection of points that adjust the shape's geometry.
        """
        GetDllLibPpt().ShapeNode_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeNode_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines if this shape is equal to another object.

        Args:
            obj (SpireObject): The object to compare with.

        Returns:
            bool: True if objects are equal, False otherwise.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeNode_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeNode_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeNode_Equals,self.Ptr, intPtrobj)
        return ret
    
    @property
    def Points(self)->List['PointF']:
        """
        Gets the vertex points defining the shape's geometry.

        Returns:
            List[PointF]: Collection of points that make up the shape's outline.
        """
        GetDllLibPpt().ShapeNode_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ShapeNode_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret

