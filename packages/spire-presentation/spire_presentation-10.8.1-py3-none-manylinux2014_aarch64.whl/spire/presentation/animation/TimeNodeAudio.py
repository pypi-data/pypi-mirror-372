from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeNodeAudio (  TimeNodeMedia) :
    """
    Represents an audio node within an animation timeline.
    
    """
#    @dispatch
#
#    def SetAudioData(self ,file:'FileInfo'):
#        """
#    <summary>
#        setTimeNodeAudio
#    </summary>
#    <param name="file">audio file</param>
#        """
#        intPtrfile:c_void_p = file.Ptr
#
#        GetDllLibPpt().TimeNodeAudio_SetAudioData.argtypes=[c_void_p ,c_void_p]
#        CallCFunction(GetDllLibPpt().TimeNodeAudio_SetAudioData,self.Ptr, intPtrfile)


    @dispatch

    def SetAudioData(self ,stream:Stream):
        """
        Sets audio data from a stream source.
        
        Args:
            stream (Stream): Input stream containing audio data
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().TimeNodeAudio_SetAudioData.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_SetAudioData,self.Ptr, intPtrstream)


    def GetAudioData(self)->List['Byte']:
        """
        Retrieves the raw audio byte data.
        
        Returns:
            List[Byte]: Byte array containing the audio data
        """
        GetDllLibPpt().TimeNodeAudio_GetAudioData.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_GetAudioData.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().TimeNodeAudio_GetAudioData,self.Ptr)
        ret = GetBytesFromArray(intPtrArray)
        return ret


    @property
    def Volume(self)->float:
        """
        Gets or sets the audio playback volume.
        
        Value ranges from 0.0 (silent) to 1.0 (maximum volume)
        
        Returns:
            float: Current volume level
        """
        GetDllLibPpt().TimeNodeAudio_get_Volume.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_Volume.restype=c_float
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_get_Volume,self.Ptr)
        return ret

    @Volume.setter
    def Volume(self, value:float):
        GetDllLibPpt().TimeNodeAudio_set_Volume.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_set_Volume,self.Ptr, value)

    @property
    def IsMute(self)->bool:
        """
        Gets or sets whether the audio is muted.
        
        Returns:
            bool: True if audio is muted, False otherwise
        """
        GetDllLibPpt().TimeNodeAudio_get_IsMute.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_IsMute.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_get_IsMute,self.Ptr)
        return ret

    @IsMute.setter
    def IsMute(self, value:bool):
        GetDllLibPpt().TimeNodeAudio_set_IsMute.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TimeNodeAudio_set_IsMute,self.Ptr, value)

    @property

    def SoundName(self)->str:
        """
        Gets the name identifier of the sound.
        
        Returns:
            str: Name associated with the audio element
        """
        GetDllLibPpt().TimeNodeAudio_get_SoundName.argtypes=[c_void_p]
        GetDllLibPpt().TimeNodeAudio_get_SoundName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TimeNodeAudio_get_SoundName,self.Ptr))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
        Determines whether the specified object is equal to the current audio node.
        
        Args:
            obj (SpireObject): The object to compare with the current audio node
            
        Returns:
            bool: True if the specified object is equal to the current audio node; otherwise False
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeNodeAudio_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeNodeAudio_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeNodeAudio_Equals,self.Ptr, intPtrobj)
        return ret

