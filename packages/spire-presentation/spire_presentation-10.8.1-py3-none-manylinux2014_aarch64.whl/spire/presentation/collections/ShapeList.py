from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple

from plum.dispatcher import Dispatcher
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeList (SpireObject) :
    """
    Represents a collection of shapes on a presentation slide.
    
    This class provides methods to manage and manipulate shapes including adding, 
    removing, accessing, and converting shapes. It supports various shape types 
    including charts, images, videos, audio, tables, and smart art.
    """
   
    @dispatch
    def __getitem__(self, key):
        """
        Gets the shape at the specified index.
        
        Args:
            key: Index of the shape to retrieve
            
        Returns:
            IShape: The shape object at the specified index
        """
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ShapeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeList_get_Item.restype=IntPtrWithTypeName
        intPtrWithType = CallCFunction(GetDllLibPpt().ShapeList_get_Item,self.Ptr, key)
        ret = None if intPtrWithType==None else self._create(intPtrWithType)
        return ret

    @staticmethod
    def _create(intPtrWithTypeName:IntPtrWithTypeName)->'IShape':
        ret = None
        if intPtrWithTypeName == None :
            return ret
        intPtr = intPtrWithTypeName.intPtr[0] + (intPtrWithTypeName.intPtr[1]<<32)
        strName = PtrToStr(intPtrWithTypeName.typeName)
        if(strName == 'GroupShape'):
            ret = GroupShape(intPtr)
        elif (strName == 'IChart'):
            ret = IChart(intPtr)
        elif (strName == 'IAudio'):
            ret = IAudio(intPtr)
        elif (strName == 'IAutoShape'):
            ret = IAutoShape(intPtr)
        elif (strName == 'IEmbedImage'):
            ret = SlidePicture(intPtr)
        elif (strName == 'ITable'):
            ret = ITable(intPtr)
        elif (strName == 'IVideo'):
            ret = IVideo(intPtr)
        elif (strName == 'IOleObject'):
            ret = IOleObject(intPtr)
        elif (strName == 'ISmartArt'):
            ret = ISmartArt(intPtr)
        elif (strName == 'ShapeNode'):
            ret = ShapeNode(intPtr)
        else:
            ret = IShape(intPtr)

        return ret


    def GetEnumerator(self)->'IEnumerator':
        """
        Gets an enumerator that iterates through the paragraph collection.
        
        Returns:
            IEnumerator: An enumerator that can be used to iterate through the collection
        """
        GetDllLibPpt().ShapeList_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


    @property

    def Parent(self)->'SpireObject':
        """
        Gets parent object for the shapes collection.
        
        Returns:
            SpireObject: Parent object of the shape collection
        """
        GetDllLibPpt().ShapeList_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    def AddFromHtml(self ,htmlText:str):
        """
        Adds text from specified HTML string.
        
        Args:
            htmlText: HTML text to add as shapes
        """
        
        htmlTextPtr = StrToPtr(htmlText)
        GetDllLibPpt().ShapeList_AddFromHtml.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddFromHtml,self.Ptr,htmlTextPtr)

    def AddFromSVG(self ,svgFilePath:str,rectangle:'RectangleF'):
        """
        Adds shapes from an SVG file.
        
        Args:
            svgFilePath: Path to SVG file
            rectangle: Bounding rectangle for the SVG content
        """
        
        svgFilePathPtr = StrToPtr(svgFilePath)
        intPtrrectangle:c_void_p = rectangle.Ptr
        GetDllLibPpt().ShapeList_AddFromSVG.argtypes=[c_void_p ,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddFromSVG,self.Ptr,svgFilePathPtr,intPtrrectangle)

    
    def AddFromSVGAsShapes(self ,svgFilePath:str):
        """
        Adds shapes from an SVG file.
        
        Args:
            svgFilePath: Path to SVG file.
        """
        
        svgFilePathPtr = StrToPtr(svgFilePath)
        GetDllLibPpt().ShapeList_AddFromSVGAsShapes.argtypes=[c_void_p ,c_char_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddFromSVGAsShapes,self.Ptr,svgFilePathPtr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeList_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeList_Equals,self.Ptr, intPtrobj)
        return ret

    @property
    def Count(self)->int:
        """
        Gets the number of elements actually contained in the collection.
           
        """
        GetDllLibPpt().ShapeList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ShapeList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'IShape':
        """
        Gets the element at the specified index.
           
        """
        
        GetDllLibPpt().ShapeList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else IShape(intPtr)
        return ret

    def SaveAsImage(self ,shapeIndex:int, dpiX:int = 96,dpiY:int=96)->'Stream':
        """
        Saves shapes to an image stream.
        
        Args:
            shapeIndex: Index of the shape to save
            dpiX: Horizontal DPI (default 96)
            dpiY: Vertical DPI (default 96)
            
        Returns:
            Stream: Image data stream
        """

        GetDllLibPpt().ShapeList_SaveAsImageDpi.argtypes=[c_void_p ,c_int,c_int,c_int]
        GetDllLibPpt().ShapeList_SaveAsImageDpi.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_SaveAsImageDpi,self.Ptr, shapeIndex,dpiX,dpiY)
        ret = None if intPtr==None else Stream(intPtr)
        return ret



    def SaveAsEMF(self ,shapeIndex:int,filePath:str):
        """
        Saves shapes to EMF format.
        
        Args:
            shapeIndex: Index of the shape to save
            filePath: Output file path
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_SaveAsEMF.argtypes=[c_void_p ,c_int,c_char_p]
        CallCFunction(GetDllLibPpt().ShapeList_SaveAsEMF,self.Ptr, shapeIndex,filePathPtr)


    def CreateChart(self ,baseChart:'IChart',rectangle:'RectangleF',nIndex:int)->'IChart':
        """
        Clones a chart and inserts it into shapes.
        
        Args:
            baseChart: Source chart to clone
            rectangle: Bounding rectangle for new chart
            nIndex: Insertion index (-1 for append)
            
        Returns:
            IChart: Newly created chart
        """
        intPtrbaseChart:c_void_p = baseChart.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_CreateChart.argtypes=[c_void_p ,c_void_p,c_void_p,c_int]
        GetDllLibPpt().ShapeList_CreateChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_CreateChart,self.Ptr, intPtrbaseChart,intPtrrectangle,nIndex)
        ret = None if intPtr==None else IChart(intPtr)
        return ret

    
    def AppendChartInit(self ,type:ChartType,rectangle:RectangleF,init:bool)->'IChart':
        """
        Adds a new chart with initialization option.
        
        Args:
            type: Type of chart to create
            rectangle: Bounding rectangle for chart
            init: Initialize with default data
            
        Returns:
            IChart: New chart instance
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendChart.argtypes=[c_void_p ,c_int,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendChart.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendChart,self.Ptr, enumtype,intPtrrectangle,init)
        ret = None if intPtr==None else IChart(intPtr)
        return ret

    def AppendChart(self ,type:ChartType,rectangle:RectangleF)->'IChart':
        """
        Adds a new chart with default initialization.
        
        Args:
            type: Type of chart to create
            rectangle: Bounding rectangle for chart
            
        Returns:
            IChart: New chart instance
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendChartTR.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendChartTR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendChartTR,self.Ptr, enumtype,intPtrrectangle)
        ret = None if intPtr==None else IChart(intPtr)
        return ret



    def AppendSmartArt(self ,x:float,y:float,width:float,height:float,layoutType:'SmartArtLayoutType')->'ISmartArt':
        """
        Adds a new SmartArt graphic.
        
        Args:
            x: X-coordinate of bounding rectangle
            y: Y-coordinate of bounding rectangle
            width: Width of bounding rectangle
            height: Height of bounding rectangle
            layoutType: SmartArt layout type
            
        Returns:
            ISmartArt: New SmartArt instance
        """
        enumlayoutType:c_int = layoutType.value

        GetDllLibPpt().ShapeList_AppendSmartArt.argtypes=[c_void_p ,c_float,c_float,c_float,c_float,c_int]
        GetDllLibPpt().ShapeList_AppendSmartArt.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendSmartArt,self.Ptr, x,y,width,height,enumlayoutType)
        ret = None if intPtr==None else ISmartArt(intPtr)
        return ret



    def InsertChart(self ,index:int,type:'ChartType',rectangle:'RectangleF',init:bool):
        """
        Inserts a new chart at specified position.
        
        Args:
            index: Insertion index
            type: Type of chart to create
            rectangle: Bounding rectangle for chart
            init: Initialize with default data
        """
        enumtype:c_int = type.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertChart.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertChart,self.Ptr, index,enumtype,intPtrrectangle,init)

    def AppendOleObject(self ,objectName:str,objectData:'Stream',rectangle:RectangleF)->IOleObject:
        """
        Adds a new OLE object.
        
        Args:
            objectName: Name of the OLE object
            objectData: Data stream for the object
            rectangle: Bounding rectangle
            
        Returns:
            IOleObject: New OLE object instance
        """
        intPtrobjectData:c_void_p = objectData.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        objectNamePtr = StrToPtr(objectName)
        GetDllLibPpt().ShapeList_AppendOleObject.argtypes=[c_void_p ,c_char_p,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendOleObject.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendOleObject,self.Ptr,objectNamePtr,intPtrobjectData,intPtrrectangle)
        ret = None if intPtr==None else IOleObject(intPtr)
        return ret
#


#    @dispatch
#
#    def AppendOleObject(self ,objectName:str,objectData:'Byte[]',rectangle:RectangleF)->IOleObject:
#        """
#    <summary>
#        Add a new OleObject to Collection
#    </summary>
#    <param name="objectName">Object Name</param>
#    <param name="objectData">Object Data</param>
#    <param name="rectangle">Rectangle should be inserted.</param>
#    <returns></returns>
#        """
#        #arrayobjectData:ArrayTypeobjectData = ""
#        countobjectData = len(objectData)
#        ArrayTypeobjectData = c_void_p * countobjectData
#        arrayobjectData = ArrayTypeobjectData()
#        for i in range(0, countobjectData):
#            arrayobjectData[i] = objectData[i].Ptr
#
#        intPtrrectangle:c_void_p = rectangle.Ptr
#
#        GetDllLibPpt().ShapeList_AppendOleObjectOOR.argtypes=[c_void_p ,c_wchar_p,ArrayTypeobjectData,c_void_p]
#        GetDllLibPpt().ShapeList_AppendOleObjectOOR.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendOleObjectOOR,self.Ptr, objectName,arrayobjectData,intPtrrectangle)
#        ret = None if intPtr==None else IOleObject(intPtr)
#        return ret
#


    def InsertOleObject(self ,index:int,objectName:str,objectData:'Stream',rectangle:RectangleF):
        """
        Inserts an OLE object at specified position.
        
        Args:
            index: Insertion index
            objectName: Name of the OLE object
            objectData: Data stream for the object
            rectangle: Bounding rectangle
        """
        intPtrobjectData:c_void_p = objectData.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        objectNamePtr = StrToPtr(objectName)
        GetDllLibPpt().ShapeList_InsertOleObject.argtypes=[c_void_p ,c_int,c_char_p,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertOleObject,self.Ptr, index,objectNamePtr,intPtrobjectData,intPtrrectangle)


