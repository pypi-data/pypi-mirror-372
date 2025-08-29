from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class _Presentation (  PptObject) :
    """
    Represents a Presentation document.
    
    This class provides methods for loading and saving presentation files from streams or files.
    """
#
#    def GetBytes(self)->List['Byte']:
#        """
#
#        """
#        GetDllLibPpt()._Presentation_GetBytes.argtypes=[c_void_p]
#        GetDllLibPpt()._Presentation_GetBytes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt()._Presentation_GetBytes,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret



    def GetStream(self)->'Stream':
        """
        Gets the presentation content as a stream.

        Returns:
            Stream: A stream containing the presentation data.
        """
        GetDllLibPpt()._Presentation_GetStream.argtypes=[c_void_p]
        GetDllLibPpt()._Presentation_GetStream.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt()._Presentation_GetStream,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat):
        """
        Loads the presentation from a stream.

        Args:
            stream: The stream containing the presentation data.
            fileFormat: The format of the presentation file.
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt()._Presentation_LoadFromStream.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromStream,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat):
        """
        Loads the presentation from a file.

        Args:
            file: The path to the presentation file.
            fileFormat: The format of the presentation file.
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_LoadFromFile.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFile,self.Ptr,filePtr,enumfileFormat)

    @dispatch

    def LoadFromFile(self ,file:str):
        """
        Loads the presentation from a file.

        Args:
            file: The path to the presentation file.
        """
        
        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_LoadFromFileF.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileF,self.Ptr,filePtr)

    @dispatch

    def LoadFromFile(self ,file:str,password:str):
        """
        Loads a password-protected presentation from a file.

        Args:
            file: The path to the presentation file.
            password: The password to open the presentation.
        """
        
        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromFileFP.argtypes=[c_void_p ,c_char_p,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileFP,self.Ptr,filePtr,passwordPtr)

    @dispatch

    def LoadFromFile(self ,file:str,fileFormat:FileFormat,password:str):
        """
        Loads a password-protected presentation from a file.

        Args:
            file: The path to the presentation file.
            fileFormat: The format of the presentation file.
            password: The password to open the presentation.
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromFileFFP.argtypes=[c_void_p ,c_char_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromFileFFP,self.Ptr,filePtr,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,stream:Stream,fileFormat:FileFormat):
        """
        Saves the presentation to a stream.

        Args:
            stream: The stream to save the presentation to.
            fileFormat: The format to save the presentation in.
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        GetDllLibPpt()._Presentation_SaveToFile.argtypes=[c_void_p ,c_void_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_SaveToFile,self.Ptr, intPtrstream,enumfileFormat)

    @dispatch

    def LoadFromStream(self ,stream:Stream,fileFormat:FileFormat,password:str):
        """
        Loads a password-protected presentation from a stream.

        Args:
            stream: The stream containing the presentation data.
            fileFormat: The format of the presentation file.
            password: The password to open the presentation.
        """
        intPtrstream:c_void_p = stream.Ptr
        enumfileFormat:c_int = fileFormat.value

        passwordPtr = StrToPtr(password)
        GetDllLibPpt()._Presentation_LoadFromStreamSFP.argtypes=[c_void_p ,c_void_p,c_int,c_char_p]
        CallCFunction(GetDllLibPpt()._Presentation_LoadFromStreamSFP,self.Ptr, intPtrstream,enumfileFormat,passwordPtr)

    @dispatch

    def SaveToFile(self ,file:str,fileFormat:FileFormat):
        """
        Saves the presentation to a file.

        Args:
            file: The path to save the presentation to.
            fileFormat: The format to save the presentation in.
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt()._Presentation_SaveToFileFF.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt()._Presentation_SaveToFileFF,self.Ptr,filePtr,enumfileFormat)

