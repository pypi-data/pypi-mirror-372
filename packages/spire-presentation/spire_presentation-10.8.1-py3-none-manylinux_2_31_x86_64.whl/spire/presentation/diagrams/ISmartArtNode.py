from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISmartArtNode (SpireObject) :
    """
    Represents a node within a SmartArt diagram structure.
    Provides properties and methods to access and manipulate the node's content, appearance, and hierarchical structure.
    """
    @property

    def ChildNodes(self)->'ISmartArtNodeCollection':
        """
        Gets the collection of child nodes under this node.

        Returns:
            ISmartArtNodeCollection: A collection of child nodes belonging to this node.
        """
        from spire.presentation.diagrams.ISmartArtNodeCollection import ISmartArtNodeCollection
        GetDllLibPpt().ISmartArtNode_get_ChildNodes.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_ChildNodes.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_ChildNodes,self.Ptr)
        ret = None if intPtr==None else ISmartArtNodeCollection(intPtr)
        return ret


    @property

    def TextFrame(self)->'ITextFrameProperties':
        """
        Gets or sets the text frame properties associated with the node.

        Returns:
            ITextFrameProperties: The text formatting properties of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_TextFrame.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_TextFrame.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_TextFrame,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @TextFrame.setter
    def TextFrame(self, value:'ITextFrameProperties'):
        """
        Sets the text frame properties for the node.

        Args:
            value (ITextFrameProperties): The text formatting properties to apply.
        """
        GetDllLibPpt().ISmartArtNode_set_TextFrame.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_TextFrame,self.Ptr, value.Ptr)

    @property

    def Line(self)->'TextLineFormat':
        """
        Gets the line formatting properties for the node's border.

        Returns:
            TextLineFormat: The line formatting settings of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Line,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property

    def LinkLine(self)->'TextLineFormat':
        """
        Gets the line formatting properties for connector lines linked to this node.

        Returns:
            TextLineFormat: The line formatting settings of connector lines.
        """
        GetDllLibPpt().ISmartArtNode_get_LinkLine.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_LinkLine.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_LinkLine,self.Ptr)
        ret = None if intPtr==None else TextLineFormat(intPtr)
        return ret


    @property
    def CustomText(self)->bool:
        """
        Indicates whether the node uses custom text formatting.

        Returns:
            bool: True if custom text formatting is applied, False otherwise.
        """
        GetDllLibPpt().ISmartArtNode_get_CustomText.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_CustomText.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_CustomText,self.Ptr)
        return ret

    @CustomText.setter
    def CustomText(self, value:bool):
        """
        Sets whether to use custom text formatting for the node.

        Args:
            value (bool): True to apply custom text formatting, False to use default.
        """
        GetDllLibPpt().ISmartArtNode_set_CustomText.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_CustomText,self.Ptr, value)

    @property
    def IsAssistant(self)->bool:
        """
        Indicates whether the node is designated as an "assistant" node in organizational charts.

        Returns:
            bool: True if the node is an assistant node, False otherwise.
        """
        GetDllLibPpt().ISmartArtNode_get_IsAssistant.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_IsAssistant.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_IsAssistant,self.Ptr)
        return ret

    @IsAssistant.setter
    def IsAssistant(self, value:bool):
        """
        Sets the assistant designation status for the node.

        Args:
            value (bool): True to mark as assistant node, False otherwise.
        """
        GetDllLibPpt().ISmartArtNode_set_IsAssistant.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_IsAssistant,self.Ptr, value)

    @property
    def Level(self)->int:
        """
        Gets the hierarchical level of the node within the SmartArt structure.

        Returns:
            int: The zero-based level index of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_Level.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Level.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Level,self.Ptr)
        return ret

    @property
    def Position(self)->int:
        """
        Gets or sets the display position order among sibling nodes.

        Returns:
            int: The current display position index.
        """
        GetDllLibPpt().ISmartArtNode_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Position.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Position,self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:int):
        """
        Sets the display position order among sibling nodes.

        Args:
            value (int): The new position index to assign.
        """
        GetDllLibPpt().ISmartArtNode_set_Position.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_Position,self.Ptr, value)

    @property

    def Click(self)->'ClickHyperlink':
        """
        Gets or sets the hyperlink behavior for mouse clicks on the node.

        Returns:
            ClickHyperlink: The hyperlink configuration for click interactions.
        """
        GetDllLibPpt().ISmartArtNode_get_Click.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_Click.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_Click,self.Ptr)
        ret = None if intPtr==None else ClickHyperlink(intPtr)
        return ret


    @Click.setter
    def Click(self, value:'ClickHyperlink'):
        """
        Sets the hyperlink behavior for mouse clicks.

        Args:
            value (ClickHyperlink): The hyperlink configuration to apply.
        """
        GetDllLibPpt().ISmartArtNode_set_Click.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_Click,self.Ptr, value.Ptr)

    @property
    def NodeHeight(self)->int:
        """
        Gets or sets the height of the node in points.

        Returns:
            int: The current height of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_NodeHeight.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeHeight.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeHeight,self.Ptr)
        return ret

    @NodeHeight.setter
    def NodeHeight(self, value:int):
        """
        Sets the height of the node.

        Args:
            value (int): The new height value in points.
        """
        GetDllLibPpt().ISmartArtNode_set_NodeHeight.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeHeight,self.Ptr, value)

    @property
    def NodeWidth(self)->int:
        """
        Gets or sets the width of the node in points.

        Returns:
            int: The current width of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_NodeWidth.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeWidth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeWidth,self.Ptr)
        return ret

    @NodeWidth.setter
    def NodeWidth(self, value:int):
        """
        Sets the width of the node.

        Args:
            value (int): The new width value in points.
        """
        GetDllLibPpt().ISmartArtNode_set_NodeWidth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeWidth,self.Ptr, value)

    @property
    def NodeX(self)->int:
        """
        Gets or sets the X-coordinate position of the node.

        Returns:
            int: The current X-coordinate position.
        """
        GetDllLibPpt().ISmartArtNode_get_NodeX.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeX.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeX,self.Ptr)
        return ret

    @NodeX.setter
    def NodeX(self, value:int):
        """
        Sets the X-coordinate position of the node.

        Args:
            value (int): The new X-coordinate value.
        """
        GetDllLibPpt().ISmartArtNode_set_NodeX.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeX,self.Ptr, value)

    @property
    def NodeY(self)->int:
        """
        Gets or sets the Y-coordinate position of the node.

        Returns:
            int: The current Y-coordinate position.
        """
        GetDllLibPpt().ISmartArtNode_get_NodeY.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_NodeY.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_NodeY,self.Ptr)
        return ret

    @NodeY.setter
    def NodeY(self, value:int):
        """
        Sets the Y-coordinate position of the node.

        Args:
            value (int): The new Y-coordinate value.
        """
        GetDllLibPpt().ISmartArtNode_set_NodeY.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_NodeY,self.Ptr, value)

    @property
    def TrChanged(self)->bool:
        """
        Indicates whether the node's transformation has been modified.

        Returns:
            bool: True if transformation changed, False otherwise.
        """
        GetDllLibPpt().ISmartArtNode_get_TrChanged.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_TrChanged.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNode_get_TrChanged,self.Ptr)
        return ret

    @TrChanged.setter
    def TrChanged(self, value:bool):
        """
        Flags the node's transformation state as modified.

        Args:
            value (bool): True to mark as changed, False otherwise.
        """
        GetDllLibPpt().ISmartArtNode_set_TrChanged.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_TrChanged,self.Ptr, value)

    @property

    def FillFormat(self)->'FillFormat':
        """
        Gets or sets the fill formatting properties for the node.

        Returns:
            FillFormat: The fill color and pattern settings of the node.
        """
        GetDllLibPpt().ISmartArtNode_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNode_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNode_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @FillFormat.setter
    def FillFormat(self, value:'FillFormat'):
        """
        Sets the fill formatting properties for the node.

        Args:
            value (FillFormat): The fill settings to apply to the node.
        """
        GetDllLibPpt().ISmartArtNode_set_FillFormat.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNode_set_FillFormat,self.Ptr, value.Ptr)

