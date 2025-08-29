import abc
import collections
import contextlib
import types

from pyplus import stack
from string import (
    whitespace,
    ascii_lowercase,
    ascii_uppercase,
    ascii_letters,
    digits,
    hexdigits,
    octdigits,
    punctuation,
    printable,
)
from typing import *
from typing import __all__ as tall

__all__ = tall + [
    "whitespace",
    "ascii_lowercase",
    "ascii_uppercase",
    "ascii_letters",
    "digits",
    "hexdigits",
    "octdigits",
    "punctuation",
    "printable",
    "abc",
    "collections",
    "contextlib",
    "types",
]

bindigits = "01"


class _LowerLitter:
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = (
        ascii_lowercase
    )


class _UpperLitter:
    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z = (
        ascii_uppercase
    )


class _Punctuation:
    (
        EXCLAMATION,
        DOUBLE_QUOTATION,
        LGO,
        DOLLAR,
        PERCENT,
        AND,
        QUOTATION,
        LEFT_BRACKETS,
        RIGHT_BRACKETS,
        ASTERISK,
        PLUS,
        COMMA,
        MINUS,
        DOT,
        SLASH,
        COLON,
        SEMINON,
        GREATER,
        EQUAL,
        LESS,
        QUESTION,
        T,
        LEFT_SQUARE_BRACKETS,
        BACKSLASH,
        RIGHT_SQUARE_BRACKETS,
        CARET,
        UNERLINE,
        BACKTICK,
        LEFT_CURLY_BRACKETS,
        VERTICAL,
        RIGHT_CURLY_BRACKETS,
        WAVE,
    ) = punctuation


class _DecNumber:
    ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, ZERO = digits


class _HexNumber:
    (
        h_ONE,
        h_TWO,
        h_THREE,
        h_FOUR,
        h_FIVE,
        h_SIX,
        h_SEVEN,
        h_EIGHT,
        h_NINE,
        h_ZERO,
        h_A,
        h_B,
        h_C,
        h_D,
        h_E,
        h_F,
    ) = hexdigits[:-6]


class _OctNumber:
    o_ONE, o_TWO, o_THREE, o_FOUR, o_FIVE, o_SIX, o_SEVEN, o_ZERO = octdigits


class _BinNumber:
    b_ONE, b_ZERO = bindigits


class _OtherType:
    NONE, TRUE, FALSE = None, True, False


class _Litter(_LowerLitter, _UpperLitter): ...


class _Number(_DecNumber, _HexNumber, _OctNumber, _BinNumber): ...


class _AllSimpleTypes(_Litter, _Punctuation, _Number, _OtherType): ...


