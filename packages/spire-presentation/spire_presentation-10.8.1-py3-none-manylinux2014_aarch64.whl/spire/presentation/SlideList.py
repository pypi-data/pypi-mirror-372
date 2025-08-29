from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideList (SpireObject) :

    """
    Represents a collection of slides in a presentation.
    
    This class provides methods to manage slides, including adding, inserting, 
    removing, and rearranging slides.
    """
    @property
    def Count(self)->int:
        """
        Gets the number of slides in the collection.
        
        Returns:
            int: The number of slides.
        """
        GetDllLibPpt().SlideList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_get_Count,self.Ptr)
        return ret

     #support x[]
    def __getitem__(self, key):
        """
        Gets a slide by index.
        
        Args:
            key (int): The zero-based index of the slide.
            
        Returns:
            ISlide: The slide at the specified index.
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().SlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_get_Item,self.Ptr, key)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret

    def get_Item(self ,index:int)->'ISlide':
        """
        Gets the slide at the specified index.
        
        Args:
            index (int): The zero-based index of the slide.
            
        Returns:
            ISlide: The slide at the specified index.
        """
        
        GetDllLibPpt().SlideList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def Append(self)->ISlide:
        """
        Appends a new slide with default layout.
        
        Returns:
            ISlide: The newly created slide.
        """
        GetDllLibPpt().SlideList_Append.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_Append.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_Append,self.Ptr)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def AppendByLayoutType(self ,templateType:SlideLayoutType):
        """
        Appends a new slide with specified layout type.
        
        Args:
            templateType (SlideLayoutType): The layout type for the new slide.
            
        Returns:
            ISlide: The newly created slide.
        """
        enumtemplateType:c_int = templateType.value

        GetDllLibPpt().SlideList_AppendT.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_AppendT.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_AppendT,self.Ptr, enumtemplateType)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def AppendBySlide(self ,slide:ISlide)->int:
        """
        Appends an existing slide to the collection.
        
        Args:
            slide (ISlide): The slide to append.
            
        Returns:
            int: The index of the added slide.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_AppendS.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideList_AppendS.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendS,self.Ptr, intPtrslide)
        return ret

    @dispatch

    def Insert(self ,index:int,slide:ISlide):
        """
        Inserts a slide at the specified position.
        
        Args:
            index (int): The zero-based index at which to insert.
            slide (ISlide): The slide to insert.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_Insert.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_Insert,self.Ptr, index,intPtrslide)

    @dispatch

    def Insert(self ,index:int)->ISlide:
        """
        Inserts an empty slide at the specified position.
        
        Args:
            index (int): The zero-based index at which to insert.
            
        Returns:
            ISlide: The newly created slide.
        """
        
        GetDllLibPpt().SlideList_InsertI.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().SlideList_InsertI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_InsertI,self.Ptr, index)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def InsertByLayoutType(self ,index:int,templateType:SlideLayoutType)->ISlide:
        """
        Inserts a slide with specified layout type at the specified position.
        
        Args:
            index (int): The zero-based index at which to insert.
            templateType (SlideLayoutType): The layout type for the new slide.
            
        Returns:
            ISlide: The newly created slide.
        """
        enumtemplateType:c_int = templateType.value

        GetDllLibPpt().SlideList_InsertIT.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().SlideList_InsertIT.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_InsertIT,self.Ptr, index,enumtemplateType)
        ret = None if intPtr==None else ISlide(intPtr)
        return ret


    @dispatch

    def Append(self ,slide:ISlide,layout:ILayout)->int:
        """
        Appends a slide with a specific layout.
        
        Args:
            slide (ISlide): The slide to append.
            layout (ILayout): The layout to apply.
            
        Returns:
            int: The index of the added slide.
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrlayout:c_void_p = layout.Ptr

        GetDllLibPpt().SlideList_AppendSL.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().SlideList_AppendSL.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendSL,self.Ptr, intPtrslide,intPtrlayout)
        return ret

    @dispatch

    def Insert(self ,index:int,slide:ISlide,layout:ILayout):
        """
        Inserts a slide with specified layout type at the specified position.
        
        Args:
            index (int): The zero-based index at which to insert.
            templateType (SlideLayoutType): The layout type for the new slide.
            
        Returns:
            ISlide: The newly created slide.
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrlayout:c_void_p = layout.Ptr

        GetDllLibPpt().SlideList_InsertISL.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_InsertISL,self.Ptr, index,intPtrslide,intPtrlayout)

    @dispatch

    def AppendByMaster(self ,slide:ISlide,master:IMasterSlide)->int:
        """
    <summary>
        Adds a slide to the collection.
    </summary>
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrmaster:c_void_p = master.Ptr

        GetDllLibPpt().SlideList_AppendSM.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().SlideList_AppendSM.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_AppendSM,self.Ptr, intPtrslide,intPtrmaster)
        return ret

    @dispatch

    def InsertByMaster(self ,index:int,slide:ISlide,master:IMasterSlide):
        """
        Appends a slide with a specific master slide.
        
        Args:
            slide (ISlide): The slide to append.
            master (IMasterSlide): The master slide to apply.
            
        Returns:
            int: The index of the added slide.
        """
        intPtrslide:c_void_p = slide.Ptr
        intPtrmaster:c_void_p = master.Ptr

        GetDllLibPpt().SlideList_InsertISM.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_InsertISM,self.Ptr, index,intPtrslide,intPtrmaster)


    def Remove(self ,value:'ISlide'):
        """
        Removes the first occurrence of a specific slide.
        
        Args:
            value (ISlide): The slide to remove.
        """
        intPtrvalue:c_void_p = value.Ptr

        GetDllLibPpt().SlideList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().SlideList_Remove,self.Ptr, intPtrvalue)


    def RemoveAt(self ,index:int):
        """
        Removes the slide at the specified index.
        
        Args:
            index (int): The zero-based index of the slide to remove.
        """
        
        GetDllLibPpt().SlideList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().SlideList_RemoveAt,self.Ptr, index)


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator to iterate through the collection.
        
        Returns:
            IEnumerator: An enumerator for the collection.
        """
        GetDllLibPpt().SlideList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().SlideList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


#    @dispatch
#
#    def ToArray(self)->List[ISlide]:
#        """
#    <summary>
#        Creates and returns an array with all slides in it.
#    </summary>
#    <returns>Array of <see cref="T:Spire.Presentation.Slide" /></returns>
#        """
#        GetDllLibPpt().SlideList_ToArray.argtypes=[c_void_p]
#        GetDllLibPpt().SlideList_ToArray.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().SlideList_ToArray,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, ISlide)
#        return ret


#    @dispatch
#
#    def ToArray(self ,startIndex:int,count:int)->List[ISlide]:
#        """
#
#        """
#        
#        GetDllLibPpt().SlideList_ToArraySC.argtypes=[c_void_p ,c_int,c_int]
#        GetDllLibPpt().SlideList_ToArraySC.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().SlideList_ToArraySC,self.Ptr, startIndex,count)
#        ret = GetObjVectorFromArray(intPtrArray, ISlide)
#        return ret



    def Move(self ,newIndex:int,OldIndex:int):
        """
        Moves a slide from one position to another.
        
        Args:
            newIndex (int): The target index position.
            OldIndex (int): The current index position of the slide.
        """
        
        GetDllLibPpt().SlideList_Move.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().SlideList_Move,self.Ptr, newIndex,OldIndex)


    def IndexOf(self ,slide:'ISlide')->int:
        """
        Gets the index of a specific slide.
        
        Args:
            slide (ISlide): The slide to locate.
            
        Returns:
            int: The zero-based index of the slide, or -1 if not found.
        """
        intPtrslide:c_void_p = slide.Ptr

        GetDllLibPpt().SlideList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlideList_IndexOf,self.Ptr, intPtrslide)
        return ret

