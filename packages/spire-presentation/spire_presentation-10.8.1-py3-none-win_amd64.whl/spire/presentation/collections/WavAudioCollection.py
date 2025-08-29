from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class WavAudioCollection (  ICollection, IEnumerable) :
    """Represents a collection of embedded WAV audio files."""

    @property
    def Count(self)->int:
        """
        Gets the number of audio files in the collection.

        Returns:
            int: The number of audio files.
        """
        GetDllLibPpt().WavAudioCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().WavAudioCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().WavAudioCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'IAudioData':
        """
        Gets the audio element at the specified index.

        Args:
            index: The zero-based index of the element to get.

        Returns:
            IAudioData: The audio data at the specified index.
        """
        GetDllLibPpt().WavAudioCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().WavAudioCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().WavAudioCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IAudioData(intPtr)
        return ret


    @dispatch

    def Append(self ,audioData:IAudioData)->IAudioData:
        """
        Adds an audio file to the collection.

        Args:
            audioData: Source audio object to add.

        Returns:
            IAudioData: The added audio object.
        """
        intPtraudioData:c_void_p = audioData.Ptr

        GetDllLibPpt().WavAudioCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().WavAudioCollection_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().WavAudioCollection_Append,self.Ptr, intPtraudioData)
        ret = None if intPtr==None else IAudioData(intPtr)
        return ret


    @dispatch

    def Append(self ,stream:Stream)->IAudioData:
        """
        Adds an audio file from a stream to the collection.

        Args:
            stream: Stream containing audio data.

        Returns:
            IAudioData: The added audio object.
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().WavAudioCollection_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().WavAudioCollection_AppendS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().WavAudioCollection_AppendS,self.Ptr, intPtrstream)
        ret = None if intPtr==None else IAudioData(intPtr)
        return ret


#    @dispatch
#
#    def Append(self ,audioData:'Byte[]')->IAudioData:
#        """
#    <summary>
#        Adds an audio to the list from byte array.
#    </summary>
#    <param name="audioData">Audio bytes.</param>
#    <returns>Added audio.</returns>
#        """
#        #arrayaudioData:ArrayTypeaudioData = ""
#        countaudioData = len(audioData)
#        ArrayTypeaudioData = c_void_p * countaudioData
#        arrayaudioData = ArrayTypeaudioData()
#        for i in range(0, countaudioData):
#            arrayaudioData[i] = audioData[i].Ptr
#
#
#        GetDllLibPpt().WavAudioCollection_AppendA.argtypes=[c_void_p ,ArrayTypeaudioData]
#        GetDllLibPpt().WavAudioCollection_AppendA.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().WavAudioCollection_AppendA,self.Ptr, arrayaudioData)
#        ret = None if intPtr==None else IAudioData(intPtr)
#        return ret
#