a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = (
    _AllSimpleTypes.a,
    _AllSimpleTypes.b,
    _AllSimpleTypes.c,
    _AllSimpleTypes.d,
    _AllSimpleTypes.e,
    _AllSimpleTypes.f,
    _AllSimpleTypes.g,
    _AllSimpleTypes.h,
    _AllSimpleTypes.i,
    _AllSimpleTypes.j,
    _AllSimpleTypes.k,
    _AllSimpleTypes.l,
    _AllSimpleTypes.m,
    _AllSimpleTypes.n,
    _AllSimpleTypes.o,
    _AllSimpleTypes.p,
    _AllSimpleTypes.q,
    _AllSimpleTypes.r,
    _AllSimpleTypes.s,
    _AllSimpleTypes.t,
    _AllSimpleTypes.u,
    _AllSimpleTypes.v,
    _AllSimpleTypes.w,
    _AllSimpleTypes.x,
    _AllSimpleTypes.y,
    _AllSimpleTypes.z,
)
A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z = (
    _AllSimpleTypes.A,
    _AllSimpleTypes.B,
    _AllSimpleTypes.C,
    _AllSimpleTypes.D,
    _AllSimpleTypes.E,
    _AllSimpleTypes.F,
    _AllSimpleTypes.G,
    _AllSimpleTypes.H,
    _AllSimpleTypes.I,
    _AllSimpleTypes.J,
    _AllSimpleTypes.K,
    _AllSimpleTypes.L,
    _AllSimpleTypes.M,
    _AllSimpleTypes.N,
    _AllSimpleTypes.O,
    _AllSimpleTypes.P,
    _AllSimpleTypes.Q,
    _AllSimpleTypes.R,
    _AllSimpleTypes.S,
    _AllSimpleTypes.T,
    _AllSimpleTypes.U,
    _AllSimpleTypes.V,
    _AllSimpleTypes.W,
    _AllSimpleTypes.X,
    _AllSimpleTypes.Y,
    _AllSimpleTypes.Z,
)
(
    EXCLAMATION,
    DOUBLE_QUOTATION,
    LGO,
    DOLLAR,
    PERCENT,
    AND,
    QUOTATION,
    LEFT_BRACKETS,
    RIGHT_BRACKETS,
    ASTERISK,
    PLUS,
    COMMA,
    MINUS,
    DOT,
    SLASH,
    COLON,
    SEMINON,
    GREATER,
    EQUAL,
    LESS,
    QUESTION,
    T,
    LEFT_SQUARE_BRACKETS,
    BACKSLASH,
    RIGHT_SQUARE_BRACKETS,
    CARET,
    UNERLINE,
    BACKTICK,
    LEFT_CURLY_BRACKETS,
    VERTICAL,
    RIGHT_CURLY_BRACKETS,
    WAVE,
) = (
    _AllSimpleTypes.EXCLAMATION,
    _AllSimpleTypes.DOUBLE_QUOTATION,
    _AllSimpleTypes.LGO,
    _AllSimpleTypes.DOLLAR,
    _AllSimpleTypes.PERCENT,
    _AllSimpleTypes.AND,
    _AllSimpleTypes.QUOTATION,
    _AllSimpleTypes.LEFT_BRACKETS,
    _AllSimpleTypes.RIGHT_BRACKETS,
    _AllSimpleTypes.ASTERISK,
    _AllSimpleTypes.PLUS,
    _AllSimpleTypes.COMMA,
    _AllSimpleTypes.MINUS,
    _AllSimpleTypes.DOT,
    _AllSimpleTypes.SLASH,
    _AllSimpleTypes.COLON,
    _AllSimpleTypes.SEMINON,
    _AllSimpleTypes.GREATER,
    _AllSimpleTypes.EQUAL,
    _AllSimpleTypes.LESS,
    _AllSimpleTypes.QUESTION,
    _AllSimpleTypes.T,
    _AllSimpleTypes.LEFT_SQUARE_BRACKETS,
    _AllSimpleTypes.BACKSLASH,
    _AllSimpleTypes.RIGHT_SQUARE_BRACKETS,
    _AllSimpleTypes.CARET,
    _AllSimpleTypes.UNERLINE,
    _AllSimpleTypes.BACKTICK,
    _AllSimpleTypes.LEFT_CURLY_BRACKETS,
    _AllSimpleTypes.VERTICAL,
    _AllSimpleTypes.RIGHT_CURLY_BRACKETS,
    _AllSimpleTypes.WAVE,
)
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, ZERO = (
    _AllSimpleTypes.ONE,
    _AllSimpleTypes.TWO,
    _AllSimpleTypes.THREE,
    _AllSimpleTypes.FOUR,
    _AllSimpleTypes.FIVE,
    _AllSimpleTypes.SIX,
    _AllSimpleTypes.SEVEN,
    _AllSimpleTypes.EIGHT,
    _AllSimpleTypes.NINE,
    _AllSimpleTypes.ZERO,
)
(
    h_ONE,
    h_TWO,
    h_THREE,
    h_FOUR,
    h_FIVE,
    h_SIX,
    h_SEVEN,
    h_EIGHT,
    h_NINE,
    h_ZERO,
    h_A,
    h_B,
    h_C,
    h_D,
    h_E,
    h_F,
) = (
    _AllSimpleTypes.h_ONE,
    _AllSimpleTypes.h_TWO,
    _AllSimpleTypes.h_THREE,
    _AllSimpleTypes.h_FOUR,
    _AllSimpleTypes.h_FIVE,
    _AllSimpleTypes.h_SIX,
    _AllSimpleTypes.h_SEVEN,
    _AllSimpleTypes.h_EIGHT,
    _AllSimpleTypes.h_NINE,
    _AllSimpleTypes.h_ZERO,
    _AllSimpleTypes.h_A,
    _AllSimpleTypes.h_B,
    _AllSimpleTypes.h_C,
    _AllSimpleTypes.h_D,
    _AllSimpleTypes.h_E,
    _AllSimpleTypes.h_F,
)
b_ONE, b_ZERO = _AllSimpleTypes.b_ONE, _AllSimpleTypes.b_ZERO
o_ONE, o_TWO, o_THREE, o_FOUR, o_FIVE, o_SIX, o_SEVEN, o_ZERO = (
    _AllSimpleTypes.o_ONE,
    _AllSimpleTypes.o_TWO,
    _AllSimpleTypes.o_THREE,
    _AllSimpleTypes.o_FOUR,
    _AllSimpleTypes.o_FIVE,
    _AllSimpleTypes.o_SIX,
    _AllSimpleTypes.o_SEVEN,
    _AllSimpleTypes.o_ZERO,
)
NONE, TRUE, FALSE = _AllSimpleTypes.NONE, _AllSimpleTypes.TRUE, _AllSimpleTypes.FALSE
