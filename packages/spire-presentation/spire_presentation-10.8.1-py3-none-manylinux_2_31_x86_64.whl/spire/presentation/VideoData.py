from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class VideoData (SpireObject) :
    """
    Represents a video embedded into a presentation.
    """
    @property

    def ContentType(self)->str:
        """
        Get the MIME type of the video.
        
        Returns:
            str: The MIME type string
        """
        GetDllLibPpt().VideoData_get_ContentType.argtypes=[c_void_p]
        GetDllLibPpt().VideoData_get_ContentType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().VideoData_get_ContentType,self.Ptr))
        return ret


#    @property
#
#    def Data(self)->List['Byte']:
#        """
#    <summary>
#        Gets the copy of an video's data.
#            Read-only <see cref="T:System.Byte" />[].
#    </summary>
#        """
#        GetDllLibPpt().VideoData_get_Data.argtypes=[c_void_p]
#        GetDllLibPpt().VideoData_get_Data.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().VideoData_get_Data,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret


#    @Data.setter
#    def Data(self, value:List['Byte']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibPpt().VideoData_set_Data.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibPpt().VideoData_set_Data,self.Ptr, vArray, vCount)


    @property

    def Stream(self)->'Stream':
        """
        Get the video data stream.
        
        Returns:
            Stream: The stream object containing video data
        """
        GetDllLibPpt().VideoData_get_Stream.argtypes=[c_void_p]
        GetDllLibPpt().VideoData_get_Stream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().VideoData_get_Stream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def GetStream(self)->'Stream':
        """
        Get a stream containing the video data.
        
        Returns:
            Stream: The stream object containing video data
        """
        GetDllLibPpt().VideoData_GetStream.argtypes=[c_void_p]
        GetDllLibPpt().VideoData_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().VideoData_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToFile(self ,fileName:str):
        """
        Save the video to a file.
        
        Args:
            fileName (str): Path to save the video file
        """
        
        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().VideoData_SaveToFile.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().VideoData_SaveToFile,self.Ptr,fileNamePtr)

