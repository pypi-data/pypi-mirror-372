from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Field (  PptObject) :
    """
    Represents a field within a presentation document.
    """
    @property

    def Type(self)->'FieldType':
        """
        Gets or sets the type of field.
        
        Returns:
            FieldType: The current field type
        """
        GetDllLibPpt().Field_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().Field_get_Type.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Field_get_Type,self.Ptr)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @Type.setter
    def Type(self, value:'FieldType'):
        """
        Sets the type of field.
        
        Parameters:
            value (FieldType): New field type to apply
        """
        GetDllLibPpt().Field_set_Type.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().Field_set_Type,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether this field is equal to another object.
        
        Parameters:
            obj (SpireObject): The object to compare with
            
        Returns:
            bool: True if objects are equal, False otherwise
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Field_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Field_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Field_Equals,self.Ptr, intPtrobj)
        return ret

