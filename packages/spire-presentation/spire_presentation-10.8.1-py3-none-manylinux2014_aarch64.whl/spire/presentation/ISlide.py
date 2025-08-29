from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISlide (SpireObject) :
    """
    Represents a slide in a presentation.
    Provides properties and methods for slide content, layout, and rendering.
    
    """
    @property

    def Theme(self)->'Theme':
        """
        Gets the theme associated with the slide.
        Returns:
            Theme: Slide theme object.
        """
        GetDllLibPpt().ISlide_get_Theme.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Theme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Theme,self.Ptr)
        ret = None if intPtr==None else Theme(intPtr)
        return ret


    @property
    def SlideNumber(self)->int:
        """
        Gets or sets the slide number in the presentation.
        Returns:
            int: Current slide number.
        """
        GetDllLibPpt().ISlide_get_SlideNumber.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideNumber.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISlide_get_SlideNumber,self.Ptr)
        return ret

    @SlideNumber.setter
    def SlideNumber(self, value:int):
        """
        Sets the slide number in the presentation.
        Parameters:
            value: New slide number.
        """
        GetDllLibPpt().ISlide_set_SlideNumber.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISlide_set_SlideNumber,self.Ptr, value)

    @property
    def Hidden(self)->bool:
        """
        Indicates whether the slide is hidden during slide shows.
        Returns:
            bool: True if hidden, False otherwise.
        """
        GetDllLibPpt().ISlide_get_Hidden.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Hidden.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISlide_get_Hidden,self.Ptr)
        return ret

    @Hidden.setter
    def Hidden(self, value:bool):
        """
        Sets whether the slide is hidden during slide shows.
        Parameters:
            value: True to hide, False to show.
        """
        GetDllLibPpt().ISlide_set_Hidden.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISlide_set_Hidden,self.Ptr, value)

    @property

    def NotesSlide(self)->'NotesSlide':
        """
        Gets the notes slide.
        
        Returns:
            NotesSlide: Read-only notes slide.
        """
        GetDllLibPpt().ISlide_get_NotesSlide.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_NotesSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_NotesSlide,self.Ptr)
        ret = None if intPtr==None else NotesSlide(intPtr)
        return ret


    @property

    def Comments(self)->List['Comment']:
        """
        Gets all author comments.
        
        Returns:
            List[Comment]: Collection of comments.
        """
        GetDllLibPpt().ISlide_get_Comments.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Comments.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_get_Comments,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, Comment)
        return ret


    @property

    def Shapes(self)->'ShapeCollection':
        """
        Gets all shapes on the slide.
        
        Returns:
            ShapeCollection: Read-only collection of shapes.
        """
        GetDllLibPpt().ISlide_get_Shapes.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Shapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Shapes,self.Ptr)
        ret = None if intPtr==None else ShapeCollection(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
        Gets or sets slide name.
        
        Returns:
            str: Name of the slide.
        """
        GetDllLibPpt().ISlide_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ISlide_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        """
        Sets slide name.
        
        Args:
            value (str): New slide name.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ISlide_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Name,self.Ptr,valuePtr)

    @property

    def SlideID(self)->'int':
        """
        Gets unique slide identifier.
        
        Returns:
            int: Read-only slide ID.
        """
        GetDllLibPpt().ISlide_get_SlideID.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideID.restype=c_int
        slideid = CallCFunction(GetDllLibPpt().ISlide_get_SlideID,self.Ptr)
        return slideid


    @property

    def MasterSlideID(self)->'int':
        """
        Gets or sets master slide identifier.
        
        Returns:
            int: ID of associated master slide.
        """
        GetDllLibPpt().ISlide_get_MasterSlideID.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_MasterSlideID.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_MasterSlideID,self.Ptr)
        ret = None if intPtr==None else int(intPtr)
        return ret


    @MasterSlideID.setter
    def MasterSlideID(self, value:'UInt32'):
        """
        Sets master slide identifier.
        
        Args:
            value (int): New master slide ID.
        """
        GetDllLibPpt().ISlide_set_MasterSlideID.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_set_MasterSlideID,self.Ptr, value.Ptr)

    @property

    def TagsList(self)->'TagCollection':
        """
        Gets slide's metadata tags.
        
        Returns:
            TagCollection: Read-only tag collection.
        """
        GetDllLibPpt().ISlide_get_TagsList.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_TagsList.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_TagsList,self.Ptr)
        ret = None if intPtr==None else TagCollection(intPtr)
        return ret


    @property

    def Timeline(self)->'TimeLine':
        """
        Gets animation timeline.
        
        Returns:
            TimeLine: Read-only animation timeline.
        """
        GetDllLibPpt().ISlide_get_Timeline.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Timeline.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Timeline,self.Ptr)
        ret = None if intPtr==None else TimeLine(intPtr)
        return ret


    @property

    def SlideShowTransition(self)->'SlideShowTransition':
        """
        Gets slide transition settings.
        
        Returns:
            SlideShowTransition: Read-only transition properties.
        """
        GetDllLibPpt().ISlide_get_SlideShowTransition.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideShowTransition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_SlideShowTransition,self.Ptr)
        ret = None if intPtr==None else SlideShowTransition(intPtr)
        return ret


    @property

    def SlideBackground(self)->'SlideBackground':
        """
        Gets slide background properties.
        
        Returns:
            SlideBackground: Read-only background settings.
        """
        GetDllLibPpt().ISlide_get_SlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_SlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_SlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def DisplaySlideBackground(self)->'SlideBackground':
        """
        Gets display background properties.
        
        Returns:
            SlideBackground: Read-only display background.
        """
        GetDllLibPpt().ISlide_get_DisplaySlideBackground.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_DisplaySlideBackground.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_DisplaySlideBackground,self.Ptr)
        ret = None if intPtr==None else SlideBackground(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """
        Gets parent presentation.
        
        Returns:
            Presentation: Parent presentation object.
        """
        from spire.presentation import Presentation
        GetDllLibPpt().ISlide_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property
    def ShowMasterShape(self)->bool:
        """
        Indicates whether to show master shapes.
        
        Returns:
            bool: True to show master shapes, False to hide.
        """
        GetDllLibPpt().ISlide_get_ShowMasterShape.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_ShowMasterShape.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISlide_get_ShowMasterShape,self.Ptr)
        return ret

    @ShowMasterShape.setter
    def ShowMasterShape(self, value:bool):
        """
        Sets visibility of master shapes.
        
        Args:
            value (bool): True to show, False to hide.
        """
        GetDllLibPpt().ISlide_set_ShowMasterShape.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISlide_set_ShowMasterShape,self.Ptr, value)


    def GetPlaceholderShapes(self,placeholder:Placeholder):
        rets = []
        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p,c_void_p,c_int]
        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype= IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr,placeholder.Ptr,0)
        ret = None if intPtrWithTypeName==None else ShapeList._create(intPtrWithTypeName)
        if(ret != None):
            rets.append(ret)

        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p,c_void_p,c_int]
        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype= IntPtrWithTypeName
        intPtrWithTypeName = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr,placeholder.Ptr,1)
        ret = None if intPtrWithTypeName==None else ShapeList._create(intPtrWithTypeName)
        if(ret != None):
            rets.append(ret)

        return rets
    
    def SaveAsImage(self)->'Stream':
        """
        Saves slide as image.
        
        Returns:
            Stream: Image data stream.
        """
        GetDllLibPpt().ISlide_SaveAsImage.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret

    
    def SaveAsImageByWH(self ,width:int,height:int)->'Stream':
        """
        Saves slide as image with specified dimensions.
        
        Args:
            width (int): Image width.
            height (int): Image height.
        
        Returns:
            Stream: Image data stream.
        """
        
        GetDllLibPpt().ISlide_SaveAsImageWH.argtypes=[c_void_p ,c_int,c_int]
        GetDllLibPpt().ISlide_SaveAsImageWH.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsImageWH,self.Ptr, width,height)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    #@dispatch

    #def SaveAsEMF(self ,filePath:str):
    #    """

    #    """
        
    #    GetDllLibPpt().ISlide_SaveAsEMF.argtypes=[c_void_p ,c_wchar_p]
    #    CallCFunction(GetDllLibPpt().ISlide_SaveAsEMF,self.Ptr, filePath)

    #@dispatch

    #def SaveAsEMF(self)->Image:
    #    """

    #    """
    #    GetDllLibPpt().ISlide_SaveAsEMF1.argtypes=[c_void_p]
    #    GetDllLibPpt().ISlide_SaveAsEMF1.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveAsEMF1,self.Ptr)
    #    ret = None if intPtr==None else Image(intPtr)
    #    return ret


    #@dispatch

    #def SaveAsEMF(self ,filePath:str,width:int,height:int):
    #    """

    #    """
        
    #    GetDllLibPpt().ISlide_SaveAsEMFFWH.argtypes=[c_void_p ,c_wchar_p,c_int,c_int]
    #    CallCFunction(GetDllLibPpt().ISlide_SaveAsEMFFWH,self.Ptr, filePath,width,height)


    def SaveDisplayBackgroundAsImage(self)->'Stream':
        """
        Saves display background as image.
        
        Returns:
            Stream: Image data stream.
        """
        GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveDisplayBackgroundAsImage,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveToFile(self ,file:str,fileFormat:'FileFormat'):
        """
        Saves slide to file.
        
        Args:
            file (str): Output file path.
            file_format (FileFormat): File format.
        """
        enumfileFormat:c_int = fileFormat.value

        filePtr = StrToPtr(file)
        GetDllLibPpt().ISlide_SaveToFile.argtypes=[c_void_p ,c_char_p,c_int]
        CallCFunction(GetDllLibPpt().ISlide_SaveToFile,self.Ptr,filePtr,enumfileFormat)


    def SaveToSVG(self)->'Stream':
        """
        Saves slide as SVG.
        
        Returns:
            Stream: SVG data stream.
        """
        GetDllLibPpt().ISlide_SaveToSVG.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_SaveToSVG.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_SaveToSVG,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def AddNotesSlide(self)->'NotesSlide':
        """
        Adds a notes slide.
        
        Returns:
            NotesSlide: Newly created notes slide.
        """
        GetDllLibPpt().ISlide_AddNotesSlide.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_AddNotesSlide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_AddNotesSlide,self.Ptr)
        ret = None if intPtr==None else NotesSlide(intPtr)
        return ret


    @dispatch

    def AddComment(self ,author:ICommentAuthor,text:str,position:PointF,dateTime:DateTime):
        """
        Adds a comment.
        
        Args:
            author (ICommentAuthor): Comment author.
            text (str): Comment text.
            position (PointF): Position on slide.
            date_time (DateTime): Comment timestamp.
        """
        intPtrauthor:c_void_p = author.Ptr
        intPtrposition:c_void_p = position.Ptr
        intPtrdateTime:c_void_p = dateTime.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_AddComment.argtypes=[c_void_p ,c_void_p,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_AddComment,self.Ptr, intPtrauthor,textPtr,intPtrposition,intPtrdateTime)

    @dispatch

    def AddComment(self ,comment:Comment):
        """
        Adds a comment.
        
        Args:
            comment (Comment): Comment object to add.
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().ISlide_AddCommentC.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_AddCommentC,self.Ptr, intPtrcomment)

    @dispatch

    def DeleteComment(self ,comment:Comment):
        """
        Deletes a comment.
        
        Args:
            comment (Comment): Comment to delete.
        """
        intPtrcomment:c_void_p = comment.Ptr

        GetDllLibPpt().ISlide_DeleteComment.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteComment,self.Ptr, intPtrcomment)

    @dispatch

    def DeleteComment(self ,author:ICommentAuthor,text:str):
        """
        Deletes comments by author and text.
        
        Args:
            author (ICommentAuthor): Author of comments.
            text (str): Text to match.
        """
        intPtrauthor:c_void_p = author.Ptr

        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_DeleteCommentAT.argtypes=[c_void_p ,c_void_p,c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentAT,self.Ptr, intPtrauthor,textPtr)

    @dispatch

    def DeleteComment(self ,author:ICommentAuthor):
        """
        Deletes all comments by author.
        
        Args:
            author (ICommentAuthor): Author of comments.
        """
        intPtrauthor:c_void_p = author.Ptr

        GetDllLibPpt().ISlide_DeleteCommentA.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentA,self.Ptr, intPtrauthor)

    @dispatch

    def DeleteComment(self ,text:str):
        """
        Deletes comments by text.
        
        Args:
            text (str): Text to match.
        """
        
        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_DeleteCommentT.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_DeleteCommentT,self.Ptr,textPtr)

#    @dispatch
#
#    def GetComments(self ,author:ICommentAuthor,text:str)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific author or specific text.
#    </summary>
#    <param name="ICommentAuthor">author of comments to find or null to find all comments.</param>
#    <param name="string">text of comments to find or "" to find all comments.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        intPtrauthor:c_void_p = author.Ptr
#
#        GetDllLibPpt().ISlide_GetComments.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        GetDllLibPpt().ISlide_GetComments.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetComments,self.Ptr, intPtrauthor,text)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret


#    @dispatch
#
#    def GetComments(self ,author:ICommentAuthor)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific author.
#    </summary>
#    <param name="ICommentAuthor">author of comments to find.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        intPtrauthor:c_void_p = author.Ptr
#
#        GetDllLibPpt().ISlide_GetCommentsA.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().ISlide_GetCommentsA.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetCommentsA,self.Ptr, intPtrauthor)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret


#    @dispatch
#
#    def GetComments(self ,text:str)->List[Comment]:
#        """
#    <summary>
#        Returns all slide comments added by specific text.
#    </summary>
#    <param name="string">text of comments to find or "" to find all comments.</param>
#    <returns>Array of <see cref="T:Spire.Presentation.Comment" />.</returns>
#        """
#        
#        GetDllLibPpt().ISlide_GetCommentsT.argtypes=[c_void_p ,c_wchar_p]
#        GetDllLibPpt().ISlide_GetCommentsT.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetCommentsT,self.Ptr, text)
#        ret = GetObjVectorFromArray(intPtrArray, Comment)
#        return ret



    def ApplyTheme(self ,scheme:'SlideColorScheme'):
        """
        Applies color scheme to slide.
        
        Args:
            scheme (SlideColorScheme): Color scheme to apply.
        """
        intPtrscheme:c_void_p = scheme.Ptr

        GetDllLibPpt().ISlide_ApplyTheme.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_ApplyTheme,self.Ptr, intPtrscheme)

    def Dispose(self):
        """Releases resources associated with the object."""
        GetDllLibPpt().ISlide_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_Dispose,self.Ptr)

    @property

    def Layout(self)->'ILayout':
        """
        Gets or sets slide layout.
        
        Returns:
            ILayout: Current slide layout.
        """
        GetDllLibPpt().ISlide_get_Layout.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Layout.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_Layout,self.Ptr)
        ret = None if intPtr==None else ILayout(intPtr)
        return ret


    @Layout.setter
    def Layout(self, value:'ILayout'):
        """
        Sets slide layout.
        
        Args:
            value (ILayout): New layout.
        """
        GetDllLibPpt().ISlide_set_Layout.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Layout,self.Ptr, value.Ptr)

