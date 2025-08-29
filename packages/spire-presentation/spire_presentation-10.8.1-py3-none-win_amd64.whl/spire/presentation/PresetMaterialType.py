from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetMaterialType(Enum):
    """
    Enumerates the types of material presets that can be applied to shapes.
    
    Attributes:
        none: No material preset applied.
        Clear: Transparent material effect.
        DkEdge: Dark edge material effect.
        Flat: Flat, non-reflective material.
        LegacyMatte: Legacy matte finish material.
        LegacyMetal: Legacy metallic material effect.
        LegacyPlastic: Legacy plastic material effect.
        LegacyWireframe: Legacy wireframe material effect.
        Matte: Non-glossy, diffuse material.
        Metal: Reflective metallic material.
        Plastic: Semi-gloss plastic material.
        Powder: Soft, powdery material texture.
        SoftEdge: Material with soft-edged lighting.
        Softmetal: Soft metallic material effect.
        TranslucentPowder: Semi-transparent powdery material.
        WarmMatte: Warm-toned matte finish material.
    """
    none = -1
    Clear = 0
    DkEdge = 1
    Flat = 2
    LegacyMatte = 3
    LegacyMetal = 4
    LegacyPlastic = 5
    LegacyWireframe = 6
    Matte = 7
    Metal = 8
    Plastic = 9
    Powder = 10
    SoftEdge = 11
    Softmetal = 12
    TranslucentPowder = 13
    WarmMatte = 14

