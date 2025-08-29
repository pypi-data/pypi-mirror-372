from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeThreeD (SpireObject) :
    """
    Represents 3D properties for a shape in a presentation.
    
    This class allows control over various 3D effects including bevels, 
    extrusion, contour, and material properties.
    """
    @property
    def ContourWidth(self)->float:
        """
        Gets or sets the width of the 3D contour.
        
        Returns:
            float: The contour width in points.
        """
        GetDllLibPpt().ShapeThreeD_get_ContourWidth.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ContourWidth.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ContourWidth,self.Ptr)
        return ret

    @ContourWidth.setter
    def ContourWidth(self, value:float):
        """
        Sets the width of the 3D contour.
        
        Args:
            value: Contour width in points.
        """
        GetDllLibPpt().ShapeThreeD_set_ContourWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ContourWidth,self.Ptr, value)

    @property
    def ExtrusionHeight(self)->float:
        """
        Gets or sets the height of the extrusion effect.
        
        Returns:
            float: Extrusion height in points.
        """
        GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight,self.Ptr)
        return ret

    @ExtrusionHeight.setter
    def ExtrusionHeight(self, value:float):
        """
        Sets the height of the extrusion effect.
        
        Args:
            value: Extrusion height in points.
        """
        GetDllLibPpt().ShapeThreeD_set_ExtrusionHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ExtrusionHeight,self.Ptr, value)

    @property
    def Depth(self)->float:
        """
        Gets or sets the depth of the 3D shape.
        
        Returns:
            float: Shape depth in points.
        """
        GetDllLibPpt().ShapeThreeD_get_Depth.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_Depth.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_Depth,self.Ptr)
        return ret

    @Depth.setter
    def Depth(self, value:float):
        """
        Sets the depth of the 3D shape.
        
        Args:
            value: Shape depth in points.
        """
        GetDllLibPpt().ShapeThreeD_set_Depth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_Depth,self.Ptr, value)

    @property

    def TopBevel(self)->'ShapeBevelStyle':
        """
        Gets the top 3D bevel style (read-only).
        
        Returns:
            ShapeBevelStyle: Top bevel configuration object.
        """
        GetDllLibPpt().ShapeThreeD_get_TopBevel.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_TopBevel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_TopBevel,self.Ptr)
        ret = None if intPtr==None else ShapeBevelStyle(intPtr)
        return ret


    @property

    def BottomBevel(self)->'ShapeBevelStyle':
        """
        Gets the bottom 3D bevel style (read-only).
        
        Returns:
            ShapeBevelStyle: Bottom bevel configuration object.
        """
        GetDllLibPpt().ShapeThreeD_get_BottomBevel.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_BottomBevel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_BottomBevel,self.Ptr)
        ret = None if intPtr==None else ShapeBevelStyle(intPtr)
        return ret


    @property

    def ContourColor(self)->'ColorFormat':
        """
        Gets or sets the color of the contour.
        
        Returns:
            ColorFormat: Current contour color object.
        """
        GetDllLibPpt().ShapeThreeD_get_ContourColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ContourColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ContourColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ContourColor.setter
    def ContourColor(self, value:'ColorFormat'):
        GetDllLibPpt().ShapeThreeD_set_ContourColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ContourColor,self.Ptr, value.Ptr)

    @property

    def ExtrusionColor(self)->'ColorFormat':
        """
        Gets or sets the color of the extrusion.
        
        Returns:
            ColorFormat: Current extrusion color object.
        """
        GetDllLibPpt().ShapeThreeD_get_ExtrusionColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ExtrusionColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ExtrusionColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ExtrusionColor.setter
    def ExtrusionColor(self, value:'ColorFormat'):
        GetDllLibPpt().ShapeThreeD_set_ExtrusionColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ExtrusionColor,self.Ptr, value.Ptr)

    @property

    def BevelColorMode(self)->'BevelColorType':
        """
        Gets or sets the color mode for 3D effects.
        
        Returns:
            BevelColorType: Current bevel color mode.
        """
        GetDllLibPpt().ShapeThreeD_get_BevelColorMode.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_BevelColorMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_BevelColorMode,self.Ptr)
        objwraped = BevelColorType(ret)
        return objwraped

    @BevelColorMode.setter
    def BevelColorMode(self, value:'BevelColorType'):
        GetDllLibPpt().ShapeThreeD_set_BevelColorMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_BevelColorMode,self.Ptr, value.value)

    @property

    def PresetMaterial(self)->'PresetMaterialType':
        """
        Gets or sets the material type for 3D effects.
        
        Returns:
            PresetMaterialType: Current material type.
        """
        GetDllLibPpt().ShapeThreeD_get_PresetMaterial.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_PresetMaterial.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_PresetMaterial,self.Ptr)
        objwraped = PresetMaterialType(ret)
        return objwraped

    @PresetMaterial.setter
    def PresetMaterial(self, value:'PresetMaterialType'):
        GetDllLibPpt().ShapeThreeD_set_PresetMaterial.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_PresetMaterial,self.Ptr, value.value)

