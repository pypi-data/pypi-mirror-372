from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IDigitalSignatures (  IEnumerable) :
    """
    Represents a Collection of DigitalSignature in Presentation.
   
    """
#
#    def Add(self ,certificate:'X509Certificate2',comments:str,signTime:'DateTime')->'IDigitalSignature':
#        """
#    <summary>
#        create a signature and add to DigitalSignatureCollection.
#    </summary>
#    <param name="certificate">Certificate object that was used to sign</param>
#    <param name="comments">Signature Comments</param>
#    <param name="signTime">Sign Time</param>
#        """
#        intPtrcertificate:c_void_p = certificate.Ptr
#        intPtrsignTime:c_void_p = signTime.Ptr
#
#        GetDllLibPpt().IDigitalSignatures_Add.argtypes=[c_void_p ,c_void_p,c_wchar_p,c_void_p]
#        GetDllLibPpt().IDigitalSignatures_Add.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().IDigitalSignatures_Add,self.Ptr, intPtrcertificate,comments,intPtrsignTime)
#        ret = None if intPtr==None else IDigitalSignature(intPtr)
#        return ret
#


