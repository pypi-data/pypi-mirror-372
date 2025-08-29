from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GroupShape (  Shape, IShape) :
    """
    Represents a group of shapes on a slide.
    """
    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the LineFormat object that contains line formatting properties for a shape.
        Read-only.
        """
        GetDllLibPpt().GroupShape_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().GroupShape_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GroupShape_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def ShapeLocking(self)->'GroupShapeLocking':
        """
        Gets shape's locks.
        Readonly.
        """
        GetDllLibPpt().GroupShape_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().GroupShape_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GroupShape_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else GroupShapeLocking(intPtr)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
        Gets the collection of shapes inside the group.
        Read-only 
        """
        from spire.presentation.ShapeCollection import ShapeCollection
        GetDllLibPpt().GroupShape_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().GroupShape_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GroupShape_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the current GroupShape is equal to another object.
        
        Args:
            obj (SpireObject): The object to compare with.
            
        Returns:
            bool: True if the objects are equal, otherwise False.
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GroupShape_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GroupShape_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GroupShape_Equals,self.Ptr, intPtrobj)
        return ret