#    @dispatch
#
#    def InsertOleObject(self ,index:int,objectName:str,objectData:'Byte[]',rectangle:RectangleF):
#        """
#    <summary>
#        Insert a object to collection.
#    </summary>
#    <param name="index">Index should be inserted.</param>
#    <param name="objectName">Object name</param>
#    <param name="objectData">Object data</param>
#    <param name="rectangle">Rectangle should be inserted</param>
#        """
#        #arrayobjectData:ArrayTypeobjectData = ""
#        countobjectData = len(objectData)
#        ArrayTypeobjectData = c_void_p * countobjectData
#        arrayobjectData = ArrayTypeobjectData()
#        for i in range(0, countobjectData):
#            arrayobjectData[i] = objectData[i].Ptr
#
#        intPtrrectangle:c_void_p = rectangle.Ptr
#
#        GetDllLibPpt().ShapeList_InsertOleObjectIOOR.argtypes=[c_void_p ,c_int,c_wchar_p,ArrayTypeobjectData,c_void_p]
#        CallCFunction(GetDllLibPpt().ShapeList_InsertOleObjectIOOR,self.Ptr, index,objectName,arrayobjectData,intPtrrectangle)

   
    def AppendVideoMedia(self ,filePath:str,rectangle:RectangleF)->'IVideo':
        """
        Adds a new video (internal link mode).
        
        Args:
            filePath: Path to video file
            rectangle: Bounding rectangle
            
        Returns:
            IVideo: New video object
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendVideoMedia.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendVideoMedia.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMedia,self.Ptr,filePathPtr,intPtrrectangle)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret
    
    def AppendVideoMediaLink(self ,filePath:str,rectangle:RectangleF,isInnerLink:bool)->'IVideo':
        """
        Adds a new video with link option.
        
        Args:
            filePath: Path to video file
            rectangle: Bounding rectangle
            isInnerLink: Use internal link
            
        Returns:
            IVideo: New video object
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendVideoMediaFRI.argtypes=[c_void_p ,c_char_p,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendVideoMediaFRI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMediaFRI,self.Ptr,filePathPtr,intPtrrectangle,isInnerLink)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret


    def AppendVideoMediaByStream(self ,stream:Stream,rectangle:RectangleF)->'IVideo':
        """
        Adds a new video from stream.
        
        Args:
            stream: Video data stream
            rectangle: Bounding rectangle
            
        Returns:
            IVideo: New video object
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendVideoMediaSR.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendVideoMediaSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendVideoMediaSR,self.Ptr, intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IVideo(intPtr)
        return ret



    def InsertVideoMedia(self ,index:int,filePath:str,rectangle:'RectangleF'):
        """
        Inserts a video at specified position.
        
        Args:
            index: Insertion index
            filePath: Path to video file
            rectangle: Bounding rectangle
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertVideoMedia.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertVideoMedia,self.Ptr, index,filePathPtr,intPtrrectangle)

    @dispatch

    def AppendAudioMediaByRect(self ,rectangle:RectangleF)->'IAudio':
        """
        Adds an audio placeholder (CD audio).
        
        Args:
            rectangle: Bounding rectangle
            
        Returns:
            IAudio: New audio object
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMedia.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMedia.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMedia,self.Ptr, intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,rectangle:RectangleF):
        """
        Inserts an audio placeholder (CD audio).
        
        Args:
            index: Insertion index
            rectangle: Bounding rectangle
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertAudioMedia.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMedia,self.Ptr, index,intPtrrectangle)

    @dispatch

    def AppendAudioMediaByPathXYEmbed(self ,filePath:str,X:float,Y:float,isEmbed:bool)->'IAudio':
        """
        Adds a new audio file with embedding option.
        
        Args:
            filePath: Path to audio file
            X: X-coordinate
            Y: Y-coordinate
            isEmbed: Embed audio in presentation
            
        Returns:
            IAudio: New audio object
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFXYI.argtypes=[c_void_p ,c_char_p,c_float,c_float,c_bool]
        GetDllLibPpt().ShapeList_AppendAudioMediaFXYI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFXYI,self.Ptr,filePathPtr,X,Y,isEmbed)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def AppendAudioMediaByPathXY(self ,filePath:str,X:float,Y:float)->'IAudio':
        """
        Adds a new audio file.
        
        Args:
            filePath: Path to audio file
            X: X-coordinate
            Y: Y-coordinate
            
        Returns:
            IAudio: New audio object
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFXY.argtypes=[c_void_p ,c_char_p,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendAudioMediaFXY.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFXY,self.Ptr,filePathPtr,X,Y)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret



    def AppendAudioMediaEmbed(self ,filePath:str,rectangle:RectangleF,isEmbed:bool)->'IAudio':
        """
        Adds a new audio file with rectangle and embed option.
        
        Args:
            filePath: Path to audio file
            rectangle: Bounding rectangle
            isEmbed: Embed audio in presentation
            
        Returns:
            IAudio: New audio object
        """
        filePathPtr = StrToPtr(filePath)
        intPtrrectangle:c_void_p = rectangle.Ptr
        GetDllLibPpt().ShapeList_AppendAudioMediaFRI.argtypes=[c_void_p ,c_char_p,c_void_p,c_bool]
        GetDllLibPpt().ShapeList_AppendAudioMediaFRI.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFRI,self.Ptr,filePathPtr,intPtrrectangle,isEmbed)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret
    
    def AppendAudioMedia(self ,filePath:str,rectangle:RectangleF)->'IAudio':
        """
        Adds a new audio file with rectangle.
        
        Args:
            filePath: Path to audio file
            rectangle: Bounding rectangle
            
        Returns:
            IAudio: New audio object
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_AppendAudioMediaFR.argtypes=[c_void_p ,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMediaFR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaFR,self.Ptr,filePathPtr,intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,rectangle:RectangleF,isEmbed:bool):
        """
        Inserts an audio file with embed option.
        
        Args:
            index: Insertion index
            filePath: Path to audio file
            rectangle: Bounding rectangle
            isEmbed: Embed audio in presentation
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFRI.argtypes=[c_void_p ,c_int,c_char_p,c_void_p,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFRI,self.Ptr, index,filePathPtr,intPtrrectangle,isEmbed)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,rectangle:RectangleF):
        """
        Inserts an audio file.
        
        Args:
            index: Insertion index
            filePath: Path to audio file
            rectangle: Bounding rectangle
        """
        intPtrrectangle:c_void_p = rectangle.Ptr

        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFR.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFR,self.Ptr, index,filePathPtr,intPtrrectangle)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,X:float,Y:float,isEmbed:bool):
        """
        Inserts an audio file with coordinates and embed option.
        
        Args:
            index: Insertion index
            filePath: Path to audio file
            X: X-coordinate
            Y: Y-coordinate
            isEmbed: Embed audio in presentation
        """
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFXYI.argtypes=[c_void_p ,c_int,c_char_p,c_float,c_float,c_bool]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFXYI,self.Ptr, index,filePathPtr,X,Y,isEmbed)

    @dispatch

    def InsertAudioMedia(self ,index:int,filePath:str,X:float,Y:float):
        """
        Inserts an audio file with coordinates.
        
        Args:
            index: Insertion index
            filePath: Path to audio file
            X: X-coordinate
            Y: Y-coordinate
        """
        
        filePathPtr = StrToPtr(filePath)
        GetDllLibPpt().ShapeList_InsertAudioMediaIFXY.argtypes=[c_void_p ,c_int,c_char_p,c_float,c_float]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaIFXY,self.Ptr, index,filePathPtr,X,Y)


    def AppendAudioMediaByStreamRect(self ,stream:Stream,rectangle:RectangleF)->'IAudio':
        """
        Adds a new audio from stream with rectangle.
        
        Args:
            stream: Audio data stream
            rectangle: Bounding rectangle
            
        Returns:
            IAudio: New audio object
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMediaSR.argtypes=[c_void_p ,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendAudioMediaSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaSR,self.Ptr, intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    def AppendAudioMediaByStreamFloat(self ,stream:Stream,X:float,Y:float)->'IAudio':
        """
        Adds a new audio from stream with coordinates.
        
        Args:
            stream: Audio data stream
            X: X-coordinate
            Y: Y-coordinate
            
        Returns:
            IAudio: New audio object
        """
        intPtrstream:c_void_p = stream.Ptr

        GetDllLibPpt().ShapeList_AppendAudioMediaSXY.argtypes=[c_void_p ,c_void_p,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendAudioMediaSXY.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendAudioMediaSXY,self.Ptr, intPtrstream,X,Y)
        ret = None if intPtr==None else IAudio(intPtr)
        return ret


    @dispatch

    def InsertAudioMedia(self ,index:int,stream:Stream,rectangle:RectangleF):
        """
        Inserts an audio from stream.
        
        Args:
            index: Insertion index
            stream: Audio data stream
            rectangle: Bounding rectangle
        """
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertAudioMediaISR.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertAudioMediaISR,self.Ptr, index,intPtrstream,intPtrrectangle)


    def IndexOf(self ,shape:'IShape')->int:
        """
        Gets the index of the first occurrence of a shape.
        
        Args:
            shape: Shape to find
            
        Returns:
            int: Index of the shape in the collection
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_IndexOf.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeList_IndexOf.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeList_IndexOf,self.Ptr, intPtrshape)
        return ret

    @dispatch

    def ZOrder(self ,index:int,shape:IShape):
        """
        Change a shape's zorder.
        Args:
            index:Target index.
            shape:Shape to move.
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_ZOrder.argtypes=[c_void_p ,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_ZOrder,self.Ptr, index,intPtrshape)

#    @dispatch
#
#    def ZOrder(self ,index:int,shapes:'IShape[]'):
#        """
#    <summary>
#        Change shapes's zorder.
#    </summary>
#    <param name="index">target index.</param>
#    <param name="shapes">shapes to move.</param>
#        """
#        #arrayshapes:ArrayTypeshapes = ""
#        countshapes = len(shapes)
#        ArrayTypeshapes = c_void_p * countshapes
#        arrayshapes = ArrayTypeshapes()
#        for i in range(0, countshapes):
#            arrayshapes[i] = shapes[i].Ptr
#
#
#        GetDllLibPpt().ShapeList_ZOrderIS.argtypes=[c_void_p ,c_int,ArrayTypeshapes]
#        CallCFunction(GetDllLibPpt().ShapeList_ZOrderIS,self.Ptr, index,arrayshapes)


    #@dispatch

    def AppendShape(self ,shapeType:ShapeType,rectangle:RectangleF)->'IAutoShape':
        """
        Adds a new shape to the collection.
        
        Args:
            shapeType: Type of shape to create
            rectangle: Bounding rectangle
            
        Returns:
            IAutoShape: New shape instance
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendShape.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendShape.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShape,self.Ptr, enumshapeType,intPtrrectangle)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret


   # @dispatch

    def AppendShapeByPoint(self ,shapeType:ShapeType,start:PointF,end:PointF)->'IAutoShape':
        """
        Adds a new shape defined by start and end points.
        
        Args:
            shapeType: Type of shape to create
            start: Starting point
            end: Ending point
            
        Returns:
            IAutoShape: New shape instance
        """
        enumshapeType:c_int = shapeType.value
        intPtrstart:c_void_p = start.Ptr
        intPtrend:c_void_p = end.Ptr

        GetDllLibPpt().ShapeList_AppendShapeSSE.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendShapeSSE.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShapeSSE,self.Ptr, enumshapeType,intPtrstart,intPtrend)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret



    def AppendRoundRectangle(self ,x:float,y:float,width:float,height:float,radius:float)->'IAutoShape':
        """
        Adds a round rectangle shape.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            width: Width of rectangle
            height: Height of rectangle
            radius: Corner radius
            
        Returns:
            IAutoShape: New shape instance
        """
        
        GetDllLibPpt().ShapeList_AppendRoundRectangle.argtypes=[c_void_p ,c_float,c_float,c_float,c_float,c_float]
        GetDllLibPpt().ShapeList_AppendRoundRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendRoundRectangle,self.Ptr, x,y,width,height,radius)
        ret = None if intPtr==None else IAutoShape(intPtr)
        return ret



    def InsertShape(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF'):
        """
        Inserts a new shape at specified position.
        
        Args:
            index: Insertion index
            shapeType: Type of shape to create
            rectangle: Bounding rectangle
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertShape.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertShape,self.Ptr, index,enumshapeType,intPtrrectangle)


    def InsertRoundRectangle(self ,index:int,x:float,y:float,width:float,height:float,radius:float):
        """
        Inserts a round rectangle shape.
        
        Args:
            index: Insertion index
            x: X-coordinate
            y: Y-coordinate
            width: Width of rectangle
            height: Height of rectangle
            radius: Corner radius
        """
        
        GetDllLibPpt().ShapeList_InsertRoundRectangle.argtypes=[c_void_p ,c_int,c_float,c_float,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().ShapeList_InsertRoundRectangle,self.Ptr, index,x,y,width,height,radius)


    def AppendShapeConnector(self ,shapeType:'ShapeType',rectangle:'RectangleF')->'IShape':
        """
        Adds a new connector shape.
        
        Args:
            shapeType: Type of connector
            rectangle: Bounding rectangle
            
        Returns:
            IShape: New connector shape
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendShapeConnector.argtypes=[c_void_p ,c_int,c_void_p]
        GetDllLibPpt().ShapeList_AppendShapeConnector.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendShapeConnector,self.Ptr, enumshapeType,intPtrrectangle)
        ret = None if intPtr==None else IShape(intPtr)
        return ret



    def InsertShapeConnector(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF'):
        """
        Inserts a new connector shape.
        
        Args:
            index: Insertion index
            shapeType: Type of connector
            rectangle: Bounding rectangle
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_InsertShapeConnector.argtypes=[c_void_p ,c_int,c_int,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertShapeConnector,self.Ptr, index,enumshapeType,intPtrrectangle)

    def AppendEmbedImageByImageData(self ,shapeType:ShapeType,embedImage:'IImageData',rectangle:RectangleF)->'IEmbedImage':
        """
        Adds a new embedded image from image data.
        
        Args:
            shapeType: Type of image shape
            embedImage: Image data object
            rectangle: Bounding rectangle
            
        Returns:
            IEmbedImage: New image shape
        """
        enumshapeType:c_int = shapeType.value
        intPtrembedImage:c_void_p = embedImage.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendEmbedImage.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImage.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImage,self.Ptr, enumshapeType,intPtrembedImage,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret


    def AppendEmbedImageByPath(self ,shapeType:ShapeType,fileName:str,rectangle:RectangleF)->'IEmbedImage':
        """
        Adds a new embedded image from file.
        
        Args:
            shapeType: Type of image shape
            fileName: Path to image file
            rectangle: Bounding rectangle
            
        Returns:
            IEmbedImage: New image shape
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr

        fileNamePtr = StrToPtr(fileName)
        GetDllLibPpt().ShapeList_AppendEmbedImageSFR.argtypes=[c_void_p ,c_int,c_char_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImageSFR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImageSFR,self.Ptr, enumshapeType,fileNamePtr,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret

    def AppendEmbedImageByStream(self ,shapeType:ShapeType,stream:Stream,rectangle:RectangleF)->'IEmbedImage':
        """
        Adds a new embedded image from stream.
        
        Args:
            shapeType: Type of image shape
            stream: Image data stream
            rectangle: Bounding rectangle
            
        Returns:
            IEmbedImage: New image shape
        """
        enumshapeType:c_int = shapeType.value
        intPtrstream:c_void_p = stream.Ptr
        intPtrrectangle:c_void_p = rectangle.Ptr

        GetDllLibPpt().ShapeList_AppendEmbedImageSSR.argtypes=[c_void_p ,c_int,c_void_p,c_void_p]
        GetDllLibPpt().ShapeList_AppendEmbedImageSSR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendEmbedImageSSR,self.Ptr, enumshapeType,intPtrstream,intPtrrectangle)
        ret = None if intPtr==None else IEmbedImage(intPtr)
        return ret



    def InsertEmbedImage(self ,index:int,shapeType:'ShapeType',rectangle:'RectangleF',embedImage:'IImageData'):
        """
        Inserts an embedded image.
        
        Args:
            index: Insertion index
            shapeType: Type of image shape
            rectangle: Bounding rectangle
            embedImage: Image data object
        """
        enumshapeType:c_int = shapeType.value
        intPtrrectangle:c_void_p = rectangle.Ptr
        intPtrembedImage:c_void_p = embedImage.Ptr

        GetDllLibPpt().ShapeList_InsertEmbedImage.argtypes=[c_void_p ,c_int,c_int,c_void_p,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_InsertEmbedImage,self.Ptr, index,enumshapeType,intPtrrectangle,intPtrembedImage)


    def AddShape(self ,shape:'Shape'):
        """
        Adds an existing shape to the collection.
        
        Args:
            shape: Shape to add
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_AddShape.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_AddShape,self.Ptr, intPtrshape)


    def AppendTable(self ,x:float,y:float,widths:List[float],heights:List[float])->'ITable':
        """
        Adds a new table to the collection.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            widths: List of column widths
            heights: List of row heights
            
        Returns:
            ITable: New table instance
        """
        #arraywidths:ArrayTypewidths = ""
        countwidths = len(widths)
        ArrayTypewidths = c_double * countwidths
        arraywidths = ArrayTypewidths()
        for i in range(0, countwidths):
            arraywidths[i] = widths[i]

        #arrayheights:ArrayTypeheights = ""
        countheights = len(heights)
        ArrayTypeheights = c_double * countheights
        arrayheights = ArrayTypeheights()
        for i in range(0, countheights):
            arrayheights[i] = heights[i]


        GetDllLibPpt().ShapeList_AppendTable.argtypes=[c_void_p ,c_float,c_float,ArrayTypewidths,c_int,ArrayTypeheights,c_int]
        GetDllLibPpt().ShapeList_AppendTable.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeList_AppendTable,self.Ptr, x,y,arraywidths,countwidths,arrayheights,countheights)
        ret = None if intPtr==None else ITable(intPtr)
        return ret



    def InsertTable(self ,index:int,x:float,y:float,columnWidths:List[float],rowHeights:List[float]):
        """
        Inserts a new table at specified position.
        
        Args:
            index: Insertion index
            x: X-coordinate
            y: Y-coordinate
            columnWidths: List of column widths
            rowHeights: List of row heights
        """
        #arraycolumnWidths:ArrayTypecolumnWidths = ""
        countcolumnWidths = len(columnWidths)
        ArrayTypecolumnWidths = c_double * countcolumnWidths
        arraycolumnWidths = ArrayTypecolumnWidths()
        for i in range(0, countcolumnWidths):
            arraycolumnWidths[i] = columnWidths[i]

        #arrayrowHeights:ArrayTyperowHeights = ""
        countrowHeights = len(rowHeights)
        ArrayTyperowHeights = c_double * countrowHeights
        arrayrowHeights = ArrayTyperowHeights()
        for i in range(0, countrowHeights):
            arrayrowHeights[i] = rowHeights[i]


        GetDllLibPpt().ShapeList_InsertTable.argtypes=[c_void_p ,c_int,c_float,c_float,ArrayTypecolumnWidths,ArrayTyperowHeights]
        CallCFunction(GetDllLibPpt().ShapeList_InsertTable,self.Ptr, index,x,y,arraycolumnWidths,arrayrowHeights)


    def RemoveAt(self ,index:int):
        """
        Removes the shape at the specified index.
        
        Args:
            index: Index of shape to remove
        """
        
        GetDllLibPpt().ShapeList_RemoveAt.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ShapeList_RemoveAt,self.Ptr, index)


    def Remove(self ,shape:'IShape'):
        """
        Removes a specific shape from the collection.
        
        Args:
            shape: Shape to remove
        """
        intPtrshape:c_void_p = shape.Ptr

        GetDllLibPpt().ShapeList_Remove.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ShapeList_Remove,self.Ptr, intPtrshape)

