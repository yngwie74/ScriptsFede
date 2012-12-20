#!/bin/env ipy
# -*- coding: utf-8 -*-

from infoentidad import INFO_ENTIDADES
from itertools import izip


class PacienteNoEncontrado(Exception):
    def __init__(self, folio, origen):
        message = 'El paciente %d no existe en el servidor %s' % (folio, origen)
        Exception.__init__(self, message)
        self.folio = folio
        self.origen = origen
# end class


def _ifnone(a):
    return a if not a is None else '<NULL>'

def _comp_error(prop_name, a, b):
    return u'\t%s:\t[%s] != [%s]' % (prop_name, _ifnone(a), _ifnone(b))

def _should_compare(p, a, b):
    return not p.startswith('_')

def _mk_property_pairs(source, reference, entity):
    return ((getattr(source, p), getattr(reference, p), p)
            for p in set(dir(source)) | set(dir(reference))
                if _should_compare(p, source, reference)
                    and entity.debe_comparar(p)
                    and hasattr(source, p)
                    and hasattr(reference, p))

def _error_list(errors, sep='\n'):
    return sep.join(errors)


class Comparison(object):
    def __init__(self, record_source, entity):
        self.record_source = record_source
        self.entity = entity
        self.errores = []
        self.src_records, self.ref_records = [], []

    @property
    def is_successful(self):
        return len(self.errores) == 0

    @property
    def result(self):
        return self._ok_result() \
            if self.is_successful \
            else _error_list(self.errores)

    def _ok_result(self):
        cuantos = len(self.src_records)
        if cuantos == 0:
            return 'OK\tsin registros en ambos servidores'
        return 'OK\t%d registro%s igual%s' % (cuantos, cuantos != 1 and 's' or '', cuantos != 1 and 'es' or '')

    def _load_records(self):
        self.src_records, self.ref_records = self.record_source.registros(self.entity)

    def _record_count_error(self):
        self.errores.append(_comp_error('\n\tNúmero de registros no coincide', len(self.src_records), len(self.ref_records)))

    def _can_compare(self):
        return self.record_source.son_comparables(self.src_records, self.ref_records)

    def _comp_record(self, source, reference):
        key = self.entity.key(source)
        pairs = _mk_property_pairs(source, reference, self.entity)
        return (key, [_comp_error(p, a, b) for (a, b, p) in pairs if a != b])

    def _compare_all_records(self):
        all_errors = \
            [self._comp_record(source, reference)
                for (source, reference) in izip(self.src_records, self.ref_records)]
        self.errores.extend(
            self._print_errors(key, errors) for key, errors in all_errors if errors)

    @property
    def didnt_find_data(self):
        return len(self.src_records) == len(self.ref_records) == 0

    def __call__(self):
        self._load_records()
        if not self._can_compare():
            self._record_count_error()
        else:
            self._compare_all_records()
        return self

    def __str__(self):
        return "%s:\t%s" % (self.entity.type_name, self.result)

    def _print_errors(self, key, errors):
        errors.sort()
        return '\n\tcon %s:\n\t%s' % (key, _error_list(errors, '\n\t'))
#end class Comparison


def comp(schema, rsrc, verbose=False):
    result = is_first = True
    comparisons = (Comparison(rsrc, entidad) for entidad in INFO_ENTIDADES[schema])
    for comparison in comparisons:
        if not comparison().is_successful or verbose:
            print comparison
            result = False
        elif comparison.didnt_find_data and is_first:
            raise PacienteNoEncontrado(rsrc.folio_paciente, rsrc.source_name)
        is_first = False
    return result
