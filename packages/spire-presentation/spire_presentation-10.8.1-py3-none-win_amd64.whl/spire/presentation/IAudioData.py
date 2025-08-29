from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IAudioData (SpireObject) :
    """
    Represents embedded audio data with methods to access audio streams.
    Provides audio content type information and saving capabilities.
    """
    @property

    def ContentType(self)->str:
        """
        Gets MIME type of the audio (e.g., 'audio/mpeg').
        Read-only string.
        """
        GetDllLibPpt().IAudioData_get_ContentType.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_get_ContentType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IAudioData_get_ContentType,self.Ptr))
        return ret


    @property

    def Stream(self)->'Stream':
        """
        Gets audio data as a stream.
        Read-only Stream object.
        """
        GetDllLibPpt().IAudioData_get_Stream.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_get_Stream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudioData_get_Stream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def GetStream(self)->'Stream':
        """Returns audio data as a new Stream instance."""
        GetDllLibPpt().IAudioData_GetStream.argtypes=[c_void_p]
        GetDllLibPpt().IAudioData_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IAudioData_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToFile(self ,fileName:str):
        """
        Saves audio data to disk.
        
        Args:
            fileName: Output file path
        """
        
        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().IAudioData_SaveToFile.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().IAudioData_SaveToFile,self.Ptr,fileNamePtr)

