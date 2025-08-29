from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AudioCD (SpireObject) :
    """
    Represents an audio CD object for presentations.

    """

    @dispatch
    def __init__(self):
        GetDllLibPpt().AudioCD_create_audioCD.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AudioCD_create_audioCD)
        super(AudioCD, self).__init__(intPtr)
    """

    """
    @property
    def StartTrack(self)->int:
        """
        Gets or sets a start track index.
        """
        GetDllLibPpt().AudioCD_get_StartTrack.argtypes=[c_void_p]
        GetDllLibPpt().AudioCD_get_StartTrack.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AudioCD_get_StartTrack,self.Ptr)
        return ret

    @StartTrack.setter
    def StartTrack(self, value:int):
        GetDllLibPpt().AudioCD_set_StartTrack.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AudioCD_set_StartTrack,self.Ptr, value)

    @property
    def StartTime(self)->int:
        """
        Gets or sets a start track time.
            
        """
        GetDllLibPpt().AudioCD_get_StartTime.argtypes=[c_void_p]
        GetDllLibPpt().AudioCD_get_StartTime.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AudioCD_get_StartTime,self.Ptr)
        return ret

    @StartTime.setter
    def StartTime(self, value:int):
        GetDllLibPpt().AudioCD_set_StartTime.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AudioCD_set_StartTime,self.Ptr, value)

    @property
    def EndTrack(self)->int:
        """
        Gets or sets a last track index
            
        """
        GetDllLibPpt().AudioCD_get_EndTrack.argtypes=[c_void_p]
        GetDllLibPpt().AudioCD_get_EndTrack.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AudioCD_get_EndTrack,self.Ptr)
        return ret

    @EndTrack.setter
    def EndTrack(self, value:int):
        GetDllLibPpt().AudioCD_set_EndTrack.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AudioCD_set_EndTrack,self.Ptr, value)

    @property
    def EndTime(self)->int:
        """
        Gets or sets a last track time.
           
        """
        GetDllLibPpt().AudioCD_get_EndTime.argtypes=[c_void_p]
        GetDllLibPpt().AudioCD_get_EndTime.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AudioCD_get_EndTime,self.Ptr)
        return ret

    @EndTime.setter
    def EndTime(self, value:int):
        GetDllLibPpt().AudioCD_set_EndTime.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AudioCD_set_EndTime,self.Ptr, value)

