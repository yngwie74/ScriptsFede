#!/env/ipy
# -*- coding: utf-8 -*-

from infoentidad import INFO_ENTIDADES

def _ifnone(a):
    return a if not a is None else '<NULL>'

def _comp_error(prop_name, a, b):
    return u'\t%s:\t[%s] != [%s]' % (prop_name, _ifnone(a), _ifnone(b))


def _print_errors(entidad, errores, source):
    if errores:
        errores.sort()
        print 'Diferencias en %s, con %s:' % (entidad.type_name, entidad.llave(source))
        print '\n'.join(error for error in errores)


def _mk_property_pairs(source, reference, entity):
    return ((getattr(source, p), getattr(reference, p), p)
            for p in dir(source)
                if entity.debe_comparar(p) and
                    hasattr(source, p) and
                    hasattr(reference, p))

def _comp_record(source, reference, entidad):
    pairs = _mk_property_pairs(source, reference, entidad)
    errors = [_comp_error(p, a, b) for (a, b, p) in pairs if a != b]
    _print_errors(entidad, errors, source)
    return not errors

def _comp_all_records(_fl_paciente, src_context, ref_context, entidad):
    src_records = entidad.cargaDatos(src_context, _fl_paciente)
    ref_records = entidad.cargaDatos(ref_context, _fl_paciente)

    if len(src_records) != len(ref_records):
        print 'Diferencias en %s:' % entidad.type_name
        print _comp_error('Número de registros no coincide', len(src_records), len(ref_records))
        return

    with_diffs = [
        1 for (source, reference) in zip(src_records, ref_records)
            if _comp_record(source, reference, entidad) == False]

    return not with_diffs


def comp(_fl_paciente, schema, src_context, ref_context):
    with_diffs = [
        entidad for entidad in INFO_ENTIDADES[schema]
            if _comp_all_records(_fl_paciente, src_context, ref_context, entidad) != True]
    return not with_diffs

