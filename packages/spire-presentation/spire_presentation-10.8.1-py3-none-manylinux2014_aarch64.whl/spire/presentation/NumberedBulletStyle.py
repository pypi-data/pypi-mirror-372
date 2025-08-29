from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class NumberedBulletStyle(Enum):
    """
    Represents the style of the numbered bullets.
    
    """
    none = -1
    BulletAlphaLCPeriod = 0
    BulletAlphaUCPeriod = 1
    BulletArabicParenRight = 2
    BulletArabicPeriod = 3
    BulletRomanLCParenBoth = 4
    BulletRomanLCParenRight = 5
    BulletRomanLCPeriod = 6
    BulletRomanUCPeriod = 7
    BulletAlphaLCParenBoth = 8
    BulletAlphaLCParenRight = 9
    BulletAlphaUCParenBoth = 10
    BulletAlphaUCParenRight = 11
    BulletArabicParenBoth = 12
    BulletArabicPlain = 13
    BulletRomanUCParenBoth = 14
    BulletRomanUCParenRight = 15
    BulletSimpChinPlain = 16
    BulletSimpChinPeriod = 17
    BulletCircleNumDBPlain = 18
    BulletCircleNumWDWhitePlain = 19
    BulletCircleNumWDBlackPlain = 20
    BulletTradChinPlain = 21
    BulletTradChinPeriod = 22
    BulletArabicAlphaDash = 23
    BulletArabicAbjadDash = 24
    BulletHebrewAlphaDash = 25
    BulletKanjiKoreanPlain = 26
    BulletKanjiKoreanPeriod = 27
    BulletArabicDBPlain = 28
    BulletArabicDBPeriod = 29
    BulletThaiAlphaPeriod = 30
    BulletThaiAlphaParenRight = 31
    BulletThaiAlphaParenBoth = 32
    BulletThaiNumPeriod = 33
    BulletThaiNumParenRight = 34
    BulletThaiNumParenBoth = 35
    BulletHindiAlphaPeriod = 36
    BulletHindiNumPeriod = 37
    BulletKanjiSimpChinDBPeriod = 38
    BulletHindiNumParenRight = 39
    BulletHindiAlpha1Period = 40

