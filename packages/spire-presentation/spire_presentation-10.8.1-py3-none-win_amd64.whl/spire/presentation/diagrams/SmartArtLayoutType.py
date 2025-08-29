from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SmartArtLayoutType(Enum):
    """
    Enumerates layout types for SmartArt diagrams.
    """
    BasicBlockList = 0
    PictureCaptionList = 1
    VerticalBulletList = 2
    VerticalBoxList = 3
    HorizontalBulletList = 4
    PictureAccentList = 5
    BendingPictureAccentList = 6
    StackedList = 7
    DetailedProcess = 8
    GroupedList = 9
    HorizontalPictureList = 10
    ContinuousPictureList = 11
    VerticalPictureList = 12
    VerticalPictureAccentList = 13
    VerticalBlockList = 14
    VerticalChevronList = 15
    VerticalArrowList = 16
    TrapezoidList = 17
    TableList = 18
    PyramidList = 19
    TargetList = 20
    HierarchyList = 21
    TableHierarhy = 22
    BasicProcess = 23
    AccentProcess = 24
    PictureAccentProcess = 25
    AlternatingFlow = 26
    ContinuousBlockProcess = 27
    ContinuousArrowProcess = 28
    ProcessArrows = 29
    BasicTimeline = 30
    BasicChevronProcess = 31
    ClosedChevronProcess = 32
    ChevronList = 33
    VerticalProcess = 34
    StaggeredProcess = 35
    ProcessList = 36
    SegmentedProcess = 37
    BasicBendingProcess = 38
    RepeatingBendingProcess = 39
    VerticalBendingProcess = 40
    UpwardArrow = 41
    CircularBendingProcess = 42
    Equation = 43
    VerticalEquation = 44
    Funnel = 45
    Gear = 46
    ArrowRibbon = 47
    OpposingArrows = 48
    ConvergingArrows = 49
    DivergingArrows = 50
    BasicCycle = 51
    TextCycle = 52
    BlockCycle = 53
    NondirectionalCycle = 54
    ContinuousCycle = 55
    MultidirectionalCycle = 56
    SegmentedCycle = 57
    BasicPie = 58
    RadialCycle = 59
    BasicRadial = 60
    DivergingRadial = 61
    RadialVenn = 62
    CycleMatrix = 63
    OrganizationChart = 64
    Hierarchy = 65
    LabeledHierarhy = 66
    HorizontalHierarhy = 67
    HorizontalLabeledHierarhy = 68
    Balance = 69
    CounterbalanceArrow = 70
    SegmentedPyramid = 71
    NestedTarget = 72
    ConvergingRadial = 73
    RadialList = 74
    BasicTarget = 75
    BasicVenn = 76
    LinearVenn = 77
    StacketVenn = 78
    BasicMatrix = 79
    TitledMatrix = 80
    GridMatrix = 81
    BasicPyramid = 82
    InvertedPyramid = 83
    PictureOrganizationChart = 84
    NameAndTitleOrganizationChart = 85

