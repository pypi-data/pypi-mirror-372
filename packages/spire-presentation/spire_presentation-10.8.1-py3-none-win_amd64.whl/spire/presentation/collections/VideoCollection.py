from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class VideoCollection (  ICollection, IEnumerable) :
    """
    Represents a collection of Video objects.
    """
    @property
    def Count(self)->int:
        """
        Gets number of text ranges in the collection.
        
        Returns:
            Integer count of text range objects.
        """
        GetDllLibPpt().VideoCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().VideoCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().VideoCollection_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'VideoData':
        """
        Get a video by index.
        
        Args:
            index (int): Index of the video to retrieve
            
        Returns:
            VideoData: Video object at the specified index
        """
        
        GetDllLibPpt().VideoCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().VideoCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().VideoCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else VideoData(intPtr)
        return ret


    @dispatch

    def AppendByVideoData(self ,videoData:VideoData)->VideoData:
        """
        Add a copy of a video from another presentation.
        
        Args:
            videoData (VideoData): Source video to copy
            
        Returns:
            VideoData: Newly added video object
        """
        intPtrvideoData:c_void_p = videoData.Ptr

        GetDllLibPpt().VideoCollection_Append.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().VideoCollection_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().VideoCollection_Append,self.Ptr, intPtrvideoData)
        ret = None if intPtr==None else VideoData(intPtr)
        return ret


    @dispatch

    def AppendByStream(self ,stream:Stream)->VideoData:
        """
        Add a video from a stream.
        
        Args:
            stream (Stream): Stream containing video data
            
        Returns:
            VideoData: Newly added video object
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().VideoCollection_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().VideoCollection_AppendS.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().VideoCollection_AppendS,self.Ptr, intPtrstream)
        ret = None if intPtr==None else VideoData(intPtr)
        return ret


#    @dispatch
#
#    def Append(self ,videoData:'Byte[]')->VideoData:
#        """
#    <summary>
#        Creates and adds a video to a presentation from byte array.
#    </summary>
#    <param name="videoData">Video bytes.</param>
#    <returns>Added video.</returns>
#        """
#        #arrayvideoData:ArrayTypevideoData = ""
#        countvideoData = len(videoData)
#        ArrayTypevideoData = c_void_p * countvideoData
#        arrayvideoData = ArrayTypevideoData()
#        for i in range(0, countvideoData):
#            arrayvideoData[i] = videoData[i].Ptr
#
#
#        GetDllLibPpt().VideoCollection_AppendV.argtypes=[c_void_p ,ArrayTypevideoData]
#        GetDllLibPpt().VideoCollection_AppendV.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().VideoCollection_AppendV,self.Ptr, arrayvideoData)
#        ret = None if intPtr==None else VideoData(intPtr)
#        return ret
#


