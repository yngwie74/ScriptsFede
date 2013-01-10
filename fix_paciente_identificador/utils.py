# -*- coding: utf-8 -*-

from System.Globalization import CharUnicodeInfo, UnicodeCategory
from System.Text import NormalizationForm


def limpia(s):
    return ' '.join((s or '').strip().split())


_NONSPACING_MARK_OR_PUNCTUATION = frozenset([UnicodeCategory.NonSpacingMark, UnicodeCategory.OtherPunctuation])

_category_of = CharUnicodeInfo.GetUnicodeCategory


def es_diacritico(c):
    return _category_of(c) == UnicodeCategory.NonSpacingMark


def es_marca_o_puntuacion(c):
    return _category_of(c) in _NONSPACING_MARK_OR_PUNCTUATION


def sin_acentos(s, filtro=es_marca_o_puntuacion):
    formd = s.Normalize(NormalizationForm.FormD)
    chars = ''.join(c for c in formd if not filtro(c))
    return chars.Normalize(NormalizationForm.FormC)


def primero(*args, **kwds):
    try:
        return next(*args, **kwds)
    except StopIteration:
        pass

