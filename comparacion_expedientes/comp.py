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

    @property
    def is_successful(self):
        return len(self.errores) == 0

    @property
    def result(self):
        return self._ok_result() \
            if self.is_successful \
            else _error_list(self.errores)

    def _ok_result(self):
        cuantos = len(self.record_source.src_records)
        if cuantos == 0:
            return 'OK\tsin registros en ambos servidores'
        return 'OK\t%d registro(s) igual(es)' % cuantos

    def _load_records(self):
        self.record_source.carga_registros(self.entity)

    def _compare_single_record(self, source, reference):
        key = self.entity.llave_str(source)
        pairs = _mk_property_pairs(source, reference, self.entity)
        return (key, [_comp_error(p, a, b) for (a, b, p) in pairs if a != b])

    def _compare_all_records(self, src_records, ref_records):
        all_errors = \
            [self._compare_single_record(source, reference)
                for (source, reference) in izip(src_records, ref_records)]

        self.errores.extend(
            self._print_errors(key, errors) for key, errors in all_errors if errors)

        return bool(all_errors)

    def _compare_records(self):
        msg_comunes = None

        src_records, ref_records = self.record_source.registros_comunes(self.entity)
        all_correct = self._compare_all_records(src_records, ref_records)

        if all_correct and len(src_records) < len(self.record_source.src_records):
            msg_comunes = '\n\t%d registro(s) igual(es)' % len(src_records)

        solo_origen = self.record_source.solo_origen(self.entity)
        solo_referencia = self.record_source.solo_referencia(self.entity)

        mensajes = (msg_comunes, solo_origen, solo_referencia)
        self.errores.extend(msg for msg in mensajes if msg)
        
    @property
    def didnt_find_data(self):
        return not self.record_source.tiene_datos

    def __call__(self):
        self._load_records()
        self._compare_records()
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
