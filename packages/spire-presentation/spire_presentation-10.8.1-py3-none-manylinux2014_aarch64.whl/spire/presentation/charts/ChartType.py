from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartType(Enum):
    """
    Represents a type of chart.
   
    """
    ColumnClustered = 0
    ColumnStacked = 1
    Column100PercentStacked = 2
    Column3DClustered = 3
    Column3DStacked = 4
    Column3D100PercentStacked = 5
    Column3D = 6
    CylinderClustered = 7
    CylinderStacked = 8
    Cylinder100PercentStacked = 9
    Cylinder3DClustered = 10
    ConeClustered = 11
    ConeStacked = 12
    Cone100PercentStacked = 13
    Cone3DClustered = 14
    PyramidClustered = 15
    PyramidStacked = 16
    Pyramid100PercentStacked = 17
    Pyramid3DClustered = 18
    Line = 19
    LineStacked = 20
    Line100PercentStacked = 21
    LineMarkers = 22
    LineMarkersStacked = 23
    LineMarkers100PercentStacked = 24
    Line3D = 25
    Pie = 26
    Pie3D = 27
    PieOfPie = 28
    PieExploded = 29
    Pie3DExploded = 30
    PieBar = 31
    Bar100PercentStacked = 32
    Bar3DClustered = 33
    BarClustered = 34
    BarStacked = 35
    Bar3DStacked = 36
    Bar3D100PercentStacked = 37
    CylinderClusteredHorizontal = 38
    CylinderStackedHorizontal = 39
    CylinderPercentsStackedHorizontal = 40
    ConeClusteredHorizontal = 41
    ConeStackedHorizontal = 42
    ConePercentsStackedHorizontal = 43
    PyramidClusteredHorizontal = 44
    PyramidStackedHorizontal = 45
    PyramidPercentsStackedHorizontal = 46
    Area = 47
    AreaStacked = 48
    Area100PercentStacked = 49
    Area3D = 50
    Area3DStacked = 51
    Area3D100PercentStacked = 52
    ScatterMarkers = 53
    ScatterSmoothLinesAndMarkers = 54
    ScatterSmoothLines = 55
    ScatterStraightLinesAndMarkers = 56
    ScatterStraightLines = 57
    StockHighLowClose = 58
    StockOpenHighLowCase = 59
    StockVolumeHighLowCase = 60
    StockVolumeOpenHighLowCase = 61
    Surface3D = 62
    Surface3DNoColor = 63
    Contour = 64
    ContourNoColor = 65
    Doughnut = 66
    DoughnutExploded = 67
    Bubble = 68
    Bubble3D = 69
    Radar = 70
    RadarMarkers = 71
    RadarFilled = 72
    Funnel = 73
    WaterFall = 74
    BoxAndWhisker = 75
    Histogram = 76
    Pareto = 77
    TreeMap = 78
    SunBurst = 79
    Map = 80