#
    def GroupShapes(self ,shapeList:'List')->'GroupShape':
        """
        Groups shapes together.
        
        Args:
            shape_list (List): Shapes to group.
        
        Returns:
            GroupShape: New group shape.
        """
        countShapes = len(shapeList)
        ArrayTypeshapeList = c_void_p * countShapes
        arrayrectangles = ArrayTypeshapeList()
        for i in range(0, countShapes):
            arrayrectangles[i] = shapeList[i].Ptr

        GetDllLibPpt().ISlide_GroupShapes.argtypes=[c_void_p ,ArrayTypeshapeList,c_int]
        GetDllLibPpt().ISlide_GroupShapes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_GroupShapes,self.Ptr, arrayrectangles,countShapes)
        ret = None if intPtr==None else GroupShape(intPtr)
        return ret




    def Ungroup(self ,groupShape:'GroupShape'):
        """
        Ungroups shapes.
        
        Args:
            group_shape (GroupShape): Group to ungroup.
        """
        intPtrgroupShape:c_void_p = groupShape.Ptr

        GetDllLibPpt().ISlide_Ungroup.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISlide_Ungroup,self.Ptr, intPtrgroupShape)


    def ReplaceFirstText(self ,matchedString:str,newValue:str,caseSensitive:bool):
        """
        Replaces first occurrence of text.
        
        Args:
            matched_string (str): Text to find.
            new_value (str): Replacement text.
            case_sensitive (bool): Case sensitivity flag.
        """
        
        matchedStringPtr = StrToPtr(matchedString)
        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().ISlide_ReplaceFirstText.argtypes=[c_void_p ,c_char_p,c_char_p,c_bool]
        CallCFunction(GetDllLibPpt().ISlide_ReplaceFirstText,self.Ptr,matchedStringPtr,newValuePtr,caseSensitive)


    def ReplaceAllText(self ,matchedString:str,newValue:str,caseSensitive:bool):
        """
        Replaces all occurrences of text.
        
        Args:
            matched_string (str): Text to find.
            new_value (str): Replacement text.
            case_sensitive (bool): Case sensitivity flag.
        """
        
        matchedStringPtr = StrToPtr(matchedString)
        newValuePtr = StrToPtr(newValue)
        GetDllLibPpt().ISlide_ReplaceAllText.argtypes=[c_void_p ,c_char_p,c_char_p,c_bool]
        CallCFunction(GetDllLibPpt().ISlide_ReplaceAllText,self.Ptr,matchedStringPtr,newValuePtr,caseSensitive)

    @property

    def Title(self)->str:
        """
        Gets or sets slide title.
        
        Returns:
            str: Title text.
        """
        GetDllLibPpt().ISlide_get_Title.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_Title.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().ISlide_get_Title,self.Ptr))
        return ret


    @Title.setter
    def Title(self, value:str):
        """
        Sets slide title.
        
        Args:
            value (str): New title.
        """
        valuePtr = StrToPtr(value)
        GetDllLibPpt().ISlide_set_Title.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().ISlide_set_Title,self.Ptr,valuePtr)

