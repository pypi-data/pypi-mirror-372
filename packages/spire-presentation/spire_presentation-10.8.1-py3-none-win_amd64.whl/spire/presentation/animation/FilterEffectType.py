from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FilterEffectType(Enum):
    """
    Represents the types of filter effects that can be applied in presentations.
    
    These effects define various visual transitions between slides or elements.
    """
    none = 0
    """No filter effect applied"""
    
    Barn = 1
    """Barn door transition effect where content splits diagonally"""
    
    Blinds = 2
    """Blinds effect where content is revealed through horizontal or vertical strips"""
    
    Box = 3
    """Box effect where content appears/disappears through a rectangular shape"""
    
    Checkerboard = 4
    """Checkerboard pattern transition where content tiles appear in sequence"""
    
    Circle = 5
    """Circular reveal effect that expands from a center point"""
    
    Diamond = 6
    """Diamond-shaped reveal effect that expands from the center"""
    
    Dissolve = 7
    """Dissolve transition where content gradually fades between slides"""
    
    Fade = 8
    """Simple fade transition between slides or elements"""
    
    Image = 9
    """Custom image-based transition effect"""
    
    Pixelate = 10
    """Pixelation effect that transitions through blocky pixels"""
    
    Plus = 11
    """Plus-sign shaped reveal effect that expands from the center"""
    
    RandomBar = 12
    """Transition with randomly appearing horizontal or vertical bars"""
    
    Slide = 13
    """Slide effect where new content pushes previous content off-screen"""
    
    Stretch = 14
    """Stretching effect that distorts content during transition"""
    
    Strips = 15
    """Diagonal strip transition effect"""
    
    Wedge = 16
    """Wedge-shaped reveal effect that expands from a point"""
    
    Wheel = 17
    """Wheel/spokes effect that rotates around a center point"""
    
    Wipe = 18
    """Wipe effect where new content replaces old content in a directional sweep"""

