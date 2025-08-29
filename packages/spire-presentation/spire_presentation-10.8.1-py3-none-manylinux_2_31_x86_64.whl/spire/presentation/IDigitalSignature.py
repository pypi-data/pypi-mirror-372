from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IDigitalSignature (SpireObject) :
    """
    Represents a digital signature in a presentation document.
    """
    @property

    def Comments(self)->str:
        """
        Gets or sets comments associated with the digital signature.
        
        Returns:
            str: The comments text associated with the signature.
        """
        GetDllLibPpt().IDigitalSignature_get_Comments.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_Comments.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IDigitalSignature_get_Comments,self.Ptr))
        return ret


    @Comments.setter
    def Comments(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().IDigitalSignature_set_Comments.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_Comments,self.Ptr,valuePtr)

    @property

    def SignTime(self)->'DateTime':
        """
        Gets or sets the date and time when the document was signed.
        
        Returns:
            DateTime: The timestamp of the digital signature.
        """
        GetDllLibPpt().IDigitalSignature_get_SignTime.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_SignTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IDigitalSignature_get_SignTime,self.Ptr)
        ret = None if intPtr==None else DateTime(intPtr)
        return ret


    @SignTime.setter
    def SignTime(self, value:'DateTime'):
        GetDllLibPpt().IDigitalSignature_set_SignTime.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_SignTime,self.Ptr, value.Ptr)

    @property
    def IsValid(self)->bool:
        """
        Indicates whether this digital signature is cryptographically valid.
        
        Returns:
            bool: True if the signature is valid, False if invalid or compromised.
        """
        GetDllLibPpt().IDigitalSignature_get_IsValid.argtypes=[c_void_p]
        GetDllLibPpt().IDigitalSignature_get_IsValid.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().IDigitalSignature_get_IsValid,self.Ptr)
        return ret

    @IsValid.setter
    def IsValid(self, value:bool):
        GetDllLibPpt().IDigitalSignature_set_IsValid.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().IDigitalSignature_set_IsValid,self.Ptr, value)