#
#    def GetPlaceholderShapes(self ,placeholder:'Placeholder')->List['IShape']:
#        """
#    <summary>
#        Gets the layout shape and master shape by placeholder.
#    </summary>
#    <param name="placeholder">The target placeholder.</param>
#    <returns></returns>
#        """
#        intPtrplaceholder:c_void_p = placeholder.Ptr
#
#        GetDllLibPpt().ISlide_GetPlaceholderShapes.argtypes=[c_void_p ,c_void_p]
#        GetDllLibPpt().ISlide_GetPlaceholderShapes.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetPlaceholderShapes,self.Ptr, intPtrplaceholder)
#        ret = GetObjVectorFromArray(intPtrArray, IShape)
#        return ret


#
#    def ReplaceTextWithRegex(self ,regex:'Regex',newValue:str):
#        """
#    <summary>
#        Replace text with regex.
#    </summary>
#        """
#        intPtrregex:c_void_p = regex.Ptr
#
#        GetDllLibPpt().ISlide_ReplaceTextWithRegex.argtypes=[c_void_p ,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().ISlide_ReplaceTextWithRegex,self.Ptr, intPtrregex,newValue)



    def GetAllTextFrame(self)->List[str]:
       """
        Gets all text content.
        
        Returns:
            List[str]: Collection of text content.
        """
       GetDllLibPpt().ISlide_GetAllTextFrame.argtypes=[c_void_p]
       GetDllLibPpt().ISlide_GetAllTextFrame.restype=IntPtrArray
       intPtrArray = CallCFunction(GetDllLibPpt().ISlide_GetAllTextFrame,self.Ptr)
       ret = GetStringPtrArray(intPtrArray)
       return ret




    def FindFirstTextAsRange(self ,text:str)->'TextRange':
        """
        Finds first occurrence of text.
        
        Args:
            text (str): Text to find.
        
        Returns:
            TextRange: Found text range.
        """
        textPtr = StrToPtr(text)
        GetDllLibPpt().ISlide_FindFirstTextAsRange.argtypes=[c_void_p ,c_char_p]
        GetDllLibPpt().ISlide_FindFirstTextAsRange.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_FindFirstTextAsRange,self.Ptr,textPtr)
        ret = None if intPtr==None else TextRange(intPtr)
        return ret
    
    @property
    def OleObjects(self)->'OleObjectCollection':
        """
        Gets OLE objects collection.
        
        Returns:
            OleObjectCollection: Collection of OLE objects.
        """
        GetDllLibPpt().ISlide_get_OleObjects.argtypes=[c_void_p]
        GetDllLibPpt().ISlide_get_OleObjects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISlide_get_OleObjects,self.Ptr)
        ret = None if intPtr==None else OleObjectCollection(intPtr)
        return ret


