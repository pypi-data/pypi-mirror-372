from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Section (SpireObject) :
    """
    Represents a logical grouping of slides in a presentation.
    Sections help organize slides into named groups for better management.
    """
#    @property
#
#    def SlideIdList(self)->'List1':
#        """
#    <summary>
#        get IDs of slides in this section.
#    </summary>
#        """
#        GetDllLibPpt().Section_get_SlideIdList.argtypes=[c_void_p]
#        GetDllLibPpt().Section_get_SlideIdList.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().Section_get_SlideIdList,self.Ptr)
#        ret = None if intPtr==None else List1(intPtr)
#        return ret
#


    def GetSlides(self)->List['ISlide']:
        """
        Retrieves all slides contained within this section.
        
        Returns:
            List[ISlide]: A list of slide objects belonging to this section.
        """
        GetDllLibPpt().Section_GetSlides.argtypes=[c_void_p]
        GetDllLibPpt().Section_GetSlides.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Section_GetSlides,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, ISlide)
        return ret



    def Move(self ,index:int,slide:'ISlide'):
        """
        Relocates a slide to a new position within this section.
        
        Args:
            index: Target position index (0-based).
            slide: Slide object to be moved.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Move.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().Section_Move,self.Ptr, index,intPtrslide)


    def Insert(self ,index:int,slide:'ISlide')->'ISlide':
        """
        Inserts a slide at the specified position within this section.
        
        Args:
            index: Target insertion position (0-based).
            slide: Slide object to insert.
            
        Returns:
            ISlide: The inserted slide object.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().Section_Insert.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Section_Insert,self.Ptr, index,intPtrslide)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret



    def AddRange(self ,slides:'IList'):
        """
        Adds multiple slides to the end of this section.
        
        Args:
            slides: List of slide objects to add.
        """
        slide_ptrs = [s.Ptr for s in slides]

        num_slides = len(slide_ptrs)
        slide_ptr_array = (c_void_p * num_slides)(*slide_ptrs)
        GetDllLibPpt().Section_AddRange.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Section_AddRange,self.Ptr, slide_ptr_array,num_slides)



    def RemoveAt(self ,index:int):
        """
        Removes the slide at the specified position.
        
        Args:
            index: Position index of slide to remove (0-based).
        """
        
        GetDllLibPpt().Section_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().Section_RemoveAt,self.Ptr, index)


    def Remove(self ,slide:'ISlide'):
        """
        Removes a specific slide from this section.
        
        Args:
            slide: Slide object to remove.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().Section_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().Section_Remove,self.Ptr, intPtrslide)


    def RemoveRange(self ,startIndex:int,count:int):
        """
        Removes a range of consecutive slides.
        
        Args:
            startIndex: Starting position index (0-based).
            count: Number of slides to remove.
        """
        
        GetDllLibPpt().Section_RemoveRange.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().Section_RemoveRange,self.Ptr, startIndex,count)

    @property

    def Name(self)->str:
        """
        Gets or sets the display name of the section.
        
        Returns:
            str: Current section name.
        """
        GetDllLibPpt().Section_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Section_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Section_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Section_set_Name,self.Ptr,valuePtr)

    @property

    def Id(self)->str:
        """
        Gets or sets the unique identifier for the section.
        
        Returns:
            str: Unique section identifier.
        """
        GetDllLibPpt().Section_get_Id.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Id.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().Section_get_Id,self.Ptr))
        return ret


    @Id.setter
    def Id(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().Section_set_Id.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().Section_set_Id,self.Ptr,valuePtr)

    @property
    def Index(self)->int:
        """
        Gets the position index of this section in the parent collection.
        
        Returns:
            int: Zero-based index position.
        """
        GetDllLibPpt().Section_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().Section_get_Index.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Section_get_Index,self.Ptr)
        return ret

